# Ship a cluster

- Ship once the wave has landed: every child merged into the PR cluster, none open, and no worktree still building toward it — a child with no pull request yet is invisible to the script, so this read is the caller's.
- `~/.claude/skills/pr-cluster/scripts/cluster.py` `ship --repo <checkout> --branch <branch>` → readies the draft promotion pull request; `refuse` names the open children, or says none merged yet; `unknown` → re-run once, then name the read that failed.
- Who merges the promotion pull request → /pull-request rule 5, for `base_branch`; its merge retires the cluster → `cookbook/retire.md`.
- Who ships → the session that founded it, once its last child merged · a child held back or a `ship` refusal → the person, through any session they ask.
