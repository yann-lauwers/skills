#!/usr/bin/env python3
import json
import os
import subprocess
import sys

CHECK = "codex-local-instructions"
LOCAL_FILE = "AGENTS.local.md"


def repo_root(cwd):
    try:
        out = subprocess.run(["git", "-C", cwd, "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return cwd
    return out.stdout.strip() if out.returncode == 0 and out.stdout.strip() else cwd


def main():
    if not os.environ.get("PLUGIN_ROOT"):
        return 0
    payload = json.load(sys.stdin)
    cwd = payload.get("cwd") or os.getcwd()
    path = os.path.join(repo_root(cwd), LOCAL_FILE)
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read().strip()
    except OSError:
        return 0
    if not text:
        return 0
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": "Instructions from %s, local to this machine:\n\n%s" % (path, text),
    }}))
    os.environ.setdefault("AGENT_HOOK_PROVIDER", "codex")
    try:
        import hook_decisions
        hook_decisions.log(CHECK, "injected", "bytes=%d source=%s" % (len(text), payload.get("source")),
                           session=payload.get("session_id"), event="SessionStart")
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
    try:
        from hook_run import run as _run
    except Exception:
        def _run(_check, fn, event=None):
            return fn() or 0
    sys.exit(_run(CHECK, main, event="SessionStart"))
