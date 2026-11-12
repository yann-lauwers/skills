# Wire contract — the line, the flags, the exit codes

- Every flag → `scripts/watch-pr.py --help`.
- The probe contract (loop, lock, backoff, blind) → /watching , § Write a probe; this file holds what is specific to the pull-request watcher.

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | a verdict line was printed, or `--once` |
| 1 | traceback (no line), or a `--once` read that did not land (a `WATCHER_ERROR` `unknown` line) |
| 2 | bad arguments |
| 3 | duplicate: another watcher holds this PR's lock |
| 4 | auth refused (HTTP 401) or `gh` missing |
| 5 | pull request not found on the first read |
| 7 | blind: no read landed for `--blind-after` (3600 s) |

## Stdout line

- One compact JSON object, flushed, then exit 0. Never a `WAITING` line outside `--once`.
- The line is printed once `verdict:key` differs from `--seen`; the key is `head|unresolved bot threads`, `head` for `DRAFT`, `head|base tip` for `BASE_ADVANCED`, each sha cut to 12 characters.

| Field | Present | Meaning |
| --- | --- | --- |
| `verdict` | always | `DRAFT` `CONFLICT` `NEW_COMMENTS` `CI_RED` `BASE_ADVANCED` `CLEAN` `MERGED` `CLOSED` `WATCHER_ERROR`; `--once` may also print `WAITING` |
| `reason` | always | one human line behind the verdict: the thread count, who merged into which base, the error's detail |
| `pr` | always | the pull request's number |
| `rearm` | every non-terminal verdict | the `--seen VERDICT:KEY` the next arm adds |
| `branch`, `base`, `integration_base` | `CONFLICT`, `BASE_ADVANCED` | the refs to integrate, and whether a pull request has already merged INTO this head (`true` `false` `"unknown"`), so it is absorbed by merge and never rebased |
| `stalled_checks` | when non-empty | review checks pending past `--bot-pending-timeout`, which stopped gating |
| `error` | `WATCHER_ERROR` | `auth` `duplicate` `pr_not_found` `gh_missing` `blind` `unknown` |

- The line carries what its row in the verdict table acts on; every other fact stays in `pr_classify.py`'s reading.

## Closeout line

- `scripts/closeout.py` prints one object: `closeout` is `removed`, `no_worktree`, `would_remove` (`--dry-run`) or `refused` with `reason`; exit 1 on `refused`.
- A refusal leaves the tree untouched: another session in it, occupancy unreadable, this session inside it (`cd` names the base checkout), uncommitted files, or a branch diff whose `git patch-id --stable` differs from the merge commit's.

## Flags worth tuning

- `--interval` (60 s) → seconds between reads.
- `--blind-after` (3600 s; 0 disables) → how long reads may fail before `blind`.
- `--fresh-window`, `--bot-pending-timeout` → `references/green-detection.md` § Tuning.
- `--seen VERDICT:KEY` → the reading already acted on; a re-arm passes the line's `rearm`.

## Lock and reads

- The lock is `fcntl.flock` on `~/.local/state/watch/pr/<owner>-<repo>-<pr>.lock`, held for the process's life and holding its pid; `--once` takes none.
- A failed read — timeout, no status line, an error body — prints nothing: a note on stderr, then a wait that doubles from `--interval` to 600 s, honouring `retry-after`.
- A 404 after a read has landed is a failed read, not `pr_not_found`.
