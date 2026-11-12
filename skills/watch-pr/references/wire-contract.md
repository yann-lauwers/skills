# Wire contract — the line, the flags, the exit codes

- Every flag → `scripts/watch-pr.py --help`.

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | a verdict line was printed, or `--once` |
| 1 | traceback (no line), or a `--once` read that did not land (a `WATCHER_ERROR` `unknown` line) |
| 2 | bad arguments |
| 3 | duplicate: another watcher holds this PR's lock |
| 4 | auth refused (HTTP 401) or `gh` missing |
| 5 | pull request not found on the first read, or none resolved from the current folder |
| 7 | blind: no read landed for `--blind-after` (3600 s) |

## Stdout line

- One compact JSON object, flushed, then exit 0. Never a `WAITING` line outside `--once`.
- The line is printed once `verdict:key` differs from `--seen`; the key is `head|unresolved bot threads`, `head` for `DRAFT`, `head|base tip` for `BASE_ADVANCED`, `head|unresolved bot threads|attempt` for `CI_RED`, the newest item's epoch second for `HUMAN_COMMENTS`; each sha cut to 12 characters.

| Field | Present | Meaning |
| --- | --- | --- |
| `verdict` | always | `DRAFT` `CONFLICT` `HUMAN_COMMENTS` `BOT_THREADS` `CI_RED` `BASE_ADVANCED` `CLEAN` `MERGED` `CLOSED` `WATCHER_ERROR`; `--once` may also print `WAITING` |
| `reason` | always | one human line behind the verdict: the thread count, who merged into which base, the error's detail |
| `pr` | always | the pull request's number |
| `rearm` | every non-terminal verdict | the next arm's whole argument list: `--pr <url> --seen VERDICT:KEY`, plus `--humans-after` once a `HUMAN_COMMENTS` line was printed |
| `failed_jobs` | `CI_RED` | per failed job: `name`, `run_id`, `attempt`, and `log`, the command that prints the job's log while the run is still going; the log carries colour codes, which `gh api` prints only under `--allow-escape-sequences` |
| `items` | `HUMAN_COMMENTS` | the newest 10: `author`, `kind` (`thread` `review` `comment`), `url` |
| `branch`, `base`, `integration_base` | `CONFLICT`, `BASE_ADVANCED` | the refs to integrate, and whether a pull request has already merged INTO this head (`true` `false` `"unknown"`), so it is absorbed by merge and never rebased |
| `stalled_checks` | when non-empty | review checks pending past `--bot-pending-timeout`, which stopped gating |
| `error` | `WATCHER_ERROR` | `auth` `duplicate` `pr_not_found` `gh_missing` `blind` `unknown` |

- The line carries what the agent acts on; every other fact stays in `pr_classify.py`'s reading.

## Flags worth tuning

- `--interval` (60 s) → seconds between reads.
- `--blind-after` (3600 s; 0 disables) → how long reads may fail before `blind`.
- `--fresh-window`, `--bot-pending-timeout` → `references/green-detection.md` § Tuning.
- `--pr N|URL` → the pull request; absent → the current folder's branch. `--repo` qualifies a bare number.
- `--seen VERDICT:KEY`, `--humans-after EPOCH` → the reading already acted on; a re-arm passes the line's `rearm` whole.

## Lock and reads

- The lock is `fcntl.flock` on `~/.local/state/watch/pr/<owner>-<repo>-<pr>.lock`, held for the process's life and holding its pid; `--once` takes none.
- A failed read — timeout, no status line, an error body — prints nothing: a note on stderr, then a wait that doubles from `--interval` to 600 s, honouring `retry-after`.
- A 404 after a read has landed is a failed read, not `pr_not_found`.
