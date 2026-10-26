# Changing the Tooling Behind worktrunk

Governs edits under `~/.config/worktrunk/` — the commands in `bin/`, a project folder such as `projects/nexus/`, the canon engine, and the hook sources a step installs into each tree — the contract that binds them and the gates that prove a change safe.

## The governing contract

- `~/.config/worktrunk/projects/nexus/CLAUDE.md` holds the nexus layer's safety contract and auto-loads only for a session whose cwd is that folder → read it before changing anything under `~/.config/worktrunk/`, wherever the session stands; it is not discoverable from the file being edited.

## Before editing

1. Read the contract.
2. Run the gate for the surface about to change, for a green baseline — a suite already red turns a clean edit into an apparent regression:
   - `bash ~/.config/worktrunk/bin/tests/suites.sh` runs every suite under `bin/tests/` and `projects/`; a surface no suite covers → say so, and the change adds one.
3. Make the change.
4. Run the gate again; green is the condition for the change to stand.

- A change that adds or moves a destructive operation lands together with a test pinning what it targets — this tree's own cluster, never the seed source or another tree's, and the fenced path prefix around any recursive delete; the test is part of the change, never a follow-up.
- `~/.config/worktrunk/` is this host's own folder, backed up by the T7 only: a saved edit is live in this host's trees at once, and reaches no other host.
- worktrunk itself is Homebrew's `worktrunk` formula on macOS, the release binaries in `~/.local/bin` on Linux, upstream `max-sixty/worktrunk`: never patch the installed binary.

## Provisioned per-tree hooks

- A setup step can install git hooks into each tree, so pulls and rebases trigger the regeneration a branch switch would otherwise leave stale: nexus's `hooks` step installs husky `post-merge`, `post-rewrite` and `sync-changed.sh` from `projects/nexus/hooks/`, excluded from git; a `relink` step writes `post-checkout`, `post-merge` and `post-rewrite` into the repo's shared hooks dir, re-running the canon linker.
- The copies are generated: edit the source, then re-provision with `git wt -C <tree> -y hook pre-start <step>`; an edit to a tree's copy lasts until the next provision overwrites it.

## When a provisioned hook fires

- post-merge fires after a pull or merge, over the range the merge brought in.
- post-rewrite fires only when a rebase actually rewrote commits.
- A rebase that fast-forwards rewrites nothing and fires neither, leaving the tree on new commits without the regeneration they needed → run the project's sync hook by hand afterwards; the canon relink also hooks post-checkout, which a fast-forward does fire.
