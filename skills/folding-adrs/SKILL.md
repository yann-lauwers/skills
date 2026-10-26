---
name: folding-adrs
description: Folds a repo's ADRs into the code — each decision ends up carried by the code, a test, `GLOSSARY.md` or a doc, built where nothing carries it yet, and the ADR file is deleted — as one round over every ADR or for one named ADR. Started only by the user typing /folding-adrs , with the ADR numbers in scope or none for all of them. Not for writing or numbering a new ADR — /domain-modeling .
disable-model-invocation: true
---

# Folding ADRs into the code

- ADRs → the root `docs/adr/`, plus the `docs/adr/` beside each `GLOSSARY.md` the repo's `GLOSSARY-MAP.md` lists; an ADR is named by its path wherever two contexts share a number.
- `<base>` → the repo's `base_branch`, per /git .
- Setup, format, lint, the full suite and one target's tests → the repo's `AGENTS.md`, else its task runner or CI workflow; none found → stop and ask.
- The command regenerating the ADR index → the same sources; absent → that step is skipped and said.
- ADR tooling — every command and check that reads the ADRs: the index regeneration, a duplicate-number check, their self-tests.
- An ADR is folded once the code, `GLOSSARY.md` and the docs carry its decision; then its file leaves.
- Design page — a page under a design or prototype folder arguing options · pick record — any file in that folder recording which option the owner chose.
- A doc keeps only what the code cannot show.
- Target — the ADR files go; every decision stays in the code, `GLOSSARY.md` or a doc.
- Scope — the ADRs on `origin/<base>` when the tree is cut, unless the owner narrows it.
- An ADR landing mid-round → the next round.
- The owner's calls — the round's scope · every `.out-of-scope/` verdict · any design option a design doc addresses to the owner · a page leaving a directory that carries an owner's pick record · the merge.
- A decision is judged against today's code, never against the ADR's own claims.
- One round, one pull request.
- One ADR outside a round → map it (`cookbook/map.md` above § Fanning out; no fan-out, no side maps), build its carrier, `cookbook/delete.md` steps 1–6, `cookbook/verify.md` § Checks and the suite and § Citations, and the canon review; no fidelity audit, no sibling brief.

## The round

1. Scope and orient → `cookbook/scope.md`.
2. Map every ADR → `cookbook/map.md`.
3. Build what the maps found missing → `cookbook/build.md`.
4. Delete the ADRs → `cookbook/delete.md`.
5. Verify, review, audit → `cookbook/verify.md`.
6. Land and brief sibling branches → `cookbook/land.md`.

## Routing

| IF | THEN read |
| --- | --- |
| starting a round, cutting its tree, deciding which ADRs are in it | `cookbook/scope.md` |
| mapping ADRs against the code, or auditing docs and `.out-of-scope/` | `cookbook/map.md` |
| turning map verdicts into code, glossary and doc changes | `cookbook/build.md` |
| deleting the ADRs and checking the ADR tooling | `cookbook/delete.md` |
| checks, the suite, the citation search, rebasing, reviews, the fidelity audit | `cookbook/verify.md` |
| the pull request, the merge, briefing other branches | `cookbook/land.md` |
| what a verdict means and what it leads to | `references/verdicts.md` |
| something went wrong — an agent died, a refusal, the base moved, a review keeps finding defects | `references/failure-modes.md` |
| writing a mapping, build, audit or sibling-branch brief | `references/briefs.md` |
| checking this skill still routes after an edit to it | `references/evaluations.md` |
