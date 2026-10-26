# Issue model

## Issue relationships

- Every fact below has a native field → write it there.
- Parent / sub-issue → write `gh issue edit <child> --parent <parent>`, undo `--remove-parent`; read `gh issue view <parent> --json subIssues --jq '.subIssues.nodes[].number'`.
- A parent holds up to 100 sub-issues and eight levels of nesting → one that would pass either takes an intermediate parent, never a body list.
- Child order → the order `subIssues` returns, reordered by the GraphQL `reprioritizeSubIssue` mutation; `gh issue list --json number,parent` returns children newest-first → never read a listing for order.
- Blocking edge → write `gh issue edit <blocked> --add-blocked-by <blocker>`, remove `--remove-blocked-by`; read `gh issue list --json number,blockedBy`.
- Unblocked when every issue in `blockedBy` is closed → read each blocker's own state; `blockedBy.totalCount` counts every blocker whatever its state and is not the gate.
- `blockedBy` returns at most 50 nodes whatever `--limit` says → a `totalCount` above the node count means the list is short and the gate is unanswered.
- Type / category → a label, per `SKILL.md § Triage labels`; an organization repo may carry it as a native Issue Type instead, per `references/vocabulary.md`.
- `gh issue list` fetches 30 issues, newest first, by default → pass `--limit` above the size of the set being read.

Provenance: child order executed 2026-09-16 on a six-child parent; the sub-issue limits are docs.github.com, *Adding sub-issues*.

## Issue state

- Filer → `gh issue view <n> --json author --jq '.author.login'`, the spelling a comment's own `author.login` carries.
- Open or closed → `gh issue view <n> --json state,stateReason,labels`; settled when `state` is in `settled_categories`, compared case-insensitively (`gh` prints `CLOSED`), or a label is in `settled_states`.
- Close → `gh issue close <n>` with `--reason completed` when done · `--reason "not planned"` when abandoned · as duplicate → `--reason duplicate --comment "Duplicate of #<canonical>"`; GitHub holds no duplicate edge, so the comment carries the relation.
- Reopen → `gh issue reopen <n>` · body edit → `gh issue edit <n> --body-file -`.
- Claim → `gh issue edit <n> --add-assignee @me` · release `--remove-assignee @me` · read `gh issue list --json assignees`.
- Linked branches → `gh issue develop <n> --list` · pull requests that close it → `gh issue list --json number,closedByPullRequestsReferences`.

Provenance: the filer read executed 2026-09-23 on `cli/cli#1`.
