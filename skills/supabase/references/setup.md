# Supabase — project config setup

## Steps

1. Discover what the repo already answers — never fabricate a value:
   - the project ref: `supabase/.temp/project-ref` after a `link`, or the project's dashboard URL the user gives;
   - the vault item: list the secrets store's item names for `<project>-supabase`; none and the CLI logged in → `secret: null`;
   - an unreachable direct endpoint → the pooler host, per `connecting.md`.
   Done when each key has a value or is named as open.
2. Write the repo's `docs/agents/integrations/supabase.md` from the template, shaped per /managing-harness , `references/skills.md` § A tool's skill and its config; a key with no answer stays out. Done when `~/.claude/skills/agents-config/scripts/agents-config get supabase --root "$CLAUDE_PROJECT_DIR"` prints it.
3. Print the path and every key left open, then continue the task.

## Template

```markdown
---
tool: supabase
role: db
status: default
secret:
  <project>-supabase
defaults:
  project-ref: <ref>
---
# supabase — <project> (db)

<reader line — /managing-harness , references/skills.md § A tool's skill and its config>
```
