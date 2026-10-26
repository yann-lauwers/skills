---
name: supabase
description: "Reaches Supabase through the `supabase` CLI, the Management API and the database's connection endpoints. Use on \"supabase cli\", \"supabase login\", \"query supabase\", \"run a migration on supabase\", \"inspect supabase\", a database connection that fails, hangs or reports \"no route to host\", a call to `api.supabase.com`, or a Supabase connection string about to be stored. Not for writing the migration — /database-migrations ; not for an index, column type, RLS policy or query plan — /postgres-patterns ."
user-invocable: false
---

# Supabase

## Project config

- Read the merged config first → `~/.claude/skills/agents-config/scripts/agents-config get supabase <key> --root "$CLAUDE_PROJECT_DIR"`, and the project file's body for the repo's own rules.
- No `docs/agents/integrations/supabase.md` in the repo → ask the user; on their yes, write it through `references/setup.md`, then continue; the floor holds no project.

| Key | What it answers |
| --- | --- |
| `secret` | the vault item `keyless run` injects — the account access token unless the body says otherwise; `null` → the CLI's own `supabase login` cache |
| `project-ref` | the hosted project a checkout links to |
| `pooler_host` | the project's own shard of the shared pooler, where the direct endpoint is unreachable |

## Management API

- Base `https://api.supabase.com/v1/`, Bearer auth with the account access token; `<SECRET>` is `secret` uppercased, every non-alphanumeric as `_`:
  `keyless run -s T=<SECRET> -- curl https://api.supabase.com/v1/<path> --variable %T --expand-header 'Authorization: Bearer {{T}}'`

## Routing

| If the task is … | Read |
| --- | --- |
| Authenticating, or running a `supabase` CLI command (`login`, `link`, `db`) | `references/cli.md` |
| Storing a connection string, or a database connection that fails, hangs, or reports no route | `references/connecting.md` |
| No project config yet | `references/setup.md` |
