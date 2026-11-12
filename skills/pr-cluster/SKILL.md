---
name: pr-cluster
description: "Runs the PR cluster — one integration branch, its child pull requests, one promotion to the trunk. Started only by /pr-cluster ."
disable-model-invocation: true
---

# PR cluster

A PR cluster lands a wave of pull requests as one: each child merges into an integration base, and one promotion pull request carries that base into the trunk.

```text
trunk ──●───────────────────────────────●   promotion pull request merged
         \                             /
          cluster/<name> ──●────●────●      draft promotion pull request, open from the founding
                           ↑    ↑    ↑
                         child child child  each cut from the cluster's tip, each targeting it
```

## Found

- A wave opening two or more pull requests against one base founds a cluster; a single pull request targets the trunk.
- Founding → a `cluster/<name>` branch holding one empty commit off the trunk, and its draft promotion pull request into the trunk.
- A cluster is live while its promotion pull request is open → a wave aimed at a live cluster joins it.

## Grow

- A child is cut from the cluster's tip, and its pull request targets the cluster.
- A pull request opened before the founding → retargeted onto the cluster.
- The cluster takes the trunk by merge: its children build on its history.

## Ship

- Every child merged and none open → ready the promotion pull request.
- The person names its merge.
- Merged → delete the cluster branch.
