# Migrations that keep the person's rows

`G` is `https://github.com/groue/GRDB.swift/blob/v7.11.1/`, `AX` is `https://github.com/androidx/androidx/blob/a12036836c464b39bde66b7e2a7c4238eef3b884/room3/` (Google's Room), `SIG` is `https://github.com/signalapp/Signal-iOS/blob/06fb42bbf4402c738fc6d37dcb2828ba6ec0ce9f/` (a production GRDB store).

## Contents

- The migration itself
- Decomposing a change too big for one step
- What ALTER TABLE can do
- Everything else: the table rebuild
- Keeping the person's rows
- Refusing a database the build does not know
- Recovery

## The migration itself

- A change is a new `registerMigration("<id>")` appended after the last one — G`GRDB/Documentation.docc/Migrations.md#L176-L198`.
- A fix to a shipped migration is a new id; keep retired ids in a `#if DEBUG` enum so the compiler refuses their reuse — SIG`SignalServiceKit/Storage/Database/GRDBSchemaMigrator.swift#L410-L490`.
- Name an id for what it does, never a bare number — SIG`SignalServiceKit/Storage/Database/GRDBSchemaMigrator.swift#L71`.
- A migration speaks SQL, strings and `Row`, never anything that describes the latest schema: a record type, its `Columns`, its `databaseTableName`, a shared SQL constant — G`GRDB/Documentation.docc/Migrations.md#L176-L198`, AX`room3-runtime/src/commonMain/kotlin/androidx/room3/migration/Migration.kt#L55-L72`.
- Each migration runs in its own transaction; one that throws rolls back, stops the ones after it, and reruns on the next launch — G`GRDB/Documentation.docc/Migrations.md#L77`, SIG`SignalServiceKit/Storage/Database/GRDBSchemaMigrator.swift#L510-L518`.
- Migration logic survives being interrupted: rerunning it after a kill produces the same result — https://developer.apple.com/videos/play/wwdc2022/10120/.
- Migrations only run forward; `migrate(_:upTo:)` below what is applied is a fatal error — G`GRDB/Documentation.docc/Migrations.md#L48-L57`.
- Migrations run in the writer queue, serialized with every other write — G`GRDB/Migration/DatabaseMigrator.swift#L186-L189`.
- Where a second process can open the file, re-check `grdb_migrations` for the id inside the migration's own transaction before doing its work — SIG`SignalServiceKit/Storage/Database/GRDBSchemaMigrator.swift#L536-L552`.
- `eraseDatabaseOnSchemaChange` stays off in every build that can open the person's real file; GRDB allows it only behind `#if DEBUG` — G`GRDB/Documentation.docc/Migrations.md#L200-L219`.
- Prefer GRDB's `db.alter(table:)` methods over raw SQL, so the compiler checks the change is available on the target OS — G`GRDB/Documentation.docc/DatabaseSchemaModifications.md#L7`.
- The app migrates before any code reads the file and every build refuses a superseded file (§ Refusing a database the build does not know) → the server-side expand, backfill, switch and contract acts collapse into one migration, which says so, since no reader sits between them — this skill's own reading.
- A backfill deferred past launch (§ Decomposing) puts a reader between them again: the code handles rows not yet backfilled until the queue drains, and the migration says so — this skill's own reading.

## Decomposing a change too big for one step

- Split a change across migrations only where one step is expensive (below) or needs its own foreign-key mode (§ Everything else); each piece is then add, backfill, constrain or rebuild, drop — https://developer.apple.com/videos/play/wwdc2022/10120/, https://developer.apple.com/videos/play/wwdc2023/10186/.
- A new NOT NULL column → one `ADD COLUMN` with a constant default, then a backfill of real values in the same migration — AX`room3-compiler/src/main/kotlin/androidx/room3/processor/ProcessorErrors.kt#L1069-L1071`, https://developer.apple.com/documentation/coredata/migrating-your-data-model-automatically.
- Only where the backfill cannot finish inside this migration (deferred past launch, below) or some rows have no value to derive is it added nullable and backfilled — SIG`SignalServiceKit/Storage/Database/GRDBSchemaMigrator.swift#L5949-L5953` — then made NOT NULL by `ALTER COLUMN … SET NOT NULL` (3.53.0) or a rebuild — https://sqlite.org/lang_altertable.html#alter_table_alter_column.
- Clean the rows a new constraint would reject in the same migration, before the constraint — https://developer.apple.com/videos/play/wwdc2023/10195/.
- A backfill streams through a cursor (`fetchCursor`), never `fetchAll` — SIG`SignalServiceKit/Storage/Database/GRDBSchemaMigrator.swift#L3947-L3963`.
- Ship at most one expensive migration — an index over a large table, a rebuild — per release, and move a backfill too slow for launch into a queue table drained after launch — SIG`SignalServiceKit/Storage/Database/GRDBSchemaMigrator.swift#L2475-L2477`, same file `#L3966-L3973`.

## What ALTER TABLE can do

| Operation | SQLite floor | Source |
| --- | --- | --- |
| rename a table | long-standing | https://sqlite.org/lang_altertable.html#altertabrename |
| rename a column (`t.rename(column:to:)`) | 3.25.0 | https://sqlite.org/releaselog/3_25_0.html |
| add a column (`t.add(column:)`) | long-standing | https://sqlite.org/lang_altertable.html#altertabaddcol |
| drop a column (`t.drop(column:)`, macOS 12+) | 3.35.0 | https://sqlite.org/releaselog/3_35_0.html |
| set or drop NOT NULL, add or remove CHECK | 3.53.0 | https://sqlite.org/lang_altertable.html#alter_table_alter_column, https://sqlite.org/releaselog/3_53_0.html |

- A rename is a rename statement, never a drop and an add — https://developer.apple.com/documentation/coredata/migrating-your-data-model-automatically.
- ADD COLUMN refuses PRIMARY KEY, UNIQUE and a STORED generated column; its default is a literal, never `CURRENT_TIME`, `CURRENT_DATE`, `CURRENT_TIMESTAMP` or a parenthesized expression; NOT NULL needs a non-NULL default — https://sqlite.org/lang_altertable.html#altertabaddcol.
- A `REFERENCES` column added while enforcement is on must default to NULL; inside a GRDB migration with the default deferred checks enforcement is off, so the column may be NOT NULL with a default naming a parent row this migration inserts first, or one an earlier migration seeded on every file; the commit-time check refuses anything else, and the migration then fails on every launch — G`GRDB/Migration/Migration.swift#L79-L109`, https://sqlite.org/lang_altertable.html#altertabaddcol.
- ADD COLUMN changes only the schema text, unless it carries a CHECK, or NOT NULL on a generated column, which is tested against every existing row (3.37.0) — https://sqlite.org/lang_altertable.html#altertabaddcol.
- DROP COLUMN refuses a column that is a PRIMARY KEY or part of one, UNIQUE, indexed, in a partial index's `WHERE`, in a CHECK not attached to it, in a foreign key, in a generated column's expression, or in a trigger or view; it rewrites the table — https://sqlite.org/lang_altertable.html#altertabdropcol.
- Name every CHECK (`CONSTRAINT status_values CHECK (…)`) so a 3.53.0 `DROP CONSTRAINT` can target it; below 3.53.0 widening a CHECK is a rebuild — https://sqlite.org/lang_altertable.html#alter_table_alter_column.
- Any feature newer than a library, written into the schema — STRICT (3.37.0), a generated column (3.31.0), a newer function or operator in a default, CHECK or index expression — makes the file unreadable to that library — https://sqlite.org/stricttables.html#backwards_compatibility, https://sqlite.org/gencol.html#compatibility; a statement using a newer form fails to run.

## Everything else: the table rebuild

A type change, a new key, turning a table STRICT, a constraint below 3.53.0 — every change ALTER TABLE cannot make — is the rebuild, in this order and no other (https://sqlite.org/lang_altertable.html#otheralter):

1. Foreign-key enforcement off, outside any transaction — `PRAGMA foreign_keys` is a no-op inside one (https://sqlite.org/pragma.html#pragma_foreign_keys).
2. Start a transaction.
3. Read the table's indexes, triggers and views: `SELECT type, sql FROM sqlite_schema WHERE tbl_name='X'`.
4. `CREATE TABLE new_X` in the new shape.
5. `INSERT INTO new_X (<columns>) SELECT <columns, converted> FROM X` — name the columns.
6. `DROP TABLE X`.
7. `ALTER TABLE new_X RENAME TO X`.
8. Recreate the indexes and triggers from step 3.
9. Drop and recreate every view the change affects, and every trigger on another table that names X.
10. `PRAGMA foreign_key_check`; any row returned is a violation, so the migration throws and rolls back (https://sqlite.org/pragma.html#pragma_foreign_key_check).
11. Commit.
12. Foreign-key enforcement back on.

- Renaming the old table out of the way first corrupts triggers, views and foreign keys — https://sqlite.org/lang_altertable.html#caution.
- Step 1 keeps the child rows: with foreign keys on, `DROP TABLE` runs an implicit DELETE that fires `ON DELETE CASCADE` — https://sqlite.org/foreignkeys.html (§ 5).
- A trigger on another table survives the drop of a table it names, so step 9 checks it — https://sqlite.org/lang_createtrigger.html#description.
- Under GRDB, a migration registered with the default deferred foreign-key checks does steps 1, 2, 10, 11 and 12 itself: foreign keys off, an IMMEDIATE transaction, a full check, commit, foreign keys back on. Write steps 3–9 in the body — G`GRDB/Migration/Migration.swift#L79-L109`, G`GRDB/Documentation.docc/Migrations.md#L115-L172`.
- On a migrator built with `disablingDeferredForeignKeyChecks()`, the default runs with foreign keys off and no check; the body calls `try db.checkForeignKeys()` itself — G`GRDB/Migration/DatabaseMigrator.swift#L313-L329`.
- With foreign keys off on the connection, the migrator runs the body in a plain IMMEDIATE transaction and checks nothing; the body calls `try db.checkForeignKeys()` itself — G`GRDB/Migration/Migration.swift#L30-L62`, G`GRDB/Core/Database+Schema.swift#L884`.
- A rebuild never uses `foreignKeyChecks: .immediate` — G`GRDB/Documentation.docc/Migrations.md#L229-L237`.
- Renaming a foreign-key column needs `.immediate`, so a rebuild and a foreign-key rename are two migrations — G`GRDB/Documentation.docc/Migrations.md#L97-L113`.
- A table with a synchronized full-text index drops the index's triggers in the same migration — `references/full-text-search.md`.
- Never take the `writable_schema` shortcut on a file whose data must survive — https://sqlite.org/lang_altertable.html#otheralter.

## Keeping the person's rows

- Erasing data is never a default: a missing migration refuses to open, and a destructive path is an explicit opt-in; Room's per-version form, `fallbackToDestructiveMigrationFrom`, is the one this skill models — AX`room3-runtime/src/commonMain/kotlin/androidx/room3/RoomDatabase.kt#L309-L377`, https://developer.android.com/training/data-storage/room/migrating-db-versions.
- A retype converts every value, and a row the new code no longer understands or shows is kept and marked with a flag column (`unsupported`, added with a constant default) — this skill's own rule.
- The product owner's decision to remove rows or values is written or approved by the owner outside the code (the ticket, a decision record) before the change opens; the migration's author cannot grant it, and the reviewer reads the record, not the citation — this skill's own rule.
- The never-remove rule (`SKILL.md`'s first premise) binds schema changes only: a delete the person asks for deletes, and rows rebuilt from another source — a cache, a search index — are dropped and rebuilt freely — this skill's own rule.
- Dropping a column purges its data and dropping a parent table cascades into its children; each is a removal under the rule above — https://sqlite.org/lang_altertable.html#altertabdropcol, https://sqlite.org/foreignkeys.html (§ 5).
- Obsolete tables are dropped by a named migration, never by editing the one that created them — SIG`SignalServiceKit/Storage/Database/GRDBSchemaMigrator.swift#L4114`.

## Refusing a database the build does not know

- `hasBeenSuperseded(db)` is true when the file holds a migration this build never registered, meaning a newer build wrote it — G`GRDB/Migration/DatabaseMigrator.swift#L548-L560`.
- Check it before `migrate`, and refuse to open a superseded file rather than erase or migrate it; GRDB's own sample checks after, which lets an older build write to a newer file — G`GRDB/Documentation.docc/DatabaseSharing.md#L77-L81`, AX`room3-runtime/src/commonMain/kotlin/androidx/room3/util/MigrationUtil.kt#L35-L49`.
- An incompatible or unopenable store is an error the app surfaces, never a reset — https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/CoreDataVersioning/Articles/vmInitiating.html, SIG`Signal/AppLaunch/AppLifecycleManager.swift#L209-L213`.

## Recovery

- A migration is never written to be reversed — this skill's own rule.
- A file that becomes unreadable → `references/maintenance.md` § Corruption.
