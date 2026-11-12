---
name: worktrunk
description: >-
  Creates, removes and serves git worktrees through worktrunk (`git wt`). Use before creating
  or removing a tree, on "is the worktree running", "canon missing", "set up worktrees for this
  repo", and before an edit under `~/.config/worktrunk/`.
---

# Worktrunk

worktrunk (`git wt`) owns every worktree, never `git worktree add|remove`. Trees live at `~/worktrees/<repo>/<branch-slug>-<hash>`. `git wt -h` lists the commands, `git wt <command> --help` their flags.

- Create → `git wt -C <repo> -y switch --create <branch> [--base <ref>] --no-cd --format json 2>/dev/null`; the tree is the JSON's `path`. A non-zero exit → rerun without `2>/dev/null` and read why.
- Remove → `git wt -C <repo> -y remove <branch> --foreground`.
- A repo with a **project folder**, `~/.config/worktrunk/projects/<repo>/` → read its `AGENTS.md` first: it names the create prefixes and its own verbs.
- Every confirmation a cookbook file names goes to the user in every mode, headless included.

| The situation is… | Read |
| --- | --- |
| where the work runs once the tree exists, a failed setup step | `cookbook/depart.md` |
| a removal the tool refused, pruning merged trees | `cookbook/delete.md` |
| whether a tree is running, at which URL, why it isn't answering | `cookbook/services.md` |
| canon missing, or a new path shared across trees | `cookbook/canon.md` |
| setting worktrunk up for a repo, or changing its entry | `cookbook/onboard.md` |
| an edit under `~/.config/worktrunk/` | `references/tooling-contracts.md` |
