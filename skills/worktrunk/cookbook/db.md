# DB — a nexus tree's own Postgres

Chooses between the `db` verbs and the `WT_DB` modes, and carries the traps behind them. `nexus-wt usage` lists the verbs; the reseed-or-restore choice is the judgment.

- Each nexus tree gets a socket-only Postgres cluster with no TCP port — 17 on macOS, 18 on Linux, `bin/lib/platform.sh` picking the binaries: data `~/.local/share/wt-pg/<12-hex>/data`, socket `~/.local/run/pg/<12-hex>/`.
- `WT_DB` on the create picks it: `own` (default) · `stack:<branch>` shares that tree's cluster (`cookbook/stack.md`) · `remote` keeps the main checkout's URL and creates no cluster, and every `db` verb then refuses.
- `WT_SKIP=db` on the create skips creating and seeding it.

## Connect and query

- `git wt -C <tree> db url` prints the URL; Postgres runs only while a dev stack, a `db start` or a connected client holds it.
- Stack down → `psql "$(git wt -C <tree> db start)" -P pager=off -c '<SQL>'`, then `git wt -C <tree> db stop`; the same bracket holds for Prisma Studio and a migration. A forgotten `db start` keeps it up: `git wt -C <tree> doctor` lists the holders and marks stale ones.
- The URL carries `?host=<socket dir>` → never `-p` or `-h localhost`: a default-port probe finds nothing and reads as "no database exists".
- Quote identifiers Postgres would otherwise fold to lowercase: `"Message"`, `"createdAt"`.
- A tree's own database is the read target, never the remote DB.

## Reset, reseed, restore

- `db reset` and `db reseed` do the same thing, with no prompt: drop and recreate the database, then restore the cached seed dump `~/.local/share/nexus/seed.dump`, re-dumped first from the main checkout's `DIRECT_URL` when older than a day; with no dump at all, `prisma db push` from the branch's schema plus `scripts/db/seed-agent.mjs` → ask before wiping data the user may still want.
- `db restore <dump>` replaces the database with a `pg_dump -Fc` file.
- All three run only on an `own` tree; a stacked tree is reset from its owner.
- A restored dump leaves the database at the DUMP's schema, never the branch's → apply the branch's own migrations afterwards, with the project's own migration command — the one that would apply them on a fresh checkout.
- The dump carries the remote DB's migration ledger, so a migration still in flight locally appears in neither ledger nor schema, and surfaces later as a missing column in whatever first touches it — a codegen run, a query, a spec.

## Troubleshooting

- `initdb` missing → run the install command the error prints; Linux stays on 18, which Ubuntu 26.04 ships in place of 17.
- A cluster that will not start with many running → macOS allows 32 shared-memory segments, one per running Postgres: `ipcs -m | grep -c '^m'`, and stop the idle ones with `db stop` or `dev down`.
- Seeding prints platform-schema warnings or `supabase_vault` restore errors → benign; the provider's internal schemas don't exist in local Postgres.

## Done

A `db` task closes on the verb named rather than assumed, and — after any reseed or restore — on the branch's own migrations replayed; a restored dump with nothing after it is a schema behind, and nothing downstream says so.
