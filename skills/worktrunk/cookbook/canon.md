# Shared Canon Across Worktrees

## How sharing works

- Gitignored canon — `CLAUDE.md`, `.claude/`, docs the repo does not track — lives once, in the main checkout; every worktree holds symlinks to it, so an edit through either path is the same edit.
- The `canon` pre-start step links it at create; a `relink` step also re-links after every checkout, merge and rewrite; a project folder's `pre-remove` can run it once more before removal.
- The engine, `~/.config/worktrunk/bin/wt-sync-shared.sh`, reads `~/.config/worktrunk/canon/<name>.conf`, `<name>` the main checkout's directory name: shared roots (`CANON_ROOTS`), filenames (`CANON_FILES`), nested doc dirs (`NESTED_DOC_DIRS`); no conf → the step is a no-op.
- Per path, on every run: main has it → symlink the worktree at it · only the worktree has it → adopt it, moving the file into main and linking back · both hold real content → warn and leave the worktree's copy untouched.

## Step 1: Confirm the gap

The engine links what existed when it last ran, so canon authored since is absent from every older tree — a missing file, never an error.

```bash
ls -la <path>          # a symlink into the main checkout is correct state
```

- A symlink pointing at the main checkout is the working state: read and edit through it, and leave the link alone; only a genuinely absent path needs repair.

**Done when:** each shared path is classified as linked or genuinely absent.

## Step 2: Re-link

```bash
git wt -C <tree> -y hook pre-start canon
```

- Never copy the file in: a copy forks it into two diverging files.

**Done when:** the step exits 0 and the previously-absent path resolves through `ls -la` to the main checkout.

## Step 3: Verify the links resolve

```bash
find <tree> -type l ! -exec test -e {} \; -print
```

**Done when:** the command returns no rows — any row is a dangling symlink, which reads as a missing file.

## Authoring canon from inside a worktree

- A gitignored doc created inside a tree exists only there until the engine next runs and adopts it; a removal that skips a sweeping `pre-remove` — `git worktree remove`, deleting the directory — destroys it.
- Author shared canon in the main checkout; already written inside a tree → run the `canon` step to adopt it before the tree goes anywhere.

## Sharing a new top-level path

1. Append the path's name to `CANON_ROOTS` in the repo's conf — no trailing slash, since it becomes a symlink.
2. Ignore it by its bare name (`.agents`, never `.agents/` or `.agents/*`): the engine shares gitignored paths only, and a symlink matches no directory pattern, so it shows untracked and fails the removal guard.
3. Anything nested under an already-shared root is covered — no entry needed.
