---
name: git
description: >-
  This setup's git policy. Use on "commit", "push", "force push", "rebase", "cherry-pick", "branch",
  a named base branch, or an entry going into `.gitignore`, `.git/info/exclude` or the global
  excludes file. Not for a pull request's body — /pr .
---

# Git

## Rewrites

- Rebase → a backup ref `git update-ref refs/archive/<branch>-<date> HEAD`, left in place, `git fetch origin <base>`, then `git rebase origin/<base>`; done when `git range-diff origin/<base> <backup-ref> HEAD` pairs every commit `=` or differs only by the resolutions taken.
- Parent squash-merged or rewritten → `git rebase --onto origin/<base> <parent's old tip>`, never a plain rebase.
- Retarget onto a base cut from the branch's current base → retarget alone · onto any other → rebase first; then `git diff <new-base>...HEAD`.
- **Rewriting published history — an amend, a rebase, a lease push — only on an instruction naming that branch**; a /watch-pr `CONFLICT` line whose `integration_base` is `false` is that instruction; a local-only branch rewrites freely.
- A branch other pull requests merge into → takes its base by merge, never rebase.
- Cherry-pick → always `-x`.

## Routing

| Task | Read |
| --- | --- |
| Make a commit | `references/commit.md` |
| Push, a refused push, a force push | `references/push.md` |
| Ignore a path — which ignore file takes the entry | `references/ignore-files.md` |
| A commit the pre-commit size check refused — its message is the procedure | `scripts/pre-commit-token-limit` |
