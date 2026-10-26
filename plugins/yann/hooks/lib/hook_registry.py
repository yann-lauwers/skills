#!/usr/bin/env python3
"""Reconcile the check registry against the source and against the decision log.

Three directions, because each hides a different defect:

  logged, not registered   a check ships verdicts nobody catalogued
  registered, not logged   a check nobody can prove ever ran — zero rows and a
                           broken wiring produce the same artifact, so this is
                           where a silently dead guard hides
  in source, not registered   an id minted at a call site and never catalogued

Ids are read from the syntax tree rather than by grep. Every check here passes its
id to the sink through a variable, so a regex inventory finds none of them and
reports a clean estate — the shape that let 115 ids go missing in the estate this
convention comes from.

Two consumers share this: the `hook-decisions` command and the session-start
reminder. One copy, because a reconciliation that disagrees with itself is worse
than none.
"""
import ast
import collections
import glob
import os
import re

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(HOOKS, "REGISTRY.md")
REGISTRY_PARTS = os.path.join(HOOKS, "registry")

# Shell passes the id as a bare word: `log_decision bash-destructive-deny deny "$1" "$sid"`.
ID_IN_SHELL = re.compile(r"""log_decision\s+["']?([a-z][a-z0-9-]{2,})["']?""")
ID_SHAPE = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)+")


# A retirement is written in prose, and prose pluralises: one id or a comma list,
# under "Retired id —" or "Retired ids —". Reading only the singular form loses a
# whole clause silently — the ids stay documented and the reconciliation reports
# them as undocumented, which is the one failure mode this parser exists to catch.
RETIRED_CLAUSE = re.compile(
    r"Retired ids?\s*[—-]\s*((?:`[a-z][a-z0-9-]+`(?:\s*,\s*|\s+and\s+)?)+)")
BACKTICKED = re.compile(r"`([a-z][a-z0-9-]+)`")


def registry_paths():
    return [REGISTRY] + sorted(glob.glob(os.path.join(REGISTRY_PARTS, "*.md")))


def registry_text(path=None):
    if path:
        return open(path, errors="replace").read()
    return "\n".join(open(p, errors="replace").read() for p in registry_paths())


def registry_ids(path=None):
    """(live ids, retired ids) from the registry's tables and its prose.

    Retired ids come from prose because that is where the registry keeps them: a
    row carrying one can only be historical, so counting it as unregistered would
    report a defect the registry has already resolved.
    """
    live, retired = set(), set()
    try:
        text = registry_text(path)
    except Exception:
        return live, retired
    for m in RETIRED_CLAUSE.finditer(text):
        retired.update(BACKTICKED.findall(m.group(1)))
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        m = re.fullmatch(r"`([a-z][a-z0-9-]{2,})`", cells[0])
        if m and m.group(1) != "id":
            live.add(m.group(1))
    return live - retired, retired


def declared_modes(path=None):
    """check id -> the mode the registry says it is in, where it says one.

    Read so that a DELIBERATE state can be told from DRIFT. A check recorded as
    `OBSERVE` and running in observe is a decision with a reason attached; the same
    check running in observe with the registry saying `ENFORCING` is the defect.
    Reporting the state instead of the disagreement means firing forever on every
    rollout somebody already decided, which is how a reminder becomes wallpaper.
    """
    out = {}
    try:
        text = registry_text(path)
    except Exception:
        return out
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        m = re.fullmatch(r"`([a-z][a-z0-9-]{2,})`", cells[0])
        if not m or m.group(1) == "id":
            continue
        # The verdict is the FIRST backticked token of the rollout cell, never any
        # occurrence of the word in it. A substring test reads `ENFORCING — no
        # observe rung` as a declaration of observe, which inverts the one column
        # this function exists to read.
        decl = re.match(r"\s*`([A-Z-]+)`", cells[-1])
        if not decl:
            continue
        token = decl.group(1)
        if token == "OBSERVE":
            out[m.group(1)] = "observe"
        elif token == "ENFORCING":
            out[m.group(1)] = "enforce"
        elif token == "RECORDING":
            # A check on an event whose output the host ignores has no
            # enforce/observe axis at all. Without this branch the mode resolver's
            # fallback prints `enforce` beside it, which claims it blocks.
            out[m.group(1)] = "record"
    return out


def python_ids(text):
    """Ids a Python hook can emit, from its syntax tree.

    Module constants named CHECK_ID* are resolved, and the first argument of a
    shared-sink call is taken. Only the first: each hook also wraps the sink in its
    own `log()` whose signature puts the id somewhere else, so reading every literal
    argument to anything named `log` collects the verdicts instead, and `deny` and
    `warn` enter the inventory as checks.
    """
    ids = set()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return ids
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id.startswith("CHECK_ID") \
                        and ID_SHAPE.fullmatch(node.value.value):
                    ids.add(node.value.value)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        is_sink = (isinstance(fn, ast.Attribute) and fn.attr == "log"
                   and isinstance(fn.value, ast.Name)
                   and fn.value.id == "hook_decisions")
        if not is_sink or not node.args:
            continue
        first = node.args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str) \
                and ID_SHAPE.fullmatch(first.value):
            ids.add(first.value)
    return ids


def code_ids(hooks_dir=None):
    """check id -> the files that can emit it."""
    directory = hooks_dir or HOOKS
    found = collections.defaultdict(set)
    for path in glob.glob(os.path.join(directory, "**", "*"), recursive=True):
        if not os.path.isfile(path) or not path.endswith((".py", ".sh")):
            continue
        try:
            text = open(path, errors="replace").read()
        except Exception:
            continue
        rel = os.path.relpath(path, directory)
        ids = python_ids(text) if path.endswith(".py") else {
            m.group(1) for m in ID_IN_SHELL.finditer(text)}
        for cid in ids:
            found[cid].add(rel)
    return found


def reconcile(logged_ids, hooks_dir=None, registry_path=None):
    """The three drift sets plus the historical one, as plain data."""
    live, retired = registry_ids(registry_path)
    in_code = code_ids(hooks_dir)
    logged = {c for c in logged_ids if c}
    return {
        "unregistered": sorted(logged - live - retired),
        "unproven": sorted(live - logged),
        "uncatalogued": sorted(set(in_code) - live - retired),
        "historical": sorted(logged & retired),
        "live": live,
        "retired": retired,
        "in_code": in_code,
    }
