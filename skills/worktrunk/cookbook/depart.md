# Depart into a ticket's worktree

## Create

0. `command -v git-wt` is empty → say so and stop.
   - No `~/.config/worktrunk/` on this host → `git wt -C <repo> -y switch --create <branch> --no-cd [--base origin/<base>]`; then § Then the work moves into it.
1. The repo's `AGENTS.local.md` lacks the worktree marker, or `~/.config/worktrunk/config.toml` holds no project entry for the repo → `cookbook/onboard.md` first.
2. A worktree for this ticket already exists → never create a second: take its path, and read who is seated there; a seat already at it holds this ticket → telling that session is the whole act, and for a build command the user typed here, name that seat to them and stop.
3. Create it:

```bash
git -C <repo> fetch origin <base>
~/.config/worktrunk/bin/wtk-new -C <repo> <branch> --base origin/<base>
```

   - `<branch>` → the convention the project's instructions state, filled from the ticket's id and title; none stated → `<author>/<short-slug>`, kebab-case; worktrunk takes it as typed and fetches nothing from the tracker.
   - Confirm the tree's `HEAD` equals `origin/<base>`'s tip before anything is seated there.
   - `WT_SKIP=<group>,…` skips the `wtk-step run` steps of those groups; a repo with a project folder → its `AGENTS.md` names any other create prefix.
   - The tree's path is `wtk-new`'s last line, `path: <tree>`.
4. A setup step failed → it names itself and aborts every later block: fix the cause, then `git wt -C <tree> -y hook pre-start <step> [<later-step>…]`, the names in `git wt -C <tree> hook show`'s order.

**Done when:** the tree exists at a known path and who is seated there has been read — a seat, nothing, or a listing that would not answer.

## Then the work moves into it

- This session's seat already stands at the path → carry on with the work here.
- A build command the user typed in this session — /implement , /implement-spec — stays in this session: work the tree from its path and commit on its branch; for /implement-spec , that branch is its integration branch.
- Otherwise → seat the work at the path through /cmux , the handoff carrying the path — a ticket and a throwaway alike.
- A throwaway tree — a repro, a spike, a measurement — reads its result off its seat's screen (/cmux , reading a seat); its seat closes with the tree.
- The terminal's prompt never tells occupancy: it shows where the seat was created, never who works the tree now.
- A listing that cannot be read → say occupancy is unknown and seat the work anyway.

**Done when:** the work is running at the tree — here, or in the session just seated there — and the reply names that seat.

## Do not stop here

Creating the worktree is never the deliverable: the work continues in the same turn, and the session says what it is doing, never asking whether to continue.
