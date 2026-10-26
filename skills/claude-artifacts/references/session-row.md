# The session row

- A session that published pages shows them as one row: an orange ⧉, a dim `Artifacts local`, then each page by slug at full weight, newest first, cut to the pane's width with a count of the rest, drawn directly above Claude Code's own artifact row.
- The pointer over a name turns it orange and underlined; a click opens the served page.
- Exactly one surface draws it at a time:

| Surface | Where it draws | Hover | Draws when |
| --- | --- | --- | --- |
| the `artifacts-local` plugin, `plugin/artifacts-local/` in this store | `PromptHint`, directly above the built-in artifact row | yes | its hooks module is loaded in that session |
| line 3 of `~/.claude/statusline.sh` | the status line, above the permission-mode row | no | the session carries no `/tmp/.ccartifacts-row-<session>` marker |

- Hover needs the plugin: a statusline command's output is raw ANSI with no event handlers.
- In a `ui.render` hook, a `Box` with a `key` is a hover scope, and a `Text` inside it takes `hover: { color: "claude", underline: true }`.
- Measured 2026-09-12 on Claude Code 2.1.269, a probe tree at each site in a pty, read back through `pyte`:

| Site | Where it lands | Verdict |
| --- | --- | --- |
| `AbovePrompt` | above the prompt input, three lines higher | not used: it takes focus, so a modifier-click opens the engine's affordance row beneath it and the row reads as two lines |
| `SessionMode` | the right end of the model row, props `{ modes: [] }` | not used: not a row |
| `PromptHint` | the band under the permission-mode row, where the engine draws its own artifact row | the site |

- `next(e)` resolves to the engine's own tree for the site → return a column of [this row, that tree], and the built-in row keeps its styles.
- Draw the name at full weight, and only the label and separators dim: a dimmed name beside the built-in row's bright one reads as disabled.
- The theme's `claude` orange is `rgb(215, 119, 87)`, read off the bytes the renderer emitted repainting a hovered name.

## What breaks it

- Both surfaces below draw from `artifact pages --session <id>`.
- The plugin writes that marker on its first draw → a session whose hooks module never loaded keeps the statusline row, whatever settings say.
- Function-hook modules sit behind `tengu_plugin_hooks_modules`, off by default → `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1` in `~/.claude/settings.json` `env`; without it the plugin lists as enabled and draws nothing, and `claude --debug` logs `hooks modules not loaded: rollout flag (tengu_plugin_hooks_modules) is off`.
- `Link` takes `https:` or `http://localhost` only, and any other URL refuses the whole tree → the plugin rewrites `127.0.0.1` to `localhost`.
- A tree that fails validation is not drawn → `claude --debug` logs the reason; `claude --plugin-dir <plugin>` reloads the module on every save.
- Install → `claude plugin marketplace add ~/.local/share/claude-artifacts/plugin`, then `claude plugin install artifacts-local@claude-artifacts`.
- The cached copy must follow the source → bump `version` in `plugin.json`.
- The loader reads the module from the source directory → an edit applies at the next session start.
- A site's props and what a hook may return → `/plugin-types <dir>` writes the build's own `claude-code.d.ts`; never from memory.
