---
name: prisma
description: "Confirms the database host before a Prisma schema write. Use before any `prisma migrate`, `db push` or `db execute` command, or a package script wrapping one; also on `migrate resolve`, `CREATE INDEX CONCURRENTLY` in a migration, or a failed `generate --sql`."
user-invocable: false
---

# Prisma

## Before a write

- A write — `migrate deploy`, `migrate dev`, `migrate reset`, `migrate resolve`, `db push`, `db execute`, or a script wrapping one.

1. `prisma migrate status`; read `Datasource "<name>": … at "<host>:<port>"`. It prints before connecting and names `directUrl`'s host when the schema sets one. Done when the host is in hand.
2. `localhost` or `127.0.0.1` → run the write · any other host → print the host, the port and the exact command, then wait for the user's yes. Done when the write ran or the user declined.

- Prisma's own agent guard stops only `migrate reset` and `db push --force-reset`; `db push --accept-data-loss` drops the data unasked → step 2's ask on every host, saying it destroys data.

## Traps

| On | Read |
| --- | --- |
| `migrate resolve`, a baseline, or `migrate status` up to date while the app misses a column | `references/traps.md` § The ledger |
| `CREATE INDEX CONCURRENTLY` | `references/traps.md` § Concurrent index |
| a failed `generate --sql` | `references/traps.md` § TypedSQL |
