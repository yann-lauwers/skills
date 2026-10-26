# Issue model

## Issue relationships

- Parent / sub-issue → no native edge; neither an epic nor a task substitutes (`references/hierarchy.md`) → the child body carries `Part of #<parent>` and the child joins a task list in the parent's body, the only queryable list of a parent's children.
- Child order → the task-list order in the parent's body; a plain listing falls back to issue number ascending.
- Blocking edge → `blocks` and `is_blocked_by` exist on Premium and Ultimate only; Free has `relates_to` alone.
  - Write → `glab issue note <blocked> --message "/blocked_by #<blocker>"`.
  - Read → `glab api "projects/:id/issues/<iid>/links"`; `:id` is filled from the clone, `<iid>` is written out.
  - Unblocked when every entry whose `link_type` is `is_blocked_by` has `state` `closed`.
  - Tier without it → a `Blocked by: #<n>, #<n>` line at the top of the body, read by the same test.
- Related, no direction → `/relate #<n>` as a note, or `--linked-issues <iid>` at create; `relates_to` on every tier.
- Type / category → a label, per `SKILL.md § Triage labels`.

## Issue state

- Filer → `glab issue view <n> -F json`, field `author.username`, the spelling a comment's author carries; unconfirmed on a live project → check it on the first read.
- Open or closed → `glab issue view <n> -F json`; settled when `state` is in `settled_categories` or a label is in `settled_states`.
- Close as done → `glab issue close <n>`.
- Close as abandoned → the same call, which has no close-reason flag → post a note naming which before closing; it is the only record.
- Close as duplicate → `/duplicate #<canonical>` as a note; it closes the issue and records the relation in one call.
- Reopen → `glab issue reopen <n>`.
- Claim → `glab issue update <n> --assignee @me`.
- Release → `glab issue update <n> --unassign`, which clears every assignee; `-a '-@me'` leaves the issue assigned.
- Read assignees → `glab issue list -O json`.
- Body edit → `glab issue update <n> --description-file -`.
- Comment → `glab issue note <n> --message "…"`; a comment is a note, and a note carries every quick action.
- Linked merge requests → `glab issue view` prints none, and its `Closed by:` line names a user → `glab api "projects/:id/issues/<iid>/related_merge_requests"` for every one mentioning the issue · `glab api "projects/:id/issues/<iid>/closed_by"` for those that close it.
