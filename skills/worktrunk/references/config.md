# `config.toml` Keys

The keys of `~/.config/worktrunk/config.toml` this setup uses; `git wt hook --help` (never `git wt --help`) documents the full hook syntax.

## Top level

- `worktree-path` — the template every tree's path renders from: `~/worktrees/{{ repo }}/<branch slug, 40 chars>-{{ branch | hash }}`, so two branches never share a directory.
- `pre-start`, `pre-remove`, `post-remove` — the global hooks, run for every repo before its own: the ownership token, the removal fence, `wt-dev forget`.

## One entry per repo

```toml
[projects."<host>/<owner>/<repo>"]
pre-remove = "<command>"
aliases.dev = "<command> {{ args }}"

[[projects."<host>/<owner>/<repo>".pre-start]]
canon = "$HOME/.config/worktrunk/bin/wtk-step canon {{ worktree_path }}"

[[projects."<host>/<owner>/<repo>".pre-start]]
deps = "$HOME/.config/worktrunk/bin/wtk-step run {{ worktree_path }} deps -- <install>"
```

- The key is the origin URL as `<host>/<owner>/<repo>`.
- `[[…pre-start]]` blocks run in order; the keys inside one block run concurrently; a failing block aborts the rest. A single-step entry may write `pre-start.<name> = "…"` instead.
- Each key names its step: `git wt -C <tree> -y hook pre-start <name>` re-runs it. `WT_SKIP` names the groups a repo's `wtk-step run` steps declare — `git wt -C <repo> hook show` lists them; `db` is nexus's.
- `aliases.<name>` → `git wt -C <tree> <name> [args]`; `{{ args }}` passes the arguments through.
- `pre-*` hooks block and a failure aborts the command; `post-*` hooks run in the background.

## Template variables

- `{{ worktree_path }}` — the tree · `{{ primary_worktree_path }}` — the main checkout · `{{ worktree_name }}` — the tree's directory name · `{{ branch }}` · `{{ repo }}` · `{{ args }}` — an alias's arguments.
- In `post-remove` they describe the removed tree; `git wt -v` prints them per run.
