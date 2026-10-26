# Verify, review, audit

## Checks and the suite

- Run the repo's lint command and the ADR tooling (`SKILL.md`).
- Run the full suite with every cache off.
- A target red under load → re-run it alone, uncached, with one job.
- A red that survives → run it on `origin/<base>` before blaming the round.
- A red in a test the round touched → find its root cause.
- Before any push, run every CI leg the repo documents running locally.
- Every commit carries the identity of the person running the round: `git log --format='%an <%ae>' origin/<base>..HEAD`.
- A wrong identity → re-author with `git rebase --exec 'git commit --amend --no-edit --reset-author' "$(git merge-base HEAD origin/<base>)"`.
- Done when lint, the ADR tooling, the full suite and the local CI legs are green, or each red is shown failing on `origin/<base>` too.

## Citations

- Search the whole tree, design pages and the ADRs included: `git grep -n -I -i -E 'adrs?[ -]?[0-9]{4}|records? [0-9]{4}|docs/adr/[0-9]{4}|\([0-9]{4}-[a-z0-9-]+\.md\)|\(0[0-9]{3}(, ?0[0-9]{3})*\)'`.
- A hit outside the ADRs that points a reader at one ADR → state the decision there in words, or name its carrier — the code, a `GLOSSARY.md` entry, or the doc that owns facts of its kind.
- A hit in an ADR left on the tree that names a folded ADR → `cookbook/delete.md` step 3.
- A hit in a design page → keep the page and restate the decision in its own words.
- A directory carrying an owner's pick record → its pages leave only on the owner's call (`SKILL.md`).
- A page in a directory with no pick record, that only argued an ADR, may go, named in the pull request with why nothing is lost.
- A hit that names no live ADR stays — any check's self-test fixture, recorded wire data, an illustrative path, a note that points no reader at a decision — and so do the ADR index's own lines, which its regeneration holds.
- Done when every hit is an ADR left on the tree citing another left on it, or one that stays.

## The base moved

- Cut a backup ref before rebasing.
- An ADR the round deleted and the base edited → stays deleted; what the base added to it goes into its carrier.
- An ADR the base added → restate its citations of folded ADRs in its own words.
- Uncommitted work is re-applied by hand onto the new base, never copied back from a parked file.
- A file both sides add entries to → keep both sides' entries, then validate it as the repo does and build.

## Reviews

1. Code review over the whole diff: bugs and concurrency. Done when its findings are fixed.
2. Architecture review over the whole diff: layer leaks, one name per concept in the glossary's words, no hand-rolled copy of a shared mechanism, test titles, anything a reader now has to guess with the ADR gone. Done when its findings are fixed.
3. Canon review over every canon and doc change, given the ADR → carrier ledger (which ADR fact went to which file): claims left standing, contradictions, a fact in two homes, meaning lost in a move. Its fixes are reviewed again, over the files they touched; a third pass still finding real defects means the plan is wrong — take it to the owner. Done when a pass finds nothing a reader would act on wrongly.

## Fidelity audit

- Fresh read-only agents check every folded decision against the final branch → `references/briefs.md` § Fidelity audit. Done when no GAP or WRONG line is left unfixed.
