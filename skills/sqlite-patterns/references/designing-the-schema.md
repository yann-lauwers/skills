# Designing the schema

Read before creating a table, or choosing a column's type, key, constraint or relation. `G`, `AX` and `SIG` are the prefixes `references/migrations.md` defines.

## Contents

- The schema carries the rules
- Keys
- Relations
- Types and STRICT
- Constraints
- Dates, booleans, UUIDs, JSON, large values
- Generated columns, views and triggers
- Case-insensitive text
- Naming, under GRDB

## The schema carries the rules

- Design the schema before the record types, and make it enforce every rule the data must keep — NOT NULL, UNIQUE, CHECK, foreign keys — G`GRDB/Documentation.docc/RecordRecommendedPractices.md#L11-L56`.
- A column is NOT NULL unless its value is genuinely sometimes unknown — same lines.

## Keys

- Every table gets an explicit primary key; a single-column key is named `id` — G`GRDB/Documentation.docc/DatabaseSchemaRecommendations.md#L101-L213`.
- An integer key is declared exactly `INTEGER PRIMARY KEY`; `INT`, `BIGINT` or `PRIMARY KEY DESC` do not alias the rowid — https://sqlite.org/lang_createtable.html#rowid.
- Never keep a bare rowid as an identifier: `VACUUM` renumbers it unless an `INTEGER PRIMARY KEY` aliases it — https://sqlite.org/rowidtable.html.
- Use `autoIncrementedPrimaryKey("id")` where a deleted id must never be reused; plain `INTEGER PRIMARY KEY` may reuse one — G`GRDB/QueryInterface/Schema/TableDefinition.swift#L120-L150`.
- A non-integer primary key of an ordinary table admits NULL unless declared NOT NULL — https://sqlite.org/lang_createtable.html#primkeyconst.
- GRDB's `primaryKey(_:_:)` adds that NOT NULL — G`GRDB/QueryInterface/Schema/TableDefinition.swift#L172-L225`.
- `WITHOUT ROWID` only for a non-integer or composite key with small rows, after measuring; GRDB observation never sees changes to such a table — https://sqlite.org/withoutrowid.html#wtu, G`GRDB/Documentation.docc/Extension/ValueObservation.md#L226-L248`.
- A value looked up with `fetchOne(_:key:)` or `deleteOne(_:key:)` carries a unique index, or those calls are a fatal error — G`GRDB/Documentation.docc/DatabaseSchemaRecommendations.md#L255-L272`.

## Relations

- Every relation is a foreign key; GRDB associations are inferred from it, and a relation with none needs `ForeignKey(…)` on both sides or crashes at the first request — G`GRDB/Documentation.docc/DatabaseSchemaRecommendations.md#L274-L334`, G`Documentation/AssociationsBasics.md#L694-L782`.
- Every foreign-key child column is covered by an index — https://sqlite.org/foreignkeys.html#fk_indexes, AX`room3-common/src/commonMain/kotlin/androidx/room3/ForeignKey.kt#L21-L44`.
- `belongsTo` indexes its column; `.references(…)` does not, so add `.indexed()` — G`GRDB/QueryInterface/Schema/TableDefinition.swift#L525-L556`, G`GRDB/QueryInterface/Schema/ColumnDefinition.swift#L615-L656`.
- The parent key is the primary key or carries a unique index — https://sqlite.org/foreignkeys.html#fk_indexes.
- A mandatory relation's column is NOT NULL: SQLite ignores a foreign key whose column is NULL — G`Documentation/AssociationsBasics.md#L694-L782`.
- A many-to-many relation is a join table keyed on the pair, with a foreign key to each side and an index on the second key column, since the composite key serves only lookups by its first — https://sqlite.org/optoverview.html#where_clause, AX`room3-compiler/src/main/kotlin/androidx/room3/processor/ProcessorErrors.kt#L604-L608`.
- Choose `ON DELETE` per relation: CASCADE where the child means nothing without its parent, RESTRICT for history the person keeps; RESTRICT fails at once even when the constraint is deferred; the default is NO ACTION — https://sqlite.org/foreignkeys.html#fk_actions, SIG`SignalServiceKit/Storage/Database/GRDBSchemaMigrator.swift#L3032`.
- SQLite ships with enforcement off per connection; GRDB turns it on by default — https://sqlite.org/foreignkeys.html#fk_enable, G`GRDB/Core/Configuration.swift#L23-L28`.

## Types and STRICT

- Outside STRICT a declared type is only an affinity, and a value that does not convert is stored as it arrived — https://sqlite.org/datatype3.html#affinity.
- A STRICT table (SQLite 3.37.0, GRDB `.strict`, macOS 12.4+) rejects a value that does not convert; the version a file needs to open is `references/migrations.md` § What ALTER TABLE can do — https://sqlite.org/stricttables.html.
- A STRICT column is `INT`, `INTEGER`, `REAL`, `TEXT`, `BLOB` or `ANY`; GRDB's `.datetime`, `.date`, `.boolean`, `.double` and `.numeric` emit names STRICT rejects, so dates go in `.text` and booleans in `.integer` there — https://sqlite.org/stricttables.html, G`GRDB/Core/Database.swift#L2096-L2145`.
- Turning an existing table STRICT is a rebuild — `references/migrations.md`.

