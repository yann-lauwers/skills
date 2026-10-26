# Maintaining the file

Read when the file grows, the `-wal` grows, a check or backup is being added, the file reports corruption, or memory has to be released. sqlite.org documents what each tool does and costs, and names no schedule; every cadence below is this skill's own. `G` and `SIG` are the prefixes `references/migrations.md` defines.

## Contents

- Free space
- The write-ahead log
- Integrity
- Corruption
- Backups
- Memory

## Free space

- A delete leaves free pages the file reuses but never returns to the disk while `auto_vacuum` is NONE, the default — https://sqlite.org/pragma.html#pragma_auto_vacuum.
- Set `PRAGMA auto_vacuum = INCREMENTAL` before the first table is created; turning it on later needs a full `VACUUM` — https://sqlite.org/pragma.html#pragma_auto_vacuum.
- With INCREMENTAL, release pages with `PRAGMA incremental_vacuum(N)`; it is a no-op in any other mode — https://sqlite.org/pragma.html#pragma_incremental_vacuum.
- Measure reclaimable space with `freelist_count` against `page_count` — https://sqlite.org/pragma.html#pragma_freelist_count.
- A full `VACUUM` rewrites the file, needs up to twice its size free on disk (half of it in the temp directory), fails with an open transaction, and renumbers every rowid not aliased by an `INTEGER PRIMARY KEY` — https://sqlite.org/lang_vacuum.html#how_vacuum_works, https://sqlite.org/tempfiles.html#transient_database_used_by_vacuum_.
- This skill's own cadence: `VACUUM` once to switch an existing file to INCREMENTAL, or after a delete that freed a large share of the file, with free disk checked first; never on every launch.
- In WAL mode, a `VACUUM` can change `auto_vacuum` but not `page_size` — https://sqlite.org/lang_vacuum.html#description.
- Leave `page_size` at 4096 — https://sqlite.org/pragma.html#pragma_page_size.

## The write-ahead log

- Automatic checkpoints are PASSIVE, at 1000 pages and on the last close; leave them on — https://sqlite.org/pragma.html#pragma_wal_autocheckpoint.
- A checkpoint recycles the `-wal` without shrinking it unless `journal_size_limit` is set; an app that keeps its connection open never reaches the last-close cleanup, so set the limit — https://sqlite.org/wal.html#avoiding_excessively_large_wal_files, https://sqlite.org/pragma.html#pragma_journal_size_limit.
- A reader that never finishes stops every checkpoint and the `-wal` grows without bound — https://sqlite.org/wal.html#avoiding_excessively_large_wal_files.
- Run `wal_checkpoint(TRUNCATE)` when no reader is open (after a bulk import, before a backup, on quit) and read its first result column: 1 means it was blocked — https://sqlite.org/pragma.html#pragma_wal_checkpoint.
- In GRDB, `try writer.writeWithoutTransaction { try $0.checkpoint(.truncate) }` — G`GRDB/Core/Database.swift#L1132-L1150`.
- After a truncating checkpoint, a `DatabasePool` observation started on an empty `-wal` delivers two initial values; run a no-op write first — G`GRDB/Documentation.docc/Extension/ValueObservation.md#L299`.

## Integrity

- `PRAGMA quick_check` is O(N) and skips UNIQUE and index-against-table checks; `PRAGMA integrity_check` is O(N log N) and does both; each returns `ok` or its findings — https://sqlite.org/pragma.html#pragma_quick_check, https://sqlite.org/pragma.html#pragma_integrity_check.
- Neither checks foreign keys; `PRAGMA foreign_key_check` does — https://sqlite.org/pragma.html#pragma_foreign_key_check.
- GRDB wraps only the foreign-key check (`db.checkForeignKeys()`); run the others as SQL, `try Row.fetchAll(db, sql: "PRAGMA quick_check")` — G`GRDB/Documentation.docc/DatabaseSchemaIntegrityChecks.md#L1-L13`.
- Log that a check failed, never its text, which can carry the person's data — SIG`SignalServiceKit/Util/SqliteUtil.swift#L102-L126`.
- A full-text index has its own check — `references/full-text-search.md` § Maintenance.
- This skill's own cadence: `quick_check` in the background after launch, `integrity_check` before a backup.

## Corruption

- Corruption arrives as `SQLITE_CORRUPT`; a file that is not a database arrives as `SQLITE_NOTADB` at open — https://sqlite.org/rescode.html#corrupt.
- On `SQLITE_CORRUPT`, record it outside the database (`UserDefaults`) — SIG`SignalServiceKit/Storage/Database/DatabaseCorruptionState.swift#L11-L52` — and leave the file and its `-wal` untouched — https://sqlite.org/howtocorrupt.html#_deleting_a_hot_journal.
- Stop writing to a corrupt file — this skill's own rule.
- Recover in tiers: `REINDEX` first; then copy rows into a freshly migrated file; then rebuild the derived data (search indexes) — SIG`SignalServiceKit/Storage/Database/DatabaseRecovery.swift#L14-L35`.
- Classify every table as must-copy, best-effort or skip, and fail a test when a table is unclassified — SIG`SignalServiceKit/tests/Storage/Database/DatabaseRecoveryTest.swift#L52-L70`.
- Replace the file only after checkpointing and closing both databases and deleting their `-wal` and `-shm` — SIG`SignalServiceKit/Storage/Database/DatabaseRecovery.swift#L490-L527`.
- Recovery is salvage: rows can vanish, deleted rows can return, and constraints can be broken — run `integrity_check` and `foreign_key_check` on the result — https://sqlite.org/recovery.html#limitations.
- sqlite.org's recovery API needs `SQLITE_ENABLE_DBPAGE_VTAB`, which a system SQLite may lack; the `sqlite3` CLI's `.recover` is the fallback — https://sqlite.org/recovery.html#building_the_recovery_api_into_an_application.
- Never replace a corrupt store with an empty one silently; surface it — SIG`Signal/AppLaunch/AppLifecycleManager.swift#L209-L213`.

## Backups

- Copy a live file only with the backup API (`try reader.backup(to: writer)`) or `VACUUM INTO` (`try writer.vacuum(into:)`); a file-system copy of the main file alone loses the `-wal`'s transactions — G`GRDB/Core/DatabaseReader.swift#L424-L470`, G`GRDB/Core/DatabaseWriter.swift#L550-L585`, https://developer.apple.com/library/archive/qa/qa1809/_index.html.
- `VACUUM INTO` needs a path that does not exist and cannot run inside a transaction; an interrupted one leaves an incomplete copy, so check the copy — https://sqlite.org/lang_vacuum.html#vacuuminto.
- Save As is the backup API — https://sqlite.org/whentouse.html#appfileformat.

## Memory

- On macOS GRDB has no automatic memory management; call `releaseMemory()`, or `releaseMemoryEventually()` on a pool in use — G`GRDB/Core/Configuration.swift#L402-L410`, G`GRDB/Core/DatabasePool.swift#L152-L198`.
- `cache_size` is per connection and not persisted: set it in `prepareDatabase`, never in a migration — https://sqlite.org/pragma.html#pragma_cache_size.
- Leave `mmap_size` at 0: an I/O error on a mapped file crashes the process — https://sqlite.org/mmap.html.
