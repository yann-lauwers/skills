---
name: watch-pr
description: "Watches one pull request to merge, acting on its watcher's verdicts. Use on 'merge once green', 'watch the pr'; also once a pull request is opened or pushed to land, or a watched one has merged with its worktree still on disk."
argument-hint: "[pr-number] [--repo]"
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/*), Bash(uv run *), Bash(gh pr *), Bash(gh api *), Bash(gh run *), Read, Skill, TaskStop, PushNotification
---

# Watch PR

- `scripts/watch-pr.py` decides each verdict per `references/green-detection.md`; this skill decides who acts on it.
- Ask the user nothing: every decision is the watcher's verdict or a pause per `references/escalation.md`.

## Arm

1. Bash with `run_in_background`, `description: "PR <N> watcher"`:

```sh
/Users/yannlauwers/.claude/skills/watch-pr/scripts/watch-pr.py --repo <owner/name> --pr <N>
```

2. Print PR, URL and task id; end the turn — the task's exit wakes the session.

- The verdict is the last `{` line of the task's output file.
- After acting → arm again, adding the line's `rearm`.

## Verdict table

- A fix ends on a push, then the re-arm: the watcher reads the moved head itself.
- Every verdict from `DRAFT` to `CLEAN` ends on a re-arm.

| Verdict | Action |
| --- | --- |
| `DRAFT` | Report the draft; the user flips it. |
| `CONFLICT` | `integration_base` `false` → rebase onto `origin/<base>`, push `--force-with-lease` · else → merge `origin/<base>`, push. Run the repo's checks before the push. |
| `NEW_COMMENTS` | Every unresolved review-bot thread → fix it · refute it, the reply quoting the line or command output that disproves it · a real finding another ticket owns → the reply names that ticket. Reply, then resolve; nothing to quote → pause. |
| `CI_RED` | Fix at root cause, push. A failure with no code root — infra, a flake → pause. |
| `BASE_ADVANCED` | Merge `origin/<base>` into `branch`, never a rebase; resolve as the union of both sides, run the repo's checks, push. |
| `CLEAN` | Report once. The merge is the user's to name. |
| `MERGED` | `/Users/yannlauwers/.claude/skills/watch-pr/scripts/closeout.py --repo <owner/name> --pr <N>` and report its line; `refused` → the removal is the user's. Then the branch's ticket: an automation owns its transition → report it · this session opened the PR → close it through the tracker's skill · else → name it to the user. |
| `CLOSED` | Report closed without merge. |
| `WATCHER_ERROR` | Report `reason`, arm nothing; `error=blind` → arm again once `gh` answers. |
| no `{` line | Arm again once; a second time → report the output file's tail. |
| the 6th fixable line in a row, or any other verdict | Pause. |
