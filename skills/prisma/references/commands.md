# Commands

What each verb reads and writes. Flags are major 6's; SKILL.md § Version carries major 7's.

| Verb | Reads | Writes |
| --- | --- | --- |
| `migrate status` | the migrations folder and the `_prisma_migrations` ledger | nothing; never compares the live schema |
| `migrate diff` | any two sources: the live database, a schema file, a migrations folder through a shadow database | nothing; `--script` renders the difference as SQL, `--exit-code` exits 0 when empty, 2 when not, 1 on error; it compares only what the schema can express, never a view, function or trigger a migration's SQL creates |
| `migrate resolve --applied <name>` · `--rolled-back <name>` | the ledger | one ledger row; runs none of the migration's SQL |
| `migrate deploy` | the migrations folder | pending migrations, in order; checks no drift, generates nothing, needs no shadow database |
| `migrate dev` | the migrations folder, replayed into a shadow database to find drift | pending migrations, then a new one; `--create-only` leaves the new one unapplied |
| `db push` | the schema | the database's schema; no migration file, no ledger row |
| `db execute` | a SQL script | the database; prints success or failure, never a query's rows |
| `generate --sql` | the schema, every TypedSQL file, and the live database; each file is type-checked against it | the generated client and its typed SQL module; without `--sql` the module stays stale |

- Every verb reaching the live database reads `directUrl` when set, else `url` (major 6; major 7 → SKILL.md § Version).
- `migrate resolve --applied` only once `migrate diff` proves the database already holds that migration's changes, and each view, function or trigger it creates is found in the database by name.
- Rows for a debugging read → the generated client, from `package_dir`:

```bash
node -e "
const { PrismaClient } = require('<generator output>');
const p = new PrismaClient();
p.<model>.findMany({ take: 3 }).then(r => console.log(JSON.stringify(r, null, 2))).finally(() => p.\$disconnect());
"
```

- Sources: Prisma 6.19.0 `-h` for each verb; prisma.io v6 CLI reference for `migrate deploy`; prisma.io v6 TypedSQL docs for the live-database requirement; Prisma 6.19.0 `generate --sql`, `migrate status`, `migrate diff --from-schema-datasource` and `db execute --schema`, measured 2026-10-02 against a `url` and a `directUrl` naming different databases, for the URL each reads.
