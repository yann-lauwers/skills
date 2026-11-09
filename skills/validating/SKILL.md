---
name: validating
description: >-
  Proves a built change against its criteria by using it the way its user does, and ends on a verdict. Use on "validate <ticket>", "validate <ticket>", "prove it works", "does this meet the criteria", "re-validate", or a brief opening `Skills: validating`.
argument-hint: "[ticket-or-criteria]"
---

# Validating

## Rules

- Proof is a capture this run took of the change in use; a passing test, a read of the code or a returned claim never is.
- Nothing reaches the owner mid-run: a question lands in `run.md` as an ask.
- The run edits no product code, test or doc; its drivers and captures live in its run folder.

## The run

1. Create the run folder `validation/<slice>/runs/<YYYY-MM-DD>_<n>/` in the reports folder, `<slice>` the ticket id lower-cased, else a kebab-case slug of the request.
2. Gather the criteria, each verbatim:
   - a ticket → its description's and every comment's, a comment replacing only the criterion it names; a spec → its child tickets'. Provenance `ticket`.
   - each the owner gave, in this conversation or as an `owner` row of the slice's newest `run.md`, less any withdrawn. Provenance `owner`.
   - none from either → write them from the change's direction, provenance `self`.
3. Per criterion, what its user observes when it holds, carrying every value the ticket states; a value never comes from the code under test.
4. Plan each: `prove` · `skip`, naming the event it waits for — the merge, CI, a release · `ask`, quoting the two sources that disagree · `review`, where it states no behaviour to observe.
5. Prove each `prove` criterion on the highest surface reaching it — the app's window, the page, the API, the command, the stored data — launched the way the repo's instructions name, one folder per scenario. A page → a Playwright browser of the run's own.
6. Use the change once more past the criteria, pressing every control it adds or changes; a console error, a failed request, a crash or a dead control, reproduced → a defect.
7. Grade into `run.md` per `references/run-md.md`, stop every process the run started, and end on one message: the verdict line, then each FAIL, defect, ask and blocker; a ticket → the verdict line and the run folder's path go on it as a comment.

## Grading

- A driver, selector or environment fault → repair the proof and re-run the scenario.
- A scenario that cannot run → each criterion it serves takes NOT EXERCISED, naming the blocker.
- A stub standing in for a real service → the criterion it serves says so, and passes only on the real one.
- A transition → captured across it, never by one still of its end state.
- Verdict, the first that holds: BLOCKED — the run stopped, naming who must act · FAIL — a criterion failed or a defect is recorded · PASS — every `prove` and every `owner` criterion passed, no ask · INCOMPLETE — anything else, naming what holds it.
- A PASS resting only on `self` criteria → the verdict line says so.
