# The application

What cmux is and how its CLI addresses a seat; which command an act runs is in the cookbooks.

## The object model

- window → workspace group → workspace → pane → surface; each is addressable by ref, index or UUID.
- A workspace group is a collapsible sidebar section owned by its anchor workspace · a workspace is one seat: a cwd, a name, its own terminals · a pane is a split within a workspace · a surface is a tab within a pane: terminal, browser, simulator, agent session.
- A group's members are workspaces only.
- Closing the anchor closes only that workspace and promotes the next member to anchor; the group survives.
- A group holding one workspace disappears when that workspace closes.
- A workspace row carries no group field → which folder a seat is in is read from the group side, as `member_workspace_refs`.

## Reaching the CLI

- Every command accepts `--json` and prints refs (`workspace:7`, `workspace_group:2`) unless `--id-format` asks otherwise.
- Every command accepts a UUID, the listing's `id`, wherever it takes a ref.
- `--command` at creation is the only way to start a process in a workspace without focusing it.
- A workspace runs whether or not a window shows it → surfacing is `workspace select`, with nothing to repair first; `switch-client` has nothing to switch when no window is attached.

## Addressing a seat

- A UUID names one seat for its whole life, across a cmux relaunch.
- A ref names one seat until cmux relaunches; the relaunch renumbers every seat and hands a freed number to another.
- An index is the row's current sidebar position; every index at or after a closing seat shifts down by one.
- Anything that outlives the turn — a note, an instruction to another session → write the UUID, and resolve it to a ref from the listing when a command needs one.
- An index → resolve it to its ref at the moment it is read; the reply names the ref it resolved to, the only place a substitution shows.

## Who may drive the socket

- Under the default socket mode, `cmuxOnly`, a caller is admitted when it descends from cmux, or runs as the same user carrying `CMUX_SOCKET_CAPABILITY`, the token cmux puts in every terminal's environment.
- The token has no expiry and survives a cmux restart.
- A process started with `nohup` from a seat keeps its access after its parent exits, because it inherits the token.
- A launchd job starts with no token and gets "Access denied - only processes started inside cmux can connect" → hand its command the token in its environment, a secrets-store item read through the injector; leave the socket mode as it is.
- `password` mode makes every caller authenticate, every caller already inside cmux included.

## The Ghostty config

- cmux embeds Ghostty: `~/.config/ghostty/config` owns font, theme, transparency and keybinds · cmux owns the windows, the sidebar, the groups, the browser and diff panes, and the socket CLI.
- A setting edited through cmux → `$C reload-config` reloads `~/.config/ghostty/config` and `~/.config/cmux/cmux.json` and refreshes terminals in place, with no app restart.
- Before editing an existing `cmux.json` → back it up to a timestamped `.bak`.
