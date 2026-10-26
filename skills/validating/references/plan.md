# Planning

- The plan fixes what each criterion must show and how this run treats it, before any file the diff changes is opened.

## Context

- The owner criteria and anything else the brief carries.
- The ticket whole, through the tracker's skill: description, criteria and every comment.
- Its parent or spec, and the section the slice serves.
- Its siblings with their states — who owns the neighbouring behaviour, and who is still building it.
- `GLOSSARY.md` and the decision records on the paths `git diff --stat <base>..<commit>` names.
- Nothing else before the plan is recorded: no code, no diff hunk, no session transcript.

## Criteria

- The ticket's criteria, each verbatim, provenance `ticket`; a spec → each child ticket's, `source` its id.
- The criteria are the description's and every comment's together: a comment replaces only a criterion it names, graded on the replacement with `source` naming that comment; a criterion no later set names stays.
- Each owner criterion the brief carries → verbatim, provenance `owner`.
- A bug's reproduction command → one criterion more, provenance `diagnosis`, proved on every run.
- None stated → named here from the slice's direction, provenance `derived`.
- Prose beside the criteria — a rationale, a design note — decides how a criterion is read, never becomes one.
- A third party's behaviour the ticket asserts — a vendor's range, an API's answer — is proved only where a criterion states its effect.

## Expected observations

- Per criterion: what a person or a calling program observes when it holds, and on which surface.
- It carries every concrete value the ticket and its comments state for that behaviour — a count, a range, a list, a wording.
- A concrete value comes from the ticket, its comments, the spec, or data the slice leaves unchanged; never from the code under test.

## Plan

| `plan` | When |
| --- | --- |
| `prove` | this run observes it |
| `skip`, with its closer | the observation cannot exist at this commit: it needs the pull request, a push's hosted checks, a release, the merge, or an act only the owner may perform; the closer names that act |
| `ask`, with its question | two sources read it differently — two criteria that cannot both hold, a criterion against a comment, the parent's direction or a decision record, or a value the ticket states against data the slice leaves unchanged; the question quotes both |
| `review` | it states no behaviour — the code's shape, a test's existence, a document's text, how the work was done; /code-review reads it from the diff |

- A criterion its context reads one way carries no ask.
- A hard driver, a missing tool or a down service is never a skip → `prove`; a hard driver or a missing tool ends NOT EXERCISED with its blocker, a down service fails preflight, per `references/evidence.md` § Preflight.
- A skip whose closer happened, or an ask a ticket comment has since answered → `prove` on the next run; on a slice with no ticket, the criterion an owner criterion settles leaves the plan.
- The ticket's direction contradicts its criteria → blocked, on the owner, quoting both; nothing is planned.

## Vehicle

- Each `prove` or `skip` criterion takes the highest rung its observation can be reached on; a lower rung only where the higher one cannot reach it, its expected observation saying why.

| Rung | The criterion is observed… | `vehicle` |
| --- | --- | --- |
| 1 | in a page or webview a person uses | `browser` |
| 1 | in a native app's own window, menu, prompt or timing | `app` |
| 2 | in a running service's answers — an API, a webhook, a queue, a replay | `service` |
| 2 | in a real process — a CLI, a script, a job, the OS — on real data | `process` |
| 3 | in what an action on its own rung left — rows, files, counts | `datastore` |
| — | in a hosted CI or release run | `ci` |

- Logic with no surface of its own → proved where its effect shows, on the highest rung reaching it; no rung reaches it → `review`.
- A criterion about the repo's own checks or tests → `process`: they run once, as the repo runs them.
- A design card or web page of a native component is `browser`, and proves nothing about the app's window.
