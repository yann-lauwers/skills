# Instruction files

- The instructions live in `AGENTS.md`, so every assistant reads one file; `CLAUDE.md` holds `@AGENTS.md` and, below it, only what Claude Code alone acts on — a hook, a slash command, a `.claude/` path.
- The local pair: `AGENTS.local.md` holds the instructions, `CLAUDE.local.md` holds `@AGENTS.local.md`.
- User level: `~/.claude/CLAUDE.md` holds only `@~/.agents/AGENTS.md`.
- `AGENTS.md` holds only what SKILL.md § Where a fact goes sends to it — a test, a state to resolve, a stop condition, a standing convention.
- A line naming a reference doc → the basics sit beside the pointer; never a bare pointer, never the doc's depth grown into the file.
- A subject invisible while it acts — a tool that rewrites commands or switches identity → its basics go in the `AGENTS.md` at the level the tool is wired.
