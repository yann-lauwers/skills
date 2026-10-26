# Evaluations

Scenario — a session opening, what the skill has to do, and what counts as failing it.

## 1 — The request never says "ADR"

- Opening: "/folding-adrs there are too many decision records again, go back over them."
- Passes when the target is said back to the owner — the files go, the decisions stay — and the round's scope is the ADRs on `origin/<base>` when the tree is cut.
- Fails when the session sweeps only the citations, or starts deleting before the owner confirms.

## 2 — A single ADR folded outside a round

- Opening: "/folding-adrs 0071, the code does that now."
- Passes when the ADR is mapped first, its carrier is named by `path:line`, and `cookbook/delete.md` steps 1–6 and `cookbook/verify.md` § Checks and the suite and § Citations run after the deletion.
- Fails when the file is removed on the word "the code does that now" with no carrier named.

## 3 — An outside fact inside an ADR

- Opening: an ADR holds a third-party tool's timing measured on one version.
- Passes when the fact lands, with its version and date, in the doc that owns facts about that tool, and nowhere else.
- Fails when the fact is dropped with the ADR, or written into `GLOSSARY.md`.

## 4 — A design page cites a folded ADR

- Opening: after the ADRs are deleted, a design page still cites a folded ADR by number, and its directory carries the owner's pick record.
- Passes when `cookbook/verify.md` § Citations finds the hit, the citation becomes the decision in the page's own words, and the page and its pick record stay.
- Fails when the search skips design pages, the number is kept as history, or the page is deleted without the owner's word.

## 5 — A repo missing a command

- Opening: "/folding-adrs" in a repo whose `AGENTS.md` names no command regenerating the ADR index.
- Passes when that step is skipped and said, and every other step runs with the repo's own commands.
- Fails when a command from another repo is run, or the round stops.

## 6 — Not started by the model

- Opening: "write this decision up as an ADR", or a session deleting an ADR file without the user typing /folding-adrs .
- Passes when this skill does not load.
- Fails when it loads without the user typing it.
