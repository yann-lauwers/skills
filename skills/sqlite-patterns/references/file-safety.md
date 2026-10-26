# The file itself

Read before choosing where the file lives, opening a connection, copying or restoring the file, importing a file from elsewhere, or linking SQLite into the app. `G` is `https://github.com/groue/GRDB.swift/blob/v7.11.1/`.

## Where it lives

- The file lives in its own directory under Application Support, so its `-wal` and `-shm` move and delete with it — G`GRDB/Documentation.docc/DatabaseConnections.md#L50-L74`.
- Never put the file on a network filesystem or in a folder a sync client copies file by file — https://sqlite.org/wal.html#overview, https://sqlite.org/howtocorrupt.html.
- Never delete a hot journal or `-wal`, and never rename or unlink the file while it is open — https://sqlite.org/howtocorrupt.html#delhotjrnl, https://sqlite.org/howtocorrupt.html#unlink.
- A restore closes every connection before replacing the file and removes the old file's `-wal` and `-shm` with it — https://sqlite.org/howtocorrupt.html.
- Copying is `references/maintenance.md` § Backups.

## Opening a connection

- Set per-connection pragmas in `Configuration.prepareDatabase`, which runs for the writer and every reader; branch on `db.configuration.readonly` for writer-only settings — G`GRDB/Core/Configuration.swift#L206-L243`.
- Set `PRAGMA trusted_schema = OFF` on every connection: sqlite.org encourages it for all applications, and it is on by default — https://sqlite.org/pragma.html#pragma_trusted_schema.
- With it off, an app-registered SQL function used in a trigger, index, CHECK or generated column is registered as innocuous — https://sqlite.org/c3ref/c_dbconfig_defensive.html#sqlitedbconfigtrustedschema.
- Set `PRAGMA application_id` once so tools recognise the file — https://sqlite.org/pragma.html#pragma_application_id.
- Under GRDB the schema's version is the migrator's `grdb_migrations` table, not `user_version` — G`GRDB/Migration/DatabaseMigrator.swift#L616`.
- Read a defaulted setting from the SQLite the app links, never from sqlite.org's stock default: Apple's build changes several, `cache_size` and `journal_size_limit` among them — https://sqlite.org/pragma.html.

## A file from elsewhere

- Any file another program or person could have written is untrusted, even one in the app's own folder — https://sqlite.org/security.html#untrusted_sqlite_database_files.
- Before using such a file: run `quick_check` or `integrity_check` and refuse it on any finding, set `cell_size_check = ON`, keep `mmap_size = 0`, and turn on `SQLITE_DBCONFIG_DEFENSIVE` — https://sqlite.org/security.html#untrusted_sqlite_database_files, https://sqlite.org/c3ref/c_dbconfig_defensive.html#sqlitedbconfigdefensive.
- This skill's own rule: import such a file by opening it read-only and copying its rows into the app's own schema, never by adopting it.

## The SQLite in the process

- Link exactly one SQLite library: two copies keep two lock tables and corrupt the file — https://sqlite.org/howtocorrupt.html#multiple_copies_of_sqlite_linked_into_the_same_application.
- Never `open()` and `close()` the database file outside SQLite in the same process, reading its header included: POSIX `close()` drops every SQLite lock on it — https://sqlite.org/howtocorrupt.html#posix_close_bug.
- Never carry a connection across `fork()` — https://sqlite.org/howtocorrupt.html#fork.
- Close explicitly only when the program depends on it; `close()` can leave a zombie connection — G`GRDB/Core/DatabaseReader.swift#L66-L88`.
- Write each change as it happens; the transaction is the save — https://sqlite.org/appfileformat.html.
