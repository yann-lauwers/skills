---
name: pr-cluster
description: "Runs the PR cluster — one integration branch several child pull requests merge into, then one promotion pull request to the trunk: whether a wave takes one, founding it, which base a child targets, shipping and retiring it. Use on 'cluster', 'start a cluster', 'ship the cluster', 'promote the cluster', 'which base does this PR target', 'is cluster/… still live', a `cluster/…` branch, or a repo declaring `integration_bases`. Not for one PR's own base or merge actor — /pull-request ; not for the body — /pr ."
---

# PR cluster

- PR cluster — an integration base (a branch matching the repo's `integration_bases`) that child pull requests merge into, plus its promotion pull request into `base_branch`.
- Every value → `agents-config get git --root <base checkout>`; the base checkout is the parent of `git rev-parse --git-common-dir`.
- `integration_bases` empty → the repo takes no cluster: every pull request targets `base_branch`.
- Founding, readying and reading a PR cluster → `~/.claude/skills/pr-cluster/scripts/cluster.py`; `found` and `ship` print `allow` · `refuse` · `unknown` first, and only `allow` lets the next step run.
- The branch name → the branch the caller hands in, and `found` checks it against a declared glob.

## Routing

| Task | Read |
| --- | --- |
| Whether a wave takes a cluster, and founding or joining it | `cookbook/found.md` |
| Which base a child pull request targets, and whether a named base is live | `references/child-base.md` |
| Readying the promotion pull request once the wave landed | `cookbook/ship.md` |
| The promotion pull request merged, or a spent base found standing | `cookbook/retire.md` |
| A PR cluster's state, or every one on the forge | `~/.claude/skills/pr-cluster/scripts/cluster.py` `status --repo <checkout> --branch <branch>` · `list --repo <checkout>` |

## The rules

1. A child's worktree is cut from the cluster's tip, never from `base_branch`; a child cut from the trunk carries none of its merged siblings' work.
2. The promotion pull request stays a draft until `ship`; a child's checks are whatever the repo's CI runs on a pull request into the cluster, never the trunk suite.
3. Every pull request here — promotion and child — is opened, retargeted and merged through /pull-request , which draws its body from /pr ; the promotion pull request is readied by `ship` alone.
4. The cluster takes `base_branch` by merge, never rebase or force push → /pull-request rule 6.
