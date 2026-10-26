# Debug

Narrows a failed Prisma command or a database that disagrees with the schema to its cause, then routes to the step that fixes it.

- A failed migrate, push or generate → find why the database state is wrong before reaching for `db push` or `migrate resolve`, which mask it.
- `migrate diff` against the live database is the ground truth for what the schema can express — `references/commands.md`.
- A `P1012` → match on its message, never its code: the code covers several causes.

## Symptoms

| Symptom | Cause | Fix |
| --- | --- | --- |
| `Unknown field` or `Property … does not exist` on the client in TypeScript | the client was not regenerated after the schema change | `generate` |
| `generate --sql` fails | the database lags the schema and its migrations, a TypedSQL file is wrong, or generate never reached the database | generate's output carries `Error: P1xxx` → that code's row; a code with no row → its message names the database, role or credential to fix in the env file the schema reads · `Errors while reading sql files` → fix the file and line it prints · otherwise the database lags: `migrate status` and `migrate diff` against it (`references/commands.md`) · another owner's database → leave it and report the lag · the schema still being edited → expected, continue the edit · the edit done → bring that database to its migrations and this schema (`cookbook/migrate.md`, through SKILL.md § Before a write), then `generate --sql` |
| `P1001` Can't reach database server | the database is down, or the URL names another host | `pg_isready -h <host> -p <port>`; the host comes from SKILL.md § Before a write |
| `P1003` Database … does not exist | the env file names a wrong database, or it was never created | a wrong name → fix the env file · never created → `cookbook/migrate.md` § Apply pending migrations, through SKILL.md § Before a write |
| `P1010` User was denied access | the role lacks a grant on that database | that database's owner grants it; never another role's credential |
| `P1012` `Environment variable not found` | the env file the schema reads is absent, or the change introduced the reference | populate that env file · the change introduced it → fix the schema |
| `P1012` `missing an opposite relation field`, or `Argument "url" is missing` | a schema defect | fix the schema |
| `P3005` The database schema is not empty | deploying to a database built by push | `cookbook/migrate.md` § Baseline a database built by push |
| `P3006` Migration failed to apply cleanly to the shadow database | that migration's SQL fails on replay | read the inner error it prints; fix that migration's SQL |
| `P3009` migrate found failed migrations, or `P3018` A migration failed to apply | a migration stopped partway | read the failed row in `_prisma_migrations` and the database's state; finish or undo its statements, then `migrate resolve --applied <name>` or `--rolled-back <name>` |
| `P3014` could not create the shadow database | the database user may not create databases | point the shadow URL at a database it may use |
| `P3015` Could not find the migration file | a migration directory lost its `migration.sql` | restore it from git, or delete the directory |
| `You must pass the --shadow-database-url if you want to diff a migrations directory.` | a major-6 diff over a migrations folder with no shadow URL | `cookbook/migrate.md` § Create a migration step 3 |
| ``The migration `<name>` was modified after it was applied.`` | a migration's file changed after a database applied it | not shipped → `cookbook/migrate.md` § Amend a migration that has not shipped · shipped → restore the file from git and write a forward migration |
| `migrate status` lists every migration pending | the database was built by push, its ledger empty | `cookbook/migrate.md` § Baseline a database built by push |
| `migrate status` up to date, the app missing a column | `resolve` recorded migrations the database never ran | `cookbook/migrate.md` § Recover from a wrong baseline |
| the schema drifted after a push | a push writes no migration | `cookbook/migrate.md` § Create a migration |
| `db execute` succeeds and prints nothing | it reports success or failure only | read rows through the generated client — `references/commands.md` |
| `db push` fails on a foreign key over an empty table | orphaned rows in an implicit many-to-many join table (`_<A>To<B>`) a table rename left | delete the orphans through the client's `$executeRaw`, then push |
| a push or migrate succeeds and the app still misses the change | the CLI reads the URL `references/commands.md` names; the app reads its own `DATABASE_URL` | compare the host each resolves, never by printing either URL |

## Error code ranges

| Range | Raised by |
| --- | --- |
| `P1xxx` | any command: connection, schema validation |
| `P2xxx` | Prisma Client's query engine |
| `P3xxx` | Prisma Migrate's schema engine |
| `P4xxx` | `db pull` |

- Codes and message texts: prisma.io v6 error reference; the two backticked refusals above: the Prisma 6.19.0 schema engine.
