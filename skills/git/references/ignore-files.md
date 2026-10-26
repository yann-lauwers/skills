# Ignore files

- Personal in every repo (Claude Code's local files: `.claude/settings.local.json`, `CLAUDE.local.md`) → the global excludes file: the one `git config --global core.excludesFile` names, else `${XDG_CONFIG_HOME:-~/.config}/git/ignore`.
- Personal to one repo (local reports, a local skill or rule, scratch) → `.git/info/exclude`, which every worktree of the clone reads.
- Ignored by everyone (build output, dependency dirs) → the committed `.gitignore`.
- Already excluded by the committed `.gitignore` → no second entry.
- Setting `core.excludesFile` stops git reading the XDG file → move its lines into the named file in the same act.
