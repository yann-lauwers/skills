---
name: worktrunk
description: >-
  Creates, lists, removes and repairs git worktrees through worktrunk (`git wt`). Use on "create a
  worktree", "show worktrees", "remove the worktree", "is the worktree running", "canon missing",
  "set up worktrees for this repo", "the worktree is broken"; also before any `git wt` or `git
  worktree add|remove` command, before cutting a tree for a ticket, a repro or a spike, and before
  an edit under `~/.config/worktrunk/`.
---

# Worktrunk

worktrunk (`git wt`) owns the worktree lifecycle. This machine's **layer**, `~/.config/worktrunk/`, adds setup steps, a removal fence and managed dev servers. Every tree lives at `~/worktrees/<repo>/<branch-slug>-<hash>`.

- A repo with a **project folder**, `~/.config/worktrunk/projects/<repo>/`, carries its own verbs and contract there. Read its `AGENTS.md` before any act its verbs cover — a database, a stack, a remote host.
- A host without the layer gets plain `git wt`: no setup steps, fence or dev servers.
- Every command takes `-C <repo>` or `-C <tree>`; the shell's cwd is never the target.
- A tree belongs to worktrunk when `wtk-owner` sits in its git admin dir; the fence refuses every other tree.
- Every confirmation a cookbook file names goes to the user in every mode, headless included: each guards a destructive or lasting act.

## The worktree marker

A repo uses worktrees when its root `AGENTS.local.md` carries this section; a repo without it works in its checkout as it stands.

```markdown
## Worktrees

- Work that will commit runs in its own worktree: `~/.config/worktrunk/bin/wtk-new -C <repo> <branch> [--base origin/<base>]` cuts it under `~/worktrees/<repo>/`.
```

- `CLAUDE.local.md` beside it reaches the line through an `@AGENTS.local.md` line, so Claude Code loads it; the `codex-local-instructions` plugin injects `AGENTS.local.md` into every Codex session.
- Both files are ignored by `~/.gitignore_global`, and the repo's canon conf lists both in `CANON_FILES`, so every tree carries the marker too.
- Read it with `grep -sF 'runs in its own worktree' "$(git -C <repo> rev-parse --show-toplevel)/AGENTS.local.md"`.

## Pick a route

Read the matching file before any other action.

| The request is… | Read |
| --- | --- |
| an overview of trees | `cookbook/dashboard.md` |
| a tree's work — create it and get it worked from there | `cookbook/depart.md` |
| whether a tree is running, at which URL, why it isn't answering | `cookbook/services.md` |
| removing a tree, or the merged ones | `cookbook/delete.md` |
| canon missing, or a new path shared across trees | `cookbook/canon.md` |
| setting worktrunk up for a repo, or changing its entry | `cookbook/onboard.md` |
| a failed command or step, stale state, a refusal | `cookbook/troubleshoot.md` |
| which command or flag does X, where something is kept | `references/command-surface.md` |
| an edit under `~/.config/worktrunk/` | `references/tooling-contracts.md` |
