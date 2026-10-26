---
name: cp
description: "Commit, then push, deferring to the repo's own commit and push conventions."
disable-model-invocation: true
allowed-tools: Bash(git:*)
argument-hint: [optional message]
---

# /cp — Commit & Push

Commit, then push, deferring to the project's own commit/push conventions — discovered by capability, not name.

1. **Find the convention skill.** Scan available skills for one whose description governs this repo's git/commit/push conventions; invoke it via the Skill tool before committing. Match on what it *does*, not a name. /cp is the trigger, so nothing auto-fired — load it explicitly. None → system-prompt commit flow.
2. **Commit.** Discovered skill's conventions if one loaded, else the system-prompt flow. `$ARGUMENTS` = commit message verbatim when given, else draft from the diff.
3. **Push.** Skill's push rules if any, else `git push` (`-u origin <branch>` if no upstream). Never `--force` without explicit user approval.

ARGUMENTS: $ARGUMENTS
