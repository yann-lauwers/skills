---
name: gitlab
description: "Operates GitLab issues and merge requests through the `glab` CLI — search, publish, fetch, relate, transition, label, comment, close. Use on 'glab', 'merge request', 'MR', 'epic', 'sub-issue', 'blocked by', a `#number` or `!number`, or a skill saying 'publish to the issue tracker' or 'fetch the relevant ticket' in a GitLab-tracked repo; before any `glab issue|mr|label|api` call. Not for opening, readying or merging an MR — /pull-request ; not for a repo whose tracker role resolves elsewhere — that tracker's skill."
---

# GitLab

- `glab` holds its own auth, infers the project from `git remote -v` → no credential or target inside a clone · outside one → `-R <group>/<repo>`.
- GitLab has two states, opened and closed; closed settles.
- A form with no provenance line has not run on this machine → read its failure as version drift and confirm it against `glab <verb> --help`; its first run records the line that ran.
- `glab issue list` returns 30 per page, newest first → `--per-page` above the set's size on every listing.
- Drafting a note a person reads → load /voice first; unavailable → say so and match the voice of the thread's recent messages.

## Project config

- Before creating, closing, labelling, relating an issue → `~/.claude/skills/agents-config/scripts/agents-config get gitlab <key> --root "$CLAUDE_PROJECT_DIR"`; the config is `~/.claude/skills/agents-config/integrations/gitlab.md`, overridden by `$CLAUDE_PROJECT_DIR/docs/agents/integrations/gitlab.md`.
- Keys → `label_creation` marker labels created unasked · `settled_categories` states that end a ticket · `settled_states` final labels on an open issue · `automated_states` set only by an automation.
- Roles to labels → the "Label in our tracker" column of `$CLAUDE_PROJECT_DIR/docs/agents/triage-labels.md`; every cell here is a label.
- The declaration absent → /setup-matt-pocock-skills writes it · the project config absent → /managing-harness writes it; until then the floor governs.
- The project body → the repo's field policy.
- `agents-config role tracker` names another tool → stop and use that tracker's skill.

## Routing

| If the task is | Read |
| --- | --- |
| read, list, comment on, label or close a merge request, resolve a thread, resolve a bare `!N` | `references/merge-requests.md` |
| hang a ticket under a parent, read a parent's children, what an epic or a task can carry | `references/hierarchy.md` |
| search, publish, fetch, label, relate or transition an issue | the section below that names it |

## Search

- Whether a ticket already covers a subject, in any state, recent arrivals included → `references/search.md`.

## Pull requests as a triage surface

- `**MRs as a request surface: yes.**` in `$CLAUDE_PROJECT_DIR/docs/agents/issue-tracker.md` → external merge requests are feature requests, listed per `references/merge-requests.md § Triage and mutation`.

## When a skill says "publish to the issue tracker"

- `glab issue create --title "…" --description-file -`, body piped in; `--description` mangles a multi-line body.
- A non-interactive create needs `--title` plus `--description`, `--description-file`, `--template` or `--attach` → anything less refuses; `--yes` never satisfies it.
- `--label` takes every axis at once → resolve each per § Triage labels first.
- Under an epic, where the tier has them → `--epic <id>` per `references/hierarchy.md`.

## When a skill says "fetch the relevant ticket"

- `glab issue view <n> --comments`

## Triage labels

- Apply or remove → `glab issue update <n> --label <a>,<b> --unlabel <c>`; `--label` adds to the set, never replaces it.
- An unknown name creates a label → resolve every target against `glab label list -F json` first.
- A triage-role target absent → `glab label create --name <name> --description "<scope>"`, then apply.
- A marker label a pass needs (`wayfinder:*`) → create unasked only where `label_creation` is `free`.
- A value the live set lacks on a drafted axis → report it, never invent it.

## Issue relationships

- Parent, child order, blocking, related, category → `references/issue-model.md § Issue relationships`.

## Issue state

- Filer, open or closed, close, reopen, assignee, body, comment, linked merge request → `references/issue-model.md § Issue state`.

## Done when

- A mutation is confirmed by a fresh `glab issue view <n> -F json` of the changed field, never the exit code.
- The reply names which config values governed — from the project file, or assumed from the floor.
