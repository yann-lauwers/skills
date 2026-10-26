# Shared Canon Across Worktrees

Keeps a repo's gitignored canon — `CLAUDE.md`, `.claude/`, docs the repo does not track — as one shared copy that every worktree links to, and repairs a tree whose links are missing.

- The repair is re-linking, never re-authoring; which paths a repo shares is its policy conf's call.

## How sharing works

- Gitignored canon lives once, in the main checkout, and every worktree holds symlinks to it: one inode, so an edit through either path is the same edit — no copies, no merge, no daemon.
- Timing — the `canon` pre-start step links it at create; a repo whose entry carries a `relink` step also re-links after every checkout, merge and rewrite through git hooks; nexus's `pre-remove` runs it once more before removal.
- Mechanism — one repo-agnostic engine, `~/.config/worktrunk/bin/wt-sync-shared.sh`, enumerates each side's gitignored paths and reconciles them.
- Policy — `~/.config/worktrunk/canon/<name>.conf`, `<name>` the main checkout's directory name, lists the shared roots (`CANON_ROOTS`), filenames (`CANON_FILES`) and nested doc dirs (`NESTED_DOC_DIRS`); no conf → the step is a no-op.
- Per path, on every run: main has it → symlink the worktree at it · only the worktree has it → adopt it, moving the file into main and linking back · both hold real content → warn and leave the worktree's copy untouched; it never merges.
- Machine state is never shared — env files, dependency directories, build output, generated clients: the setup steps write those per tree.

## Step 1: Confirm the gap

The engine links what existed when it last ran, so canon authored since is absent from every older tree — a missing file, never an error.

```bash
ls -la <path>          # a symlink into the main checkout is correct state
git -C <tree> status   # canon showing as ignored or absent is also correct
```

- A symlink pointing at the main checkout is the working state: read and edit through it, and leave the link alone; only a genuinely absent path needs repair.

**Done when:** each shared path is classified as linked or genuinely absent.

## Step 2: Re-link

```bash
git wt -C <tree> -y hook pre-start canon
```

- Never copy the file in: a copy forks it into two diverging inodes. A stacked tree needs the step like any other.

**Done when:** the step exits 0 and the previously-absent path resolves through `ls -la` to the main checkout.

## Step 3: Verify the links resolve

```bash
find <tree> -type l ! -exec test -e {} \; -print
```

- Any row is a dangling symlink, which every tool reads as a missing file rather than an error, so a repair reports success and the gap surfaces later, elsewhere.

**Done when:** the command returns no rows.

## Authoring canon from inside a worktree

- A gitignored doc created inside a tree exists only there until the engine next runs and adopts it; removing that tree by any route but nexus's `pre-remove` — `git wt remove` in another repo, `git worktree remove`, deleting the directory — destroys it.
- Author shared canon in the main checkout; already written inside a tree → run the `canon` step to adopt it before the tree goes anywhere.

## Sharing a new top-level path

1. Append the path's name to `CANON_ROOTS` in `~/.config/worktrunk/canon/<name>.conf` — no trailing slash, since it becomes a symlink. `WT_CANON_CONF` points one engine run at a different conf.
2. Add it to the repo's ignore rules, per the repo's own ignore-file convention: the engine shares gitignored paths only.
3. Anything nested under an already-shared root is covered — no entry needed.
