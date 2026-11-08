---
name: pr-cluster
description: "Runs the PR cluster — one integration branch, its child pull requests, one promotion to the trunk. Started only by /pr-cluster ."
disable-model-invocation: true
---

# PR cluster

- PR cluster — an integration base (a `cluster/*` branch) that child pull requests merge into, plus its promotion pull request into the trunk.
- Trunk — the branch `refs/remotes/origin/HEAD` names in the base checkout, the parent of `git rev-parse --git-common-dir`.
- Founding, readying and reading a PR cluster → `~/.claude/skills/pr-cluster/scripts/cluster.py`; `found` and `ship` print `allow` · `refuse` · `unknown` first, and only `allow` lets the next step run.
- The branch name → the branch the caller hands in, and `found` refuses one outside `cluster/*`.

## Routing

| Task | Read |
| --- | --- |
| Whether a wave takes a cluster, and founding or joining it | `cookbook/found.md` |
| Which base a child pull request targets, and whether a named base is live | `references/child-base.md` |
| Readying the promotion pull request once the wave landed | `cookbook/ship.md` |
| The promotion pull request merged, or a spent base found standing | `cookbook/retire.md` |
| A PR cluster's state, or every one on the forge | `~/.claude/skills/pr-cluster/scripts/cluster.py` `status --repo <checkout> --branch <branch>` · `list --repo <checkout>` |

## The rules

1. A child's worktree is cut from the cluster's tip, never from the trunk; a child cut from the trunk carries none of its merged siblings' work.
2. The promotion pull request stays a draft until `ship`; a child's checks are whatever the repo's CI runs on a pull request into the cluster, never the trunk suite.
3. Every pull request here — promotion and child — takes its body from /pr ; the promotion pull request is readied by `ship` alone, and merged only once the person names the merge.
4. The cluster absorbs the trunk by merge; a rebase or force push of it never runs.
