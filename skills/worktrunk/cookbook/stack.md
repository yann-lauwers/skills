# Stack a nexus Worktree on Another Branch

Builds a nexus tree on top of another branch's work and shares that tree's database, so each branch of a dependent chain gets a checkout without paying for its own data. The create form is fixed once the base is chosen; how deep to stack and where to branch from is the work's shape.

## When to stack

- Stack where the new branch depends on unmerged work in another branch: a chain of PRs each building on the last, a follow-up fix that only makes sense against the parent's schema.
- Independent work → branch from the base with a database of its own: `--base <base>` alone, cheaper to reason about.

## Step 1: Create the stacked tree

```bash
WT_DB=stack:<owner-branch> ~/.config/worktrunk/bin/wtk-new -C <repo> <branch> --base <owner-branch>
```

- `WT_DB` picks the database and `--base` the git base, independently: drop `--base` to share a database without the code.
- The owner branch must have a tree this setup created, on a local database rather than `remote`; otherwise the `identity` step refuses and names which.
- The borrower creates and seeds no cluster of its own.

**Done when:** the create exits 0 and the tree appears in `git wt -C <repo> list`.

## Step 2: Confirm what it borrowed

```bash
git wt -C <tree> db url
git wt -C <owner-tree> db url
```

- Postgres starts on demand: `git wt -C <tree> db start` from the borrower starts the shared cluster; never reset the borrower, which has none of its own.

**Done when:** both commands print the same URL.

## How the borrow is recorded

- The tree's `.wt-dev/identity`, excluded from git, records `PG_MODE=stack` and the owner's `PG_ID`.
- Deep stacks inherit rather than chain: a tree stacked on a borrower records the original owner's cluster.
- A cluster is reaped only when no live tree's identity names it and its owner's path is gone, so the last tree out reaps it.

## Removing a member of a stack

- Remove per `cookbook/delete.md`. Removing the owner while borrowers live keeps the cluster for them, but `db reset`, `reseed` and `restore` run only from the owner → remove the borrowers first wherever the data may still need a reset.
