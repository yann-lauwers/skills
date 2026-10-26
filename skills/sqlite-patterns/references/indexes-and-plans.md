# Indexes and query plans

Read before adding an index, or when a query is slow, or when a list reading related rows is slow. The plan decides whether an index is used, never the query text, so a slow query is read through `EXPLAIN QUERY PLAN` before any index is added. `G` is `https://github.com/groue/GRDB.swift/blob/v7.11.1/`.

## Reading a plan

- Get it through GRDB with raw SQL: `try Row.fetchAll(db, sql: "EXPLAIN QUERY PLAN <the statement>", arguments: …)`; GRDB has no plan helper. Find the statement it generated with `db.trace { … }` or `db.trace(options: .profile)`, set in `Configuration.prepareDatabase` — G`README.md#L5500-L5551`, G`GRDB/Documentation.docc/Extension/Configuration.md#L23-L41`.

| The line reads | It means |
| --- | --- |
| `SCAN t` | every row of `t` is visited |
| `SEARCH t USING INDEX i (…)` | only the rows the index narrows to are visited |
| `SEARCH t USING COVERING INDEX i (…)` | the table itself is never read |
| `SEARCH t USING INTEGER PRIMARY KEY (rowid=?)` | a direct key lookup |
| `USE TEMP B-TREE FOR ORDER BY` (or `GROUP BY`, `DISTINCT`) | a separate sort an index in the right order would remove |

Source: https://sqlite.org/eqp.html.

- A test asserts a plan has no `SCAN <table>`, never pins the whole string; the format changes between releases — https://sqlite.org/eqp.html.

## Choosing the index

- Equality columns first, then at most one range or ordering column last, with no gaps — https://sqlite.org/optoverview.html#where_clause.
- `WHERE a = ? AND b = ? ORDER BY c` is served by one index on `(a, b, c)`, which removes both the scan and the temp sort — https://sqlite.org/queryplanner.html#_searching_and_sorting_with_a_multi_column_index.
- Never keep two indexes where one is a prefix of the other; drop the shorter — https://sqlite.org/queryplanner.html#_multi_column_indices.
- A covering index carries every column the query reads, so the table is never touched — https://sqlite.org/queryplanner.html#_covering_indexes.
- A partial index is used only when the query's WHERE repeats the index's term literally; SQLite does no algebra — https://sqlite.org/partialindex.html.
- An expression index matches only the identical expression, built from deterministic functions — https://sqlite.org/expridx.html.
- Every foreign-key child column carries an index — `references/designing-the-schema.md` § Relations.
- A `LIKE` uses an index only on a column indexed `COLLATE NOCASE`, with a pattern not starting with a wildcard; `'%abc%'` never uses a b-tree index and belongs to a trigram full-text index — https://sqlite.org/optoverview.html#the_like_optimization, `references/full-text-search.md`.
- Index a JSON field through a VIRTUAL generated column (`kind TEXT AS (payload ->> '$.kind')`) and query the column, or through GRDB's `create(index:on:expressions: [JSONColumn("payload")["kind"]])` and the same `JSONColumn` subscript in the query; an expression index is used only when the query spells the expression exactly — https://sqlite.org/expridx.html#how_to_use_indexes_on_expressions, G`GRDB/Documentation.docc/JSON.md#L27-L50`.
- Add an index for a predicate a plan showed as a `SCAN`, not on a guess — https://sqlite.org/queryplanner.html#_tables_without_indices.

## Landing it

- The index ships in a new migration — `references/migrations.md`.
- `db.create(indexOn: "t", columns: [...])` names it `index_t_on_<cols>`; `column(...).indexed()` names it `t_on_<col>`; a later migration dropping it by name needs the right shape. `db.create(index:on:columns:options:condition:)` takes an explicit name and a partial-index condition — G`GRDB/Documentation.docc/DatabaseSchemaModifications.md#L198-L247`, G`GRDB/QueryInterface/Schema/ColumnDefinition.swift#L185-L215`.
- After the migration, confirm by re-running `EXPLAIN QUERY PLAN`: the `SCAN` became `SEARCH … USING INDEX` and the temp b-tree is gone — https://sqlite.org/eqp.html.

## Statistics

- Run `PRAGMA optimize` after every schema change — https://sqlite.org/pragma.html#pragma_optimize.
- A long-lived connection runs `PRAGMA optimize=0x10002` at open and `PRAGMA optimize` periodically — https://sqlite.org/pragma.html#pragma_optimize.
- A short-lived connection runs `PRAGMA optimize` before closing — https://sqlite.org/pragma.html#pragma_optimize.
- A bare `ANALYZE` is never required, and since 3.46.0 `PRAGMA optimize` bounds its own cost — https://sqlite.org/lang_analyze.html.
- GRDB runs no `PRAGMA optimize` of its own (this skill's reading of the v7.11.1 source, where `PRAGMA optimize` does not occur); run it from `prepareDatabase` only where `db.configuration.readonly == false`, since a pool's read-only readers fail it when analysis is due, and after `migrate` — https://sqlite.org/pragma.html#pragma_optimize, G`GRDB/Documentation.docc/DatabaseSharing.md#L60-L64`.

## Related rows

- Load related rows with `including(all:)`, `including(required:)` or `including(optional:)`, never a fetch per row: `including(all:)` costs one extra query per association level, whatever the row count — G`Documentation/AssociationsBasics.md#L94-L135`, G`GRDB/QueryInterface/Request/QueryInterfaceRequest.swift#L2165-L2270`.
- Read the base rows and their prefetched rows in one `read`, so both see one snapshot — `references/concurrency.md`.
- Aggregates over related rows are `annotated(with: Author.books.count)` and `having(_:)`, in the same query — G`Documentation/AssociationsBasics.md#L2285-L2360`.
- Batch a large `IN (…)` below the host-parameter limit (32766 since 3.32.0) — https://sqlite.org/limits.html#max_variable_number.
