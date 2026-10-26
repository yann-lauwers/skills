# Rollout and the decision log

## The decision log

- Instrument the blocking tier first and hardest: with no per-fire record, "never fired" and "fires wrongly every day" are the same data.

### Row schema

Append-only, one row per fire, positional and escaped:

| # | Field | Why it earned its place |
|---|---|---|
| 1 | `timestamp` | "how often" without "since when" cannot tell a check noisy since day one from one that started misfiring last week |
| 2 | `session` | groups a run |
| 3 | `event` | which lifecycle point |
| 4 | `actor` | which concurrent worker earned the row. **Measured: 52% of blocks were unattributable for want of this one field** — a check hammered by one badly-briefed worker looks identical to a broadly noisy check, and promotion then runs on merged distributions |
| 5 | `check_id` | a stable literal, passed **by the call site** — never derived from the message text, which would be keying on wording |
| 6 | `mode` — `enforce` / `observe` | **the most load-bearing field.** Without it a false-positive rate is contaminated in both directions |
| 7 | `verdict` — `deny` · `block` · `warn` · `would-deny` | an observe-mode check logs `would-deny`, never silence |
| 8 | `subject` | a bounded fingerprint of what was caught — tool name plus a hash or first N characters. You cannot judge "was this catch correct" without it. **Never log a full command**; they contain credentials |
| 9 | `outcome` | whether the actor complied, retried, or overrode. This is what turns a counter into evidence |

- One health counter in its own file, incremented on every write failure, so "no rows" and "could not write" leave different artifacts.

### Escape at the writer, unconditionally

```python
def _field(v):
    """One field: never a separator, never a newline, never None.

    A positional log with no escaping does not merely corrupt a field when a value
    contains a newline — it FORGES A WHOLE ROW, one that parses perfectly and is
    attributed to a component that never ran.
    """
    return str(v).replace("\t", " ").replace("\n", " ").replace("\r", " ")
```

### Logging must never change the verdict

Wrap every log write so a telemetry failure cannot suppress the decision it describes:

```python
try:
    log_decision(...)
except Exception:
    pass          # fail-open: telemetry must never suppress the verdict it describes
```

### Keep probe rows out of the log, and out of it explicitly

- Drive a live hook by hand — a payload piped into the script to read its verdict — only with `HOOK_STATE_ROOT` pointed at a temp directory.
- Never redirect `HOME` to sandbox a probe: a shell hook sources its logging sink from `$HOME`, so its rows go silent while the guard still renders its verdict.
- A probe row already in the log → exclude it by session id from an explicit list, opt-in; never by a pattern over the id's shape.
- A filter over a decision log errs toward showing too much; never a default-on one.

### Querying it

```bash
# schema drift — is more than one arity present?
awk -F'\t' '{c[NF]++} END{for(k in c) print k" cols: "c[k]}' decisions

# which checks fire most, and with what verdict
awk -F'\t' '{print $5}' decisions | sort | uniq -c | sort -rn | head
awk -F'\t' '{print $5"\t"$7}' decisions | sort | uniq -c | sort -rn

# blocks across the whole store
find . -name decisions -print0 | xargs -0 awk -F'\t' '$7=="deny"||$7=="block"' | wc -l
```

## A model-judged hook cannot be instrumented — and that decides where you may use one

- A `type: "prompt"` or `type: "agent"` hook writes no row. Its entire return schema is `{"ok": true|false, "reason": "..."}`. There is no field for telemetry, and no code of yours runs — the host calls the model.
- You can add a `type: "command"` handler on the same event, but handlers **run in parallel and cannot see each other's output**, so it can record that the event occurred and never what the judge decided.

| Mechanism | Command hook | Prompt / agent hook |
|---|---|---|
| per-fire decision row | yes | **no** |
| observe mode (`would-deny`) | yes | **no** — nothing to withhold and nothing to record |
| measured false-positive rate | yes | **no** |
| promotion on data | yes | **no** |
| feedback channel | the log | **a human noticing a bad block** |

- A model-judged gate ships on its judge prompt being right and retires on a human complaint → choose it deliberately, for a fuzzy call only:
  - Write the judge to fail toward passing: enumerate the legitimate-neighbour classes in the prompt and instruct it to pass anything it is unsure about.
  - State its recovery per `messages.md` § Where the override lives — an in-command override in its reason text, removing its wiring entry in its registry row — since no rollout window catches a bad judge first.
  - Count the cost at the right unit: a `UserPromptSubmit` prompt hook is one model call *per message you send*, on the critical path, with a 30-second default timeout.
  - Instrumentation needed → a `type: "command"` hook that calls a model itself and writes its own rows; never a prompt hook.

## Observe mode

- A marker file next to the hooks: present = the check records but does not act; absent = it enforces.

```python
OBSERVE = os.path.isfile(os.path.join(HOOKS_DIR, ".<check>-observe"))
...
log_decision(sid, event, CHECK_ID, "would-deny" if OBSERVE else "deny", mode=...)
if not OBSERVE:
    emit_deny(message)
```

