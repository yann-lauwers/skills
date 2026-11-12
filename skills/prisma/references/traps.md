# Traps

- Measured on Prisma 6.19.0 and PostgreSQL 17, 2026-11-12.

## The ledger

- `migrate status` compares the migrations folder to the `_prisma_migrations` ledger, never the live schema: it reports `Database schema is up to date!` on a database a push changed, or one whose migrations were only recorded.
- `migrate resolve --applied <name>` writes the ledger row and runs none of the SQL, exit 0 even on an empty database → first `prisma migrate diff --from-schema-datasource <schema> --to-schema-datamodel <schema> --exit-code`: 0 → the database holds the schema · 2 → the printed changes are what it lacks.

## Concurrent index

- `CREATE INDEX CONCURRENTLY` applies only as the single statement of its own migration file, on `migrate deploy` and on a shadow-database replay; beside any other statement the file fails with `P3018`, database error `25001`, and leaves an unfinished ledger row.

## TypedSQL

- `generate --sql` type-checks every SQL file against the live database, so `Errors while reading sql files … column "<x>" does not exist` has two causes: the file is wrong, or the schema already holds `<x>` and the database lags it → mid-edit that is expected, continue · the edit done → bring the database to the schema, then generate again.
