# Retire a cluster

Merging the promotion pull request ends the wave. A session the person names to merge runs all three steps in one turn · a merge the person keeps → hand them steps 1 and 3 written out; the next founding's backstop retires whatever is left undone.

1. Before merging: `gh pr list --base <cluster> --state open --json number,headRefName` is empty; non-empty → the merge waits on those children; name them.
2. Merge it.
3. Delete the remote branch. `git wt -C <checkout> list` shows a tree on the branch → `git wt -C <checkout> -y remove <branch> --force -D --foreground`, never without `-D`, which keeps a squash-merged base the integration check misses. No tree, and a checkout still holds the ref → `git -C <checkout> update-ref -d refs/heads/<branch>`, never `branch -d`, which refuses a squash-merged base.

## A spent base found standing

- `~/.claude/skills/pr-cluster/scripts/cluster.py` `status` reads `spent` and the branch still stands → its reason says `closed` → stop, name the promotion pull request and the children merged into the base, delete nothing; the person decides · `merged` → run step 1's read first: non-empty → stop, name those children, delete nothing; where they go is the person's call · empty → step 3.
