#!/usr/bin/env python3
"""PreToolUse guard — keep a reports tree in its declared shape.

Failure it prevents: a report artifact lands at a path outside the report tree's
shape, so no report links it, a sweep over runs/ misses it, and a second evidence
root starts accumulating. That is how a `visual-tests/` tree came to exist beside
the real one.

Contract (verified against references/events-and-contracts.md):
  exit 0 + no stdout  -> no opinion, the call proceeds through normal permissions
  exit 0 + JSON deny  -> blocked, reason shown to the model
  any other exit      -> NON-blocking. A crash here is an absent guard, so every
                         payload field is coerced at the entry point and no path
                         may raise.

Modes, per check: `HOOK_MODE_VALIDATION_REPORT_LAYOUT=observe`, set in the
`env` of `~/.claude/settings.json`. "observe" records the verdict and never denies;
"enforce" denies. Observe writes a different verdict value than enforce so a
promotion can be proven safe from the log alone.

This guard reads only paths. It never reads file contents and never prints one.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

# The shared decision sink. A check that writes rows of its own devising is
# invisible to the AST inventory reconciling code against the registry.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
try:
    import reports_path
except Exception:
    reports_path = None
try:
    import hook_decisions
except Exception:            # a broken sink leaves the guard itself working, and
    hook_decisions = None    # `hook-decisions --drift` reports it as never logged
try:
    import hook_mode
except Exception:
    hook_mode = None

CHECK_ID = "validation-report-layout"
DEFAULT_MODE = None   # resolved from lib/hook_mode.py DEFAULTS

try:
    from report_kinds import KINDS
except Exception:                      # lib/report_kinds.py is the vocabulary's
    KINDS = None                       # one home. Unreachable -> this guard has
                                       # no opinion, never a stale one: a DENY
                                       # gate on a stale set refuses legal writes.

# Bookkeeping files that legitimately sit at the reports root.
ROOT_FILES = {".last-prune", ".DS_Store"}

# OS and editor debris appears at every depth and says nothing about the tree's
# shape. Denying it would be noise the reader cannot act on.
IGNORED_NAMES = {".DS_Store", "Thumbs.db", ".gitkeep", ".keep"}

RUN_KEY = re.compile(r"^\d{4}-\d{2}-\d{2}_[1-9]\d*$")


def log(session, verdict, detail):
    """Record every fire. Without rows, 'never fired' and 'fires wrongly every
    day' are the same data."""
    if hook_decisions:
        hook_decisions.log(CHECK_ID, verdict, detail, session=session,
                           mode=(hook_mode.resolve(CHECK_ID, DEFAULT_MODE)
                                 if hook_mode else DEFAULT_MODE))


def rel_under_reports(path):
    """The portion beneath whichever reports tree holds `path`, or None.

    Delegated to lib/reports_path.py, which resolves through the declaration —
    `AGENTS_REPORTS_DIR`, then the vault root by role — rather than through the
    `docs/reports/` segment. That segment was a symlink and is gone; a
    guard predicating on it matches nothing now, quietly, since a shape guard that
    never fires looks exactly like a tree whose shape is respected.

    Returns None for anything it cannot place — an empty parse is 'I don't know',
    never 'it is safe'. The helper unreachable is the same answer, for the same
    reason: this guard states no opinion rather than guessing at a path.
    """
    if reports_path is None:
        return None
    tail = reports_path.rel_under_reports(path)
    return tail or None


def names_a_report(tok):
    """Whether a bash operand plausibly points into a reports tree.

    Selecting a candidate is a different job from placing one, and it runs against
    a command line rather than a payload path — so it asks the resolver, which
    places the absolute reports path a command carries. A bare
    `docs/reports/` segment test covers none of them: that path is now a real
    directory inside a repo wherever it exists at all.
    """
    return bool(tok) and rel_under_reports(tok) is not None