## Constraints

- A `DEFAULT` is a constant — https://sqlite.org/lang_createtable.html#dfltval.
- A CHECK passes when it evaluates to NULL, so an enum column is `NOT NULL` with a named `CHECK (x IN (…))` — https://sqlite.org/lang_createtable.html#check_constraints.
- Code reading an enum column decodes a value it does not know without crashing: the file can hold rows the CHECK never saw — https://sqlite.org/lang_createtable.html#ckconst.
- A uniqueness rule that may need a temporary violation (reordering positions) is a unique index, `create(indexOn:…, options: .unique)`, which can be dropped; a `.unique()` in the table body cannot — G`GRDB/Documentation.docc/DatabaseSchemaRecommendations.md#L236-L253`.

## Dates, booleans, UUIDs, JSON, large values

- SQLite has no date type; one encoding per column, kept — https://sqlite.org/datatype3.html#datetime.
- GRDB stores a `Date` as `"YYYY-MM-DD HH:MM:SS.SSS"` UTC text, precise to the millisecond; a `Date` nested inside a JSON value is milliseconds since 1970 instead — G`README.md#L1234-L1287`, G`README.md#L2618-L2664`.
- A boolean is the integer 0 or 1 — https://sqlite.org/datatype3.html#boolean.
- GRDB stores a `UUID` as a 16-byte blob; a custom UUID or Date strategy applies to record encoding and key lookups only, so `filter { $0.id == uuid }` misses rows stored another way — G`README.md#L2686-L2747`.
- The encoding of a date or UUID column is set by the migration that creates it; changing it later is a data migration over every row — G`README.md#L2686-L2747`.
- Store JSON as TEXT (`.jsonText`); JSON functions reject a BLOB argument, and GRDB's `jsonb…` functions compile only against a custom SQLite — G`GRDB/Documentation.docc/JSON.md#L13-L25`, G`GRDB/JSON/SQLJSONFunctions.swift#L791`.
- Never bind JSON as `Data`: GRDB binds `Data` as a BLOB, which SQLite may read as JSONB — https://sqlite.org/json1.html#the_json_blob_input_bug, G`GRDB/Documentation.docc/JSON.md#L77-L105`.
- Guard a JSON column with `CHECK (json_valid(col))` — https://sqlite.org/json1.html#the_json_valid_function.
- A JSON field that is filtered is indexed — `references/indexes-and-plans.md` § Choosing the index.
- Keep a BLOB under about 100 KB in the file; store a larger one as a file beside it and keep its name — https://sqlite.org/intern-v-extern-blob.html.

## Generated columns, views and triggers

- A generated column is VIRTUAL unless declared STORED; only VIRTUAL can be added by ALTER TABLE — https://sqlite.org/gencol.html#virtual_versus_stored_columns.
- A generated column uses only its own row and deterministic functions, and `PRAGMA table_info` omits it (`table_xinfo` lists it) — https://sqlite.org/gencol.html#limitations.
- Name every column of a view; generated column names can change between SQLite releases — https://sqlite.org/lang_createview.html#description.
- Write every trigger as `AFTER`, explicitly: `BEFORE` is the default, and a BEFORE trigger that changes its own row is undefined — https://sqlite.org/lang_createtrigger.html#cautions_on_the_use_of_before_triggers.
- `RETURNING` omits changes made by triggers and cascades and returns rows in no fixed order; re-read where those matter — https://sqlite.org/lang_returning.html#limitations_and_caveats.
- An UPSERT (`ON CONFLICT … DO UPDATE`) updates in place and fires only on uniqueness conflicts — https://sqlite.org/lang_upsert.html#description.

## Case-insensitive text

- `COLLATE NOCASE` folds only the 26 ASCII letters: `'É'` and `'é'` differ — https://sqlite.org/datatype3.html#collating_sequences.
- A name unique regardless of case across languages stores a folded key column (`folding(options: [.caseInsensitive, .diacriticInsensitive], locale: nil)`) with a unique index on it — this skill's rule, from the NOCASE limit above.
- Never use `PRAGMA case_sensitive_like`; it is deprecated and can make a schema look corrupt — https://sqlite.org/pragma.html#pragma_case_sensitive_like.

## Naming, under GRDB

- GRDB's defaults are singular camelCase tables and columns; any other convention needs explicit configuration — G`GRDB/Documentation.docc/DatabaseSchemaRecommendations.md#L13-L99`.
- A snake_case schema names its columns in `CodingKeys` raw values and derives `Columns` from them; never mix in `.convertFromSnakeCase`, which leaves `Column(CodingKeys.x)` naming a column that does not exist — G`GRDB/QueryInterface/SQL/Column.swift#L141-L143`, G`GRDB/Record/FetchableRecord.swift#L1085-L1105`.
- `belongsTo("x")` adds a camelCase `xId` column; in a snake_case schema write `t.column("x_id", …).notNull().references("x", onDelete: …).indexed()` — G`GRDB/QueryInterface/Schema/TableDefinition.swift#L429-L596`.
- Name an index for its table and purpose; `create(indexOn:)` names it `index_<table>_on_<cols>` and `.indexed()` names it `<table>_on_<col>`, which a later drop by name must match — G`GRDB/Documentation.docc/DatabaseSchemaModifications.md#L198-L247`.
