# Server defaults

- A fresh database takes these before the first migration runs.

```sql
-- A connection idle inside an open transaction holds its locks and its snapshot;
-- 30s is long enough for any request and short enough that a leaked one is cleared.
ALTER SYSTEM SET idle_in_transaction_session_timeout = '30s';
-- A statement past this is cancelled rather than left to hold the pool. Set on the
-- application role, never server-wide: a migrator and a known long job run as
-- another role and keep no limit.
ALTER ROLE <app_role> SET statement_timeout = '30s';

-- Needs a restart, not a reload, before CREATE EXTENSION below reports anything.
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';

-- The ranking that references/slow-queries.md reads.
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Before PostgreSQL 15 every role could create objects in `public`; 15 revoked
-- CREATE already, and this takes the rest so the application role owns only
-- what a migration granted it.
REVOKE ALL ON SCHEMA public FROM public;

SELECT pg_reload_conf();
```

- `max_connections` and `work_mem` → no default here; size them to the host's RAM and to the pool in front of the database — `work_mem` bounds each sort or hash operation, several per query and per session at once, and hash operations take `hash_mem_multiplier` times it.
