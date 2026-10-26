---
name: git
description: >-
  This setup's git policy — a repo's base and production branch, commit subject and trailers,
  branch naming, push and force-push rules, and which ignore file takes an entry. Use on "commit",
  "push", "rebase", "cherry-pick", "branch", a named base branch, `base_branch: auto`,
  `branch_pattern: auto`, `docs/agents/integrations/git.md`, or an entry going into `.gitignore`,
  `.git/info/exclude` or the global excludes file. Not for pull requests — /pull-request ; not for
  issue and PR reads through the forge's CLI — /github .
---

# Git

## Project config

- Before any git act → `~/.claude/skills/agents-config/scripts/agents-config get git <key> --root "$CLAUDE_PROJECT_DIR"`; the floor is `~/.claude/skills/agents-config/integrations/git.md`, overridden by `$CLAUDE_PROJECT_DIR/docs/agents/integrations/git.md`.
- Keys read here → `base_branch` · `production_branch` · `commit_trailers` · `branch_pattern`; the pull-request keys are /pull-request 's.
- Every diff, review, comparison and rebase target → `base_branch`; a pull request's own → its `baseRefName`; never inferred from a branch name or the injected `gitStatus` "Main branch:" line.
- `base_branch: auto` → `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`, else `git symbolic-ref --short refs/remotes/origin/HEAD` minus `origin/`, else the checked-out branch; name the one assumed.
- `branch_pattern: auto` → the shape the repo's twenty most recent branch names share; none → `<author>/<short-slug>`, kebab-case; `null` → the repo creates no branches.
- Project file absent → ask the user; on their yes, write it per `references/setup.md`, then continue; never fabricate a base branch, assignee or deploy model.

## Rewrites

- Rebase → `git rebase origin/<base>`, upstream always named; a backup ref (`backup/<branch>-<date>`) first; done when `git diff <backup-ref> HEAD` is empty or explained by the resolutions taken.
- Parent squash-merged or rewritten → `git rebase --onto origin/<base> <parent's old tip>`, never a plain rebase.
- Retarget → the new base was cut from the base the branch sits on → retarget alone; otherwise rebase first; then `git diff <new-base>...HEAD`.
- Rewriting published history → only on an instruction naming that branch; a /watch-pr line whose `rewrite` is `allow` is that instruction; a local-only branch rewrites freely.
- A branch other pull requests merge into → takes its base by merge, never rebase: /pull-request rule 6.
- Cherry-pick → always `-x`.

## Routing

| Task | Read |
| --- | --- |
| Make a commit | `references/commit.md` |
| Push, a refused push, a force push | `references/push.md` |
| Write a repo's missing project config | `references/setup.md` |
| Ignore a path — which ignore file takes the entry | `references/ignore-files.md` |
