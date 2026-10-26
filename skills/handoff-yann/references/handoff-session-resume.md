# Handoff — Session Resume Format

Reader — a fresh Claude Code or Claude.ai session, handed the whole file as its prompt.

## The body

- The file is the prompt: select all, copy, paste gives a working brief with zero edits.
- First line is the brief's first sentence: no slash-command prefix, title, HTML comment or fence around the prompt.
- Every fact the next session needs lives inside the body; no prose before or after it.
- A fence inside the body only for a literal code or shell snippet the receiving session uses.
- A file reference carries a `path:line` anchor where one line matters; a bare path where the whole file is the unit.
- Length: 30–120 lines; detail past that goes in a referenced file beside the handoff.

## Sections

- Required, in this order: `## Goal` · `## Files` · `## Approach` · `## Out of scope` · `## Success criteria` · `## Agent dispatch suggestion`.
- `## Agent dispatch suggestion` names the skills the next session invokes first.
- Add every further section the pickup needs to land cold — `## Current state`, `## Open questions`, `## Assumptions`, `## Risks` among them — where it reads naturally; never cut needed context to fit the required set.

## Design status

- Every brief states in its opening lines, as a sentence and never a section, whether the design is settled; a brief that says nothing reads as settled.
- Settled → say so, and the brief proceeds as written.
- Not settled → the brief's first act sorts each open question: the codebase can answer it → investigate · only the user knows → an interview, the brief naming the interview skill, never a design pass.
- Design not settled → `## Agent dispatch suggestion` names the skill that settles it — the interview or the investigation — and no engineer, since a named engineer reads as a decision already taken.
- Restate every open question the work being handed off carries, each marked investigate or ask.
