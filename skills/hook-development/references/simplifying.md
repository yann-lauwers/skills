# Simplifying an existing hook

Making a working hook smaller; every verdict it changes is named and probed.

## Prove it

- One probe, two runs, each under its own fresh `HOOK_STATE_ROOT=$(mktemp -d)`: the same events — at least one firing each check id — through a copy of the whole pre-change hook tree, libraries included, and through the new tree; rows compared on check, verdict, detail and mode; only a named change moves one.
- Each changed rule → a probe case the old script answers differently; the new script then moves under `testing.md` § Break on purpose.
- A pattern rewrite → also `trigger-design.md`'s differential equivalence.

## Where it lives

- The wiring never defers to a second copy.
- Retiring a wired copy on a live host → `shared-layer.md` § Change, add or retire a handler.

## What it decides

- Which files a rule reaches → derived from the repository — path containment, `git check-ignore` — never a list of extensions, folders or languages.
- A costly lookup that only relaxes a refusal → asked once a refusal is otherwise due.
- Machinery serving one artifact → goes once that artifact's owner removes the need, in a pass of its own.
- Text the session still holds → never owed again; compaction re-arms per `messages.md` § Re-fire, re-arm, escalate.

## How it reads

- A library shipped beside the hook → imported with no optional-import fallback; a lazy import stays lazy (`robustness.md` § Cost).
- A file past the repo's size limit → split by job into modules named for their behaviour; the entry file keeps the event dispatch.
- Text the agent reads → `messages.md` § Anatomy.

## What it adds

- Nothing around the simplification: no new spec, ledger or check; a test guarding only what was removed goes with it; an arm that wrote a check id is retired per `registry.md` § Retiring a check.
