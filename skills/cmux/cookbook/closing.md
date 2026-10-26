# Closing

- Which seats are finished is the caller's call · where the caller names none, the reads in § Closing one seat decide.
- The seat this session sits in → § Closing your own seat, whatever closes it; no other section applies to it.

## Closing one seat

- Closing kills whatever runs in the seat.
- Close another session's seat when its work's end is established — the caller names it finished (the unit merged, the session was killed, the deliverable landed elsewhere) — it is stranded (its directory gone), or both reads come back empty: `$C read-screen --workspace <ref>` shows no session mid-turn and `git -C <path> status --porcelain` prints nothing.
- Otherwise close nothing; report what the seat still holds.
- A seat with a running process refuses without `--force` (`confirmation_required`):

```sh
$C workspace close <workspace-ref> --force
```

## Closing your own seat

```sh
${CLAUDE_SKILL_DIR}/scripts/close-status.sh [--no-pr]                 # what the decision needs, in one read
${CLAUDE_SKILL_DIR}/scripts/self-close.sh <workspace-ref|uuid> [--delay <s>] [--reason <text>] [--timeout <s>]
```

1. Run `close-status.sh` first; it answers which ref. An unresolved ref → close nothing; never guess one.
2. Read its output, its `BLOCKERS` list included, as input to a judgement, never a verdict.
3. The work has left → run `self-close.sh` on the ref; `--delay` (default 8 seconds) holds the close until the closing reply reaches the user → raise it for a long closing message.
4. Read the arming line before trusting it: the script exits non-zero when its detached child is not alive.

- Never close your own seat with `workspace close` itself, `--force` or not: only `self-close.sh` survives to verify it.
- Exit 0 → closed and verified, or no seat to close · 1 → the close failed or could not be verified · 2 → usage, or a ref naming no live workspace.
- A failure raises a `⚠️ self-close failed` seat; a seat that outlives its work with no alarm → read `~/.claude/logs/cmux-self-close-FAILED.txt`.
- After any change to `self-close.sh` → run `bash scripts/self-close-test.sh`, which holds its contract against the stub beside it; `SELF_CLOSE=<copy>` runs it against a mutation.

## Sweeping stranded seats

A worktree's removal leaves its seat standing.

1. List every workspace: `$C workspace list --json`.
2. Test each `current_directory` against the filesystem.
3. Close every miss.

## Removing a folder

| Intent | Command |
| --- | --- |
| dissolve the folder, keep every seat | `$C workspace-group ungroup <group-ref>` |
| dissolve it and close every member | `$C workspace-group delete <group-ref> --close-workspaces` |

- `ungroup` is the reversible one: the seats survive and can be regrouped.
- `ungroup` leaves every surviving seat at the sidebar's top level → ungroup only a folder with no open member.
- A folder with live members → first move each into its repository's folder with `$C workspace-group add --group <that folder> --workspace <ref>`, recoloured to that folder's hue in the same act — `cookbook/repair.md` § The three drifts carries the second line.
- `--close-workspaces` kills every session in the folder at once → only when the whole effort is finished and each member meets § Closing one seat's close condition · this session's own seat among the members → close the others one by one, then § Closing your own seat.
- A folder empties as its last member closes, so an effort whose seats were all closed one by one needs no teardown.
