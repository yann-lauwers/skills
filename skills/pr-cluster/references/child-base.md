# A child's base

## Liveness

- An integration base is live while its promotion pull request is open, spent once that pull request merged or closed — `status`'s reason says which, and only a merged one may be retired → `~/.claude/skills/pr-cluster/scripts/cluster.py` `status`: `live` · `spent` · `founded` (the branch stands, no promotion pull request ever opened) · `absent` (no branch).
- Every reader of a named base runs this test → never reads it off the ref or `git ls-remote`.

## Resolving the base

- A stack base passed in outranks this ladder → /pull-request rule 2.
- `integration_bases` empty, or no `cluster_base_source` → the base the line above found, else `base_branch`; the ladder below never runs.
- Otherwise:
  1. Read the ticket the branch is named for, and its parent.
  2. That source names a branch — the parent ticket under `parent-ticket` — and it is live → that branch is the base.
  3. It names none, a `founded`, `spent` or `absent` one, or `production_branch` → `base_branch` · `unknown` → re-run once, then stop and name the read; never `base_branch`.

## Resolve at creation time, not from the worktree's own base

- Resolve the base when the pull request is created, never from the branch the worktree was cut from.
- A pull request already open when its integration base is cut → /pull-request rule 10; whether the retarget needs a rebase → /git , § Rewrites.
