# Troubleshoot

Diagnoses and fixes common failures — refusals, failed steps, locks, stale state, broken links. The first read decides the section; which fix applies is diagnostic judgment.

## First step: read the tree's state

```bash
git wt -C <repo> list
git wt -C <tree> dev status
git wt -C <tree> doctor          # nexus: managed env keys by name, the cluster and its holders
```

- Read the output before applying any fix below; a fix matched by guess lands in the wrong section.
- Apply that section's fix, then re-run the read; done when the issue it named has cleared.

## No ownership token

- `git -C <tree> rev-parse --git-dir` fails → the link broke, not the token: § `fatal: not a git repository` inside a tree `git worktree list` still lists, then re-run `~/.config/worktrunk/bin/wtk-step fence <tree>`.
- The session made it itself with `git wt … --no-hooks` → to keep working in it: `[WT_DB=… WT_SKIP=…] git wt -C <tree> -y hook pre-start`, repeating the create's prefixes; to remove it: `~/.config/worktrunk/bin/wtk-step own <tree>`, then the removal.
- Otherwise → nothing proves this setup made it; leave it to whatever made it.
- Never `--no-hooks`: it skips the fence and every teardown, leaving units, a cluster and a tunnel behind.

## Exit 75

- `dev up`, `dev down` or `remove` waited 60 s on another start or stop of the same tree; the message names the holder's pid → let it finish, or find what that pid is before touching it.

## `dev up` exits 2 or 5

- `2` with "portless proxy is not running" → `portless proxy start`, once per boot; it runs as root on 443.
- `2` on the `ports` edge → a port already held; the message names its holder.
- `5` → a `dev down` arrived while it waited and won; start again only if the stop was not meant.

## A tunnel left pending

- A destroy that failed — Cloudflare unreachable — stays recorded and never blocks the cluster sweep → `~/.config/worktrunk/projects/nexus/nexus-wt tunnel-retry` once it is reachable; it destroys every recorded tunnel whose tree is gone.

## Setup step failed

```bash
git wt -C <tree> hook show                                  # step names, in order
git wt -C <tree> -y hook pre-start <step> [<later-step>…]   # re-run them
```

- A failing block aborts every block after it → re-run the failed step and every later one, in order.
- `--dry-run` renders the commands without running them; `-v` prints the template variables.
- A step to skip on the next create → `WT_SKIP=<group>,…` (`references/config.md`).
- A step prints a skip and a success alike → confirm its effect on disk.

## Repo not matched to its entry

- The entry key is the origin URL as `<host>/<owner>/<repo>` → a renamed repo or a changed remote leaves its trees with only the global steps: rename the `[projects."…"]` key to match `git -C <repo> remote get-url origin`.
- The canon conf matches the main checkout's directory name instead → a renamed directory makes the `canon` step a clean no-op: rename its conf with it.

## `fatal: not a git repository` inside a tree `git worktree list` still lists

- The two link files stopped agreeing: a tree's `.git` names the repo and `.git/worktrees/<id>/gitdir` names the tree back, both absolute unless `worktree.useRelativePaths` is set, so renaming or moving either rots them.
- From the repo, `git worktree list` keeps listing the tree as present; from inside it, every git command fails — each reads a different half of a link that no longer round-trips.
- A directory renamed under `~/Code` breaks the canon match at the same moment → § Repo not matched to its entry.

1. Read the link: `cat <tree>/.git` — starts `gitdir: ..` is relative, `gitdir: /` is absolute.
2. Repair, and make future ones relative:
```bash
git -C <repo> config worktree.useRelativePaths true
git -C <repo> worktree repair <tree>
```
3. Sweep the repo: `git -C <repo> worktree list --porcelain` marks each tree whose directory is gone `prunable`.

## A tree deleted by hand

- Moved rather than deleted → `git -C <repo> worktree repair <new-path>` before anything below.
- The directory went without `git wt remove`, so no teardown ran:
  1. `git -C <repo> worktree prune` drops git's entry.
  2. `~/.config/worktrunk/bin/wt-dev forget <tree-path>` stops what its units left running and deletes their records.
  3. nexus → `~/.config/worktrunk/projects/nexus/nexus-wt pg-sweep <main-checkout>` reaps clusters no live tree names, then `~/.config/worktrunk/projects/nexus/nexus-wt tunnel-retry` destroys every recorded tunnel whose tree is gone.

## Node clients fail TLS against a `.localhost` URL

- portless's CA is in the keychain, not in Node's store → `NODE_USE_SYSTEM_CA=1`.

## Shared canon missing from a tree

The canon is intact in the main checkout, and the repair is re-linking, never re-authoring → `cookbook/canon.md`.
