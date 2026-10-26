# The hardening cycle

The ordered procedure for a whole hook layer: find what is wrong with it, fix it without breaking it, prove the fixes hold, and know when it is done.

## The loop

| # | Step | Concretely |
|---|---|---|
| 1 | Analyse everything | a fleet of parallel audit lanes against the live layer |
| 2 | Produce a ranked task list | all findings triaged into one persisted, tiered table |
| 3 | Fix, in order, each proven live | waves — one defect class per wave, one commit per wave |
| 4 | Verify the fixes with a new fleet | lanes briefed to distrust the fixer |
| 5 | Loop until no mistakes | back to step 1 with the closed set excluded |

- **Never skip steps 4 and 5: a discovery fleet is not a verification fleet, and finding more defects never proves the last fix worked.**

## Phase 0 — Before touching anything

1. Establish sole-writer status — `testing.md` § Before breaking a copy. Done when `ps` shows no other writer on the tree and no lane this session dispatched is still running.
2. Take the baseline yourself; never trust a figure you were handed. Done when the decision log's per-check counts are recorded, with every tool the hooks shell out to confirmed present on this host.
3. Confirm every path the brief names exists. Done when `ls` has listed each one.
4. Open a durable ledger file before any dispatch, the constraints in it as a numbered list. Done when the file is on disk.

## Phase 1 — Dispatch the audit fleet

Done when every lane's report file exists on disk.

- Scope the lanes disjointly on one axis, held for the iteration:

| Axis | Use when |
|---|---|
| by question — false positives, wake path, logging, concurrency, messages | first iteration; the defects' location is unknown |
| by issue-cluster | mining a body of evidence rather than a codebase |
| by suspicion — one lane per recent wave, plus subsystems | after a round of fixes |
| by adapter/component | the layer has clear structural seams |
| by class — one lane per known defect class, hunting the next instance | once classes are named |
| by shipped change — one lane per wave, told to distrust it | verification (Phase 6) |

- Every brief names what the other lanes own and carries the closed set as an explicit "do not re-report these" list.
- One shared brief file, plus a thin per-lane dispatch naming only the lane id, its scope and its output path; never the full brief inline per dispatch.
- Pin the model per lane; an unset model inherits the session's.
- Two or three lanes run blind, alongside the anchored lanes, never instead of them — the brief is `test-agents.md` T-A1.

### The shared brief — required sections

1. The mandate, in one sentence: "This iteration's mandate is RESILIENCE, not only discovery" scopes differently from "find defects".
2. The standard, stated identically every iteration: *a hook must fire in every case where it should, and never in a case where it should not — for any user, on any machine, any uid, any session, any payload.*
3. The role: *"you produce EVIDENCE with citations, not opinions."*
4. The system: file inventory, state paths, how to drive a hook live (`testing.md` § The proof), and where the wiring authority is — *"the wiring file is the authority — `settings.json` at every level. Transcribe it; never assume."*
5. Method: read the small sources IN FULL; grep the large ones; slice, never dump.
6. Hard rules, copied verbatim:
   1. READ-ONLY on the real tree. Never write the real state root — always a throwaway `HOOK_STATE_ROOT`.
   2. **Do not implement fixes.** Propose them precisely; someone else applies them.
   3. **Drive the real code.** A claim from reading source is a HYPOTHESIS. Report what you OBSERVED.
   4. **Tag every measurement `[LIVE]` — a row the host wrote under a real session id — or `[FIXTURE]` — a direct drive.**
   5. **A quote you cannot find in the primary source is DROPPED, not hedged.**
   6. Use `2>&1`, never `2>/dev/null` — you will need the diagnostics.
   7. **If you claim a check catches something, show the row move.** Drive the payload, break the predicate in a scratch copy of the tree, drive the copy, read the row — `testing.md` § Break on purpose — **and confirm the unbroken copy gives the live row first.**
   8. **Assert on the surface the mechanism actually writes.** Find the observable before judging the behaviour.
7. The known defect classes, each with its instance count — "look for the next instance".
8. The exact output schema below, and an explicit output file path.
9. The closing line: "The FILE is the deliverable."

### The output schema

```
## <lane>-<n> — <one-line title>
**Observed** — what happened, with the reproduction.
**Evidence** — the measurement.  Confidence: VERIFIED | REPORTED.  Tag: [LIVE] | [FIXTURE].
**Location** — file:line.
**Failure direction** — fails open / fails closed / noise / cost.
**Proposed fix** — precise, not implemented.
**Live proof** — the payload, and the row it moves to if this regresses.
**Generalizable lesson** — ONE rule, zero project vocabulary.
```

- An unverifiable finding → `Confidence: REPORTED`, kept, never dropped.
- The report closes on `## Reusable techniques`, quoting the code, and on `## What I could not establish` — `testing.md` § The report lists its recurring entries.

