# Migrate

Creates, proves, applies and amends migrations, pushes without one, baselines a pushed database, recovers a wrong baseline, and carries the SQL Prisma's generator cannot write.

- Run a workflow's steps in order: each write in it passes SKILL.md § Before a write.
- `generate --sql` runs once the database holds the change: it type-checks every TypedSQL file against the live database · plain `generate` reads no database.
- `workflow_doc` says when to push and when to migrate; this file says how.
- Flags below are major 6's; major 7's replacements are SKILL.md § Version.

## Create a migration

1. Edit the schema, then `scripts.create_migration` → run it as the project config's body says · none → `<runner> migrate dev --create-only --name <snake_case_name>`, whose empty `migration.sql` means the schema adds nothing over the migrations folder. Done when `migrations/<timestamp>_<name>/migration.sql` holds SQL. · the script reports nothing to do → the folder already reproduces the schema; stop.
2. Read the generated SQL; a drop, or a `NOT NULL` column without a default on a table holding rows → stop and sequence the change before applying it. Done when neither remains or the user accepted it.
3. Prove it complete — the migrations folder reproduces the schema: `scripts.check_migration` → run it · none → `<runner> migrate diff --from-migrations <dir> --to-schema-datamodel <schema> --shadow-database-url "$SHADOW_DATABASE_URL" --exit-code`, the shadow URL reaching the environment through the `role: app-secrets` injector, never typed. Done when it exits 0; any other exit with SQL printed — 2 from the raw verb — is what would ship missing.

## Apply pending migrations

1. `scripts.apply_migration` → run it · none → `<runner> migrate deploy`. Done when `migrate status` reports the database up to date.
2. `generate`. Done when it exits 0.

## Push without a migration

1. `scripts.push` → run it · none → `<runner> db push`. A data-loss warning stops it → `--accept-data-loss` only after SKILL.md § Consent guard's ask. Done when it reports the database in sync.
2. `generate`. Done when it exits 0.

## Amend a migration that has not shipped

1. Prove it has not shipped: `git branch -r --contains <commit that added it>`; the `production_branch` or `base_branch` the `role: vcs` config names appears → stop and write a forward migration instead. Done when only feature branches carry it; keep that list.
2. Edit its `migration.sql`; rename its directory when the name no longer fits — the directory name is the ledger's `migration_name`. Done when the file says what the schema needs.
3. Update the schema to match, and every TypedSQL file naming a changed column. Done when both agree with the migration.
4. Replay it on a local database rebuilt from a state before it, then § Apply pending migrations. Done when `migrate status` reports up to date. A database still holding the pre-edit row → `migrate dev` reports ``The migration `<name>` was modified after it was applied.`` (Prisma 6.19.0 schema engine).
5. `generate`, then § Create a migration step 3. Done when both exit 0.
6. Tell the owner of every branch step 1 listed to rebase. Done when each is told.

## Baseline a database built by push

- `migrate status` listing every migration pending, or `P3005` on deploy → the database never recorded its migrations.

1. Prove the live database matches the schema: `<runner> migrate diff --from-schema-datasource <schema> --to-schema-datamodel <schema> --exit-code`. Exit 0 → continue · exit 2 → stop: the database lacks what the printed SQL holds; push or apply it instead. A migration creating a view, function or trigger → find each in the database by name. Done when it exits 0 and every such object is found.
2. Record each directory under `migrations/` as applied, oldest first: `<runner> migrate resolve --applied <directory-name>`. Done when every directory is recorded.
3. `<runner> migrate status`. Done when it reports up to date.

## Recover from a wrong baseline

- `migrate status` up to date while the app misses a column or table → `resolve` recorded migrations the database never ran.

1. Run § Baseline step 1's diff, and look up by name each view, function or trigger the recorded migrations create; the diff's output and every object not found are what the database lacks. Done when the gap is in hand.
2. Host in `local_hosts` → § Push without a migration · any other host → stop and hand the user the diff. Done when the diff exits 0 or the user holds it.
3. Restart whatever reads the database. Done when it serves the column.

## SQL Prisma cannot express

- Views, triggers, functions, extensions, grants, partial-index predicates, generated columns and `CREATE INDEX CONCURRENTLY` → the change also edits the schema → § Create a migration step 1, then add the SQL to its `migration.sql`, a drop before the statement it blocks and the re-create after · SQL alone → `migrations/<UTC YYYYMMDDHHMMSS>_<name>/migration.sql` holding it, the layout `migrate dev --create-only` writes.
- `CREATE INDEX CONCURRENTLY` ships alone in its own migration file.
- Never apply such DDL to a database directly: it exists there and nowhere the migrations folder builds.

## Rename a field

- A field renamed in the schema generates an `ADD` and a `DROP`, losing the column's data → keep the column with `@map("<column>")` (`@@map` for a model's table), or edit the generated SQL to `ALTER TABLE … RENAME COLUMN`.
