# Found or join a cluster

- Run once per wave of pull requests aimed at one base, never once per pull request.
- Inputs → the repo, the cluster's name, and the count of units this wave will commit.
- A base cut once its children are already open is a retarget → /pull-request rule 10.
- `integration_bases` empty → § Fewer than two, whatever the count.

## Read the base first

- `~/.claude/skills/pr-cluster/scripts/cluster.py` `status` settles the step: `live` → every pull request this wave opens takes it, whatever the count; stop · `founded` → step 1 below, then step 2 · `spent` → the backstop in `cookbook/retire.md` § A spent base found standing: its empty arm → then the count · non-empty → the founding stops there · `absent` → the count.

## The count

- Count the units whose pull requests would target the same base branch; a unit that commits nothing — grilling, analysis, review — counts none.
- The test is the target branch, never the repository: two units aimed at different bases share none.
- An unknown count founds, a doubtful one does not: one session that will open more than one pull request, or cannot say how many → founds.

## Two or more → found it

1. `~/.claude/skills/pr-cluster/scripts/cluster.py` `found --repo <checkout> --branch <branch>` → `allow` names one of three states: created (one empty commit off `base_branch`, no checkout touched) · exists with no promotion pull request · live, which joins it and ends here. `refuse` naming a spent base → `cookbook/retire.md` § A spent base found standing, then step 1 again · `refuse` for a glob mismatch, or `unknown` → stop and name the reason.
2. Open its promotion pull request against `base_branch` through /pull-request , as a draft; it stays open while the wave lands, and `status` reads the base's liveness off it.

## Fewer than two → none

- Every pull request targets `base_branch`.

## Done when

- The base is a value, never an absence: the cluster where one was founded, `base_branch` where none was; every pull request this wave opens copies that value.
- Say which case this was.