### While the lanes run

- Read the primary sources yourself: the API reference in full, the house conventions to match, the method docs; never act on a procedural summary of a document.
- Poll for output with a bounded loop, never by idling.

## Phase 2 — Consume the reports

Done when one consolidated register, built from every report file, is on disk.

- Read every report from its file — `test-agents.md` § Reading what comes back.
- Re-derive every load-bearing measurement first-hand before acting on it; the register states: *every report was read first-hand and its load-bearing measurements re-derived; no lane's summary of its own work was taken on trust.*
- Check a lane's evidence, its proposed fix and its reproduction each on its own: a conclusion that survives does not certify its evidence, a fix can introduce a collision, and a fixture artifact that confirms a prior hypothesis is still an artifact.
- A negative check prints its empty result: `echo "(none above = confirmed absent)"`.
- Verify any number that would be a finding, and separate stderr before counting anything.

## Phase 3 — Triage into one ranked, persisted table

Done when the tiered table is on disk with its cross-cutting pattern section.

- Once per iteration, after every report is consumed: one file, four tiers, one line per finding — `<lane> <id>  <one-sentence defect>`.

```
CLOSED by <waves/commits>: <lane ids>

## TIER 1 — an ENFORCING deny is bypassed, or a catastrophic act reaches `allow`
## TIER 2 — crash, data loss, or a guard failing CLOSED
## TIER 3 — silent when it should fire / no evidence surface
## TIER 4 — cost (real, none catastrophic)
```

- Tier 1 means the guard did not guard, an emitted `allow` included — `trigger-design.md` § The empty parse is "I don't know".
- A false positive on the satisfying side of a gate ranks above a noisy one.
- Persist the table to disk and work the waves against it in order.
- Close the file on a cross-cutting pattern section: what the findings have in common.

## Phase 4 — The wave

One wave = one defect class, worked to closure, with its own live proof, its own break on purpose and its own commit; never one wave per lane or per finding.

1. Reproduce the defect on the current tree, before any edit. Done when it reproduces, or is recorded as already fixed or not reproducing.
2. Fix it. Done when the fix holds and every wrong attempt is recorded by name.
3. Sweep the class: name and count every sibling, and fix a class spanning several sites once, in a shared helper — `trigger-design.md`'s Third-Instance Rule. Done when the siblings are named and counted; never "n/a" without a reason.
4. Prove the fix live and break it on purpose — `testing.md` § The proof and § Break on purpose. Done when the row moved under the break and returned after the restore.
5. Re-drive the proofs of every check the change touched, before and after. Done when both sets of rows are stated.
6. Write the changelog entry to the contract below.
7. Commit — one per wave.

### The changelog entry contract

```
### <id> — <one-line change>
**Issue** — what was observed, with a reproduction.
**Evidence** — the measurement, first-hand.
**Change** — what was altered, exactly.
**Why this fix** — why this and not the alternatives.
**Class sweep** — the siblings checked, and what was found. NEVER "n/a" without a reason.
**Proven by** — the payload driven, and the rows before, during and after the break.
```

- The changelog is held to the code's evidence rules: a wrong entry is corrected in place — *"That is a factual error in this log, corrected here."*
- Before changing a check, read its previous entries; a check fixed repeatedly → the defect is one level up.

## Phase 5 — Defer

- A defect a wave cannot close properly → a row in an OPEN table: the defect, its measured cost, the proposed fix and why it is deferred; "later" is no reason.
- Every deferral carries an objective re-arm condition — `messages.md` § A deferral without a re-arm condition is a permanent off switch.
- A stated limitation is a task until the thing it says is needed has been tried; "needs fault injection" → `testing.md` § Paths no payload reaches.

## Phase 6 — Verification

Done when every shipped wave has a verification report from a lane that did not write the fix.

- A separate fleet, its mandate never discovery, one lane per shipped wave, briefed to distrust the fixer:
  - reproduce the original defect on the current tree, and fail to reproduce it;
  - enumerate the defect class, not the reported instance;
  - break the fixed predicate in a copy and watch the row move;
  - measure the opposite direction for regressions.
- The author of a change is never the sole author of its proof payloads; a change to a blocking guard is not done until someone who did not write it has tried to get past it.

## Phase 7 — Generalise across the estate

- Each closed wave's learnings → a class, swept across the whole estate.
- A recurring class gets a structural fix — a check, a shared helper — never prose alone.
- Record a verified non-defect as such, with its verification.
- A contradiction → flagged with its settling probe named, never guessed.

## The proofs, in order

Run the layers in this order; each one's failures are cheaper to diagnose than the next one's. Technique detail in `testing.md`; dispatch briefs in `test-agents.md`. Every layer is driven once and reported; none is kept as a file.

### A · Live drive

