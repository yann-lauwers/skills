# The shared hook layer

One user-level layer runs on Claude Code, on every host. Its home is the `yann` plugin: `~/Code/skills/plugins/yann/hooks/`, wired in `plugins/yann/hooks/hooks.json`, installed from `yann-lauwers/skills`.

## Change, add or retire a handler

- Edit the script under `~/Code/skills/plugins/yann/hooks/`.
- Wire it → its entry in `plugins/yann/hooks/hooks.json`; a handler not listed there runs nowhere.
- A Python handler's command is `"$HOME/.pyenv/versions/3.13.3/bin/python3" "${CLAUDE_PLUGIN_ROOT}/hooks/<x>.py"`, never a `python3` off `PATH`; a shell handler's is `bash "${CLAUDE_PLUGIN_ROOT}/hooks/<x>.sh"`.
- Commit and push in `~/Code/skills`, then `claude plugin marketplace update yannlauwers && claude plugin update yann@yannlauwers` (background auto-update takes it otherwise); every other host runs the same update.
- No renderer and no drift check stand behind the file: the file is what runs.
- Retiring → the entry leaves `hooks.json` in the same commit as the script's deletion and the registry's retirement clause, per `registry.md` § Retiring a check.
- A session keeps the hook list it started with: an updated plugin reaches open sessions only after `/reload-plugins` or a restart.
