# Hierarchy — what can hold a child ticket

## What each type may hold

- Epic → child epics and issues · Premium, Ultimate.
- Issue → tasks · every tier.
- Issue → objectives and key results · Ultimate.
- Issue → another issue · never.
- An issue belongs to at most one epic → on Free the parent is a plain issue and the edge lives in text.
- A ticket carrying a marker label (`SKILL.md` § Triage labels), on a tier with epics → stays an issue, hung under an existing epic with `--epic <id>` at create or `/set_parent` after, so its marker label keeps working.
- `glab issue` has no verb that creates an epic → use one that already exists.

## Why a task is not a child ticket

- A bare `glab issue list` sends no `issue_type` filter → tasks come back mixed in, with iids from the issues' sequence; a listing that must be issues only passes `--issue-type issue`.
  Provenance: 2026-09-16, unauthenticated against `gitlab-org/cli` — one page of 100 returned 97 `issue` and 3 `task`.
- A task's parent is a work-item edge no `glab issue` verb reads or writes; only the experimental `glab work-items` reaches it → a task filed as a child ticket lands in triage with a parent no pass can see.
- Tasks → checklist work inside one ticket · a child ticket → the body convention.

## Hanging an issue under an epic, where the tier has them

- At create → `glab issue create --epic <id> …`; `<id>` is the epic's global ID, never the `&iid` a body line cites.
- After the fact → `issue update` has no `--epic` → `glab issue note <n> --message "/set_parent &<epic-iid>"`; `/set_parent` takes an `#IID`, a reference or a URL.
- Reading an epic's children → group-scoped, outside `glab issue`: `glab api` against the group's work-items or epic-issues endpoints, confirmed against docs.gitlab.com first, since the epic REST API is deprecated for the work-items GraphQL surface.

## The sigils, since a parent line is written by hand

- `#<n>` issue · `!<n>` merge request · `&<n>` epic · `~<name>` label; cross-project, each takes a `<group>/<project>` prefix.
- A wrong sigil resolves to a different object of the same number and still renders as a live link → check it before writing a `Part of` line.
