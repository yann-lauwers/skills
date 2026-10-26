---
name: github
description: "Operates GitHub issues and pull requests through the `gh` CLI — searches, publishes, fetches, relates, transitions and labels an issue; reads, comments on, labels or closes a pull request. Use on 'gh issue', 'close that issue', 'sub-issue', 'blocked by', 'label it', an issue named by `#number`, or a skill saying 'publish to the issue tracker' or 'fetch the relevant ticket' in a GitHub-tracked repo. Also fires before any `gh issue|pr|label|api` call or `curl` to `api.github.com`. Not for opening, retargeting or merging a pull request; not for a repo whose tracker role resolves elsewhere — that tracker's skill."
---

# GitHub

- `gh` holds its own auth and infers the repo from `git remote -v` → no credential or target inside a clone · outside one → `--repo <owner>/<name>` · an API call outside `gh` → § Calls.
- GitHub has two states, open and closed, and three close reasons — `COMPLETED`, `NOT_PLANNED`, `DUPLICATE`; every close reason settles.
- Load /voice before drafting a comment a person reads; unavailable → say so, and match the voice of the thread's recent messages.

## Calls

- `gh api` covers the case → use it.
- Any other scripted call → `~/.claude/skills/agents-config/scripts/agents-config get --role vcs secret --root "$CLAUDE_PROJECT_DIR"`; `null` → no item is wired: report it missing and stop · an item → through the injector, the token expanded by the child's own shell, `<SECRET>` being the name the secrets store's skill mints from it:

```sh
keyless run -s T=<SECRET> -- sh -c 'curl -s -H "Authorization: Bearer $T" -H "Accept: application/vnd.github+json" https://api.github.com/<path>'
```

Provenance: run 2026-09-13 against `/user` with `NEXUS_GITHUB_PAT`, answered `200`.

## Project config

- Before creating, closing, labelling or relating an issue → `~/.claude/skills/agents-config/scripts/agents-config get github <key> --root "$CLAUDE_PROJECT_DIR"`; the config is `~/.claude/skills/agents-config/integrations/github.md`, overridden by `$CLAUDE_PROJECT_DIR/docs/agents/integrations/github.md`.
- Keys → `label_creation` marker labels created unasked · `settled_categories` states that end a ticket · `settled_states` final labels on an open issue · `automated_states` set only by an automation.
- The project body → the repo's field policy.
- Roles to labels → the "Label in our tracker" column of `$CLAUDE_PROJECT_DIR/docs/agents/triage-labels.md`; every cell here is a label.
- The declaration absent → /setup-matt-pocock-skills writes it · the project config absent → /managing-harness writes it; until then the floor governs.
- An issue act, and `agents-config role tracker` names another tool → stop and use that tracker's skill · names nothing → no tracker is chosen; the floor holds no target to inherit.

## Routing

| If the task is | Read |
| --- | --- |
| draft a label, category or priority whose carrier here is unknown | `references/vocabulary.md` |
| read, list, comment on, label or close a pull request · a bare `#N` · a merge from a worktree errored | `references/pull-requests.md` |
| search, publish, fetch, label, relate or transition an issue | the section below that names it |

## Search

- Whether a ticket covers a subject, in any state, recent arrivals included → `references/search.md`.

## Pull requests as a triage surface

- `**PRs as a request surface: yes.**` in `$CLAUDE_PROJECT_DIR/docs/agents/issue-tracker.md` → external pull requests are feature requests, listed per `references/pull-requests.md`.

## When a skill says "publish to the issue tracker"

- `gh issue create`; `--label` takes every axis at once and creates none → a target absent from the repo fails the create: resolve each against `gh label list` first.

## When a skill says "fetch the relevant ticket"

- `gh issue view <n> --comments`

## Triage labels

- Apply or remove → one `gh issue edit <n> --add-label "<a>,<b>" --remove-label "<c>"`, moving the issue from its current set to the set handed over.
- A triage-role target absent → `gh label create <name> --description "<scope>"`, then apply.
- A marker label a pass needs (`wayfinder:*`) → create unasked only where `label_creation` is `free`.
- A value the live set lacks on a drafted axis → report it, never invent it, whatever `label_creation` says.

## Issue relationships

- Parent, child order, blocking, category → `references/issue-model.md § Issue relationships`.

## Issue state

- Filer, open or closed, close, reopen, assignee, body, linked pull request → `references/issue-model.md § Issue state`.

## Done when

- A mutation is confirmed by a fresh `gh issue view <n> --json …` of the changed field, never by the exit code.
- The reply names which config values governed — read from the project file, or assumed from the floor.
