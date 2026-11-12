---
name: supabase
description: "Reaches Supabase through its CLI and Management API. Use before a `supabase` command or a call to `api.supabase.com`, or when a connection to a `supabase.co` host fails."
user-invocable: false
---

# Supabase

- The CLI first: its `Management APIs` commands cover projects, branches, secrets, functions and config, and `--help` documents each.
- The Management API — base `https://api.supabase.com/v1`, Bearer `SUPABASE_ACCESS_TOKEN` — only for what the CLI lacks, such as `GET /v1/projects/<project-ref>/config/database/pooler`.
- `No route to host` on `db.<project-ref>.supabase.co` → a network verdict, the credential is fine: that host is IPv6-only → connect through the `db_host` and `db_user` that call returns, port 5432.
