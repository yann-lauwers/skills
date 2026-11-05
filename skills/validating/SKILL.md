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

A validation **proves** a built slice against its criteria by using it on its **vehicle** — the page, the app, the API, the command, the stored data — the way its user does. A proof is an artifact this run captured at the slice's commit; a passing test, a read of the code or a returned claim is context, never proof.

- **Slice** — the ticket or spec under proof; a spec's criteria are its child tickets'.
- **Report** — `$AGENTS_REPORTS_DIR/validation/<slice>/`, `<slice>` the ticket id lower-cased, else a kebab-case slug. Unset → ask the user where reports go, and stop.
- **Run** — one proof of the slice at one commit: `<report>/runs/<YYYY-MM-DD>_<n>/`, holding `run.md` and one directory per scenario.

A validation is owed only where the slice changes something a person or a program uses. A slice read only as text → say so in one line and stop.

## Pick a branch

- A brief opening `Skills: validating` → § The run.
- Otherwise → § Opening a run.

## Opening a run

1. **Resolve the slice**: the id named, else the ticket id in the branch name, else the slug the request states; none → ask. Its base is `git merge-base HEAD <ref>`, `<ref>` the one named, else `origin/HEAD`. Whether it is owed comes from the ticket and `git diff --stat <base>..HEAD`.
   **Done when** the slice, HEAD's hash and the base's hash are noted.
2. **Check the tree**: `git status --porcelain` prints nothing, and `git log <base>..HEAD` holds the slice's commits. Otherwise name what is uncommitted or missing, and stop.
3. **Dispatch the run** as a background subagent. Its brief opens `Skills: validating`, then carries the slice, the worktree, the commit, the base, the report directory, every standing owner criterion in the owner's words, and what this conversation knows that the ticket does not.
   Standing owner criteria: the `owner` rows of the newest `run.md` with a verdict line, plus this conversation's, less any the owner withdrew.
4. **Hold the tree**: no edit, commit, setup or test run in the worktree until the agent returns.
5. **Relay** the verdict line at the head of the run's `run.md`, then the agent's final reply whole. No verdict line → report the run unfinished.
   - Each ask → the owner. The answer → a ticket comment naming the criterion it settles; no ticket → it joins the next brief's owner criteria.
   - Stop every process the reply names as still running.
6. **Blocked on a dev server** the repo's `AGENTS.md` declares → start it once by the command it names. Its health check answers within 5 minutes → dispatch again from step 3; otherwise stop it and relay. Every later relay names each server this step left running.
7. **A fix lands** as a new commit → again from step 2; the new run proves every criterion at that commit.

## The run

Nothing reaches the owner mid-run: a question, a grant or a decision lands in `run.md` as an ask, a skip or a blocker. The run edits no product code, test, config or doc; its drivers and captures live in its run directory.

**Blocked** at any step → write the head of `run.md` with verdict `BLOCKED`, the blocker and who must act, and a table holding at least every owner criterion; then steps 8–9.

1. Create the run directory, `<n>` one past today's highest.
2. Read the task per `references/plan.md` § Context, and the newest `run.md` with a verdict line. **Done when** the slice's direction fits one sentence.
3. `git rev-parse HEAD` is the brief's commit, and `git diff --stat <base>..<commit>` carries the change the ticket describes; otherwise blocked, on the builder.
4. Plan into `run.md` per `references/plan.md`. **Done when** every criterion has a plan, and each `prove` one a vehicle and an expected observation.
5. Preflight per `references/evidence.md` § Preflight; any failure → blocked.
6. Prove each `prove` criterion per `references/evidence.md`, then the walk where a vehicle is `browser` or `app`.
7. Grade into `run.md` per § Grading. **Done when** every `prove` criterion has a verdict and its evidence paths.
8. HEAD is still the brief's commit and `git status --porcelain` prints nothing; otherwise blocked, naming what moved.
9. Stop every process the run started, then end on the final reply: the verdict line, then each FAIL, defect, ask, skip, `review` criterion and blocker, and anything left outside the run directory.

## run.md

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

1. **BLOCKED** — a blocker stopped the run; the line names who must act.
2. **FAIL** — a criterion failed, or a defect is recorded.
3. **PASS** — at least one `prove` criterion, each passed in this run, every owner criterion in the table, no ask, no defect.
4. **INCOMPLETE** — anything else; the line names each criterion holding it, or that nothing was proved.

The verdict line opens with its verdict. `skip` and `review` never move it.
