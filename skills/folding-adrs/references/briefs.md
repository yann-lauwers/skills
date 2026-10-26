# Briefs

- Each brief → one file all agents of its kind read first; each agent's prompt names that file, its batch — a builder's items — and its report path.
- `<batch>`, `<report path>` and a builder's `<numbered…>` items come from the agent's prompt · `<t>` and `<file>` stay for the runner to fill · every other `<…>` slot is filled in the file before the first dispatch.
- A slot left empty → no dispatch.
- Keep every line outside a slot verbatim.

## Mapping

```
Read-only. Worktree <path>. Write your report to <report path>, appending each ADR's section the moment you finish it.

For each ADR in <batch>: read it whole; follow every supersede and narrow link, inside or outside the batch. For each decision in it — the decision, each rejected option worth guarding, each consequence, each measured outside fact — give:
- the decision as it stands today, in ≤15 words;
- its carrier at HEAD by path:line, found with git grep and opened;
- a verdict: CARRIED · NEEDS-WORK · DIVERGED · EXTERNAL · NOT-CODE · OBSOLETE;
- for NEEDS-WORK and DIVERGED, the smallest change that makes the code say it: the exact new name, test title and assertion, or file;
- any GLOSSARY.md term the decision needs and the glossary lacks.
Verdicts and the bar for CARRIED: ~/.claude/skills/folding-adrs/references/verdicts.md — read it first.
Before reporting that nothing carries a decision, run one search known to hit, to prove the route works.
The read-first gate may refuse a file until every ADR is read; run the exact command it prints, once, never piped or redirected.
```

## Build

```
Worktree <path>. Do not commit. Apply every item below, then run the commands to green and report each item done, files touched, and every command with its exit code.
The repo's rules and its lint command (<lint command>) hold every line. Prove each new test by breaking the code it guards, watching it fail, and restoring.
Items: <numbered; each names the exact end state and the file, and points at its map section>.
Commands: <test command for one target, uncached, with <t> where the target goes> per target touched; nothing repo-wide, since other builders edit the same tree.
```

## Fidelity audit

```
Read-only. Worktree <path>, HEAD final. The ADRs are readable at `git show <folding commit>^:<ADR dir>/<file>`. The earlier maps at <map paths> are claims to verify, not truth.
For each decision in ADRs <batch> — following supersede chains — name where HEAD carries it by path:line, and give CARRIED · GAP · WRONG · OBSOLETE, by the bar in ~/.claude/skills/folding-adrs/references/verdicts.md (read it first); an outside measurement is carried only with its version and date. For GAP and WRONG, give the smallest fix and its file. Run a known-hit search before reporting any GAP.
Report per ADR, then a list of GAP and WRONG lines only, most consequential first. Append as you go to <report path>.
```

## Sibling branches

```
<round's pull request> merged into <base> as <merge commit>: ADRs <numbers> are deleted and their decisions live in the code, GLOSSARY.md and the docs. Before rebasing: fetch <base>, cut a backup ref, list your own diff.
- A modify/delete conflict on a folded ADR → keep it deleted; carry your change into the ADR's carrier (code, test, GLOSSARY.md, or the doc that owns that kind of fact).
- A new ADR your branch adds → numbered per its `docs/agents/domain.md`; silent → /domain-modeling ; then <the ADR index command>; never hand-merge the ADR index.
- Renamed or removed symbols — move every use: <old → new, read from the round's diff>.
- A file both sides add entries to → keep both sides' entries, validate it as the repo does, build.
- GLOSSARY.md and docs → keep <base>'s wording, add your change on top; never restore a sentence that cites an ADR.
- After rebasing: <lint command>, the tests of every target you touch, and the identity of every commit.
- A folded decision you cannot place → read it at `git show <merge commit>^:<ADR dir>/<file>` and ask, never guess.
```
