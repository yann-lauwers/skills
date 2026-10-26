---
name: local-markdown
description: "Operates a repo's local-markdown issue tracker — tickets as files under `.scratch/`, no remote service: search, publish, fetch, relate, transition, close. Use on '.scratch', 'local tickets', 'markdown tracker', a skill saying 'publish to the issue tracker' or 'fetch the relevant ticket' in such a repo, an edit to a ticket file under `.scratch/<effort>/issues/` or its `PRD.md` / `map.md`, or a changed `Status:`, `Type:`, `Blocked by:` or `Duplicate of:` line. Not for a repo whose tracker role resolves elsewhere — that tracker's skill."
---

# Local markdown

## Project config

- Before any mutation → `~/.claude/skills/agents-config/scripts/agents-config get local-markdown <key> --root "$CLAUDE_PROJECT_DIR"`; the config is `~/.claude/skills/agents-config/integrations/local-markdown.md`, overridden by `$CLAUDE_PROJECT_DIR/docs/agents/integrations/local-markdown.md`.
- Keys → `label_creation` · `settled_categories` the `Status:` values that end a ticket · `settled_states` any further `Status:` value the repo treats as final · `automated_states`.
- Roles to `Status:` values → the "Label in our tracker" column of `$CLAUDE_PROJECT_DIR/docs/agents/triage-labels.md`.
- The declaration absent → /setup-matt-pocock-skills writes it · the project config absent → /managing-harness writes it; until then the floor's values govern, and the reply says they were assumed rather than read.
- `agents-config role tracker` names another tool → stop and use that tracker's skill.

## Routing

| If the task is | Read |
| --- | --- |
| whether a ticket covers a subject, in any state · recent arrivals | `references/search.md` |
| parent, child order, blocking, category | `references/issue-model.md § Issue relationships` |
| filer, open or closed, close, reopen, claim, body edit, comment, linked pull request | `references/issue-model.md § Issue state` |
| where a file goes · publish · fetch · apply a role | the section below that names it |

## The layout

- One effort per directory → `.scratch/<feature-slug>/`.
- The PRD → `.scratch/<feature-slug>/PRD.md` · a wayfinder map → `.scratch/<effort>/map.md`.
- One file per ticket → `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`; never a single combined tickets file.
- A ticket's role → a `Status:` line near the top of its file · its category → a `Type:` line beside it.

## Search

- Whether a ticket already covers a subject, in any state, recent arrivals included → `references/search.md`.

## Pull requests as a triage surface

- No pull-request intake.

## When a skill says "publish to the issue tracker"

- Create the file per § The layout under `.scratch/<feature-slug>/`, at the next free `NN`, creating the directory where it is missing.

## When a skill says "fetch the relevant ticket"

- Read the file at the path, or the one numbered as named.

## Triage labels

- Every role here is a state → the `Status:` line holds exactly one role, replaced on each transition.
- A marker a pass needs → a line in the file; nothing is ever created in a store.

## Issue relationships

- Parent, child order, blocking, category → `references/issue-model.md § Issue relationships`.

## Issue state

- Filer, open or closed, close, reopen, assignee, body edit, comment, linked pull request → `references/issue-model.md § Issue state`.
