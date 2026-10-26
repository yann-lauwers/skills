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
- The line is printed once `verdict:key` differs from `--seen`; the key is `head_sha|unresolved_bot_threads`, `head_sha` for `DRAFT`, `head_sha|base_tip_sha` for `BASE_ADVANCED`.

| Field | Type | Present | Meaning |
| --- | --- | --- | --- |
| `verdict` | string | always | `DRAFT` `CONFLICT` `NEW_COMMENTS` `CI_RED` `BASE_ADVANCED` `CLEAN` `MERGED` `CLOSED` `WATCHER_ERROR`; `--once` may also print `WAITING` |
| `reason` | string | always | one human line behind the verdict |
| `rearm` | string | every non-terminal verdict | the flags that replace their namesakes on the next arm, e.g. `--seen CI_RED:<head>\|<n>` |
| `pr`, `repo`, `url`, `branch`, `base` | scalars | always | identity and refs |
| `head_sha` | string | always | the measured HEAD |
| `ci` | string | not on `WATCHER_ERROR` | `green` `pending` `failed` `none`, after supersession dedupe; `none` is zero runs, never green |
| `unresolved_bot_threads` | int | not on `WATCHER_ERROR` | review threads opened by a review bot, unresolved |
| `bots` | object | not on `WATCHER_ERROR` | `participates`, `pending_on_head`, `done_on_head`, `stalled_checks` |
| `integration_base` | `true` `false` `"unknown"` | not on `WATCHER_ERROR` | a pull request has already merged INTO this head, so it is absorbed by merge and never rebased |
| `base_tip_sha` | string or null | not on `WATCHER_ERROR` | the base tip this reading measured against; null when no local checkout answers |
| `behind_by`, `base_changed_files`, `conflict_source` | int, int, `git` `forge` | `CONFLICT`, `BASE_ADVANCED` | commits the base carries that the head lacks, files that differ between their merge base and the tip, and whether a trial merge of the two shas or GitHub's `mergeable` decided |
| `rewrite`, `rewrite_reason` | strings | `CONFLICT` | /pull-request 's `pr_policy.py may-rewrite` answer for the head — `allow` `refuse` `unknown` — and why; `unknown` when no checkout or no rule module answers |
| `merged_by`, `merge_commit_sha`, `merged_at` | strings | `MERGED` | |
| `error`, `detail` | strings | `WATCHER_ERROR` | `auth` `duplicate` `pr_not_found` `gh_missing` `blind` `unknown` |

## Flags worth tuning

- `--interval` (60 s) → seconds between reads.
- `--blind-after` (3600 s; 0 disables) → how long reads may fail before `blind`.
- `--fresh-window`, `--bot-pending-timeout` → `references/green-detection.md` § Tuning.
- `--seen VERDICT:KEY` → the reading already acted on; a re-arm passes the line's `rearm`.

## Lock and reads

- The lock is `fcntl.flock` on `~/.local/state/watch/pr/<owner>-<repo>-<pr>.lock`, held for the process's life and holding its pid; `--once` takes none.
- A failed read — timeout, no status line, an error body — prints nothing: a note on stderr, then a wait that doubles from `--interval` to 600 s, honouring `retry-after`.
- A 404 after a read has landed is a failed read, not `pr_not_found`.