def classify(rel):
    """(ok, reason). `rel` is a path relative to the reports tree that holds it."""
    parts = [p for p in rel.split("/") if p]
    if not parts:
        return True, ""
    if parts[-1] in IGNORED_NAMES:
        return True, ""

    head = parts[0]
    if len(parts) == 1:
        if head in ROOT_FILES or head in KINDS:
            return True, ""
        if head.endswith(".md"):
            return False, (
                f"`{head}` sits at the reports root. The one report kind is "
                f"validation/<slice>-validation/runs/<YYYY-MM-DD>_<n>/report.md; any other finding goes in the reply"
            )
        return False, (
            f"`{head}/` is not a report kind. The one kind is: {', '.join(sorted(KINDS))}"
        )

    if head not in KINDS:
        return False, (
            f"`{head}/` is not a report kind. The one kind is: {', '.join(sorted(KINDS))}; "
            "a finding, design, diagnosis or build record goes in the reply."
        )

    rest = parts[1:]

    if len(rest) == 1 and rest[0].endswith(".md"):
        return False, (
            f"`{head}/{rest[0]}` is a lone file. A {head} report is a directory: "
            f"{head}/<slice>-{head}/runs/<YYYY-MM-DD>_<n>/report.md"
        )

    slice_name, tail = rest[0], rest[1:]
    if not tail:
        return True, ""  # creating the report directory itself

    if tail[0] != "runs":
        if len(tail) == 1 and tail[0].endswith(".md"):
            return False, (
                f"`{head}/{slice_name}/{tail[0]}` sits loose in the report directory. "
                f"A run's report is {head}/{slice_name}/runs/<YYYY-MM-DD>_<n>/report.md"
            )
        return False, (
            f"`{head}/{slice_name}/{tail[0]}` is loose inside a report directory. "
            f"A report holds runs/<YYYY-MM-DD>_<n>/, each with its report.md and <scenario>/ directories — put "
            f"this run's artifacts in runs/<date>_<n>/{tail[0]}/"
        )

    if len(tail) == 1:
        return True, ""  # the runs/ directory itself

    key = tail[1]

    if not RUN_KEY.match(key):
        return False, (
            f"`{key}` is not a run key. The key is <YYYY-MM-DD>_<n>, counting from 1 "
            f"— the day's first run is {datetime.now(timezone.utc):%Y-%m-%d}_1."
        )
    return True, ""


def candidate_paths(tool, tool_input):
    """Paths this call would create or write. Unparseable -> empty, i.e. no opinion."""
    out = []
    if tool in ("Write", "Edit", "NotebookEdit"):
        p = tool_input.get("file_path")
        if isinstance(p, str):
            out.append(p)
        return out

    if tool == "Bash":
        cmd = tool_input.get("command")
        if not isinstance(cmd, str):
            return out
        # Only path-creating verbs. Reads (ls, cat, find, grep) never trip this.
        for m in re.finditer(
            r"(?:^|[;&|]\s*)\s*(mkdir|touch|cp|mv|tee)\b([^;&|]*)", cmd
        ):
            for tok in m.group(2).split():
                if tok.startswith("-"):
                    continue
                tok = tok.strip("'\"")
                if names_a_report(tok):
                    out.append(tok)
        # Redirection into the tree: > path / >> path.
        #
        # The `>` must be preceded by whitespace, a digit fd, or the start of the
        # command. Without that anchor the `>` closing a placeholder inside PROSE
        # reads as a redirect: `<repo>/docs/reports/<kind>/` matched, captured
        # `/docs/reports/<kind>/` as a write target, and denied a documentation
        # edit that redirected nothing. Measured 2026-09-08 while editing the very
        # rule this guard cites.
        #
        # This is law 1 — fire on the act, not on the character. A redirect is a
        # shell operator in operator position, and `>` inside a word is not one.
        for m in re.finditer(r"(?:^|[\s;&|(])\d?>>?\s*(\S+)", cmd):
            tok = m.group(1).strip("'\"")
            if names_a_report(tok):
                out.append(tok)
    return out


def main():
    if KINDS is None:
        return 0
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0  # unparseable payload -> no opinion
    if not isinstance(payload, dict):
        return 0

    tool = payload.get("tool_name") or ""
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = {}
    session = str(payload.get("session_id") or "")

    findings = []
    for path in candidate_paths(tool if isinstance(tool, str) else "", tool_input):
        rel = rel_under_reports(path)
        if rel is None:
            continue
        ok, reason = classify(rel)
        if not ok:
            findings.append((path, reason))

    if not findings:
        return 0

    path, reason = findings[0]
    mode = hook_mode.resolve(CHECK_ID, DEFAULT_MODE) if hook_mode else DEFAULT_MODE
    if mode == "observe":
        log(session, "would-deny", f"{path} :: {reason}")
        return 0

    log(session, "deny", f"{path} :: {reason}")
    message = (
        f"{reason}\n\n"
        "The report tree's shape, beneath the reports dir this repo declares:\n"
        "  validation/<slice>-validation/runs/<YYYY-MM-DD>_<n>/report.md\n"
        "  validation/<slice>-validation/runs/<YYYY-MM-DD>_<n>/<scenario>/<artifact>\n\n"
        "Writing somewhere else starts a second evidence root that no report links. "
        "Where a validation report lands is /validating 's own; every other pass "
        "answers in its reply."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": message,
        }
    }))
    return 0


if __name__ == "__main__":
    # The recorder is optional by construction. A hook copied away from its lib
    # must still run: crashing on a missing import is the very failure this
    # wrapper exists to record, and it would fail closed on the one path where
    # nothing is left to write the row.
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
    try:
        from hook_run import run as _run
    except Exception:
        def _run(_check, fn, event=None):
            return fn() or 0
    sys.exit(_run("validation-report-layout", main, event="PreToolUse"))
