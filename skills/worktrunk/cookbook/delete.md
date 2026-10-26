# Remove a Worktree

Removes a worktree without losing work: what each removal destroys is checked before it runs, because teardown never reverses.

- The pre-flight runs before every removal; which trees go is the user's call, what each one carries is not.

## What removal does

`git wt remove --help` carries the flags and the six checks that decide whether a branch is integrated; the order below is this machine's.

1. A dirty tree — staged, modified or untracked files — is refused before any hook runs, unless `--force`.
2. The global `pre-remove` fence refuses a tree with no `wtk-owner` token → `cookbook/troubleshoot.md` § No ownership token; never `--no-hooks`, which skips the fence and every teardown with it.
3. The project's `pre-remove` runs: nexus sweeps worktree-born canon into the main checkout, then stops the dev stack; a `wtk-web` repo stops its dev server.
4. The tree goes — in the background unless `--foreground`. The branch goes with it only when it is integrated into the default branch (`_` or `⊂` in `git wt list`); `--no-delete-branch` always keeps it, `-D` deletes it unmerged.
5. `post-remove` runs in the background: `wt-dev forget` stops what the tree's units left running and deletes their records; nexus also reaps clusters no live tree names and destroys the tree's tunnel.

- Gitignored files are no dirt to the guard and go with the tree: env copies, build output, and canon authored inside the tree that no step adopted.
- `--format json` prints one object per removal; its `branch_outcome` — `deleted`, `retained_unmerged`, `retained_checked_out`, `not_attempted`, … — says what happened to the branch, which the exit code never does.
- Exit `75` → another start or stop of the tree held its lock for 60 s; the message names the holder's pid. A `pre-remove` refusal exits non-zero with the tree intact.

## Step 1: Establish what the tree carries

```bash
git -C <tree> status --porcelain          # uncommitted work
git -C <tree> log --oneline @{u}..HEAD    # commits not on the remote
```

- Either returns rows → surface them to the user and ask before removing; both silent → the tree is safe to remove.
- Canon authored inside the tree and not yet adopted → adopt it first, per `cookbook/canon.md` § Authoring canon from inside a worktree.
- `git wt list` marks integrated branches `_` or `⊂`: the ones a cleanup pass looks for.

**Done when:** every tree slated for removal is known to be clean, or the user has chosen to lose what it holds.

## Step 2: Choose the removal form

- `git wt -C <repo> -y remove <branch> --foreground` — one tree, keeps the dirty-tree guard, waits for the result. The default.
- `--no-delete-branch` — removes the checkout, keeps the branch.
- `-D` — deletes the branch unmerged → only where the user named it, or the branch's work is established as landed and the integration check missed it (a squash merge with hundreds of commits landed since).
- `--force` — removes a dirty tree → only where the user chose to lose what Step 1 surfaced.
- `git wt -C <repo> step prune --dry-run`, then `git wt -C <repo> -y step prune --foreground` — every integrated tree and branch of one repo; it skips dirty, locked and younger-than-`--min-age` (1 day) trees, and the fence refuses a tree with no token. Preview first, every time.
- ASK USER before `--force` or `-D`, unless they named that form themselves, or Step 1 established that specific tree clean and its branch landed.
- A detached tree has no branch → pass its path in place of `<branch>`.

**Done when:** the output reports the removal and its `branch_outcome`, or reports a refusal that left the tree intact.

## Step 3: Confirm the outcome

```bash
git wt -C <repo> list
git -C <repo> worktree list
```

- Removal takes the directory from under anything still standing in it — a shell, a running process, a terminal seat — and tells none of them → whatever put them there takes them down.

**Done when:** the tree is absent from both listings, its branch is gone or kept as chosen, and canon it authored sits in the main checkout. A path still in `git worktree list` but gone from disk clears with `git -C <repo> worktree prune`; what its units and cluster left behind → `cookbook/troubleshoot.md` § A tree deleted by hand.

## When the worktree should survive

- A worktree whose PR is open is still the branch's working checkout: a pipeline that created it for a batch of work keeps it until the PR merges.
- Reaping merged worktrees is its own pass, run deliberately, never a cleanup step tacked onto other work.
