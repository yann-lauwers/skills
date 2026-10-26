# Verdicts

## Mapping, per decision

| Verdict | Means | Leads to |
| --- | --- | --- |
| CARRIED | at `path:line`, a type or function whose name says it, a test whose title names the failure, a `GLOSSARY.md` entry, or a doc line (dated and versioned for an outside fact) already says it | nothing |
| NEEDS-WORK | nothing says it | a build item: a rename, an extraction, a test titled by the failure, a moved piece of logic |
| DIVERGED | the code does something other than the ADR says | judge which side is right today; build or restate toward it; a structural divergence goes to a design pass |
| EXTERNAL | a fact about a third-party tool, platform, library or service, not about this repo | one dated, versioned line in the doc that owns facts of its kind |
| NOT-CODE | a process or tooling rule | the script's `--help`, the task runner's description of the task, CI or the doc that owns the process says it |
| OBSOLETE | no longer applies to today's code | nothing; name what replaced it |

- A rejected option counts as carried only where something would fail, or a reader would be told, if it came back.
- A glossary dependence — the decision only reads right with a term `GLOSSARY.md` lacks → a glossary item.

## Docs, per section and per doc

- Section → outside fact (keep, dated) · process (keep where no check holds it) · derivable from code (cut) · stale (cut) · cites an ADR (restate).
- Doc → keep · cut to what the code cannot show · delete · merge into its owner.

## `.out-of-scope/`, per entry

- still true · rewrite (one clause stale; the refusal stands) · delete.

## Fidelity audit, per decision

- CARRIED (with its carrier) · GAP (nothing carries it; a later change could undo it unnoticed) · WRONG (a carrier says something else, or contradicts the code) · OBSOLETE.

## Reviews

- Code and architecture → BLOCKING · IMPORTANT · NIT, each with evidence and a command.
- Canon → each defect with the act a reader would take wrongly; a finding naming no such act is optional.