### One semantic, one primitive

- Define what observe means once, in one shared function every check calls; never per-check convention.
- Its one meaning: record `would-deny` and act on nothing — never fully silent, never a rate-limited warning, never identical output with an `[observe]` suffix, which is a no-op.

### Four properties the mode must have

1. Distinguishable in the log: observe writes `would-deny`, enforce writes `deny`; identical rows leave nothing to justify the flip.
2. No rate limiting in the measuring mode; rate limits belong to the acting mode.
3. Only blocking checks get one: an advisory has no enforcement to withhold, so its "observe" is a no-op or a silencing, and its rollout gate is its promotion to blocking. An advisory kept for its rows alone ships only with a named reader of those rows — named in its row's `fires when` cell, per `registry.md` § Row schema; none → it does not ship.
4. It carries a date, and the question the reading settles; a window with no date is a check switched off.

- Declare the due date and its question in the same table that declares the mode, and have the reminder read that table: adding a check to observe then schedules its review.
- An entry carrying no date → report it; never refuse to run on it.

### The marker file is per-machine state — never ship it

```gitignore
# Observe markers are per-INSTALLATION rollout state, never shipped state.
hooks/.*-observe
```

- A gitignore rule does not untrack a file that is already tracked → `git rm --cached` it explicitly, and verify:

```bash
git ls-tree -r HEAD --name-only | grep -i observe   # must be empty
```

- Never commit an active marker: a fresh clone then downgrades a blocking check while it still reads as wired and the registry still says ENFORCING.
- A reconciliation of "is this check enforcing?" reads the working tree, the surface the running session obeys — never the index or HEAD.

## Choosing the default: compare failure DIRECTIONS, not probabilities

| Ship record-only | Ship enforcing |
|---|---|
| a clone silently downgrades a blocking check; nothing on that machine reveals it; undetectable without reading source | an unvalidated check blocks something legitimate on day one |
| **silent and invisible** | **loud and recoverable in one re-issue** |

- Loud-and-recoverable wins, payable only when every blocking verdict states its recovery per `messages.md` § Where the override lives.

## When does a check need a measurement window at all?

- Correct-Act Test: can a correct action produce this verdict?

| Predicate shape | Window needed? |
|---|---|
| Infers intent (`new < old * 0.3` means "truncation") | **yes** — retiring a deprecated section is indistinguishable from a truncation by size alone |
| Depends on state the system itself may have failed to record ("saw the path and never read it") | **yes** — a read through a route your feeds do not capture yields a deny on an action the reader was entitled to take |
| Compares a payload field to a fixed table, or counts against a constant | **no** — structural, not inferential. There is no input under which a correct act reads as the 25th dispatch |
| Reads the action's own resolved target | **no** |

- A check with a known false-positive class and high volume → fix the predicate; never open a window.

## Clearing the flip

- Never clear a rollout by waiting out a window: flip it, run genuine work against it, and read the log.

1. Rename the marker, never delete it — append a suffix the code cannot match (`.rm1-observe` → `.rm1-observe.hold`). Done when the check enforces; note the rename date.
2. Run the genuine-work journeys (`test-agents.md` T-A7) against it, the adjacent and off-path buckets included. Done when every scenario has run.
3. Read every row the check produced. Done when each deny is a correct catch and no legitimate work was blocked.
4. Record the flip with its reason and step 1's date. Done when the record carries the reason, step 1's date and both corpus counts.
5. A false positive appears → rename it back.

- The disarmed `.hold` residue is the one marker form that ships; an active marker is never committed.

### The reminder carries the counts, not the date alone

| Carry | Why |
|---|---|
| rows since the window opened, and per day | zero fires is itself a verdict — the rule landed, or the check is dead, and those read identically unless the number is shown |
| the verdict spread | separates a recorded verdict from an acted one; a window that is all one value has measured nothing |
| a breakdown of what was caught | the direction of the catch is the finding — which predicate fired, and on what |
| the same numbers from before the window | a count with no baseline cannot say whether anything moved |
| the question the reading settles | the reader acts on it instead of re-deriving it from the rows |
| a paste-ready prompt to act on it | the gap between "I should look at this" and "I am looking at this" is where a review dies |

- Count from the first fully acting day, never the day of the flip.
- "It fired correctly once" is no clearance: before flipping, measure against two corpora written independently of the implementation — the class targeted and its legitimate neighbours — and record both numbers beside the flip.

## The flip record, and why it needs a reader

- Never try to forbid a by-hand flip (`touch`/`rm`); detect the divergence:
  - At session start, glob the marker set as the running session sees it.
  - Diff against the recorded state.
  - Backfill missing rows, flagged as uncorroborated.
  - Emit one line when a marker is currently gating a blocking-tier check.

## Deliberate end-state

- At the close of any hardening cycle, every gate carries a recorded terminal state and a reason, the deliberately-off ones included.

| Check | End state | Reason |
|---|---|---|
| … | ENFORCING / observe / advisory-permanent | why this is the intended resting state |

- A marker on disk with no recorded reason is an open question, not a rollout.
