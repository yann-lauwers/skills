---
name: database-migrations
description: "Plans and writes a zero-downtime schema migration — expand, backfill, switch and contract as separate migrations, batched backfills, the lock each statement takes, whether each step reverses. Any server database and tool; statement forms are PostgreSQL's. Use on 'add a column', 'backfill this table', 'drop the old column', 'rename this column', 'add an index', or a `CREATE TABLE`, `ALTER TABLE`, `CREATE INDEX` or large `UPDATE` going into a migration file. Not for on-device SQLite — /sqlite-patterns ; not for index or type choice — /postgres-patterns ; not for Prisma's query API — /prisma-patterns — or CLI — /prisma ."
metadata:
  origin: ECC
  source: https://github.com/affaan-m/ECC/blob/main/skills/database-migrations/SKILL.md
---

# Database Migrations

Router for schema change against a live database: which act a statement belongs to, the PostgreSQL form that takes no lock, and the shapes that fail.

Fires on the act, not the word: creating or altering a table, adding or dropping a column or an index, writing a backfill, or setting migration tooling up in a new repo — on any server database; the DDL rows are PostgreSQL's. A change reviewed rather than written enters through the same table.

## The four acts

A schema change on any server store lands in four acts, in this order, each shipped before the next begins; the statements below are PostgreSQL's:

- expand — the new shape, additive only: nullable, defaulted, or a new table
- backfill — the data, in bounded batches
- switch — the code that reads and writes the new shape
- contract — the old shape dropped, once nothing reads it

- A destructive step — a drop, a rename, a narrowed type, a constraint an existing row could violate — never ships with the code that needs the new shape.
- A rename is an expand plus a contract, never one statement.
- Acts collapsed into fewer → say which act absorbed which, and why the readers in between are safe.
- Every migration states whether it is reversible; one that is not names its recovery.
- A backfill over a table large enough to hold a lock names its batch size and its stopping condition.

## Before acting

Match the work against the routing table, read the matched `references/*.md`, then write the migration. A change touching several acts reads one file per act — the expand statement and the contract statement are different rows.

## Routing table

| Intent | Read |
| --- | --- |
| IF deciding how a change splits into migrations, or what has to ship before what | THEN `references/planning.md` |
| IF writing the DDL or the backfill itself — a column, an index, a rename, a drop, a large `UPDATE` | THEN `references/postgres-ddl.md` |
| IF driving Prisma — generating, deploying, or hand-writing SQL Prisma cannot express | THEN /prisma |
| IF the repo runs Drizzle or Kysely rather than Prisma | THEN `references/typescript-alternatives.md` |
| IF the server is not PostgreSQL, or the repo runs Alembic | THEN § The four acts, with the statement forms from that engine's own docs |
| IF reviewing a migration someone wrote, or one behaved badly in production | THEN `references/anti-patterns.md` |
| IF the request matches none of the above | THEN `references/planning.md`, say which row was closest |

## Non-negotiables

1. Every change is a migration file — production schemas are never altered by hand.
2. Production is forward-only: a rollback is a new forward migration, never an edit to one that has run.
3. DDL and DML ship in separate migrations.
4. A migration is tested against production-sized data before it is applied; one that is fine on 100 rows locks on 10M.
5. A deployed migration is immutable.
6. A push lands only on a database nobody else uses, and the change ships as a migration proved to reproduce the schema.
7. A migration no deploy branch contains is amended in place and replayed from a state before it; every branch carrying it rebases.
