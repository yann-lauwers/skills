# Changing the Tooling Behind worktrunk

## Before and after the edit

- Each project folder's `CLAUDE.md` holds its safety contract and auto-loads only for a session whose cwd is that folder → read every `projects/*/CLAUDE.md` before changing anything under `~/.config/worktrunk/`.
- `bash ~/.config/worktrunk/bin/tests/suites.sh` runs every suite under `bin/tests/` and `projects/`: green before the edit, and green after it for the change to stand; a surface no suite covers → say so, and the change adds one.
- A change that adds or moves a destructive operation lands with a test pinning what it targets — this tree's own data, never a shared source or another tree's, and the fenced path prefix around any recursive delete; never a follow-up.
- A saved edit is live in this host's trees at once, and reaches no other host.
- worktrunk itself is Homebrew's `worktrunk` formula on macOS, the release binary in `~/.local/bin` on Linux: never patch the installed binary.

## Provisioned per-tree hooks

- A `relink` step writes `post-checkout`, `post-merge` and `post-rewrite` into the repo's shared hooks dir; a project folder's step installs its own hook sources, excluded from git.
- The copies are generated: edit the source, then re-provision with `git wt -C <tree> -y hook pre-start <step>`; an edit to a tree's copy lasts until the next provision.
- A fast-forward rebase fires only `post-checkout`, never `post-merge` or `post-rewrite` → after one, run the project's sync hook by hand.
