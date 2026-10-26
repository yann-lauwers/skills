# Build what the maps found missing

Each step reads the maps, never memory.

1. Glossary, in the main loop: apply each glossary line the maps raised, as the repo's `docs/agents/domain.md` allows a term to be born (none → /domain-modeling ); every claim `GLOSSARY.md` makes past what the code does is cut to the code. Done when each glossary line the maps raised is applied.
2. Outside facts, in the main loop: each one goes, dated and versioned, into the doc that owns facts of its kind — the repo's `AGENTS.md` routes by surface where it maps one; no doc owns the kind → a new doc, named in the pull request. A "how the project decided" pointer becomes the name of the code that acts on it. Done when no outside fact lives only in an ADR.
3. Structure: a decision the code holds in several hand-rolled copies, or a layer leak, goes to a design pass before any builder touches it; a design option addressed to the owner waits for the owner's pick. Done when each structural finding has a recommended design.
4. Code, by builders in parallel, one per disjoint set of files → `references/briefs.md` § Build. Once every builder has returned, the main loop runs the repo's format command, then its lint command, before the first commit. Done when every NEEDS-WORK and DIVERGED item has landed or is reported unfinished.

## Writing build items

- An item names the exact end state — the new name, the test's title and assertion, the file — never "the way the repo does it".
- A constant a builder touches keeps the expression that says where it comes from.
- A new file → `git ls-files <path>` first, never replacing a file of that name.
- A test waits on the event itself, never by polling.
- A recorded fixture is re-recorded from the real program, never copied under a new version's name.
- Builders never commit.
- The main loop commits by explicit pathspec — `git commit -- <paths>` — and reads `git show --stat HEAD` after each commit.
