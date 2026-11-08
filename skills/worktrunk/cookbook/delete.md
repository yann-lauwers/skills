# Remove a Worktree

Which trees go is the user's call; what each one carries is checked before it goes, since teardown never reverses.

## Step 1: Check what the tree carries

Run this as its own call, and read it before any removal:

```bash
git -C <tree> status --porcelain                    # uncommitted work
git -C <tree> log --oneline HEAD --not --remotes    # commits on no remote branch
```

- Both silent → the tree goes, on to Step 2.
- Rows → decide per row: commit and push what the branch still needs, ask the user where the work is theirs to keep, or let it go with the tree where it is disposable — a build artefact, a probe, a scratch edit.
- Canon authored inside the tree and not yet adopted → `git wt -C <tree> -y hook pre-start canon` moves it into the main checkout first.
- Gitignored files never show here and go with the tree: env copies, build output.

**Done when:** every row has a decision, and what the branch still needs is pushed.

## Step 2: Remove

- `git wt -C <repo> -y remove <branch> --foreground` — one tree. The default.
- Every integrated tree of one repo → `git wt -C <repo> step prune --dry-run`, then `git wt -C <repo> -y step prune --foreground`.
- `--force` removes a tree whose rows Step 1 chose to lose; `-D` deletes a branch the integration check missed though its work landed — a squash merge with hundreds of commits landed since. Either one on a row the user owns → ask them first.
- The fence refuses a tree with no `wtk-owner` token → this setup did not make it: leave it to whatever did, and report it.

**Done when:** the tree is gone from `git -C <repo> worktree list`, or a refusal is reported with the tree intact.

## When the worktree should survive

- A worktree whose PR is open is still the branch's working checkout: a pipeline that created it for a batch of work keeps it until the PR merges.
- Removal takes the directory from under anything still standing in it — a shell, a running process, a terminal seat — and tells none of them → whatever put them there takes them down.
