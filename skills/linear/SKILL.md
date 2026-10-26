---
name: linear
description: "Reads, creates and updates Linear tickets through its GraphQL API. Use on 'linear', a ticket id like NEX-123, 'file it', 'create a ticket', 'move it to', 'comment on it', 'find the ticket', or a call to `api.linear.app/graphql`. Not for a ticket id in 'work on' or 'start' — /implement ."
---

# Linear

GraphQL at `https://api.linear.app/graphql`, no MCP.

## Project config

- Secret item, team and state keys → `~/.claude/skills/agents-config/scripts/agents-config get linear --root "$PWD"`; what one repo adds (its project, its marker label, its state notes) → the body of its `docs/agents/integrations/linear.md`.
- No project file → the team from `teams { nodes { id key } }`, the secret from the store's item names; neither resolves → ask for it by name.
- Never fabricate a team key, identifier prefix or token item.
- Cancel → the state `cancel_state` names · the sprint → the state `sprint_state` names.

## Call

```bash
keyless run -s LINEAR_KEY=<secret> -- curl -s https://api.linear.app/graphql \
  -H 'Content-Type: application/json' \
  --variable %LINEAR_KEY --expand-header 'Authorization: {{LINEAR_KEY}}' \
  --data @query.json
```

- The raw key, no `Bearer` prefix.
- A shape not below → the live schema: `__type(name: "<Input>") { inputFields { name type { name kind ofType { name } } } }`.
- `errors[]` or `success: false` → surface the message verbatim; `RATELIMITED` → wait until `X-RateLimit-Requests-Reset`, retry once.

Provenance: executed 2026-10-22 through `keyless run` against team `NEX` — bootstrap, issue by id, my issues, search, history, issueUpdate, commentCreate and issueRelationCreate all HTTP 200, no `errors`; `issueCreate` unexecuted in this shape.

## Workflow

1. Read first: the team's states, labels and members (Bootstrap); mutations take their UUIDs, never names.
2. Write every field in one call.
3. Bulk change → show the grouping before applying.
4. Re-read what you wrote.

## Rules

- A ticket or comment carries no PII, internal host, `.env` value, token, absolute machine path or scratch filename; a path in it is repo-relative, with no line number; copy useful content inline.
- A state moves only when the user names it or a pass's own steps do; "the PR merged" describes the work, never the field.

## Filing a ticket

- Only when the user asks.
- Before creating → search for a ticket already covering it; found → name it to the user and create nothing until the user answers.

## Queries

```graphql
# Bootstrap — once per flow; match a state by `type` before `name`
{ team(id: "<TEAM KEY>") { id
    labels(first: 250) { nodes { id name description retiredAt parent { name } } }
    states { nodes { id name type } }
    members(first: 100) { nodes { id name displayName app } } } viewer { id } }

# Issue by id — the identifier works
{ issue(id: "NEX-123") { id identifier title description state { name type } priority
    labels { nodes { id name } } assignee { displayName } parent { identifier }
    children { nodes { identifier state { name } } } comments { nodes { body user { displayName } } } } }

# My open issues
{ viewer { assignedIssues(first: 100, filter: { state: { type: { nin: ["completed", "canceled"] } } }) {
    pageInfo { hasNextPage endCursor } nodes { identifier title state { name } priority } } } }

# Search — every state
{ searchIssues(term: "<words>", includeComments: true, first: 10) { nodes { identifier title state { name } url } } }

# History — who moved or labelled it
{ issue(id: "NEX-123") { history(first: 50) { nodes { createdAt actor { displayName } fromState { name } toState { name } } } } }

# Children in order — sort client-side: the config's `child_order` `sort_order` → by `subIssueSortOrder` ascending · `created` → by `createdAt`
{ issue(id: "NEX-123") { children(first: 250) { nodes { identifier state { name type } assignee { id } subIssueSortOrder createdAt } } } }

# Blockers — incoming `blocks` relations
{ issue(id: "NEX-123") { inverseRelations { nodes { id type issue { identifier state { name type } } } } } }
```

- Unblocked → per `~/.claude/skills/agents-config/SKILL.md` § `role: tracker` (`settled_categories`, `settled_states`), narrowed by the repo body's state notes; a relation's `id` is what `issueRelationDelete` takes.

```graphql
mutation { issueCreate(input: { teamId: "<uuid>", title: "…", description: "…", labelIds: ["<uuid>"], projectId: "<uuid>" }) { issue { identifier url } } }
mutation { issueUpdate(id: "NEX-123", input: { stateId: "<uuid>", priority: 4, labelIds: ["<uuid>"] }) { success issue { state { name } } } }
mutation { commentCreate(input: { issueId: "<uuid>", body: "…" }) { success } }
mutation { issueRelationCreate(input: { issueId: "<uuid>", relatedIssueId: "<uuid>", type: blocks }) { success } }
```

- `labelIds` replaces the whole set → send the current set with the change.
- `commentCreate` and `issueRelationCreate` take UUIDs only → `issue(id: "NEX-123") { id }`.
- `issueRelationCreate` → `issueId` is the blocker or the duplicate; `type` ∈ `blocks · duplicate · related`.
- The `Duplicate` state is refused until the `duplicate` relation exists → write the relation first.
- Priority → `1` Urgent · `2` High · `3` Medium · `4` Low · `0` none.
- A sub-issue → `parentId`; Linear copies only the team, so every other field goes in the input.
- Aliases batch several writes in one request (`u1: issueUpdate(…) u2: …`).
- A label a pass needs and the set lacks → `issueLabelCreate(input: { teamId, name, description, parentId })`, as the config's `label_creation` allows.

## Scripts

- `scripts/watch-ticket.py --ticket <id> --secret <NAME> --then <act> [--comments-matching <regex> --expect <n>] [--seen V:K]` → waits until a ticket completes, or until `--expect` comments matching the regex land; arm it per /watching with `run_in_background`, `--secret` the config's `secret`, `--then` the act the woken session runs; `--once` prints the current line.
- `scripts/upload.py --secret <NAME> <file>...` → prints `<file>\t<assetUrl>` per file; embed an image as `![caption](<assetUrl>)`, any other file as `[name](<assetUrl>)`; an `assetUrl` answers only with the key.

| Watcher verdict | The woken session |
| --- | --- |
| `COMMENTED` | reads every matching comment the line lists past the previous line, then re-arms with the line's `rearm` |
| `COMMENTS_IN` | runs the line's `then` |
| `COMPLETED` | runs the line's `then` |
| `CANCELED` | reports the ticket closed without completing; what waited on it is the owner's call |
| `GONE` | reports the ticket deleted |
| `WATCHER_ERROR` | `auth` → report it and stop · `duplicate` → another watcher holds the ticket, leave it · `blind` → report it, re-arm once |
| any other | stops and prints the raw line |
