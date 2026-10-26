# GRDB records and observation

Read before writing or changing a record type, a persistence call, or an observation that feeds the interface. `G` is `https://github.com/groue/GRDB.swift/blob/v7.11.1/`.

## Shape

- One record type per table, and it is the only type that writes that table: a `Codable` struct conforming to `FetchableRecord` and `PersistableRecord` — G`GRDB/Documentation.docc/RecordRecommendedPractices.md#L60-L64`.
- A NOT NULL column is a non-optional property; an auto-incremented `id: Int64?` is the one exception, and such a type is not `Identifiable` — G`GRDB/Documentation.docc/RecordRecommendedPractices.md#L123-L171`.
- Columns are a nested `Columns` enum derived from `CodingKeys` (`Column(CodingKeys.id)`) — G`GRDB/Documentation.docc/RecordRecommendedPractices.md#L298-L311`.
- The default table name is the type name camelCased; any other is an explicit `static let databaseTableName` — G`GRDB/Record/TableRecord.swift#L333-L343`.
- A raw stored form stays private behind a computed property; a text column read as an enum conforms to `DatabaseValueConvertible` — G`GRDB/Documentation.docc/RecordRecommendedPractices.md#L173-L292`.
- A read joining tables decodes into its own `Decodable, FetchableRecord` type whose coding keys match the association keys — G`Documentation/AssociationsBasics.md#L849-L1211`.
- Record types crossing `read`/`write` are `Sendable` structs; GRDB's `Record` class is not `Sendable` and is discouraged since GRDB 7; an `@Observable` model is a separate class holding them — G`GRDB/Documentation.docc/SwiftConcurrency.md#L115-L197`.
- A static `databaseSelection` is a computed property under Swift 6 — G`GRDB/Documentation.docc/SwiftConcurrency.md#L84-L113`.
- A nested value encoded as JSON keeps `sortedKeys` on any encoder that overrides the default, or comparison and observation see changes that are not there — G`README.md#L2618-L2664`.
- A migration never uses the record type — `references/migrations.md`.

## Persistence calls

- `update` and `updateChanges` throw when no row has the record's key; `save` updates, then inserts when nothing changed — G`README.md#L2171-L2173`.
- `updateChanges` writes only the changed columns — G`README.md#L2841-L2876`.
- Customise persistence with callbacks, never by overriding `insert`, `update` or `save` — G`README.md#L2179`.
- Upsert needs SQLite 3.35.0, overwrites every column but the key, and fires insert callbacks only — G`README.md#L2181-L2211`.
- `upsertAndFetch` with the default `updating: .allColumns` overwrites every column on conflict, including columns a later migration adds; where some columns hold the person's own edits, pass `updating: .noColumnUnlessSpecified` and assign the columns meant to refresh — G`GRDB/Record/MutablePersistableRecord+Upsert.swift#L81-L137`.
- A delete is a call the code makes on purpose, never an unnamed side effect of a schema change — `references/migrations.md` § Keeping the person's rows.

## Observation

- `ValueObservation` delivers the value and each change after it, coalesced; `DatabaseRegionObservation` delivers every committed transaction; a `TransactionObserver` sees changes before commit — G`GRDB/Documentation.docc/Extension/ValueObservation.md#L93-L97`.
- It refetches on any change to the tables and columns it reads, even when its value stays the same; add `removeDuplicates()` — G`GRDB/Documentation.docc/Extension/ValueObservation.md#L250-L299`.
- Keep observations bounded: observe a list once, never each element; stop an observation when its view goes; share one with `shared(in:)` — G`GRDB/Documentation.docc/Extension/ValueObservation.md#L250-L299`.
- Do the expensive work in `.map`, off the database — G`GRDB/Documentation.docc/Extension/ValueObservation.md#L250-L299`.
- `.immediate` scheduling fetches the first value synchronously on the main actor; use it only for a very fast fetch — G`GRDB/Documentation.docc/Extension/ValueObservation.md#L99-L181`.
- Keeping later fetches off the main thread needs a `DatabasePool` and `tracking(regions:fetch:)` or `trackingConstantRegion(_:)` — G`GRDB/Documentation.docc/Extension/ValueObservation.md#L99-L181`.
- No observation sees another connection's writes, a schema change, a `WITHOUT ROWID` table, or SQL GRDB did not compile; call `db.notifyChanges(in:)` after those — G`GRDB/Documentation.docc/Extension/ValueObservation.md#L226-L248`.
- An observation retains the connection until it stops — G`GRDB/Documentation.docc/Extension/ValueObservation.md#L13-L91`.
