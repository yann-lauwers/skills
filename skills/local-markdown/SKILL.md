---
name: local-markdown
description: "Operates a repo's local-markdown issue tracker under `.scratch/`. Started only by /local-markdown ."
disable-model-invocation: true
---

# Local markdown

## Project instructions

- Settled → a `Status:` of `resolved`, `out-of-scope`, `duplicate` or `wontfix`, or any further value the project's instructions treat as final.
- Roles to `Status:` values → the "Label in our tracker" column of `$CLAUDE_PROJECT_DIR/docs/agents/triage-labels.md`.
- The declaration absent → /setup-matt-pocock-skills writes it.
- The project's instructions name another issue tracker → stop and use that tracker's skill.

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
