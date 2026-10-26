---
name: validating
description: >-
  Proves a built ticket or spec against its acceptance criteria by using it the way its user does —
  the launched app, the served page, the API, the command, the stored data. Use when the request
  says "validate NEX-123", "validate this", "prove it works", "test it in the app", "does this meet
  the criteria", "re-validate" or "publish the validation", or a dispatched brief opens with
  `Skills: validating`. Not for whether the diff matches its spec on paper — /code-review ;
  root-causing what a proof found — /diagnosing-bugs ; fixing it — /tdd .
argument-hint: "[ticket-or-spec-id]"
---

# Validating

- Slice — the ticket or spec under proof; a spec's criteria are its child tickets'.
- Report — `$AGENTS_REPORTS_DIR/validation/<slice>-validation/`, `<slice>` the ticket id lower-cased, else the slice's kebab-case slug; setup work or no repo → `~/.agents/reports/validation/<slice>-validation/`; a repo with the variable unset → wire it per /obsidian § Wire a repo's reports, and a declined wiring takes the user level, saying the repo is unwired; the user level unwired too → the report directory sits in the session's scratchpad, and the verdict stays in the reply.
- Run — one proof of the slice at one commit: `runs/<key>/` in the report, `<key>` `<YYYY-MM-DD>_<n>`, holding `report.md` and one directory per scenario.
- Proof run — the repo's own start-and-finish unit around a launched build, inside a Run; a repo with none has none.
- Every criterion is proved by using the feature on its vehicle; a passing test is never its proof.
- A run edits no product code, test, config or canon; its drivers and captures live in its run directory.
- Owed only where the slice changes something a person or another program uses — a screen, a command, an API, stored data, a launched app; a slice whose every change is read only as text → say so in one line and stop.

## Which half runs here

- A brief opening `Skills: validating` → § The run.
- A publish ask → `references/publish.md`; no run opens.
- Otherwise → § Opening a run.

## Opening a run

1. Resolve the slice — the id named, else the ticket id in the branch name, else the slug and objective the request states; none → ask — its base — `git merge-base HEAD <ref>`, `<ref>` the one the request names, else `origin/HEAD`, else the repo's default branch — and whether it is owed, from the ticket and `git diff --stat <base>..HEAD`.
2. `git status --porcelain` in the worktree prints nothing, and `git log <base>..HEAD` holds the slice's commits; otherwise → name what is uncommitted or missing, and stop. Done when HEAD's hash and the base's hash are noted.
3. Dispatch the run in the background with the Agent tool — `general-purpose`, `opus`, `run_in_background: true` — a prompt opening `Skills: validating`, then the slice, the worktree, the commit and its base, the report directory, every owner criterion still standing in the owner's words — the `owner` rows of the newest run whose `report.md` carries a verdict line, plus this conversation's, less any the owner withdrew — and what this conversation holds that the ticket does not.
4. The worktree takes no edit, commit, setup or test run until the agent returns.
5. The agent returns → read the head of its run's `report.md` and relay that verdict line, then the final reply whole; no `report.md`, or no verdict line in its head → report the run unfinished.
   - Each ask → the owner; the answer → a comment on the ticket naming the criterion it settles; no ticket → the answer joins the next brief's owner criteria.
   - A process the reply names still running → stop it by its PID.
   - Replying or not → abandon each proof run still open whose folder sits under the run's `runs/<key>/`, through the repo's command for abandoning one; a machine the repo hands out for the validation then ends by the repo's own rule.
6. BLOCKED on a dev server the repo declares that does not answer → start it once through this machine's dev-server registry from the worktree — for an app launched in a virtual machine, there through the repo's command for running on that machine, never the registry, its pid on that machine noted and stopped by that pid; its health check, from the repo's `AGENTS.md`, answers within 5 minutes → dispatch again from step 3; it does not, or the run blocks on it again → stop it and relay; every relay from here on names each dev server this step started that is still running.
7. A fix lands as a new commit → again from step 2; the new run proves every criterion at that commit.

## The run

- Nothing reaches the owner mid-run: a question, a grant or a decision becomes an ask, a skip or a blocker in `report.md`.
- Blocked at any step → write `report.md`'s head with the verdict line `BLOCKED`, naming the blocker and who must act, and its table holding at least every owner criterion the brief carries; then steps 8–9, step 8 adding to the verdict line.

1. Create `runs/<key>/` in the report, `<n>` one past today's highest.
2. Read the task per `references/plan.md` § Context, and the newest `report.md` in the report carrying a verdict line, where one exists. Done when the slice's direction fits one sentence.
3. `git rev-parse HEAD` in the worktree is the brief's commit, and `git diff --stat <base>..<commit>` carries the change the ticket describes; otherwise → blocked, on the builder.
4. Plan per `references/plan.md` into `report.md`, before opening any file the diff changes. Done when every criterion has its plan, and each `prove` one its vehicle and expected observation.
5. Preflight per `references/evidence.md` § Preflight; any failure → blocked.
6. Prove each `prove` criterion per `references/evidence.md`, then the walk where a `prove` criterion's vehicle is `browser` or `app`; finish every proof run opened here before step 7.
7. Grade per § Grading into `report.md`. Done when every `prove` criterion has a verdict and its evidence paths.
8. HEAD is still the brief's commit and `git status --porcelain` prints nothing; otherwise → blocked, naming what moved.
9. Stop every process the run started and abandon every proof run still open, then end on the final reply: the verdict line, then each FAIL, defect, ask, skip, `review` criterion and blocker, and anything the run left outside its run directory.

## report.md

- Head: slice, commit, base, date, the verdict line.
- One table: `| C | criterion, verbatim | provenance | source | plan | vehicle | expected | verdict | evidence |`.
- Below it, each in its own section where it has any: FAIL dossiers (steps, expected, observed), defects, asks, blockers with who must act, observations.

## Grading

- A verdict rests on an artifact this run produced at the brief's commit; never on a returned claim, the code read, or a test passing.
- A probe the run writes counts once it reads differently at the base or before the action.
- A driver, selector, environment or build-under-test fault → repair the proof and re-run the scenario; never a FAIL.
- A service that stops answering mid-run → blocked, per `references/evidence.md` § Preflight.
- A scenario that cannot run → each criterion it serves takes NOT EXERCISED with its concrete blocker.
- A FAIL never pauses the run; it carries its dossier.
- The code following a recorded decision a criterion contradicts → that criterion becomes an ask quoting both.
- A reproducible defect on the slice's own surface outside every criterion → a defect, naming its steps and the scenario holding it.
- Behaviour a sibling ticket owns → an observation naming that ticket.

## Verdict

- BLOCKED → a blocker stopped the run; the line names who must act.
- PASS → at least one `prove` criterion, each passed in this run, and every owner criterion the brief carries in the table; no ask, no defect.
- FAIL → a criterion failed, or a defect is recorded.
- INCOMPLETE → anything else, a run with no `prove` criterion included; the line names each criterion holding it, or that nothing was proved.
- Two hold → the first in this list.
- `skip` and `review` never move the verdict.
- The verdict line opens with its verdict.
- Publish only on a message the owner typed asking for it, per `references/publish.md`.

| IF | THEN read |
| --- | --- |
| reading the task, planning | `references/plan.md` |
| preflight, isolation, medium, scenarios, the walk | `references/evidence.md` |
| the owner asks to publish | `references/publish.md` |
