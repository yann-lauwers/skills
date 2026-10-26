# Build procedure

Nine steps for one check, from a signal to a shipped guard. `deciding.md` runs before step 1; `events-and-contracts.md` is read before any file is written.

1. Write the failure sentence: one sentence naming the concrete failure this prevents. It needs "should" → stop: a preference, not a gate. Done when the sentence names a failure.
2. Choose the observable the hook reads: a payload field, a file's existence, a state feed, a sequence of prior actions. "What the user said" → stay on this step until a behavioural one is found. Done when the observable is an act or a state.
3. Write the trigger against the observable, applying laws 1–3 below, after reading `trigger-design.md`. Done when its checklist passes.
4. Write the message from the template in `messages.md`, before the logic. Done when its checklist passes.
5. Mint the check id and register it: one stable literal per check, the registry row in the same change as the check, never a follow-up or a batch pass — `registry.md`. Done when the row exists.
6. Log the decision — id, verdict, mode, and a bounded fingerprint of what was caught; `rollout.md` carries the row schema. Done when a fire writes a row.
7. Prove it live — `testing.md` § The proof: one real payload per case — fires · silent when the prerequisite is met · silent on look-alikes · still fires when an unrelated row sits in the prerequisite feed. Done when each case's row is the one expected.
8. Break it on purpose — `testing.md` § Break on purpose. Done when the row moved against a deliberate break and came back after a plain `cp` restore.
9. Roll out. Advisory → ship it. Blocking → ship behind an observe marker, measure, then flip deliberately and record the flip — `rollout.md`. Done when `done-when.md` holds.

A second script landing on an event already hooked is folded into the one engine, never added beside it — `registry.md` § One engine, not many hooks, and `robustness.md` § Ordering inside one engine for where the deny sits in the fold.

## The ten laws

| # | Law | Detail |
|---|---|---|
| 1 | Fire on the ACT, not the word: match the act on a quote-and-heredoc-stripped view; read the operands from the raw text. | `trigger-design.md` |
| 2 | An empty parse means "I don't know", never "it is safe": every path where parsing produced nothing defaults to no opinion. | `trigger-design.md` |
| 3 | Put the allowlist on the closed side: exclude the small closed set of readers, never allowlist the unbounded set of callers. | `trigger-design.md` |
| 4 | A crashed hook is an absent hook: coerce every payload field at the entry point, never a blanket `try/except`. | `robustness.md` |
| 5 | A hook that hangs is invisible: review every pattern for cost as well as correctness; assert the shape of the cost curve, never a wall-clock second count. | `robustness.md` |
| 6 | The message is a prompt, not an error code: fact, consequence, one runnable action, and an explicit no-op exit. | `messages.md` |
| 7 | Instrument the blocking tier first. | `rollout.md` |
| 8 | Record-only mode writes a different value than acting mode. | `rollout.md` |
| 9 | A proof never seen to move proves nothing. | `testing.md` § Break on purpose |
| 10 | The same defect at its third instance → stop fixing instances: name the shared helper once, prove it once, make every trigger call it. | `trigger-design.md` § Command position, not substring — the Third-Instance Rule |

## Where each proof lives

Nothing ships on the inner loop alone — `test-agents.md` § The governing principle: test the SESSION, not the hook.

| | Layer | What it proves | Where |
|---|---|---|---|
| Inner | A · Live drive | the program reads stdin, decides, exits correctly — every gate × {satisfied, unsatisfied} × look-alikes | `testing.md` § The proof |
| Inner | D · Break on purpose | the proof can move at all | `testing.md` § Break on purpose |
| Inner | E · Cost & concurrency | it does not hang; parallel actors do not destroy shared state | `robustness.md` |
| Outer | B · Live wiring | the host actually invokes it on the events you think, and a deny actually blocks | `test-agents.md` T-A4 |
| Outer | C · Genuine work | it guards real user journeys without obstructing them — and firing actually changes behaviour | `test-agents.md` T-A7 |

The full ordered sequence, with the fault-injection, false-positive census and hostile-payload layers between these, is `hardening-cycle.md` § The proofs, in order.
