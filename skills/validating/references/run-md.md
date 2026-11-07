# run.md

Read by the opener relaying it and by the next run, which takes its `owner` rows.

- Head: slice, commit, base, date, the verdict line.
- One table: `| C | criterion, verbatim | provenance | source | plan | vehicle | expected | verdict | evidence |`.
- Below it, a section for each that has entries: FAIL dossiers (steps, expected, observed), defects, asks, blockers with who must act, observations.

## Grading

- A probe the run writes counts once it reads differently at the base, or before the action.
- A driver, selector, environment or build fault → repair the proof and re-run the scenario; the criterion keeps its chance at PASS.
- A service that stops answering mid-run → blocked.
- A scenario that cannot run → each criterion it serves takes NOT EXERCISED, naming its blocker.
- A FAIL carries its dossier, and the run goes on.
- Code following a recorded decision a criterion contradicts → that criterion becomes an ask quoting both.
- A reproducible defect on the slice's own surface outside every criterion → a defect, with its steps and scenario.
- Behaviour a sibling ticket owns → an observation naming that ticket.

## Verdict

The first that holds:

1. BLOCKED — a blocker stopped the run; the line names who must act.
2. FAIL — a criterion failed, or a defect is recorded.
3. PASS — at least one `prove` criterion, each passed in this run, every owner criterion in the table, no ask, no defect.
4. INCOMPLETE — anything else; the line names each criterion holding it, or that nothing was proved.

- The verdict line opens with its verdict; `skip` and `review` never move it.
