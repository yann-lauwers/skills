# Redis — project config setup

Writes the repo's `docs/agents/integrations/redis.md` when it is absent.

## Steps

1. Discover what the repo already answers — never fabricate a value:
   - container and published port: a `redis` service in `docker-compose*.yml` or `compose*.yml`;
   - key shape: the key factory or namespace helper, else `.set(` / `.get(` call sites; nothing to infer from → `<namespace>:<resource>:<id>`, written as this repo's `key_pattern`;
   - a managed `REDIS_URL` for staging or production in `.env.example` → one body line naming the store that holds it by role.
   Done when each key has a value or is named as open.
2. Write the file from the template, shaped per /managing-harness , `references/skills.md` § A tool's skill and its config. Done when `~/.claude/skills/agents-config/scripts/agents-config get redis --root "$CLAUDE_PROJECT_DIR"` prints it.
3. Print the path and every key left open, then continue the task.

## Template

```markdown
---
tool: redis
role: cache
defaults:
  container: <container name>
  key_pattern: '<segment order>'
---
# redis — <project> (cache)

<reader line — /managing-harness , references/skills.md § A tool's skill and its config>
```
