# Failure modes

Each line: a failure a round has met → where its fix lives.

- The request read as "remove the citations" → `cookbook/scope.md` step 1.
- Mapping agents die or stall → `cookbook/map.md` § Fanning out.
- A builder runs out of context → probe which items landed with a script over the tree; give a fresh builder only the rest.
- A builder dies mid-run → resume it, naming the item reached and what landed since.
- The read-first gate refuses a file, or refuses again after `<base>` brought new ADRs → `references/briefs.md` § Mapping, the gate line.
- A tool or hook refuses a step → do what its message names; a way out that is the owner's goes to the owner with the exact command.
- A file must come out of a commit → `git restore --staged --source=HEAD~1 <path> && git commit --amend --no-edit` keeps the working copy; a file the commit added → `git rm --cached <path>` and amend.
- The base moved mid-round → `cookbook/verify.md` § The base moved.
- A commit carries the wrong identity → `cookbook/verify.md` § Checks and the suite.
- A builder followed a vague item into a break, or brought back a fixture, a polling test or a replaced file → `cookbook/build.md` § Writing build items.
- A fact moved into a doc now lives in two places → the doc that owns the mechanics keeps it; the other surface points there.
- A restatement lost an exception or widened its object → restate with the ADR's own noun; diff each line against the ADR's exceptions.
- An always-loaded rule points at a deleted ADR in prose → `cookbook/delete.md` step 5.
- The canon review keeps finding defects its own fixes made → `cookbook/verify.md` § Reviews, step 3.
- A commit swept in files nobody meant to stage → `cookbook/build.md` § Writing build items, the pathspec line.
- ADR tooling fails with few or no ADRs → `cookbook/map.md` § Side maps, then `cookbook/delete.md` step 4.
- The full suite is red → `cookbook/verify.md` § Checks and the suite.
- An ADR's own claims are wrong → `SKILL.md`: judge against today's code.
- Open branches collide with the round's deletions and renames → `cookbook/land.md` step 2.
