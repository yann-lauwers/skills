# Indexes

- Add an index only for a predicate the plan already shows as a filter on a scan, and name that predicate and that plan.

## Type follows the operator

| Query pattern | Index type | Form |
| --- | --- | --- |
| `WHERE col = value`, `WHERE col > value` | B-tree (default) | `CREATE INDEX idx ON t (col)` |
| `WHERE a = x AND b > y` | Composite B-tree | `CREATE INDEX idx ON t (a, b)` |
| `WHERE jsonb_col @> '{...}'` | GIN | `CREATE INDEX idx ON t USING gin (col)` |
| `WHERE tsv @@ to_tsquery(...)` | GIN | `CREATE INDEX idx ON t USING gin (col)` |
| Range scans over a column whose values follow insert order — a timestamp on an append-only table | BRIN | `CREATE INDEX idx ON t USING brin (col)` |

- BRIN only where the column's values correlate with physical row order; a table updated in place or bulk-loaded out of order → B-tree.

## Composite order

- Equality columns first, then the range column.

```sql
CREATE INDEX idx ON orders (status, created_at);
-- serves: WHERE status = 'pending' AND created_at > '2024-01-01'
-- does not bound the scan: WHERE created_at > '2024-01-01' alone; PostgreSQL 18's skip scan may still use it
```

## Covering index

- Covering index — `INCLUDE` carries non-key columns in the leaf, so an index-only scan answers without the heap.
- The plan shows an `Index Scan` whose target list is a few non-key columns → `INCLUDE` them; an `Index Only Scan` reporting `Heap Fetches:` → `VACUUM`, never this.

```sql
CREATE INDEX idx ON users (email) INCLUDE (name, created_at);
-- SELECT email, name, created_at FROM users WHERE email = $1 becomes an index-only scan
```

## Partial index

- Partial index — a `WHERE` on the index keeps out the rows a query never asks for.
- The query's own predicate has to imply the index predicate at planning time, or the planner ignores it; a bound parameter in place of the predicate's value never implies it.

```sql
CREATE INDEX idx ON users (email) WHERE deleted_at IS NULL;
-- serves queries that also say WHERE deleted_at IS NULL
```
