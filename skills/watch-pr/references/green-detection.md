# Green detection — bot signals and the verdict rules

- `scripts/pr_classify.py` is the executable form of these rules, `scripts/pr_reads.py` the reads behind them; read this file before changing either.
- Ask whether each bot is done on the current HEAD, never whether unresolved threads exist now: a bot pending on a fresh HEAD has zero threads, and calling that `CLEAN` is the false green.

## How each bot signals done on HEAD

| Bot | Done signal on HEAD | Notes |
| --- | --- | --- |
| **Bugbot** (Cursor) | check run `Cursor Bugbot` (app slug `cursor`) at `status=completed`, whatever its conclusion | its bugs arrive as review threads under `conclusion=neutral` |
| **Bugbot Autofix** (Cursor) | none: excluded by `NON_REVIEW_BOT_JOBS` | runs beside the review and after it |
| **cursor[bot]** (inline reviewer) | a review authored by `cursor` whose `commit.oid == HEAD` | same vendor app as Bugbot |
| **CodeRabbit** | an app slug `coderabbit` check run at `status=completed`, whatever its conclusion, or a `coderabbitai` review on HEAD | either signal alone is done; absent is not pending |
| **CI** (GitHub Actions) | check runs from app `github-actions` | green = at least one surviving run, every one completed in {success, neutral, skipped}; zero runs is `none`, never green |

## The traps

### False-green

- A participating bot's review check on HEAD in `queued` or `in_progress`, inside the bot-pending timeout → gates.
- The PR inside the fresh window (default 420 s) with no completed check and no review from a participating bot → gates; this covers the registration race.
- An empty CI set is not a pass: zero surviving runs from a CI app is the state `none`. Inside the fresh window → `WAITING`; outside it → `CLEAN` whose reason says no CI ran.
- The fresh window runs from `reviewable_age_seconds` — the later of the HEAD commit and the last `ready_for_review` event — never from the commit alone.

### Draft

- `DRAFT` is decided from `draft` before any CI fact is read: jobs guarded on `draft == false` report `skipped`, which counts as passing.
- `DRAFT` is emitted once per HEAD and the watch continues, so `ready_for_review` resumes the same run.

### Absent-bot

- A bot gates only when it participates: a check on HEAD, or a review or comment it authored.
- Outside the fresh window, a participating bot's missing signal stops gating too.

### Stalled-bot

- A job matching `NON_REVIEW_BOT_JOBS` never gates.
- A review check pending past `--bot-pending-timeout` (default 1800 s) stops gating and is reported under `bots.stalled_checks`.

### Cancelled-supersession

- `dedupe_check_runs` keeps the most recently created run per app slug and name, never the newest `started_at`; a cancelled run that is still the newest for its name counts as failing.

## Mergeability, and the base

- A checkout answers for the repo → `Scm.facts` runs `git merge-tree --write-tree <head> <base tip>`, touching no working tree: exit 1 is `CONFLICT`, exit 0 is not; the line carries `conflict_source: git`.
- No checkout, or a failing git command → `Scm.facts` returns `None`, never a clean answer; `CONFLICT` is then `mergeable == false` or `mergeable_state == dirty`, with `conflict_source: forge`.
- GitHub's `mergeable` lags a moved base or a fresh push; trust it only as that fallback. `mergeable: null` → the read re-requests `pulls/{n}`, 3 s × 5.
- A base push moves nothing in the pull request's own read → the base ref is read each cycle (`git/ref/heads/{base}`), uncached.
- `behind_by` → `git rev-list --count <head>..<tip>` · `base_changed_files` → the diff between their merge base and the tip.
- `mergeStateStatus BEHIND` is never used: GitHub reports it only where the base requires up-to-date heads.

## Verdict rules

- Evaluated in order; the first match wins.
- `CONFLICT` sits ahead of the bot-wait rules, threads outrank CI red, and CI pending outranks `CLEAN`.

| # | Condition | Verdict |
| --- | --- | --- |
| 0 | `merged` | `MERGED` |
| 1 | closed without merge | `CLOSED` |
| 2 | `draft` | `DRAFT` |
| 3 | the trial merge conflicts, else `mergeable == false` or `mergeable_state == dirty` | `CONFLICT` |
| 4 | a review bot's review check pending on HEAD inside the bot-pending timeout | `WAITING` |
| 5 | bots participate, none done on HEAD, PR inside the fresh window | `WAITING` |
| 6 | unresolved bot threads > 0 | `NEW_COMMENTS` |
| 7 | `ci == failed` | `CI_RED` |
| 8 | `ci == pending` | `WAITING` |
| 9 | `ci == none` and PR inside the fresh window | `WAITING` |
| 10 | `ci == none` outside it | `CLEAN`, reason naming that no CI ran |
| 11 | otherwise | `CLEAN` |
| 12 | a `CLEAN` reading on a branch other PRs have merged into, whose base carries ≥ 1 changed file | `BASE_ADVANCED` |

- Rule 12 rewrites a settled reading rather than sitting in the chain, so it fires only once nothing else is owed on this head.
- Rule 12 triggers on changed files, never on the commit count.
- Rule 12 fires only where `pr_policy.merged_into` counts pull requests merged into the head; an unreadable count emits no `BASE_ADVANCED`.
- What a `CONFLICT` does is `pr_policy.may_rewrite`'s question, separate from rule 12: anything but `allow` is a merge.

## Tuning

- Fresh window (`--fresh-window`, 420 s), counted from `reviewable_age_seconds` → raise when bots register late · lower when the watch lingers in `WAITING` on PRs whose bots are not configured.
- Bot-pending timeout (`--bot-pending-timeout`, 1800 s) → lower when stalls are common · raise when a slow review bot is cut off (its name in `bots.stalled_checks` while its verdict was still coming).
- Adding a bot → extend `BOT_TOKENS`, add its done signal to the table above, and add any non-review sibling job to `NON_REVIEW_BOT_JOBS` in the same edit.
- CI apps → only `github-actions` gates CI by default; a third-party CI adds its slug to `CI_APP_SLUGS`.
