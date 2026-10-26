# Depart into a ticket's worktree

For a session that arrived carrying one ticket: create its worktree, then get the ticket worked by a session seated at it — this session where its own seat already stands at that path or the work is a build command Yann typed in this session, a session seated there through /cmux otherwise. Where the work runs has one right answer; only the wording of the report is judgment.

## Create

0. No recorded opt-out, the repo has a worktrunk project entry, and `command -v git-wt` is empty → say so and stop.
   - No `~/.config/worktrunk/` on this host → `git wt -C <repo> -y switch --create <branch> --no-cd [--base origin/<base>]`, with no onboarding and no `WT_DB`/`WT_SKIP` prefixes; then § Then the work moves into it.
1. Neither a recorded opt-out in `docs/agents/worktrees.md` nor a project entry for the repo in `~/.config/worktrunk/config.toml` → `cookbook/onboard.md` first.
2. Create it:

```bash
~/.config/worktrunk/bin/wtk-new -C <repo> <branch> [--base origin/<base>]
```

   - `<branch>` → `~/.claude/skills/agents-config/scripts/agents-config get --role vcs branch_pattern`, filled from the ticket's id and title; `auto` → the version-control tool's skill resolves it: worktrunk takes it as typed and fetches nothing from the tracker.
   - A shared base goes as `--base origin/<base>` after `git -C <repo> fetch origin <base>`; then confirm the tree's `HEAD` equals that ref's tip before anything is seated there.
   - nexus → prefix `WT_DB=own` (the default), `WT_DB=stack:<branch>` or `WT_DB=remote` (`cookbook/db.md`); `WT_SKIP=<group>,…` skips setup groups (`references/config.md`).
   - It retries git's concurrent-add race on its own, and switches to an existing branch that has no tree instead of creating it.
   - The path → `git wt -C <repo> list --format json`, the item whose `branch` matches: where the work runs, and the path the handoff names where this session is not the one seated there.
3. Read what it printed: a failed setup step names itself and aborts the steps after it → `cookbook/troubleshoot.md` § Setup step failed.

- A worktree for this ticket already exists — an earlier run made one, or the work is being picked up → never create a second: take the existing path and read who is seated there first; a seat already at it holds this ticket → telling that session is the whole act, and for a build command Yann typed here, name that seat to him and stop.

**Done when** the tree for this ticket exists at a known path and occupancy at that path has been read — a client launched at that path, or a seat created there: a seat, nothing, or a listing that would not answer.

## Then the work moves into it

- A session started at the worktree, its seat created at that path, is the occupant: carry on with the work.
- A build command Yann typed in this session — /implement , /implement-spec — stays in this session: work the tree from its path and commit on its branch; for /implement-spec , that branch is its integration branch.
- A session started anywhere else seats the work at the path through /cmux , the handoff carrying the path this file resolved — a ticket and a throwaway alike.
- A throwaway tree — a repro, a spike, a measurement, a sweep nobody filed — reads its result off its seat's screen (/cmux , `references/observing.md`); its seat closes with the tree.
- The terminal's own prompt never tells occupancy: it shows where the seat was created, never who works the tree now.
- A listing that cannot be read → say the occupancy is unknown and seat the work anyway: a seat created at the path is the readable answer whatever the earlier read returned.

**Done when** the work is running in a session started at the worktree — this one where its seat is already there, or the one just seated at it — or in this session working the tree from its path for a build command Yann typed here. Where a reader would not answer, the reply says occupancy was unknown and names the seat it created.

## Do not stop here

Creating the worktree is never the deliverable: the work continues in the same turn — here where this session already stands at the tree or runs a build command Yann typed, in the session it seats otherwise — and the session says what it is doing, never asking whether to continue.
