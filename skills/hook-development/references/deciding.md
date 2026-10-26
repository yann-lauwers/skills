# Deciding what to build

Answer these four in order, before any hook file is written.

## 1. Is a hook the right instrument at all?

Whether a hook is the home at all, against a check, a permission or a rule → /managing-harness § Where a fact goes. This table splits the cases that reach a hook.

| Signal | Instrument |
|---|---|
| The action would provably fail, orphan something, or ship something broken | Hook, blocking |
| The action is legal but a documented step was skipped | The document first: walk it as its reader and repair where it fails to say the step. A hook, advisory, only once the description is right — checking what the description now makes checkable |
| The agent needs a fact about the environment | Not a hook — /managing-harness § Where a fact goes picks its home, or return it as context |
| Judgement about intent, tone, or quality | Not a deterministic hook — § 2 |
| Stopping a human from doing something | Not a hook — the permission system |

Provable-Failure Test — the concrete failure the action causes, stated in one sentence without "should": stated → a block may be justified · needs "should" or "ideally" → a nudge at most.

## 2. Deterministic or model-judged?

| | Deterministic (`type: "command"`) | Model-judged (`type: "prompt"` / `"agent"`) |
|---|---|---|
| Fires on | events, file state, action sequences, payload fields | the model's reading of the input |
| Cost | one process, milliseconds | a model call on the critical path |
| Reproducible | yes — same input, same verdict, forever | no |
| Provable | fully, by one live drive and a break on purpose | only statistically |
| Instrumentable | yes — every fire writes a row | no. Its whole return is `{ok, reason}`; no code of yours runs |
| Rollout | observe mode, measured, promoted on data | none available — ships on the judge being right, retires when a human complains |
| Right for | "did the required artifact get written", "is this command destructive", "was the prerequisite met" | genuinely fuzzy calls where a wrong answer is cheap and flying blind is accepted |

- A model-judged hook has no decision log, false-positive rate, observe window or data to promote or retire it on — `rollout.md` § A model-judged hook cannot be instrumented.
- Default to deterministic: judge behaviour, file state and sequences of actions; leave language to the model.
- A predicate that is really an opinion — whether prose is "good enough" → a prompt hook, its non-determinism accepted, or no gate; never a deterministic hook.

### The request that will arrive, and how to answer it

- A request for a hook that fires on wording → never build the keyword scanner silently: a guard everyone believes in that misfires in both directions is worse than a refusal.
- Answer in three moves:
  1. Name the mismatch concretely — a word list has false positives in both directions and cannot judge tone — never "hooks shouldn't do that".
  2. Offer the route that exists: a `type: "prompt"` hook on `UserPromptSubmit` sends the input to a model and returns `{"ok": false, "reason": "..."}` — `events-and-contracts.md` § Prompt and agent hooks. The rule is "never let a regex pretend to be model judgement", not "never use model judgement".
  3. The user still wants the deterministic version → build it, and state what it will and will not catch in the message the hook itself emits. Disagree once, then commit.
- The same three moves answer every request whose predicate is an opinion: quality, tone, intent, "is this a good idea".

## 3. Block or nudge?

- Block only when certain: a misfiring nudge costs one line of noise; a misfiring block costs the user their action, their trust, and their compliance with every other gate.
- Default to nudge. Promote to block on data, once the decision log shows the check firing correctly and only correctly — `rollout.md`.
- Only checks that can block get a record-only rollout — `rollout.md` § Four properties the mode must have carries the mechanism.

## 4. Which event?

Pick it from the event table of the hooks reference `events-and-contracts.md` names.

- `PostToolUse` cannot block — the tool already ran. Blocking there is a design error, not a strict setting.
- A hook fires inside subagents too — `robustness.md` § Concurrency; for proving one, `testing.md` § The masking trap.

Decided → `build-procedure.md`.
