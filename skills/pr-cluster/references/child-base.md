# A child's base

## Liveness

- An integration base is live while its promotion pull request is open, spent once that pull request merged or closed — `status`'s reason says which, and only a merged one may be retired → `~/.claude/skills/pr-cluster/scripts/cluster.py` `status`: `live` · `spent` · `founded` (the branch stands, no promotion pull request ever opened) · `absent` (no branch).
- Every reader of a named base runs this test → never reads it off the ref or `git ls-remote`.

## Resolving the base

- A stack base the caller passes in outranks this ladder.
- Otherwise:
  1. Read the ticket the branch is named for, and its parent.
  2. The parent names a branch and it is live → that branch is the base.
  3. It names none, a `founded`, `spent` or `absent` one, or the branch that deploys → the trunk · `unknown` → re-run once, then stop and name the read; never the trunk.

## Resolve at creation time, not from the worktree's own base

- Resolve the base when the pull request is created, never from the branch the worktree was cut from.
- A pull request already open when its integration base is cut → retarget it, `gh pr edit <n> --base <cluster>`; whether the retarget needs a rebase → /git , § Rewrites.
