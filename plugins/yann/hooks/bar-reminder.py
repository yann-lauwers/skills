#!/usr/bin/env python3
"""UserPromptSubmit — restate the bar as one fixed line on a session's 1st prompt, then every 5th.

The prompt count is kept per session_id, so it survives compaction. Without a
usable session_id or a writable state dir the hook stays silent.

Off switch: `touch ~/.claude/state/bar-reminder/off`.
"""
import json
import os
import re
import sys

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.environ.get("BAR_REMINDER_STATE_DIR") or os.path.expanduser(
    "~/.claude/state/bar-reminder")
OFF_MARKER = os.path.join(STATE_DIR, "off")
EVERY = 5

MESSAGE = (
    "The bar: best-in-class, not done. A turn ending on something external (CI, a PR, a "
    "deploy, someone else's reply elsewhere) arms a watcher first: /watching or /watch-pr ."
)


def safe_session(value):
    if not isinstance(value, str):
        return None
    return value if re.fullmatch(r"[A-Za-z0-9._-]{1,128}", value) else None


def due(session):
    path = os.path.join(STATE_DIR, session)
    try:
        with open(path, encoding="utf-8") as fh:
            count = int(fh.read().strip() or 0)
    except FileNotFoundError:
        count = 0
    count += 1
    os.makedirs(STATE_DIR, exist_ok=True)
    tmp = "%s.%d.tmp" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(str(count))
    os.replace(tmp, path)
    return count == 1 or count % EVERY == 0


def main():
    if os.path.exists(OFF_MARKER):
        return
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    session = safe_session(payload.get("session_id") if isinstance(payload, dict) else None)
    try:
        if session is None or not due(session):
            return
    except Exception:
        return
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": MESSAGE}}))
    try:
        sys.path.insert(0, os.path.join(HOOKS_DIR, "lib"))
        import hook_decisions
        hook_decisions.log("bar-reminder", "warn", "chars=%d" % len(MESSAGE),
                           session=session,
                           event="UserPromptSubmit")
    except Exception:
        pass


if __name__ == "__main__":
    sys.path.insert(0, os.path.join(HOOKS_DIR, "lib"))
    try:
        from hook_run import run as _run
    except Exception:
        def _run(_check, fn, event=None):
            return fn() or 0
    sys.exit(_run("bar-reminder", main, event="UserPromptSubmit"))
