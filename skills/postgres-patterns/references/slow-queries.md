# Slow queries

## Read the plan first

- Read `EXPLAIN (ANALYZE, BUFFERS)`, never a bare `EXPLAIN`, which only estimates; `ANALYZE` executes the statement → a write runs it inside `BEGIN; … ROLLBACK;`.

| In the plan | It means | The one change |
| --- | --- | --- |
| `Seq Scan` on a large table with a `Filter:` and `Rows Removed by Filter` in the thousands | no index serves the predicate | an index chosen per `references/indexes.md` |
| `rows=` estimate off from `actual rows=` by an order of magnitude | statistics are stale, and every join order above it is chosen on the wrong number | `ANALYZE <table>`, then re-read the plan before touching the query |
| `Sort Method: external merge Disk:` | the sort spilled past `work_mem` | an index in the `ORDER BY` order, or `SET LOCAL work_mem` inside the transaction that runs the statement — outside one, `SET LOCAL` warns and does nothing |
| `Nested Loop` with a large outer side | the planner expected few outer rows and got many | usually the stale-statistics row above; failing that, an index on the inner join key |
| `Index Scan` whose target list is a few non-key columns | the index finds the rows and the heap is visited for the payload | an `INCLUDE` covering index |
| `Index Only Scan` with a large `Heap Fetches:` | the visibility map has holes, so the heap is checked per row for visibility | `VACUUM <table>` so the map fills — no index change |

- One change per read.

## Which queries to read

- Rank by `pg_stat_statements` mean time, the extension created and preloaded per `references/server-defaults.md`; then a second reading ordered by `total_exec_time`.

```sql
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC;
```

## Foreign keys with no index

- Index every foreign key's referencing columns: PostgreSQL indexes only the referenced side, the primary key or unique constraint it must point at. This finds the ones without one:

```sql
SELECT conrelid::regclass, a.attname
FROM pg_constraint c
JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey)
WHERE c.contype = 'f'
  AND NOT EXISTS (
    SELECT 1 FROM pg_index i
    WHERE i.indrelid = c.conrelid AND a.attnum = ANY(i.indkey)
  );
```

## Dead rows

- Dead rows — the old versions an `UPDATE` or `DELETE` leaves in place until vacuum reclaims them.

```sql
SELECT relname, n_dead_tup, n_live_tup, last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

- A table that keeps landing here → a lower `autovacuum_vacuum_scale_factor` on that table, set through `ALTER TABLE … SET (…)`; a one-off `VACUUM` clears only the backlog.
