---
name: postgres-patterns
description: "Chooses an index or column type, writes a Row Level Security policy, sets a fresh database's defaults, diagnoses a slow query by reading its plan, and lands a schema change on a populated table without a lock — expand, backfill, switch, contract — at the SQL layer of a PostgreSQL server. Use on 'this query is slow', 'add a column', 'backfill this table', 'rename this column', 'drop the old column', 'which index should this have', 'write the RLS policy', 'why is this doing a seq scan', 'what type for this column', or a `.sql` file, `EXPLAIN` output, `CREATE INDEX`, `CREATE POLICY`, `ALTER TABLE` or a large `UPDATE` under edit. Not for Prisma — /prisma-patterns ; not for on-device SQLite — /sqlite-patterns ."
metadata:
  origin: ECC
  source: https://github.com/affaan-m/ECC/blob/main/skills/postgres-patterns/SKILL.md
  credit: Based on Supabase Agent Skills (Supabase team, MIT License)
---

# PostgreSQL Patterns

- Read the plan through `EXPLAIN (ANALYZE, BUFFERS)` before adding any index.
- A statement touching a table that already holds rows → `references/migrations.md` lands it, in its lock-free form and its own file.

## Routing table

| Intent | Read |
| --- | --- |
| IF choosing an index type, its column order, a covering or a partial index | THEN `references/indexes.md` |
| IF picking the type for a column — an id, a string, a timestamp, an amount, a flag | THEN `references/column-types.md` |
| IF writing or reviewing a Row Level Security policy | THEN `references/rls.md` |
| IF a query is slow, a plan shows a seq scan, or a table has grown dead rows | THEN `references/slow-queries.md` |
| IF setting timeouts, monitoring or schema grants on a fresh database | THEN `references/server-defaults.md` |
| IF the statement is the migration itself — adding the index concurrently, backfilling, renaming, dropping | THEN `references/migrations.md` |
| IF the request matches none of the above | THEN `references/slow-queries.md`, say which row was closest |
