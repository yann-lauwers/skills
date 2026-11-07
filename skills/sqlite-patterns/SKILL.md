---
name: sqlite-patterns
description: "Designs, migrates and maintains an app's own on-device SQLite file through GRDB or better-sqlite3. Use on a new migration or `ALTER TABLE` on a shipped store, a `DatabaseMigrator`, `db.create(table:)`, `new Database(` from `better-sqlite3`, `db.pragma`, `ValueObservation`, `DatabaseQueue` vs `DatabasePool`, `EXPLAIN QUERY PLAN`, `SQLITE_BUSY`, 'database is locked', FTS5, corruption, a backup, `VACUUM`. Not for PostgreSQL — /postgres-patterns ."
---

# SQLite patterns

## Rules

- A schema change never removes a row or loses a value the person made, unless the product owner decided it outside the code and the pull request adding the migration cites that decision — `references/migrations.md` § Keeping the person's rows.
- A shipped migration is never edited, and every new one is proven before merge — `references/migrations.md`, `references/proving-migrations.md`.
- Every rule in the references cites its sqlite.org page, GRDB file (tag `v7.11.1`), or Room, Apple or Signal source; a rule marked as this skill's own cites none.
- The commit message or the reply names the rule and source each choice in the change follows.
- A rule the references don't carry → read from its source before it is applied, never recalled.

## Before acting

Read the SQLite version the app links (`SELECT sqlite_version()`), whether it is the system library or a bundled one, and the GRDB version the package pins; each reference states the floor its features need.

## Routing table

| Intent | Read |
| --- | --- |
| designing tables for a feature, or choosing a key, a relation, a type, STRICT, a constraint, JSON or a collation | `references/designing-the-schema.md` |
| registering a migration, adding, renaming, dropping or retyping a column, or rebuilding a table | `references/migrations.md` |
| writing the tests that gate a migration, or setting up schema snapshots | `references/proving-migrations.md` |
| adding an index, a query or a list is slow, or an `EXPLAIN QUERY PLAN` output is in hand | `references/indexes-and-plans.md` |
| opening the connection, choosing `DatabaseQueue` or `DatabasePool`, setting WAL or `synchronous`, or on `SQLITE_BUSY` | `references/concurrency.md` |
| writing or changing a GRDB record type, a persistence call, or a `ValueObservation` | `references/records.md` |
| adding or querying full-text search | `references/full-text-search.md` |
| the file or its `-wal` grows, on `SQLITE_CORRUPT`, or adding a check, a backup or memory release | `references/maintenance.md` |
| placing the file, setting per-connection pragmas, importing a file from elsewhere, or linking SQLite | `references/file-safety.md` |
| none of the above | `references/designing-the-schema.md`, say which row was closest |

- A change spanning rows → read one reference per row it touches.

## Done when

- A schema change is a new migration after the last shipped one, with its schema snapshot committed and a path test from every shipped version passing.
- A rebuild follows the documented order with foreign-key enforcement off while the old table drops.
- A new index was chosen from a plan, and the plan was read again after it.
