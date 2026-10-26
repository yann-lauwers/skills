# Message craft

- A hook's output is a prompt read by a model mid-task, never an error code: a correct verdict delivered badly changes nothing.
- Write the message before the logic; a message that cannot be stated clearly is a rule not yet defined.

## Anatomy

### A NUDGE — advisory, blocks nothing, injected as context

Five parts, in order:

1. The check id in brackets, first token — the key tying the transcript to the decision log and the registry.
2. The observation, as a fact, with the real value interpolated; never an inference dressed as a fact.
3. The consequence — one clause on what goes wrong if it stands.
4. One action, runnable — an exact command, field name or path, with placeholders filled from the payload.
5. The no-op exit, explicit and first-class — "if X, take no action and do not mention this"; mandatory for anything firing on a proxy metric.

### A DENY — blocks the call; the reader must do something else

- Parts 1–4 as a nudge.
- Part 5 is the in-command override; none → say "Refused outright — there is no accepted spelling"; an environment override stays out of the message per § Where the override lives.
- Length scales up: include the matched substring or the resolved target, so a false positive is diagnosable without re-running.
- A deny on one spelling of an act names every spelling with the same effect, and the replacement.
- A wrong next action the reader is likely to take → close it off beside the right one.

#### Where the override lives decides whether your guard is a guard

| Placement | Who can use it | Right when |
|---|---|---|
| **In the command** — `re-issue with ACK=1` | the agent, unilaterally, in the next turn | the guard protects the *user* from a mistake the agent is well placed to judge. Recoverable in one action, no human round-trip |
| **In the process environment** — set in the settings file's `env` | **only a human, out of band** | the guard protects against *the agent itself*. A turn cannot set its own environment |

- The test: if the reader does exactly what the message says, is the dangerous thing prevented or performed? Performed → the override is in the wrong place, since an agent reading an in-command override appends the token and re-issues.
- Each recovery is stated where whoever can use it looks: an in-command override → the reason the agent reads · an environment override, or a prompt or agent hook's only recovery, removing its wiring entry → once, in the registry listing the check — `~/Code/skills/plugins/yann/hooks/REGISTRY.md` for this layer, the repo's own canon for a hook delivered into a repo — never in text the agent reads.

## The rules behind those verdicts

- Write every text a hook hands the model — a deny reason, `additionalContext` — as facts: the observation and the remedy stated (*"The accepted form is `pnpm typecheck`"*), never an order to the model (*"You must not deploy"*), which can trip the host's prompt-injection defences and surface the text to the user instead of using it as context; the no-op exit's pinned wording is the one exception.

- Never promise a recovery generically: the check that knows the situation writes the recovery, since a blanket suffix is false exactly where the deny matters most.
- Deletion Test on every citation: deleting a rule number, section reference or internal name costs the reader nothing → it was decoration; deleting it removes the actionable content → put the content in the message.
- Compute every path from the same constant the code uses, resolving from where the reader stands; never type one.
- Never assert a certainty the check cannot have, and never prescribe an irreversible act on a pattern match.
- One nudge per line; several checks speaking at once → label every part, the first included.
- Four messages about one subject are one message.

## Re-fire, re-arm, escalate

### Gates: no deduplication at all

- A gate fires on every matching action until its prerequisite is met, and is safe only while both hold:
  - its prerequisite is satisfiable by real activity;
  - its own stated remedy clears it.

### Advisories: once per obligation, keyed on the situation

- Never key the limiter on compliance: key it on the situation — `once_key = hash(the open work set)` — so an unchanged situation stops nagging and any new item mints a fresh key and budget.
- Re-arm on the activity that creates the obligation, never on the compliance that discharges it.

### The other half of the contract: what your design means for the reader

- Silence from a correctly keyed advisory carries no information about resolution: it goes quiet while the obligation is still outstanding.
- A signal that re-fires with its condition still true is a defect signal about the work, never noise about the signal.
- "I answered it once" is not a resolution state; a reader sorting nudges into already-addressed · false-positive · not-applicable names the fourth bucket: still unresolved, acknowledged.
- A re-firing nudge stays unacted on only when: the condition is demonstrably false · it is a verified false positive · its premise does not hold · an explicit tracked deferral carries a recorded reason, an objective re-arm condition and a durable task.
- Owning the reader's instructions too → write this rule there; owning only the hook → put one clause in the message: *"this re-fires while the condition holds; it going quiet means the condition changed, not that you handled it."*

### A deferral without a re-arm condition is a permanent off switch

