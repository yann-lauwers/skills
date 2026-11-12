# The shared hook layer

One user-level layer runs on Claude Code and Codex, on every host. Its home is `~/Code/skills`: one plugin per job under `plugins/<plugin>/hooks/`, the registry and the shared modules under `hooks/`, installed from `yann-lauwers/skills`.

## Change, add or retire a handler

- Edit the script under `~/Code/skills/plugins/<plugin>/hooks/`; a new job → a new plugin, listed in `.claude-plugin/marketplace.json`.
- Wire it → its entry in that plugin's `hooks/hooks.json`; a handler not listed there runs nowhere.
- A Python handler's command is `"$HOME/.pyenv/versions/3.13.3/bin/python3" "${CLAUDE_PLUGIN_ROOT}/hooks/<x>.py"`, never a `python3` off `PATH`; a shell handler's is `bash "${CLAUDE_PLUGIN_ROOT}/hooks/<x>.sh"`.
- A module two plugins import lives in `hooks/lib/`; a plugin takes it as a real copy in its own `hooks/lib/`, never a symlink, since both installers drop a link leaving the plugin; `hooks/sync-lib` refreshes every copy and bumps each plugin it changed, and the repo's pre-commit refuses a stale one.
- A handler reads its plugin's files through its own directory or `${CLAUDE_PLUGIN_ROOT}`, never `~/.claude/hooks/`.
- A changed plugin ships on a `version` bump: `hooks/bump-plugins`, and the repo's pre-commit refuses a change without one. Commit and push in `~/Code/skills`, then `claude plugin marketplace update yannlauwers && claude plugin update <plugin>@yannlauwers` (background auto-update takes it otherwise); every other host runs the same update.
- Retiring → the entry leaves `hooks.json` in the same commit as the script's deletion and the registry's retirement clause, per `registry.md` § Retiring a check.
- A session keeps the hook list it started with: an updated plugin reaches open sessions only after `/reload-plugins` or a restart.
