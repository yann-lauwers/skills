# Pull requests

## Listing external pull requests for triage

- `gh pr list --json` has no author-association field → list from the REST endpoint, which carries `author_association`:

```
gh api 'repos/<owner>/<name>/pulls?state=open&per_page=100' --paginate \
  --jq '.[] | select(.author_association | IN("OWNER","MEMBER","COLLABORATOR") | not) | {number,title,author:.user.login}'
```

- `OWNER`, `MEMBER` and `COLLABORATOR` are the repo's own people and stay out; every other association, `FIRST_TIMER` included, is listed.

Provenance: executed 2026-10-05 against `cli/cli`, gh 2.95.0 — 43 of 75 open pull requests listed (CONTRIBUTOR 18, NONE 25; MEMBER 32 kept out).

## The `pr` verbs

- Comment, label and close a pull request → `gh pr comment`, `gh pr edit --add-label` / `--remove-label`, `gh pr close`, never the issue verbs: an issue verb on a pull request's number addresses nothing.
- A bare `#42` → `gh pr view 42`, falling back to `gh issue view 42`.

## A merge run from inside a worktree errors after the merge has landed

- `gh pr merge --delete-branch` from a worktree merges through the API, then git refuses the local switch to the base: `fatal: '<base>' is already used by worktree at '<base checkout>'` → the local cleanup failed, never the merge.
- Never re-issue a merge against a pull request already `MERGED`.

1. Confirm → `gh pr view <n> --json state,mergeCommit`; `MERGED` with a commit oid means it landed.
2. Finish by hand from the base checkout → fetch with `--prune`, fast-forward, delete the remote branch, which the error leaves standing.

## What the history says about merges

- What a repo permits → `gh repo view --json squashMergeAllowed,mergeCommitAllowed,rebaseMergeAllowed` · what it does → its history; a `(#N)` suffix on trunk commit subjects means squash.