- A gate treating "recorded as deferred" as satisfaction disarms itself for good: the record does not expire when its reasons do.
- Every deferral carries an objective, checkable re-arm condition, and lives in the durable store the reminder reads.
- Only the user grants a deferral, on their quotable approval; a deferral an agent grants itself is not a deferral.
- An obligation held only in prose does not survive a context reset → make it a tracked item.
- A reminder reading the deferral store lists every deferral still open.

### Rate limiting is a correctness surface

- Key the limiter per rule, not per check: a once-per-session gate shared across N rules lets one noisy rule silence the other N−1.

### Re-arm after a context compaction

- Compaction keeps the evidence that a prerequisite was met and loses the content → invalidate the evidence: archive the read-log at the compaction event, so the gates re-arm and force the re-read at the next gated action.
- Pair it with one orientation line naming which document.

### Three tiers, plus an observe rung

| Tier | Behaviour | Entry requirement |
|---|---|---|
| **Blocking** | denies the action | driven red on a known-bad input, and a measured false-positive rate |
| **Advisory** | injected as context, blocks nothing | a real consequence clause |
| **Annotation** | recorded only, no output | none |

- Promotion runs on data from the decision log; demotion is instant.

## Who sees it — and hiding turn-end noise

### At `Stop`, there is no invisible channel

Both turn-end outputs render to the user:

| Output | What the user sees |
|---|---|
| `decision: "block"` + `reason` | renders as a **hook error** |
| `hookSpecificOutput.additionalContext` | renders labelled **`Stop hook feedback`** — no error styling, but fully visible |

`suppressOutput: true` does **not** help: it hides raw *stdout* only, and neither of these travels that way.

Both also share the same loop protections, which you must handle either way: the input carries **`stop_hook_active`**, true when the turn is already continuing because of a stop hook, and the host **overrides the hook and ends the turn after 8 consecutive blocks**. Check `stop_hook_active` or you will block on a condition that can never resolve, eight times, in front of the user.

### The deferred-delivery pattern ("whisper")

- A turn-end advisory for the model alone, which the user gains nothing from seeing → never emit it at `Stop`:
  1. At `Stop`: append the message to a queue in session state and return nothing.
  2. At the next `UserPromptSubmit`: read the queue, emit it as `additionalContext`, and clear it.

This works because of an asymmetry in the contract: at `UserPromptSubmit`, `additionalContext` is injected as a **system reminder the model reads with no visible transcript entry** — while at `Stop` the equivalent field is labelled and shown. Same field name, different visibility, different event.

- No next prompt arrives → the queued advisory is never delivered; decide per message whether that loss matters — "you left work untracked" stays visible.
- The queue is a file: write it under the same atomicity discipline as any shared state.
- Write a queued message as a standing fact that still reads correctly one turn later, never "the command you just ran".

### Before you reach for hiding, check you are not treating a symptom

- A guard that has to be hidden to be tolerable fires too often → fix the trigger; never hide something because it fires too much.
- Check first: does it fire only when it should (once per obligation, § Advisories) · is the user the right audience · is it a block or an advisory.
- Hide only what the model needs and the user cannot act on; never hide a block.

## Delivery channels

| Channel | Event | What it does |
|---|---|---|
| `permissionDecision: "deny"` + `permissionDecisionReason` | PreToolUse | the call does not run; the reason reaches the model as the tool's outcome. **The only channel that changes what happens rather than what is known** |
| `additionalContext` | tool events, prompt events, compaction | injected as a system reminder; blocks nothing. The workhorse |
| `decision: "block"` + `reason` | Stop, SubagentStop, and others | refuses to end the turn and feeds the reason back. **Must enumerate the legal exits**, or the reader has no way to comply |
| `systemMessage` | any | displays to the **human**. One-way: a hook can show a question but cannot collect an answer |
| stdout | UserPromptSubmit, UserPromptExpansion, SessionStart | added as context on those three events; written to the debug log elsewhere |
| exit code | any | 2 blocks with stderr as the reason; anything else non-zero is a non-blocking error |

- A message that must reach the human — a destructive-action block only a person can resolve → `permissionDecisionReason` may not be enough; pair it with `systemMessage`.

## Checklist

- [ ] Check id is the first token
- [ ] The observation is a fact with a real interpolated value, not an inference
- [ ] There is a consequence clause
- [ ] There is exactly one runnable action, with placeholders filled
- [ ] A nudge has an explicit first-class no-op exit
- [ ] A deny names its in-command override in runnable syntax, or says there is none for its reader
- [ ] Its environment override, or a prompt or agent hook's recovery, is in the registry listing the check
- [ ] A deny includes the matched substring or resolved target
- [ ] No rule number or internal name carries actionable content (Deletion Test)
- [ ] Every path is computed from the same constant the code uses
- [ ] Every interpolated value has a sentence terminator after it
- [ ] The limiter is keyed on the situation, never on compliance
