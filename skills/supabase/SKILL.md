---
name: supabase
description: "Reaches Supabase through its CLI, Management API and connection endpoints. Use on \"supabase login\", \"query supabase\", \"run a migration on supabase\", \"inspect supabase\", a database connection that fails, hangs or reports \"no route to host\", a call to `api.supabase.com`, or a Supabase connection string about to be stored."
user-invocable: false
---

# Supabase

Needs: `SUPABASE_ACCESS_TOKEN` — one Supabase account's access token; the CLI reads it on every command and, with neither it nor a cached login, stops on "Access token not provided".

## The project's own choices

- The hosted project a checkout links to, and its pooler shard where the direct endpoint is unreachable → as the project's instructions state them, else read off its connection string per `references/connecting.md`; none stated → ask the user.

## Management API

- Base `https://api.supabase.com/v1/`, Bearer auth with the account access token:
  `curl https://api.supabase.com/v1/<path> --variable %SUPABASE_ACCESS_TOKEN --expand-header 'Authorization: Bearer {{SUPABASE_ACCESS_TOKEN}}'`

## Routing

| If the task is … | Read |
| --- | --- |
| Authenticating, or running a `supabase` CLI command (`login`, `link`, `db`) | `references/cli.md` |
| Storing a connection string, or a database connection that fails, hangs, or reports no route | `references/connecting.md` |
