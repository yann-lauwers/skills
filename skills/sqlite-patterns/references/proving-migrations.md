# Proving a migration

Read before merging a migration, or when setting up an app's migration tests. The bar is Google's Room: a committed schema snapshot per version, and a test that builds each old version, fills it, migrates it, and compares the result to the snapshot. `G`, `AX` and `SIG` are the prefixes `references/migrations.md` defines.

## Contents

- Schema snapshots
- The path tests
- The test database
- Asserting schema and rows

## Schema snapshots

- Commit one schema snapshot per migration id, beside the tests; never ship them in the app — https://developer.android.com/training/data-storage/room/migrating-db-versions (§ Export schemas), AX`room3-common/src/commonMain/kotlin/androidx/room3/Database.kt#L93-L109`.
- Produce a snapshot by migrating a fresh in-memory database `upTo:` that id and writing `try db.dumpSchema(to: &text)`; it leaves out `sqlite_`/`grdb_` objects and FTS shadow tables and sorts its output stably — G`GRDB/Dump/Database+Dump.swift#L235-L318`.
- This skill's own rule, in two checks. A test regenerates every snapshot from a fresh migration and fails when one differs from its committed file. CI fails when a shipped id's committed snapshot differs from the last release tag (`git diff <tag> -- <snapshots>`). An edit that changes a shipped migration's schema fails the first if its snapshot is left alone, and the second if it is regenerated. A third check covers edits that change only data: CI fails when `git diff <tag> -- <migrator source>` changes or removes a line that existed at the tag, so a shipped migration's body is append-only whatever it does.
- Room guards the same fact on the device: a stored schema hash refuses a file whose schema changed without a version bump — AX`room3-runtime/src/commonMain/kotlin/androidx/room3/RoomConnectionManager.kt#L359-L379`.
- Dump the full schema from a fresh migration in CI as well — SIG`SignalServiceKit/tests/Storage/Database/GRDBSchemaMigratorTest.swift#L13-L57`.
- A schema comparison that must see generated columns reads `PRAGMA table_xinfo`, not `table_info` — https://sqlite.org/gencol.html#limitations.

## The path tests

- Each new migration gets a test that migrates a fresh database `upTo:` the previous id, inserts rows with raw SQL, runs the full migrator, and asserts the schema and every seeded value read back, converted — https://developer.android.com/training/data-storage/room/migrating-db-versions (§ Test a single migration), G`GRDB/Documentation.docc/Migrations.md#L48-L57`.
- Insert the old rows with raw SQL: the record types describe the latest schema, not the old one — https://developer.android.com/training/data-storage/room/migrating-db-versions (§ Test a single migration).
- Include the empty-table case — SIG`SignalServiceKit/tests/Storage/Database/GRDBSchemaMigratorTest.swift#L289-L340`.
- One test migrates the earliest shipped schema, with rows, to the latest — https://developer.android.com/training/data-storage/room/migrating-db-versions (§ Test all migrations).
- This skill's own rule, beyond Room's: run the path test from every shipped id to the latest, since each start takes a different path.
- A migration that adds a trigger fires it once in its test: `UPDATE OF` accepts a column that does not exist and the trigger then never fires — https://sqlite.org/lang_createtrigger.html#description.

## The test database

- Tests run on an unnamed in-memory `DatabaseQueue()` so each is isolated; `DatabaseQueue(named:)` shares one database across every test using the name — G`GRDB/Core/DatabaseQueue.swift#L60-L100`.
- Build the test database from the app's own `Configuration`, so the pragmas and functions `prepareDatabase` sets apply in tests too — G`Documentation/DemoApps/GRDBDemo/GRDBDemo/Database/AppDatabase.swift#L71-L97`.
- A queue has no concurrent readers, so behaviour only a `DatabasePool` has (snapshot isolation, observation after a truncating checkpoint) needs a test on an on-disk pool — G`GRDB/Documentation.docc/Extension/ValueObservation.md#L299`.
- Control time in tests through `Configuration.transactionClock` — G`GRDB/Documentation.docc/RecordTimestamps.md#L109`.

## Asserting schema and rows

- Assert rows with `dumpContent(format: .quote())` or `dumpTables`; never snapshot the default `.debug()` format, which "is not suitable for … testing" — G`GRDB/Dump/DumpFormats/DebugDumpFormat.swift#L15-L19`, G`GRDB/Dump/DumpFormats/QuoteDumpFormat.swift#L13-L23`.
- Assert `PRAGMA foreign_key_check` returns no row, and that every index and trigger from before a rebuild exists after it — https://sqlite.org/pragma.html#pragma_foreign_key_check.
- A table with a synchronized full-text index is checked with the FTS5 `integrity-check` at rank 1 — `references/full-text-search.md`.
