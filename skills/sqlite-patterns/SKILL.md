---
name: sqlite-patterns
description: "Designs, migrates, proves and maintains an app's own SQLite file — one file on the person's device, opened through GRDB in Swift or better-sqlite3 in Node or Electron: tables, constraints, data-safe migrations and their tests, indexes and plans, WAL and busy handling, FTS5, integrity, corruption, backups. Use on a new migration or `ALTER TABLE` on a shipped store, a `DatabaseMigrator` or a migrations list, `db.create(table:)`, `new Database(` from `better-sqlite3`, `db.pragma`, `ValueObservation`, `DatabaseQueue` vs `DatabasePool`, `EXPLAIN QUERY PLAN`, `SQLITE_BUSY`, 'database is locked', `VACUUM`. Not for PostgreSQL — /postgres-patterns and /database-migrations ."
---

# SQLite patterns

Router for an app's own SQLite file: one process, one person, a file on their device that outlives every build that reads it. The bar is the team whose product this is — Google's Room and Apple's Core Data: every schema version is snapshotted, every migration is proven against the snapshot before it ships, and nothing erases the person's data by default.

Two premises hold across every reference:

- A schema change never removes a row or loses a value the person made, unless the product owner decided it outside the code, and the pull request adding the migration cites that decision — `references/migrations.md` § Keeping the person's rows.
- A shipped migration is never edited, and every new one is proven before merge — `references/migrations.md`, `references/proving-migrations.md`.

Every rule names the sqlite.org page, the GRDB file (tag `v7.11.1`), or the Room, Apple or Signal source it comes from; a rule marked as this skill's own has none. Carry the citation into the change: the commit message or the reply names the rule each choice follows. A rule this skill does not carry is read from its source before it is applied, never recalled.

## Before acting

Read the SQLite version the app links (`SELECT sqlite_version()`), whether it is the system library or a bundled one, and the GRDB version the package pins; each reference states the floor its features need.

## Routing table

| Intent | Read |
| --- | --- |
| IF designing tables for a feature, or choosing a key, a relation, a type, STRICT, a constraint, JSON or a collation | THEN `references/designing-the-schema.md` |
| IF registering a migration, adding, renaming, dropping or retyping a column, or rebuilding a table | THEN `references/migrations.md` |
| IF writing the tests that gate a migration, or setting up schema snapshots | THEN `references/proving-migrations.md` |
| IF adding an index, a query or a list is slow, or an `EXPLAIN QUERY PLAN` output is in hand | THEN `references/indexes-and-plans.md` |
| IF opening the connection, choosing `DatabaseQueue` or `DatabasePool`, setting WAL or `synchronous`, or on `SQLITE_BUSY` | THEN `references/concurrency.md` |
| IF writing or changing a GRDB record type, a persistence call, or a `ValueObservation` | THEN `references/records.md` |
| IF adding or querying full-text search | THEN `references/full-text-search.md` |
| IF the file or its `-wal` grows, on `SQLITE_CORRUPT`, or adding a check, a backup or memory release | THEN `references/maintenance.md` |
| IF placing the file, setting per-connection pragmas, importing a file from elsewhere, or linking SQLite | THEN `references/file-safety.md` |
| IF the request matches none of the above | THEN `references/designing-the-schema.md`, say which row was closest |

A change often spans rows — a new table is a design, a migration and its proof — so read one reference per row it touches.

## Done when

- The change is a new migration after the last shipped one, with its schema snapshot committed and a path test from every shipped version passing.
- No row or value the person made is lost, unless the product owner decided so outside the code, cited in the pull request that adds the migration.
- A rebuild follows the documented order with foreign-key enforcement off while the old table drops.
- A new index was chosen from a plan, and the plan was read again after it.
- Every choice in the change names its source.
