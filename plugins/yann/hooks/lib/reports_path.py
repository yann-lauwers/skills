#!/usr/bin/env python3
"""Decide whether a path is inside a reports tree, and what it is relative to it.

Three hooks answered this independently, each with its own literal:
`guard-report-tree.py` held `REPORTS_SEG = "docs/reports/"`, `stamp-report-frontmatter.py`
held a three-segment tuple, and `prune-registry-check.sh` had already moved off the
symlink and recorded that "nothing depends on it existing" — which the other two
contradicted. Third instance, so the helper is named once here and every caller uses it.

WHY IT MATTERS BEYOND DEDUPLICATION. `docs/reports` used to be a symlink derived from a
repo's `env.AGENTS_REPORTS_DIR`. It is gone, and a guard whose predicate was that segment
now matches nothing — which does not fail loudly, it goes quiet. A reports tree with no
shape guard looks exactly like one being respected. Resolving through the declaration is
what kept the guards working across the removal, and what makes their coverage checkable
now. `pr-needs-proof.py` is the worked case of the other outcome: it kept the join, every
listdir raised, and it returned "no opinion" for every repo for as long as nobody looked.

RESOLUTION ORDER, and every rung is a declaration rather than a guess:

  1. `AGENTS_REPORTS_DIR` in the process environment — what a session inside a wired
     repo carries, because `.claude/settings.local.json` puts it there.
  2. The same key read out of `<repo>/.claude/settings.local.json`, for a path whose
     repo is identifiable but whose environment did not carry it.
  3. The vault root, resolved from the config declaring `role: vault`. Beneath it,
     `projects/<slug>/reports` and the root `reports` are reports trees by construction.
     This is the rung the post-symlink world runs on, and it is the one a path-ancestry
     walk cannot reach: a report living in the vault has no repo above it, so nothing
     on its way up carries a declaration. Caught by the battery before any hook used
     this helper.
  4. The user-level tree, `~/.agents/reports`, resolved through its own pointer.
Every rung is a declaration. There is deliberately no rung matching a `docs/reports/`
segment: that path is now a real directory inside a repo wherever it exists at all, so
matching it would resolve to the accident rather than to the tree.

COST. Rungs 1 and 2 are a dict read and a short filesystem walk, and they answer for
every path written from inside a repo. Rung 3 shells out, so it is reached only when the
cheap rungs miss AND the path plausibly names a reports tree — this helper runs on every
Edit and Write, and an unconditional subprocess there would be a cost the guard does not
earn. The result is cached for the process, which for a hook is one call per fire.

BOUNDARY, stated because it is not obvious from the rungs: rung 2 walks up from the
PATH, so it sees a declaration only when the file sits inside the repo that declares it.
A tree outside the vault AND outside its own repo is placed by nothing here. Reaching it
would mean enumerating every repo on the machine on every Edit and Write, which is cost
this helper does not earn — and after the symlink removal every declared dir is under the
vault, where rung 3 answers.

`None` means "not a report", never "unknown". An unresolvable declaration yields no
match, so a caller stays silent rather than guessing — the same law-2 discipline every
other check here follows: an empty parse is no opinion.
"""
import json
import os

# The user-level tree's pointer. It is a symlink into the vault and stays one: it is
# named in the closed set of surfaces allowed to carry a vault location
# (the obsidian skill's `SKILL.md` § Root).
USER_POINTER = "~/.agents/reports"


def _norm(path):
    if not isinstance(path, str) or not path:
        return None
    try:
        return os.path.realpath(os.path.expanduser(path))
    except Exception:
        return None


def _rel_if_under(path, tree):
    """`path` relative to `tree`, or None. Both are realpaths already."""
    if not tree or not path:
        return None
    if path == tree:
        return ""
    prefix = tree.rstrip("/") + "/"
    if not path.startswith(prefix):
        return None
    # Both arguments are realpaths, so `..` has already been collapsed and cannot
    # appear here. The transitional legacy rung matches the raw path instead, and
    # carries its own traversal check for exactly that reason.
    return path[len(prefix):].strip("/")


_VAULT_ROOT = []          # one-slot cache; [] unresolved, [None] resolved-to-nothing


def _vault_root():
    """The vault root, by role. Resolved once per process, never written down."""
    if _VAULT_ROOT:
        return _VAULT_ROOT[0]
    import re
    import subprocess
    root = None
    try:
        out = subprocess.run(
            [os.path.expanduser("~/.claude/skills/agents-config/scripts/agents-config"), "role", "vault"],
            capture_output=True, text=True, timeout=5)
        if out.returncode == 0:
            for token in (out.stdout or "").split():
                if not token.startswith(("floor=", "project=")):
                    continue
                try:
                    with open(token.split("=", 1)[1], errors="replace") as fh:
                        head = [next(fh, "") for _ in range(40)]
                except Exception:
                    continue
                for line in head:
                    m = re.match(r"\s*vault_root:\s*(\S+)\s*$", line)
                    if m:
                        cand = _norm(m.group(1).strip("'\""))
                        if cand and os.path.isdir(cand):
                            root = cand
                        break
                if root:
                    break
    except Exception:
        root = None
    _VAULT_ROOT.append(root)
    return root


