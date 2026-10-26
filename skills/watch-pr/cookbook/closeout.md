# Close out a merged PR

- Every field comes from the `MERGED` line — `repo`, `branch`, `merge_commit_sha`, `merged_by`, `base`; no line in hand → `${CLAUDE_SKILL_DIR}/scripts/watch-pr.py --repo <owner/name> --pr <N> --once`.
- `worktree_path`, `worktree_occupied` and `session_inside` come from `${CLAUDE_SKILL_DIR}/scripts/worktree-occupancy.py --repo <owner/name> --branch <branch>`, run from this session's own Bash in its own `pwd`.
- The removal is irreversible; each refusal ends the pass.

1. `worktree_path` null → report the merge (who, into which base); stop.
2. `worktree_occupied` `true` or `"unknown"` → refuse, naming the peer or the reader that could not answer; the removal is the user's.
3. `session_inside` `true` → `cd` to the base checkout (parent of `git rev-parse --git-common-dir`).
4. `git -C <worktree_path> status --porcelain` prints anything → refuse, naming the files.
5. `git -C <worktree_path> fetch origin <base>` then `git cherry origin/<base> HEAD`: no `+` lines → clear · `+` lines → clear only when the branch diff's `git patch-id --stable` equals `<merge_commit_sha>`'s; else refuse, unmerged local work.
6. `git wt -C <worktree_path> -y remove <branch> -D --foreground`; exit 75 → another start or stop holds the tree's lock, rerun once it frees; other non-zero → print the stderr tail, stop.
7. Done when `git worktree list` lacks `worktree_path` and `git branch --list <branch>` is empty (else `git branch -D <branch>`, which Step 5's patch-id check licenses by proving the work landed — `-d` refuses a squash-merged branch); report merged-by, base, worktree and branch gone, and the ticket closing still owed.
