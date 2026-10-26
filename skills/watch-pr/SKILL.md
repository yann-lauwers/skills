---
name: watch-pr
description: "Watches one pull request until it merges, acting only on its watcher's lines. Use on \"watch the pr\", \"observe the pr until it's merged\", \"keep the pr green until merge\", \"watch pr and close the worktree\"; also when a pull request was just opened or pushed with intent to land it, a watcher line needs acting on, or a merged pull request this session watched still has its worktree on disk. Not for a watcher over anything else — /watching ; not for opening, readying or merging — /pull-request ; not for bulk worktree pruning — /worktrunk ."
argument-hint: "[pr-number] [--repo]"
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/*), Bash(uv run *), Bash(gh pr *), Bash(gh api *), Bash(gh run *), Bash(git worktree *), Bash(git rev-parse *), Bash(git wt *), Bash(git branch *), Read, Skill, TaskStop, PushNotification
---

# Watch PR

- `scripts/watch-pr.py` decides each verdict per `references/green-detection.md`; this skill decides who acts on it.
- The watcher is a probe armed in the background; it prints one line when a verdict is news, then exits → /watching , § Arm a probe.
- Ask the user nothing: every decision is the watcher's verdict or a pause per `references/escalation.md`.

## Arm

1. PR: the first argument, else `gh pr view --json number`; repo: `--repo`, else the cwd's.
2. `/Users/yannlauwers/.claude/skills/watch-pr/scripts/watch-pr.py --repo <owner/name> --pr <N> --once` → `MERGED` or `CLOSED` is acted on per its row and nothing is armed.
3. Bash with `run_in_background`, `description: "PR <N> watcher"`:

```sh
/Users/yannlauwers/.claude/skills/watch-pr/scripts/watch-pr.py --repo <owner/name> --pr <N>
```

4. Print PR, URL and task id; end the turn — the task's exit wakes the session.

- The verdict is the last line of the task's output file that starts with `{`.
- After acting → arm again with the same command plus the line's `rearm` flags, which replace their namesakes.
- Tuning flags (`--interval`, `--blind-after`, `--fresh-window`, `--bot-pending-timeout`) only when the user set them → `references/wire-contract.md`.
- Stop → `TaskStop <task id>`.

## Verdict table

- Each line is one JSON object.
- A fix ends on a push; the re-armed watcher reads the moved head on its first read — never re-poll.

| Verdict | Action |
| --- | --- |
| `DRAFT` | Report the draft; who flips it → /pull-request rule 12. Re-arm. |
| `CONFLICT` | The line's `rewrite` is `allow` → rebase onto `origin/<base>`, resolve, run the repo's checks, `git push --force-with-lease`. `refuse`, `unknown` or absent → `git merge origin/<base>`, resolve, check, push. Re-arm. |
| `NEW_COMMENTS` | Every unresolved review-bot thread → fix it (commit, push) · refute it, the reply quoting the line or command output that disproves it · a real finding another ticket owns → the reply names that ticket. Then resolve it (`gh api graphql`, `resolveReviewThread`). Never resolve without a reply; nothing to quote → pause. Re-arm. |
| `CI_RED` | `gh run list --branch <branch> --status failure`, then `gh run view <id> --log-failed`; fix at root cause, push. A failure with no code root — infra, a flake → pause. Re-arm. |
| `BASE_ADVANCED` | In a checkout of `branch`, `git merge origin/<base>`, never a rebase; resolve as the union of both sides, run the repo's checks, push. Re-arm. |
| `CLEAN` | Report once. The session that opened this PR runs /pull-request 's merge preflight; any other session → the merge is the user's to name. Re-arm, so the merge is observed. |
| `MERGED` | Run `cookbook/closeout.md`. Then the ticket the branch names closes the way the tracker closes work: an automation owns the transition → report it; else the session that opened this PR closes it through the tracker's skill; any other session names it to the user. The repo declares a hosted design medium the merged diff touched → push per /claude-design § Pushing. The watcher has exited. |
| `CLOSED` | Report closed without merge. The watcher has exited. |
| `WATCHER_ERROR` | `error=duplicate` → another watcher holds this PR; report its pid, arm nothing. `error=blind` → no read landed for the whole `--blind-after`; report `detail`, arm again once the network or `gh` answers. `error=auth` → report; the user signs `gh` in. Any other → report `detail`. |
| no `{` line | The task exited with none → arm again once with the same command; a second time → report the output file's tail. |
| the 6th fixable line in a row, or any other verdict | Pause per `references/escalation.md`. |
