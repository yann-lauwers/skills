#!/usr/bin/env python3
import json
import os
import sys

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HOOKS_DIR, "lib"))
from commit_command import git_call
from guard_output import CHECK_ID, log
try:
    import hook_shell
except Exception:
    hook_shell = None
try:
    import commit_guard
except Exception:
    commit_guard = None


def git_calls_on_line(command, cwd):
    calls = []
    for statement, where in hook_shell.statements_with_cwd(command, cwd):
        try:
            for argv in hook_shell.invocations(statement):
                if argv and argv[0] == "git":
                    call = git_call(argv, where)
                    if call:
                        calls.append(call)
        except Exception:
            continue
    return calls


def judge_bash(session, command, cwd):
    if "git" not in command:
        return 0
    try:
        calls = git_calls_on_line(command, cwd)
    except Exception:
        return 0
    commits = [(repo, args) for repo, sub, args in calls if sub == "commit"]
    if not commits:
        return 0
    if commit_guard is None:
        log(CHECK_ID, session, "broken", "commit_guard unloadable — commit let through")
        return 0
    commit_guard.judge_commits(session, commits, calls)
    return 0


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict) or payload.get("tool_name") != "Bash" or hook_shell is None:
        return 0
    tool_input = payload.get("tool_input")
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    if not isinstance(command, str):
        return 0
    cwd = payload.get("cwd")
    cwd = cwd if isinstance(cwd, str) and os.path.isdir(cwd) else None
    return judge_bash(payload.get("session_id"), command, cwd)


if __name__ == "__main__":
    try:
        from hook_run import run
    except Exception:
        def run(_check, fn, event=None):
            return fn() or 0
    sys.exit(run(CHECK_ID, main, event="PreToolUse"))
