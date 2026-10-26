# One writer, WAL and busy handling

Read before opening a connection, choosing a queue or a pool, setting a journal mode, or meeting `SQLITE_BUSY` / "database is locked". `G` is `https://github.com/groue/GRDB.swift/blob/v7.11.1/`.

## One writer

- SQLite allows any number of readers and exactly one writer at a time, in every journal mode — https://sqlite.org/whentouse.html, https://sqlite.org/isolation.html.
- Open one `DatabaseQueue` or `DatabasePool` per file for the life of the process; a second connection brings `SQLITE_BUSY` and breaks observation — G`GRDB/Documentation.docc/Concurrency.md#L17-L28`.
- All writes through one queue or pool are serialized; every `read` and `write` is a transaction, a write inside `read` throws, and access methods are not reentrant — G`GRDB/Documentation.docc/Concurrency.md#L76-L183`.

## Queue or pool

- Unsure → `DatabaseQueue`: one connection, every access serialized, and it opens in-memory for tests — G`GRDB/Documentation.docc/DatabaseConnections.md#L17-L23`.
- Slow writes stalling the reads that feed the UI → `DatabasePool`: one writer plus a pool of read-only connections, five by default (`maximumReaderCount`) — G`GRDB/Documentation.docc/Concurrency.md#L237-L241`, G`GRDB/Core/Configuration.swift#L337-L360`.
- Store code takes `any DatabaseWriter` (reads: `any DatabaseReader`), so the switch is one line where the connection is made — G`GRDB/Documentation.docc/Concurrency.md#L237-L241`, G`Documentation/DemoApps/GRDBDemo/GRDBDemo/Database/AppDatabase.swift#L19`.

## WAL

- WAL lets readers and the one writer proceed together; it does not add writers — https://sqlite.org/wal.html#concurrency.
- The mode is stored in the file and persists; read back what `PRAGMA journal_mode=WAL` returns rather than assuming it took, and it cannot change inside a transaction — https://sqlite.org/wal.html#persistence_of_wal_mode.
- A pool sets WAL unless it is read-only; a queue leaves the file's stored mode as it is and sets WAL only with `config.journalMode = .wal` — G`GRDB/Core/Configuration.swift#L290-L322`, G`GRDB/Documentation.docc/Extension/DatabasePool.md#L59-L65`.
- WAL needs every process on the same host and a writable directory for the `-wal` and `-shm` files — https://sqlite.org/wal.html.
- GRDB sets `synchronous = NORMAL` with WAL: no corruption, but the last commits may roll back after a power loss or OS crash; they survive an app crash — G`GRDB/Core/Database.swift#L531-L561`, https://sqlite.org/pragma.html#pragma_synchronous.
- Set `synchronous = FULL` in `prepareDatabase` where every commit must survive power loss — https://sqlite.org/howtocorrupt.html.
- Finish every read promptly, never holding one across user interaction — `references/maintenance.md` § The write-ahead log.

## Busy handling

- A write that begins `DEFERRED`, reads, then writes can get `SQLITE_BUSY` (in WAL, `SQLITE_BUSY_SNAPSHOT`) that no busy handler retries; begin writes `IMMEDIATE` — https://sqlite.org/lang_transaction.html#immediate, https://sqlite.org/rescode.html#busy.
- Never rely on a busy timeout alone: the handler is skipped when waiting could deadlock — https://sqlite.org/c3ref/busy_handler.html.
- GRDB opens every write transaction `IMMEDIATE`; `busyMode` stays `.immediateError` for one process and becomes `.timeout(…)` only when another process writes the same file — G`GRDB/Documentation.docc/DatabaseSharing.md#L147-L168`, G`GRDB/Core/Configuration.swift#L326-L331`.
- WAL can still answer `SQLITE_BUSY` on a read during recovery or while the last connection closes; handle it rather than crash — https://sqlite.org/wal.html#sometimes_queries_return_sqlite_busy_in_wal_mode.

## Swift concurrency

- In async code write `try await writer.read { … }` / `write { … }`; they honour cancellation and roll back. Inside a `Task { }` closure the compiler can pick the blocking overload — G`GRDB/Documentation.docc/SwiftConcurrency.md#L13-L34`, same file `#L199-L230`.
- Record types crossing `read`/`write` are `Sendable` structs — `references/records.md` § Shape.
