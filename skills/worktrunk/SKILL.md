---
name: worktrunk
description: >-
  Creates, lists, removes and repairs git worktrees through worktrunk (`git wt`) and this
  machine's layer on it — per-repo setup steps, shared canon, dev servers behind portless names,
  nexus's socket-only Postgres and tunnel. Use when the request says "create a worktree", "show
  worktrees", "worktree status", "delete the worktree", "clean up merged worktrees", "prune
  worktrees", "is the worktree running", "the .localhost URL", "dev up", "check the db", "reseed
  the db", "stack on a branch", "share its db", "canon missing in the worktree", "CLAUDE.md is
  missing in this worktree", "set up worktrees for this repo", "the worktree is broken", "git wt",
  "worktrunk" or "portless". Also fires on the ACT — before any `git wt`, `git-wt`, `wtk-new`,
  `wtk-step`, `wt-dev`, `wtk-web` or `nexus-wt` command; a worktree about to be created for a
  ticket, a repro or a spike; `git worktree add` or `git worktree remove` about to run by hand; a
  repo with neither a worktrunk project entry nor a recorded opt-out; an edit under
  `~/.config/worktrunk/`.
---

# Worktrunk

worktrunk (`git wt`) owns the worktree lifecycle; `~/.config/worktrunk/` adds this machine's setup steps, teardown fences, detached dev units and nexus's per-tree stack. Trees live at `~/worktrees/<repo>/<branch-slug>-<hash>`.

- No mode — YOLO or headless — skips a confirmation this skill puts to the user: each guards a destructive or lasting act — a forcing remove, a database wipe, a branch convention every later branch follows.
- Every command takes `-C <repo>` or `-C <tree>`; never rely on the shell's cwd.
- A tree belongs to worktrunk when `wtk-owner` sits in its git admin dir; the global `pre-remove` fence refuses every other tree.
- `~/.config/worktrunk/` is per host: a host without it gets plain `git wt` — no setup steps, fences, dev units or nexus stack.
- Write `git wt`; `wt` is the same binary.

## Before acting

Read the file the routing table matches before any other action.

## Cookbook — Intent Routing

| IF the request is… | THEN | Examples |
| --- | --- | --- |
| A worktree overview | Read `cookbook/dashboard.md` | "show worktrees", "worktree status", "worktree overview", "which trees are merged" |
| Is it running, at which URL, why isn't it answering | Read `cookbook/services.md` | "is the worktree running", "dev up", "the .localhost URL", "check the logs", "the frontend isn't loading", a nexus tree on the remote host |
| Getting work into its own worktree — create it, then get it worked from there | Read `cookbook/depart.md` | a session given one ticket; a session cutting a tree for a repro, a spike or a measurement |
| Remove a worktree, or clean up merged ones | Read `cookbook/delete.md` | "delete the worktree", "remove the tree", "prune worktrees", "clean up merged worktrees" |
| Build a nexus tree on another branch's work or database | Read `cookbook/stack.md` | "stack on a branch", "WT_DB=stack", "borrow the db", "share its db" |
| A nexus tree's database — connect, query, reset, reseed, restore | Read `cookbook/db.md` | "check the db", "query the db", "db url", "reseed the db", "pg won't start" |
| Shared canon missing, or sharing a new path across worktrees | Read `cookbook/canon.md` | "canon missing in the worktree", "CLAUDE.md is missing in this worktree", "re-link the canon", "share docs/ across worktrees" |
| Settle whether a repo uses worktrees, and set worktrunk up where it does — or change its entry | Read `cookbook/onboard.md` (+ `references/config.md` for the keys) | "set up worktrees for this repo", "add this repo to worktrunk", "add a setup step", "add a dev alias", a repo with neither a project entry nor a recorded opt-out |
| A command fails, a step failed, stale state, a refusal | Read `cookbook/troubleshoot.md` | "the worktree is broken", "remove refused", "exit 75", "re-run a setup step" |
| Which command or flag does X, or where something is kept | Read `references/command-surface.md` | "where is the worktrunk config", "where are the dev logs", "which flag keeps the branch" |
| Change a command under `~/.config/worktrunk/`, a project folder, or a hook a step installs | Read `references/tooling-contracts.md` | "edit wtk-step", "change nexus-wt", "re-provision the husky hooks" |
