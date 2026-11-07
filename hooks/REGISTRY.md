# Hook check registry

**A check that is not listed in this registry is a defect: add the row in the same commit that adds the check.**

**A check that is removed is retired in the same commit: the row goes, its `Retired id` clause arrives in `registry/retired.md`, and every surface that named it is cleared.**

## Parts

- This file — the wiring, how to read a decision row, the readers and the rollout mode.
- One part per tier of live check, each a table of `id · component · event · fires when · class · rollout`, the blocking tier first: `registry/deny.md` · `registry/permit.md` · `registry/act.md` · `registry/warn.md`; an ANNOT row counting a withheld deny or grant sits beside that tier's rows, so a row's class is its class cell.
- `registry/project.md` — checks a repo enforces, listed so their ids reconcile; none writes the shared log.
- `registry/no-verdict.md` — the handlers that decide nothing; every handler in `~/.claude/settings.json` is a row in a tier part or a name there.
- `registry/retired.md`, `registry/retired-to-2026-10-07.md` — every retired id, verdict and pattern name.
- `registry/outside-packs.md` — the keyless pack, plugin handlers and Orca's entries, which run beside this layer's on the same events.
- A new tier or subject → a new part, linked here; a part over 20,000 bytes splits.

## The wiring

- `hooks/hooks.json` in this plugin is what runs; it is hand-written, and the `event` column records where a check was wired when its row was written.
- Every matching handler runs in parallel, and none sees another's output or `updatedInput`; array position confers no precedence, and which of two conflicting verdicts wins is unverified.

## Reading a decision row

Rows are JSON lines in `$HOOK_STATE_ROOT/hook-decisions.jsonl` (default `~/.claude/state/hook-decisions.jsonl`), one per fire:

```json
{"ts": "<ISO 8601 UTC>", "check": "<id>", "session": "<session_id>", "verdict": "<verdict>", "detail": "<bounded fingerprint, 200 chars>", "mode": "<enforce|observe>"}
```

- Optional keys, absent by default: `mode` (always written by a check with an observe rung), `event`, `actor`, `outcome`, `provider` (absent means Claude; `codex` marks a row a Codex entry wrote with `AGENT_HOOK_PROVIDER=codex`), and `backfilled` (a derived value, not observed).
- Verdicts: `deny` · `ask` (put to the person through the host's prompt) · `would-deny` (observe: recorded, allowed) · `warn` · `stamped` / `would-stamp` · `injected` / `truncated` / `silent` · `credited` / `slice` / `unknown-verb` · `preloaded` · `over-cap` · `unresolved` · `broken` (a model judge could not answer; allowed) · `inert` (a self-test found the guard unable to work) · `abstain` (the observable was unreadable; `detail` carries `class=<why>`) · `error` (the hook raised; the action proceeded unguarded).
- Silent evaluations write no row; the log counts fires, not calls.
- `lib/hook_run.py` wraps every Python hook's `main()` and writes a raise as `verdict=error` with `outcome=raised` under the hook's id; an `error` without that mark is a condition the handler recorded itself.
- Both sinks — `lib/log-decision.sh` and `lib/hook_decisions.py` — write through one writer that strips control characters and counts a failed write in `hook-decisions.health`.
- `detail` names the pattern or rule that matched, never the payload.

## Readers

- `hook-decisions` (`~/.local/bin/`): a per-check summary; `--drift` reconciles this registry against the source (by AST) and the log, counting verdict-bearing rows only and listing crashes apart — the last 24 hours (`lib/hook_log_summary.py` `RECENT`) as a discrepancy, older ones as history; `--modes` prints what every check is doing now; `--exclude-probes` hides the session ids in `lib/probe-sessions.txt`, an explicit list, never a pattern.
- `lib/hook_registry.py` `registry_text()` joins this file and every `registry/*.md`; `hook-decisions` reads the rows through it, so a part needs no reader change.

## Rollout mode

- `lib/hook_mode.py` resolves a check's mode from `HOOK_MODE_<CHECK_ID>` in the environment, else the default the check passes, else `enforce`; a turn cannot set its own environment, so the guarded session cannot reach its guard's mode.
- Change a mode in `env` of `~/.claude/settings.json`, and record why in the same change, in the check's rollout cell.
- A mode never lives in a file: a session can create a file, but cannot set its own environment.
- `~/.local/bin/hook-review-notify`, run daily by `com.yann.hook-review-notify` through `run-if-due.sh`, DMs the last day's crashes; `--dry-run` prints instead of sending.
- The rollout cell's first backticked token — `ENFORCING`, `OBSERVE` or `RECORDING` — is what `hook-decisions --modes` compares against the running mode.

