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

A validation **proves** a slice by using it the way its user does, on its **vehicle**: the page, the app window, the API, the command, the stored data.

- Slice — the ticket or spec under proof; a spec's criteria are its child tickets'.
- Report — `$AGENTS_REPORTS_DIR/validation/<slice>-validation/`, `<slice>` the ticket id lower-cased, else the slice's kebab-case slug.
- `$AGENTS_REPORTS_DIR` unset in a repo → set it under `env` in the repo's `.claude/settings.local.json` to the vault's `projects/<repo>/reports`; setup work, no repo, or the owner declines → `~/.agents/reports/validation/<slice>-validation/`, the vault's own reports folder.
- Run — one proof of the slice at one commit: `runs/<YYYY-MM-DD>_<n>/` in the report, holding `run.md` and one directory per scenario.
- Proof run — the repo's own start-and-finish unit around a launched build, inside a Run; a repo with none has none.
- A run writes only inside its run directory: no product code, test, config or canon.
- Owed only where the slice changes something a person or another program uses; a slice read only as text → say so in one line and stop.

## Which half runs here

- A brief opening `Skills: validating` → § The run.
- A publish ask the owner typed → `references/publish.md`; no run opens.
- Otherwise → § Opening a run.

## Opening a run

1. Resolve the slice: the id named, else the ticket id in the branch name, else the slug and objective the request states; none → ask. Its base is `git merge-base HEAD <ref>`, `<ref>` the one the request names, else `origin/HEAD`. Whether it is owed comes from the ticket and `git diff --stat <base>..HEAD`.
2. The worktree is clean and `<base>..HEAD` holds the slice's commits; otherwise name what is uncommitted or missing, and stop. Done when HEAD's and the base's hashes are noted.
3. Dispatch the run with the Agent tool — `general-purpose`, `opus`, in the background — its prompt opening `Skills: validating`, then the slice, worktree, commit, base and report directory; every owner criterion still standing, in the owner's words: the newest verdicted run's `owner` rows plus this conversation's, less any the owner withdrew; and what this conversation holds that the ticket does not.
4. The worktree takes no edit, commit, setup or test run until the agent returns.
5. On return, relay the verdict line from the head of its `run.md`, then its final reply whole; no verdict line → report the run unfinished. Then:
   - each ask → the owner; the answer → a ticket comment naming the criterion it settles, or with no ticket, an owner criterion in the next brief.
   - stop every process the reply names as running, and abandon every proof run still open under the run directory through the repo's command; a machine the repo handed out ends by the repo's rule.
6. BLOCKED on a dev server the repo declares → start it once through this machine's dev-server registry; in a virtual machine, through the repo's command for that machine, noting its pid there. Its `AGENTS.md` health check answers within 5 minutes → dispatch again from step 3; otherwise stop it and relay. Every later relay names each dev server this step left running.
7. A fix lands as a new commit → again from step 2; the new run proves every criterion at that commit.

## The run

- Nothing reaches the owner mid-run: a question, a grant or a decision becomes an ask, a skip or a blocker in `run.md`.
- Blocked at any step → write `run.md`'s head with verdict `BLOCKED`, the blocker and who must act, its table holding at least every owner criterion the brief carries; then steps 8–9, step 8 adding to the verdict line.

1. Create `runs/<key>/` in the report, `<n>` one past today's highest.
2. Read the task per `references/plan.md` § Context, and the newest run's `run.md` carrying a verdict line. Done when the slice's direction fits one sentence.
3. `git rev-parse HEAD` is the brief's commit and `git diff --stat <base>..<commit>` carries the change the ticket describes; otherwise → blocked, on the builder.
4. Plan per `references/plan.md` into `run.md`. Done when every criterion has its plan, and each `prove` one its vehicle and expected observation.
5. Preflight per `references/evidence.md` § Preflight; any failure → blocked.
6. Prove each `prove` criterion per `references/evidence.md`, then the walk where a vehicle is `browser` or `app`; finish every proof run opened here.
7. Grade per § Grading into `run.md`. Done when every `prove` criterion has a verdict and its evidence paths.
8. HEAD is still the brief's commit and the worktree is clean; otherwise → blocked, naming what moved.
9. Stop every process and abandon every proof run this run opened, then end on the final reply: the verdict line, then each FAIL, defect, ask, skip, `review` criterion and blocker, and anything left outside the run directory.

## run.md

- Head: slice, commit, base, date, the verdict line.
- One table: `| C | criterion, verbatim | provenance | source | plan | vehicle | expected | verdict | evidence |`.
- Below it, each in its own section where it has any: FAIL dossiers (steps, expected, observed), defects, asks, blockers with who must act, observations.

## Grading

- A verdict rests on an artifact this run produced at the brief's commit; never on a returned claim, the code read, or a test passing.
- A probe the run writes counts once it reads differently at the base or before the action.
- A driver, selector, environment or build-under-test fault → repair the proof and re-run the scenario; never a FAIL.
- A service that stops answering mid-run → blocked.
- A scenario that cannot run → each criterion it serves takes NOT EXERCISED with its concrete blocker.
- A FAIL carries its dossier and the run goes on.
- The code following a recorded decision a criterion contradicts → that criterion becomes an ask quoting both.
- A reproducible defect on the slice's own surface outside every criterion → a defect, naming its steps and scenario.
- Behaviour a sibling ticket owns → an observation naming that ticket.

## Verdict

- BLOCKED → a blocker stopped the run; the line names who must act.
- PASS → at least one `prove` criterion, each passed in this run, and every owner criterion the brief carries in the table; no ask, no defect.
- FAIL → a criterion failed, or a defect is recorded.
- INCOMPLETE → anything else, a run with no `prove` criterion included; the line names each criterion holding it, or that nothing was proved.
- Two hold → the first in this list.
- `skip` and `review` never move the verdict.
- The verdict line opens with its verdict.

| IF | THEN read |
| --- | --- |
| reading the task, planning | `references/plan.md` |
| preflight, isolation, medium, scenarios, the walk | `references/evidence.md` |
| the owner asks to publish | `references/publish.md` |
