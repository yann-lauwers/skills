---
name: worktrunk
description: >-
  Creates, removes and serves git worktrees through worktrunk (`git wt`). Use on "create a
  worktree", "remove the worktree", "is the worktree running", "canon missing", "set up worktrees
  for this repo"; also before any `git wt` or `git worktree add|remove` command, before cutting a
  tree for a ticket, a repro or a spike, and before an edit under `~/.config/worktrunk/`.
---

# Worktrunk

worktrunk (`git wt`) owns the worktree lifecycle. This machine's **layer**, `~/.config/worktrunk/`, adds setup steps, a removal fence and managed dev servers. Every tree lives at `~/worktrees/<repo>/<branch-slug>-<hash>`.

- A repo with a **project folder**, `~/.config/worktrunk/projects/<repo>/`, carries its own verbs and contract there. Read its `AGENTS.md` before any act its verbs cover — a database, a stack, a remote host.
- A host without the layer gets plain `git wt`: no setup steps, fence or dev servers.
- Every command takes `-C <repo>` or `-C <tree>`; the shell's cwd is never the target; `remove` and `step prune` take `-C <repo>`, since the tree goes from under `-C <tree>`.
- A tree under `~/worktrees/` is created and removed through `git wt`, never `git worktree add` or `remove`: those skip the ownership token, the fence and every teardown, leaving units and a project folder's resources behind.
- Every confirmation a cookbook file names goes to the user in every mode, headless included: each guards a destructive or lasting act.
- `git wt -h` lists worktrunk's commands, `git wt <command> --help` one command's flags; `git wt --help` looks for a man page that is not installed.

## Pick a route

Read the matching file before any other action.

| The request is… | Read |
| --- | --- |
| a tree's work — create it and get it worked from there | `cookbook/depart.md` |
| removing a tree, or the merged ones | `cookbook/delete.md` |
| whether a tree is running, at which URL, why it isn't answering | `cookbook/services.md` |
| canon missing, or a new path shared across trees | `cookbook/canon.md` |
| setting worktrunk up for a repo, or changing its entry | `cookbook/onboard.md` |
| an edit under `~/.config/worktrunk/` | `references/tooling-contracts.md` |
