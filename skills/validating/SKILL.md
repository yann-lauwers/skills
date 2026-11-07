---
name: validating
description: >-
  Proves a built ticket or spec against its acceptance criteria by using it the way its user does.
  Use on "validate <ticket>", "prove it works", "does this meet the criteria", "re-validate", or a
  brief opening `Skills: validating`. Not for whether the diff matches its spec on paper —
  /code-review ; root-causing a failure — /diagnosing-bugs .
argument-hint: "[ticket-or-spec-id]"
---

# Validating

- Proof — an artifact this run captured at the slice's commit, using the slice on its vehicle the way its user does; a passing test, a read of the code or a returned claim is context, never proof.
- Slice — the ticket or spec under proof; a spec's criteria are its child tickets'.
- Report — `$AGENTS_REPORTS_DIR/validation/<slice>/`, `<slice>` the ticket id lower-cased, else a kebab-case slug; unset → ask the user where reports go, and stop.
- Run — one proof of the slice at one commit: `<report>/runs/<YYYY-MM-DD>_<n>/`, holding `run.md` and one directory per scenario.
- A slice changing nothing a person or a program uses → say so in one line and stop.

## Pick a branch

| The request is… | Read |
| --- | --- |
| a brief opening `Skills: validating` | `cookbook/run.md` |
| anything else — open a run, relay it, re-run after a fix | `cookbook/open.md` |
| what a run reads before planning, its criteria, plan values and vehicles | `references/plan.md` |
| preflight, isolation, medium, scenarios, the walk, browser and app scenarios | `references/evidence.md` |
| `run.md`'s shape, grading, the verdict | `references/run-md.md` |
