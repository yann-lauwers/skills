---
tool: git
role: vcs
status: default
secret: null
defaults:
  base_branch: auto
  pr_assignee: "@me"
  pr_draft: false
  commit_trailers: false
  merge_actor: agent-after-approval
  merge_actor_by_base:
  production_branch: null
  branch_pattern: auto
  review_bots: []
  integration_bases: []
  cluster_base_source: null
---
# git

Read by the `git`, `pull-request` and `pr-cluster` skills and the `pr-merge-approval` hook, and by any consumer through `agents-config get git <key>`.
