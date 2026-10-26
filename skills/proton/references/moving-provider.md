# Moving to another provider

Consumers resolve the store by role and read through `keyless run`, whose names survive a swap, so no consumer, tool config, rule or project file changes.

## Rewrite

- `~/.claude/skills/agents-config/integrations/proton.md` → renamed to the new tool, same `role` and `vault`; the session directory stays out of it, in keylessd's config.
- keylessd's config → declare the new provider as a store in the same pass, or every injected name degrades.
- This skill → `references/session-keeper.md` is a redesign: the two-hour token session is Proton's.

## Rename only

- Every other file naming the vendor in passing: `grep -RIl -i proton ~/Code/skills/ ~/.agents/AGENTS.md ~/.local/bin/`, minus this skill and its config.
- The hooks name the vendor on purpose — a guard on every Bash call cannot afford a role lookup → the census finds them; rename them, never make them resolve by role.
