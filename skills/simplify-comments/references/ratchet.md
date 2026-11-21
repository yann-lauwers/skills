# The ratchet

The lint check that keeps the count from rising. Build it in the repo's own lint, as its other rules are built.

## Shape

- **Zero reached** → a plain ban: any comment but a tool line fails. No baseline file.
- **Comments left** → a baseline the check reads: each file still holding comments, with its count. More than its count fails; fewer fails too, naming the entry to lower, so the baseline only shrinks. A file absent from the baseline is held at zero.
- **Tool lines** → an allow-list in the check, each kind named. A disable directive names its rule and gives its reason.
- **Excuses kept as tool lines** → listed per file with the rule each lifts; the check fails on a listed entry its file no longer uses.

## Where each language goes

- A language whose linter exposes comments (ESLint's `sourceCode.getAllComments()`, a Ruff or SwiftLint rule) → a rule there.
- Every other tracked file type → one script that reads git's file list, with a reader per comment syntax that skips strings.
- Leave out recorded fixtures, generated files and lockfiles, each by name.

## Proof

- Run the check on the tree before the deletions: it lists the same comments as the inventory.
- One probe comment per language fails it; a tool line of each kind passes.
- A test of the rule earns its place for the allow-list and the shrink-only baseline, the two parts a later edit breaks silently.
