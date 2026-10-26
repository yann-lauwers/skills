# Git — project config setup

- First use of this skill in a repo with no `$CLAUDE_PROJECT_DIR/docs/agents/integrations/git.md` → write it.
- Which keys and what body the file carries → /managing-harness , `references/skills.md` § A tool's skill and its config; this file adds what each git key answers.

## What earns a line

- Never restate a rule a skill already enforces (draft state, title style, the report-reference block, when a production deploy is consented to).
- What each key answers, where this repo names it:
  - `base_branch` → the trunk is not what `auto` derives (a repo merging into `staging` while the forge default is `main`).
  - `production_branch` → a branch deploys to production on merge, and `base_branch` is then pinned literally; where it is not `base_branch`, `merge_actor_by_base` names who may merge onto it · where they are one branch, one entry answers for both: a `merge_actor_by_base` rule naming it, else `merge_actor`.
  - `branch_pattern` → a house branch-naming convention, especially one a tracker links against · `null` → the repo creates no branches.
  - `review_bots` → automated reviewers that comment on pull requests here.
  - `merge_actor` · `merge_actor_by_base` → who merges a pull request here, and the map where that answer differs by target base; a floor `merge_actor_by_base` rule outranks a project `merge_actor`, and only a project rule for the same base overrides it.
  - `merge_actor_by_base` → always an indented block, one `<base or pattern>: <actor>` per line, each key an exact base name or a pattern holding `*` (`*` any run, `.` literal, every other character a regular expression); a key with no `*` is an exact name, `?` or `[` included; an exact name first, then the longest matching pattern; the `pr-merge-approval` hook parses only that form, so an inline map reads as no rules.
  - `integration_bases` → the globs of the integration bases this repo cuts, a non-empty list opting the repo into PR clusters; on github.com needed only for a base with no merged child yet; off github.com the only protection, so list every base; a `merge_actor_by_base` pattern that is an integration base is listed here too, spelled with `*` in that map, where a `?` or `[` is an exact name while here it globs.
  - `cluster_base_source` → `parent-ticket` where a branch takes the base its ticket's parent names.
  - `commit_trailers` · `pr_assignee` · `pr_draft` → where this repo departs from the owner's standing preference.
  - `secret` → the item name when this repo scripts the forge API outside `gh`.
- A git convention no key holds that a skill reads → release-warning wording · a commit-subject form · a commit-scope snapshot; a close-out or a trap only this repo runs → the repo's `AGENTS.md`, per /managing-harness , `references/skills.md` § A tool's skill and its config.

## Bootstrap

1. Resolve what is already true → `~/.claude/skills/agents-config/scripts/agents-config resolve git` for the levels in play, then the floor's values; every question below is a delta against them.
2. Discover what the repo answers, never fabricate:
   - Default branch → `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`, the value `auto` derives; the trunk matching it means no `base_branch` line, except in a repo with a `production_branch`.
   - Pull-request practice → `gh pr list --state all --limit 20 --json headRefName,isDraft,assignees`, against the merged defaults.
3. Ask the repo owner what discovery cannot answer → who merges a pull request (per target base where the repo cuts integration bases or names a `production_branch`, one repo-wide answer otherwise) · whether a branch deploys to production. Name the floor value each answer would override; an answer naming integration bases writes their glob into `integration_bases` beside the `merge_actor_by_base` rule.
4. Write the file with the resolved delta set, then print its path, every delta and the floor value it overrides.
5. Continue the task against the merged config.

- Done when the file resolves through `~/.claude/skills/agents-config/scripts/agents-config get git --root "$CLAUDE_PROJECT_DIR"`.

## Template

```markdown
---
tool: git
role: vcs
defaults:
  base_branch: <branch>
  production_branch: <branch>
  branch_pattern: <pattern>
  review_bots: [<bot>, <bot>]
  merge_actor: <person | agent-after-approval | agent>
  merge_actor_by_base:
    <base or pattern>: <actor>
  integration_bases: [<glob>]
---
# git — <project>

<reader line — /managing-harness , references/skills.md § A tool's skill and its config>

## Production-deploy branch

- Merging `<production_branch>` deploys to <target>. Release warning: `<wording>` — what the deploy reaches, naming no branch.

## Commit scopes

- Not an allowlist: `<scope>` · `<scope>`.
```
