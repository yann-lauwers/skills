# Evidence

## Preflight

- Every vehicle the `prove` criteria use gets the one act its first scenario needs, all before any scenario, every failure collected:
  - each service it reaches → the health check the repo's `AGENTS.md` names for it, run on the machine the app runs on — a machine the repo opens at the first proof run → after the `app` preflight's launch opens it; one that does not answer is a failure, naming the dev server the repo declares for it to this machine's dev-server registry, where it declares one — for an app launched in a virtual machine, to the repo's command for running on that machine.
  - each prerequisite the repo's `AGENTS.md` leaves to the person → checked, never worked around.
  - `datastore` → the store answers, with every migration the brief's commit carries applied.
  - `browser` or `service` → the served build carries the brief's commit: something the commit introduced answers.
  - `app` → one isolated instance of a build carrying the brief's commit, launched, read once through the reader its scenarios use, and finished, per /native-app-verification .
  - `ci` → the hosted run for the brief's commit exists.
- Who must act on a failure: `owner` — a grant, a locked screen, a credential, a decision, a fact the repo's `AGENTS.md` lacks, a service the repo declares no dev server for · `builder` — the build fails, carries another commit, or a service whose dev server the repo declares does not answer.

## Isolation

- The worktree stays at the brief's commit with no tracked file changed; the run's step 8 checks it.
- A driver or a test double on this host — a stub server, a loopback feed — runs as a Bash background task (`run_in_background: true`), so it stays in this session's process tree, on a port no listener holds.
- An isolated app instance → launched, recorded and stopped per /native-app-verification .
- A service or driver the app reaches listens on the machine the app runs on → a loopback port on this host never reaches a virtual machine.
- A driver the app reaches, for an app launched in a virtual machine → started there through the repo's command for running on that machine, after the first proof run opens it, its pid on that machine recorded in the run directory and stopped by that pid at the run's step 9.
- A test double is a driver; services are the repo's.
- Data the run creates — a record, a flag override, a file — lands only in stores its worktree or its instance owns; the final reply names each.
- A proof that must write where another checkout or the person works — a shared keyspace, a signed-in account, the person's own app → an owner prerequisite at preflight.

## Medium

| The claim is about… | `medium` |
| --- | --- |
| anything a person could watch happen — a transition, a hold, an arrival order | `series` |
| a state nothing moves through | `still` |
| a surface with nothing to see — a log line, a status, a row, an output | `raw` |

- A transition never grades on one still of its end state.
- A series window opens before the action and closes once the state it produced settles.
- A datastore proof is the query beside its output; a log line is never screenshotted.
- A screen recording only when the brief asks, beside its series.

## Scenarios

- One directory per scenario in the run directory, its name letters, digits, `.`, `_`, `-`; every capture it takes sits inside it.
- Each PASS or FAIL criterion's evidence cell names its scenario and captures; a datastore, log or file the run reads is a `raw` scenario of its own.

## Walk

- Once per run where a `prove` criterion's vehicle is `browser` or `app`: the slice's surface used the way its user would, past the criteria's paths — every control the slice adds or changes, pressed once.
- A `series` scenario named `walk`; what it finds goes to defects or observations.
- Watched for what no criterion names: a console error, a failed request, a crash, an error message, a control that does nothing; each one reproduced → a defect.

## Browser

- Dispatch each browser scenario, the walk included, to the agent the repo's browser-testing route names, that route's skill injected, one agent per scenario or coherent group; the run opens no browser.
- Hand each agent its scenario directory, the criteria it serves with their expected observations, its medium and the window; require every artifact's path back.

## Launched app

- The run drives it on an isolated instance, per /native-app-verification ; never through the browser agent.
- The repo names a launching party other than the run — a pass that proves the slice counts as the run → write the check and its command into the scenario directory; its criteria take NOT EXERCISED, blocked on that party.
- A time criterion → measured per /native-app-verification , recorded `raw`: the command, the count, the median and the worst.
- A sample reads state through the app's control surface or its accessibility tree; a pixel frame of a backgrounded instance is no sample.