def _vault_trees(path):
    """Reports trees under the vault that could contain `path`.

    Derived from the root rather than enumerated, so a project wired tomorrow needs
    no edit here.
    """
    root = _vault_root()
    if not root:
        return []
    prefix = root.rstrip("/") + "/"
    if not path.startswith(prefix):
        return []
    rest = path[len(prefix):].split("/")
    # The user-level tree sits at the vault root, not under a wrapper folder: it holds
    # reports bound to no project, and a parent segment naming one would be a claim the
    # tree cannot make. Moved out of `agents/` on 2026-09-09 — that folder meant "Claude's
    # own", and a page belonging to a project was being filed under it.
    trees = [os.path.join(root, "reports")]
    if len(rest) >= 3 and rest[0] == "projects" and rest[2] == "reports":
        trees.insert(0, os.path.join(root, "projects", rest[1], "reports"))
    return trees


def _declared_dirs(path):
    """Reports dirs declared by any repo on `path`'s way up, nearest first.

    Walks up from the path rather than from the working directory, because a hook's
    cwd says nothing about the file it was handed.
    """
    out = []
    env = os.environ.get("AGENTS_REPORTS_DIR")
    if env:
        n = _norm(env)
        if n:
            out.append(n)
    cur = os.path.dirname(path or "")
    seen = 0
    while cur and cur != "/" and seen < 40:
        seen += 1
        settings = os.path.join(cur, ".claude", "settings.local.json")
        if os.path.isfile(settings):
            try:
                with open(settings, errors="replace") as fh:
                    declared = (json.load(fh).get("env") or {}).get("AGENTS_REPORTS_DIR")
            except Exception:
                declared = None
            n = _norm(declared) if declared else None
            if n:
                out.append(n)
        cur = os.path.dirname(cur)
    return out


def report_rel(path):
    """(tree, rel) when `path` is inside a reports tree, else None.

    `tree` is the realpath of the tree it sits in; `rel` is the portion beneath it,
    which is what every caller's shape rules are written against.
    """
    real = _norm(path)
    if not real:
        return None

    for tree in _declared_dirs(real):
        rel = _rel_if_under(real, tree)
        if rel is not None:
            return tree, rel

    for tree in _vault_trees(real):
        rel = _rel_if_under(real, tree)
        if rel is not None:
            return tree, rel

    user = _norm(USER_POINTER)
    if user and os.path.isdir(user):
        rel = _rel_if_under(real, user)
        if rel is not None:
            return user, rel

    return None


def rel_under_reports(path):
    """Just the relative portion, for a caller that does not need the tree."""
    found = report_rel(path)
    return found[1] if found else None


def reports_dir_for(repo_root):
    """Where THIS repo's reports live, or None when the repo is unwired.

    The reverse of `report_rel`, and a caller needs it whenever the question is
    "does a report about X exist" rather than "is this path a report" — the design
    gate reading `<repo>/docs/reports/arch/` is the worked case. Joining that path
    by hand fails a specific way once the symlink is gone: the directory is simply
    absent, which reads as "no arch record" rather than as "unwired", so the gate
    fires on every ticket instead of going quiet.

    None means unwired, and every caller must treat it as NO OPINION rather than as
    an empty tree. The two are opposite verdicts and a missing directory looks the
    same from the outside.
    """
    root = _norm(repo_root)
    if not root:
        return None

    settings = os.path.join(root, ".claude", "settings.local.json")
    try:
        with open(settings, errors="replace") as fh:
            declared = (json.load(fh).get("env") or {}).get("AGENTS_REPORTS_DIR")
    except Exception:
        declared = None
    n = _norm(declared) if declared else None
    if n and os.path.isdir(n):
        return n

    # Undeclared: derive from the vault the same way the wiring does, so a repo
    # wired before the declaration existed still resolves.
    vault = _vault_root()
    if vault:
        cand = os.path.join(vault, "projects", os.path.basename(root), "reports")
        if os.path.isdir(cand):
            return cand

    # A `<repo>/docs/reports` directory is deliberately NOT consulted. It used to be
    # the symlink into the vault; with the link gone, anything at that path is a real
    # directory inside the repo — evidence that landed in git history by mistake, and
    # returning it would make this resolver point at the accident.
    return None
