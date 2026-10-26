# Full-text search

Read before adding, changing or querying a full-text index. `G` is `https://github.com/groue/GRDB.swift/blob/v7.11.1/`.

## Choosing the table

- FTS5 is compiled into GRDB by default; its Swift API sits behind `#if SQLITE_ENABLE_FTS5` — G`Package.swift#L15-L20`, G`GRDB/FTS/FTS5.swift#L1`.
- Index a table the store keeps with an external-content FTS5 table (`t.synchronize(withTable:)`) — G`Documentation/FullTextSearch.md#L597-L617`.
- Index text the store does not keep — a cache over another program's data — with a contentless-delete table (`contentless_delete=1`); prefer it over a plain contentless table — https://sqlite.org/fts5.html#contentless_delete_tables.
- The content table's key is an `INTEGER PRIMARY KEY`: `VACUUM` renumbers any other rowid and breaks the index's link — https://sqlite.org/lang_vacuum.html#how_vacuum_works.
- A temporary synchronized table is a fatal error — G`GRDB/FTS/FTS5.swift#L231-L239`.

## Keeping it in sync

- `synchronize(withTable:)` writes three AFTER triggers (`__<fts>_ai`, `__<fts>_ad`, `__<fts>_au`) and runs `rebuild` to index existing rows — G`GRDB/FTS/FTS5.swift#L265-L281`.
- Without GRDB, write sqlite.org's three triggers, passing `old.*` to the `'delete'` command, then `INSERT INTO ft(ft) VALUES('rebuild')` in the same migration — https://sqlite.org/fts5.html#external_content_tables, https://sqlite.org/fts5.html#external_content_table_pitfalls.
- The `'delete'` command gets the exact old values, or the index drifts — https://sqlite.org/fts5.html#the_delete_command.
- Dropping the FTS table leaves its triggers, which then block every write to the content table; call `db.dropFTS5SynchronizationTriggers(forTable:)` in the same migration — G`Documentation/FullTextSearch.md#L624-L647`.
- External-content and contentless tables turn REPLACE into ABORT, so an `INSERT OR REPLACE` into the content table does not reach the index — https://sqlite.org/fts5.html#external_content_tables.

## Querying

- Build a query from the person's text with `FTS5Pattern(matchingAllPrefixesIn:)` or another non-throwing initializer; it returns nil for input that makes no pattern, and `matching(nil)` fetches no row — G`Documentation/FullTextSearch.md#L484-L569`.
- `MATCH` against the regular table fails; join the FTS table on `rowid` — G`Documentation/FullTextSearch.md#L660-L685`.
- Order by relevance with `.order(Column.rank)` (bm25 by default); a weighted bm25 is raw SQL — G`Documentation/FullTextSearch.md#L572-L588`, https://sqlite.org/fts5.html.
- Normalise search text and indexed text to the same Unicode form (`precomposedStringWithCanonicalMapping`); NFD input misses NFC content — G`Documentation/FullTextSearch.md#L694-L706`.

## Tokenizers

- `unicode61` (the default) is case-insensitive and removes Latin diacritics; set `remove_diacritics 2` to remove them from every Latin character — https://sqlite.org/fts5.html#unicode61_tokenizer.
- `porter` matches English word roots; `trigram` gives substring search and indexed `LIKE`/`GLOB`, and matches nothing under three characters — G`Documentation/FullTextSearch.md#L385-L458`, https://sqlite.org/fts5.html#the_trigram_tokenizer.
- A custom tokenizer is registered in `prepareDatabase`, so every connection that reads the table registers it — G`Documentation/FTS5Tokenizers.md#L60-L95`.

## Maintenance

- Check an external-content index against its table with `INSERT INTO ft(ft, rank) VALUES('integrity-check', 1)`; `PRAGMA integrity_check` does not compare them — https://sqlite.org/fts5.html#the_integrity_check_command.
- On `SQLITE_CORRUPT_VTAB`, run `rebuild`: the index is derived and rebuilding loses nothing — https://sqlite.org/fts5.html#the_rebuild_command.
- After a bulk load, run `optimize` once; `automerge` handles ordinary writes; `merge` spreads the work over steps — https://sqlite.org/fts5.html#the_optimize_command.
- Deleted text stays readable in the index unless `secure-delete` is on, and in the file unless `PRAGMA secure_delete = 1` — https://sqlite.org/fts5.html#the_secure_delete_configuration_option.