- Every gate × {fires · look-alike · legitimate neighbour · empty parse · malformed payload}, one real payload each — `testing.md` § The proof.
- Read three verdict classes: deny, silent, and *no opinion*.
- Keep payload dimensions distinct: a shared HOME, project dir and cwd make every target in scope by construction.
- Every widening change re-drives the false-positive cases.

### D · Break on purpose

- `testing.md` § Break on purpose.
- The unbroken drive comes first and gives the expected row, or every later move is uninterpretable.
- A break that misses its anchor, or breaks the parse, proves nothing, never a verdict.
- A row that does not move → probe what the break changed before calling it inert.

### D2 · Fault injection

- Any path no input can reach — "if this check crashes, do X" → `testing.md` § Paths no payload reaches.

### A2 · False-positive census

- `test-agents.md` T-A5: trigger × every carrier — quoted, heredoc, echoed, commit message, grep pattern, README prose — in both fresh-session and shared-session modes, the expected verdict labelled before running.

### A3 · Hostile payloads

- `robustness.md` § The hostile payloads; every shape exits 0.

### B · Live wiring

1. Build a disposable project under `mktemp -d`, wire a real `settings.json`, validate it as JSON immediately.
2. Redirect only the hook's state root, never `HOME` — credentials live there.
3. Point the guard at a canary: a harmless throwaway path, so the deny is safe to drive.
4. Drive it with a real headless session.
5. Run the negative control: unwire the hook, recreate the canary, issue the identical command, confirm the canary dies.
6. Restore settings from a named backup and re-validate.

- Step 5 is never skipped.
- Prove host invocation: the decision row carries the host session's id, distinct from the id the direct probe produced.

### C · Genuine work

- Verify each lane's claims against the decision-log rows its session wrote, never from its report.
- `test-agents.md` T-A7; a prior read masks a read-prerequisite gate for the whole session lineage — `testing.md` § The masking trap.
- Never say a skill exists, that hooks are under test, or which behaviours are checked.
- Sandbox each lane with an explicit boundary sentence.
- Dispatch at least one on-path case and at least one misroute — a request for exactly what the doctrine forbids.
- Instruct the agent to do the forbidden thing, by name.
- Write the scoring rubric to a file before the lanes return: numbered rows, each with "why it matters", an empty Result column, an explicit pass bar, a named "interesting failure", and a closing block mapping every possible outcome to the fix it implies.

### E · No-orphan and syntax

- Both directions in one command: files on disk that nothing references, and references that do not resolve; plus cross-references between reference files, and a syntax parse of every shipped file.

### F · Non-regression

- Re-drive the proofs of every check the change touched, before and after, with the rows stated, only once sole-writer status is established — `testing.md` § Before breaking a copy.

## Delta sweeps against a live source

1. Measure growth before dispatching — records, changelog entries, decision rows; nothing moved → no dispatch.
2. Brief the delta lane with an explicit record offset, the exclusion list of classes already held ("do NOT re-report these"), and a demand for REVERSALS flagged loudly.
3. Require a per-fact CONFIRMED / REFUTED / NOT-SEEN verdict on everything already encoded as fact; NOT-SEEN is recorded as unrefreshed, never as re-verified.
4. Require a closing `## Nothing-new check` listing which known classes recurred.
5. A reversal arrives → grep your own artifacts for the refuted claim first, then read the rest of the report.
6. Verify activity against the tree and the git log, never the changelog alone: a project's record stopping is no evidence its work stopped.
7. Distrust your own sentences of the form *"which no code change removes"*.

## When something looks unknowable

- No way to observe a mechanism directly → observe a consequence only that mechanism produces.
- The probe's constraint is the experiment: *"Do not use any tool. Do not read, search, grep or open any file. If you reach for a tool you have failed the question."*
- Require the answer to distinguish "in my context" from "inferred from general knowledge", and say why: *"that distinction is the entire point of this question."*
- Probe two different agent types, and state the residual inference not measured.
- Every probe gets an output file path.

## Shipping

1. Drive the live proofs from the artifact being shipped — the copy, the extracted zip — never from the source.
2. `diff -rq` the shipped copy against the source before every re-ship, printing `(silence = identical)`.
3. State the gaps in the reply.
4. State snapshot vs live when handing over a copy of something still changing.
5. Leave every gate in a recorded deliberate end state — `rollout.md` § Deliberate end-state.

## Known limits of this method

- Verification gets crowded out by discovery, and nothing records which loop steps have run.
- The fixer verifies their own fixes.
- Per-lane dispatches still leak hand-copied lessons past the shared brief.
- Model and dispatch settings drift when left unset.
- The changelog entry contract is not enforced: a wave can ship with its narrative in the commit message alone.
- Iteration cost is measured nowhere.
- Lane disjointness is asserted, never computed.
- The rubric's discriminating power is untested against a failing lane.
