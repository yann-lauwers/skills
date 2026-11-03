# The session row

The row Claude Code draws above its own artifact row, naming each page this session published: an orange ⧉, a dim `Artifacts local`, then each slug at full weight, newest first; a click opens the served page. Both surfaces draw from `artifact pages --session <id>`, and exactly one draws at a time:

| Surface | Draws when | Hover |
| --- | --- | --- |
| the `artifacts-local` plugin (`plugin/artifacts-local/` in the store), at the `PromptHint` site | its hooks module loaded this session | yes |
| line 3 of `~/.claude/statusline.sh` | the session has no `/tmp/.ccartifacts-row-<session>` marker, which the plugin writes on its first draw | no |

## Drawing it

- `next(e)` resolves to the engine's own tree for the site → return a column of [this row, that tree].
- A `Box` with a `key` is a hover scope; a `Text` inside takes `hover: { color: "claude", underline: true }`.
- Only the label and separators dim; a dim name beside the built-in row's bright one reads as disabled.
- A site's props and what a hook may return → `/plugin-types <dir>` writes the build's own `claude-code.d.ts`.

## What breaks it

- Function-hook modules need `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1` in `~/.claude/settings.json` `env`; without it the plugin lists as enabled, draws nothing, and `claude --debug` logs `hooks modules not loaded: rollout flag (tengu_plugin_hooks_modules) is off`.
- `Link` accepts `https:` or `http://localhost` only, and any other URL refuses the whole tree → the plugin rewrites `127.0.0.1` to `localhost`.
- A tree that fails validation draws nothing; `claude --debug` logs why, and `claude --plugin-dir <plugin>` reloads the module on every save.
- Install → `claude plugin marketplace add ~/.local/share/claude-artifacts/plugin`, then `claude plugin install artifacts-local@claude-artifacts`; bump `version` in `plugin.json` so the cached copy follows the source.
