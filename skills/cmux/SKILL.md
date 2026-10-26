---
name: cmux
description: "Creates, groups, titles, recolours, reads and closes this machine's terminal seats — cmux workspaces and workspace groups. Use on 'cmux', 'workspace group', 'open a terminal for this', 'read that seat's screen', 'rename the seat', 'close the seat', 'the sidebar is messy'. Also fires before any `cmux` invocation that creates, groups, renames, recolours, closes or writes into a seat, and on a `workspace list` row whose `current_directory` is gone from disk. Not for deciding which units of work there are — the caller names them."
allowed-tools: Bash(/Applications/cmux.app/Contents/Resources/bin/cmux *), Bash(cmux *), Read, Grep, Glob
---

# cmux

- What runs inside a seat belongs to whoever started it.
- Seat — a cmux workspace, one sidebar row; cmux fills `role: terminal`.
- The CLI → `/Applications/cmux.app/Contents/Resources/bin/cmux`, on PATH in every zsh through `~/.zshenv` and in every cmux workspace; written `$C` in every file here, and the scripts' `CMUX_BIN` default.
- The seat a session sits in → `$CMUX_WORKSPACE_ID`, which cmux exports into every workspace; unset → the session is in no seat.
- A row's title, folder and contents stay true to its work.

## Project config

- Read a value with `~/.claude/skills/agents-config/scripts/agents-config get --role terminal <key> --root <repo>`, never from memory.
- `seat_folders` → `per-repository` · `per-effort`: which folder a repo's seats join; the only key a repo writes, in its own config.
- The role resolves to nothing → the terminal is unwired on this machine: say so and stop; never reach for another terminal application.

## What cmux imposes on the shape

- A workspace group is the folder and its anchor workspace the sidebar header → whatever runs in the anchor runs in the folder itself.
- Groups do not nest → depth past one folder is carried by member order and each seat's title.

## Routing table

| Intent | Read |
| --- | --- |
| IF creating a folder, seating a unit, or placing several units as seats | THEN `cookbook/seating.md` |
| IF a session runs in a folder's own header, or the sidebar disagrees with the work | THEN `cookbook/repair.md` |
| IF closing a finished seat — the one this session sits in included — sweeping stranded rows, or dissolving a folder | THEN `cookbook/closing.md` |
| IF reading a seat, writing into one, surfacing one, or renaming and recolouring | THEN `references/observing.md` |
| IF the object model, addressing, a command's shape, socket access from outside cmux, the Ghostty config, or adopting tmux work is the question | THEN `references/application.md` |
| IF which folder a repo's seats join, or which tool fills `role: terminal` is the question | THEN § Project config |
