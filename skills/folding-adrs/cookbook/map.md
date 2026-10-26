# Map every ADR

- Map each decision inside an ADR, never the ADR as one unit: its decision, each rejected option worth guarding, each consequence, each measured outside fact.
- Follow every supersede and narrow link both ways, across batches: an ADR is judged as it stands after the last ADR touching it.
- A carrier is named by `path:line`, in a form `references/verdicts.md` § Mapping accepts.

## Fanning out

- Read-only mapping agents, one shared brief file → `references/briefs.md` § Mapping.
- At most 8 ADRs per agent, 3–5 for a retry; four agents in flight.
- A dead agent → relaunch only the ADRs its partial report lacks.
- A remainder of a few ADRs → map them in the main loop.

## Side maps, in parallel

- Docs: each section of each doc outside the ADRs, and each doc → a verdict from `references/verdicts.md` § Docs.
- `.out-of-scope/`, where the repo has one: each entry → a verdict from `references/verdicts.md` § `.out-of-scope/`, with the line in the product that decides it.
- A fact an `.out-of-scope/` entry holds that the code needs → moves to its own home before the entry goes.
- ADR tooling (`SKILL.md`): in a temporary copy of the repo with the round's ADRs deleted, run each; note every exit code.

Done when every ADR in scope has a section with a verdict per decision, and the side maps are written.
