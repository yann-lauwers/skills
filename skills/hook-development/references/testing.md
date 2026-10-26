# Proving a hook live

- A hook is proven by driving the real file once and reading what it decided.
- In the user-level layer, and in any repo that keeps no hook suite, nothing is kept as a test file; a repo that keeps one also runs its suite.
- This proves the program; whether it guards real work is `test-agents.md` T-A7.

## The proof

1. Build one payload of the shape the host sends for the event — copied from a transcript's call, or written field by field from the event's schema in the hooks reference `events-and-contracts.md` names. Done when it carries every field the hook reads.
2. Point the state root at a fresh temp directory: `HOOK_STATE_ROOT=$(mktemp -d)`, never `HOME` — `rollout.md` § Keep probe rows out of the log, and out of it explicitly. Done when the directory is empty.
3. A gate with a prerequisite → write the prerequisite through its real feed: drive the feeding event's payload into the same `HOOK_STATE_ROOT` and session id first; for the substance case, feed an unrelated row the same way. Done when the feed holds the row its real writer wrote.
4. Pipe the payload into the hook through the exact command the wiring runs — copied from the handler's `command` in the settings file of the level that wires it, with `CLAUDE_PROJECT_DIR` set to the repo root for a project hook — never a `python3` off `PATH`. Done when stdout, stderr and the exit code are captured.
5. Read the decision row back from `$HOOK_STATE_ROOT/hook-decisions.jsonl`; a handler that writes none is read by its stdout and exit code. Done when the row names the expected check and verdict.
6. Drive the look-alikes the same way, one payload each: the act behind a wrapper, the act spelled differently, and the same token as text — in `echo`, a commit message, a `grep` pattern, a heredoc body, a heredoc whose opener carries a redirect (`<<'EOF' 2>&1`), an inline interpreter string, a filename. Done when the act fires and every mention stays silent.
7. Once wired, read a row under a real host session id in `~/.claude/state/hook-decisions.jsonl`, distinct from the probe's id. Done when the host itself produced it.

## Break on purpose

- A proof never seen to move proves nothing.

- Break a copy, never the live file: every session runs the live file, and a broken guard is off for all of them.

1. Establish sole-writer status — § Before breaking a copy. Done when nothing else writes the hook's directory.
2. Copy the hook's tree aside with plain `cp`: `cp -R "$(readlink -f <hooks dir>)/." <scratch>/hooks/`, and keep a second plain `cp` of the hook file as `<scratch>/<hook>.orig`. Done when `cmp` reports the copied hook identical to the live one, and the copy resolves every helper it loads inside `<scratch>/hooks/` — grep the hook for `$HOME`- or `~`-anchored paths, and run such a hook with `HOME` pointed at a scratch home whose `.claude/hooks` links to the copy.
3. Drive the payload through the wiring command with the hook path swapped to the copy. Done when the copy gives the live row.
4. Break the predicate in the copy in the smallest way that still parses — invert the condition, drop a negation, delete one clause of a conjunction, remove the emission. Done when the copy still parses.
5. Drive the same payload into a fresh state root. Done when the exit code is 0, or 2 where the broken predicate's verdict is a deny the hook signals by exit code, stderr carries no traceback, and the row shows the verdict the broken predicate yields; any other non-zero exit or a `check-error` row means the break crashed the hook — redo it.
6. Restore with plain `cp <scratch>/<hook>.orig <scratch>/hooks/<hook>`, never `cp -p`: a restored mtime makes a timestamp-fingerprinting reader skip the reload. Drive once more. Done when the original row is back.

- A row that does not move → the payload never reached the predicate, or the break is inert: read what the break changed before calling the predicate proven.

## Paths no payload reaches

- A branch no input reaches — the per-check exception record, a lock timeout, a store-write failure, a "cannot resolve the repo" fallback — is broken on purpose the same way: plant the fault in the copy, drive one payload, restore with `cp`.
- Read four things off that drive: the error is recorded, it names the check that failed, the process exits 0, and a healthy sibling still fires.

## The masking trap

- A gate that unlocks on prior session state is unprovable in a session where that state already exists: any earlier read — by this session, a helper, a background agent — satisfies the prerequisite and the proof passes for nothing.
- That state spans the whole agent lineage: a subagent's payload carries the parent's session id (`robustness.md` § Concurrency).

| Step | Actor | Action | Verdict |
|---|---|---|---|
| A | main loop | the gated command | **deny** |
| B | worker | reads the governing document | (writes to the shared read-log) |
| C | main loop | the identical command | **allow, no output at all** |

- Countermeasures, strongest first:
  1. A fresh state root per drive.
  2. A fresh session id per payload.
  3. Read the state back after the drive, so a pass for the wrong reason is visible.
  4. A live trip in a host session → a fresh session, or the state directory deleted first and asserted empty.
  5. Prerequisites that are durable artifacts on disk over session state.
- One-shot flags consumed by whoever arrives first → fire the same event from two actor identities and confirm both see it, where that is the intent.
- A durable flag with no clearing writer and no age bound → grep every flag key for its writer, reader and clear sets before trusting any proof of the gate it controls.

## Before breaking a copy

- Establish that nothing else writes the tree — no other session, no lane this session dispatched — with `ps`, before the break, never after the surprise.
- A row that changes identity between drives of one payload is a concurrency signal: stop and find the other writer.
- Stamp the proof with what it measured — the commit or the mtime of the file under test.

## The report

- The proof is reported in the reply: the payload, the command, the row before the break, the row during it, the row after the restore, and the host row with its session id.
- Every report ends with "What I could not establish"; recurring entries:
  - whether an `allow` verdict overrides configured deny rules, which decides whether a guard's silence is safe;
  - true-positive recall — real traffic bounds false positives well and false negatives badly;
  - filesystem generality, where atomicity and locking were measured only locally.
- Settled, never re-litigated:
  - a crashed hook fails open — exit 1 is a non-blocking error, so a "bypass" finding of that class is real;
  - concurrency is measurable only with several real processes — a single-process measurement is unmeasured, never a pass.
