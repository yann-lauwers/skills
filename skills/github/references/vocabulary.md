# Resolving what this repo can carry

- Before drafting any field → resolve what carries its axis in this repo; nothing announces it.
- Labels, every axis expressed as one → `gh label list --limit 100 --json name,description`; each `description` states its label's scope, the definition a drafter chooses from.
- Category as a native field → `gh api graphql -f query='{repository(owner:"O",name:"R"){issueTypes(first:25){nodes{name isEnabled}}}}'`.
  - Nodes → the repo carries native Issue Types; category is `--type`, not a label.
  - `issueTypes: null` → a user-owned repo: a label is the only carrier.
- Account type → `gh api /repos/<o>/<r> --jq .owner.type`, `Organization` or `User`; `/orgs/<org>/issue-types` lists types, `/users/<login>/issue-types` answers 404.
- Priority as a project field → `gh project list --owner <o>`, then the project's single-select fields.
  - Reading needs the `read:project` scope; only writing a field needs the wider `project`.
  - Scope missing → `gh project list` refuses with `missing required scopes [read:project]` and names `gh auth refresh -s read:project`.
  - `INSUFFICIENT_SCOPES` → report the axis unmeasured, never absent.

Provenance: executed 2026-09-16, gh 2.95.0 — `cli/cli` answered `Organization` with three types, a user login answered `Not Found`, `gh project list` without the scope refused as quoted.
