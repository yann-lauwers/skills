# Migrations on a live table

Landing a schema change on a PostgreSQL table that already holds rows: which act a statement belongs to, the form that takes no lock, and the shapes that fail. Read before writing any `ALTER TABLE`, `CREATE INDEX`, rename, drop or large `UPDATE` into a migration file; a change touching several acts reads every section it touches.

## The four acts

A schema change lands in four acts, in this order, each shipped before the next begins:

- expand — the new shape, additive only: nullable, defaulted, or a new table
- backfill — the data, in bounded batches
- switch — the code that reads and writes the new shape
- contract — the old shape dropped, once nothing reads it

- A destructive step — a drop, a rename, a narrowed type, a constraint an existing row could violate — never ships with the code that needs the new shape.
- A rename is an expand plus a contract, never one statement.
- Acts collapsed into fewer → say which act absorbed which, and why the readers in between are safe.
- Every migration states whether it is reversible; one that is not names its recovery.
- A backfill over a table large enough to hold a lock names its batch size and its stopping condition.
- The server is not PostgreSQL, or the repo runs Alembic → these acts, with the statement forms from that engine's own docs.

## Non-negotiables

1. Every change is a migration file — production schemas are never altered by hand.
2. Production is forward-only: a rollback is a new forward migration, never an edit to one that has run.
3. DDL and DML ship in separate migrations.
4. A migration is tested against production-sized data before it is applied; one that is fine on 100 rows locks on 10M.
5. A deployed migration is immutable.
6. A push lands only on a database nobody else uses, and the change ships as a migration proved to reproduce the schema.
7. A migration no deploy branch contains is amended in place and replayed from a state before it; every branch carrying it rebases.

The tool driving the migration: Prisma → /prisma · Drizzle or Kysely → `references/drizzle-kysely.md`.

## The dual-write plan

The column exists in two shapes for as long as anything reads the old one, so the application writes both across the middle of the plan. Reading is what moves; writing is what waits.

```
Phase 1: EXPAND
  - Add new column/table (nullable or with default)
  - Deploy: app writes to BOTH old and new
  - Backfill existing data

Phase 2: MIGRATE
  - Deploy: app reads from NEW, writes to BOTH
  - Verify data consistency

Phase 3: CONTRACT
  - Deploy: app only uses NEW
  - Drop old column/table in separate migration
```

A rename is this plan and never one statement — § Renaming a column below carries the four steps as SQL.

## What that looks like on a calendar

```
Day 1: Migration adds new_status column (nullable)
Day 1: Deploy app v2 — writes to both status and new_status
Day 2: Run backfill migration for existing rows
Day 3: Deploy app v3 — reads from new_status only
Day 7: Migration drops old status column
```

The gaps carry the safety, not the ordering alone: the drop waits until no deploy in flight, no queued job and no long-running transaction still names the old column. Compressing Day 3 to Day 7 into one release is what turns a plan into an outage.

## Checklist before applying

1. The migration carries both UP and DOWN, or is marked irreversible with its recovery path written down.
2. No full table lock on a large table — concurrent forms only.
3. Every new column is nullable or has a default; `NOT NULL` without a default never lands on an existing table.
4. Indexes on existing tables are built concurrently, never inline.
5. The backfill is its own migration, separate from the DDL, with a stated batch size and stopping condition.
6. The whole plan was run against a copy of production data, at production size.
7. The rollback plan is documented.

## Adding a column

```sql
-- GOOD: Nullable column, no lock
ALTER TABLE users ADD COLUMN avatar_url TEXT;

-- GOOD: Column with default (Postgres 11+ is instant, no rewrite)
ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true;

-- BAD: NOT NULL without default on existing table (requires full rewrite)
ALTER TABLE users ADD COLUMN role TEXT NOT NULL;
-- This locks the table and rewrites every row
```

## Adding an index

```sql
-- BAD: Blocks writes on large tables
CREATE INDEX idx_users_email ON users (email);

-- GOOD: Non-blocking, allows concurrent writes
CREATE INDEX CONCURRENTLY idx_users_email ON users (email);
```

- `CREATE INDEX CONCURRENTLY` cannot run inside a transaction block → its own statement, outside `BEGIN` and outside any tool that wraps a migration in one.

Prisma's route for `CONCURRENTLY` is /prisma , `cookbook/migrate.md` § SQL Prisma cannot express.

## Renaming a column

A direct `RENAME` breaks every reader the instant it commits, so the rename is an expand plus a contract with a deploy between them.

```sql
-- Step 1: Add new column (migration 001)
ALTER TABLE users ADD COLUMN display_name TEXT;

-- Step 2: Backfill data (migration 002, data migration)
UPDATE users SET display_name = username WHERE display_name IS NULL;

-- Step 3: Update application code to read/write both columns
-- Deploy application changes

-- Step 4: Stop writing to old column, drop it (migration 003)
ALTER TABLE users DROP COLUMN username;
```

## Removing a column

```sql
-- Step 1: Remove all application references to the column
-- Step 2: Deploy application without the column reference
-- Step 3: Drop column in next migration
ALTER TABLE orders DROP COLUMN legacy_status;
```

The code goes first in every case: a column dropped while a running instance still selects it errors on that instance's next query, and the deploy order is the only thing preventing it.

## Backfilling a large table

One `UPDATE` over every row holds a lock for the whole run and blocks writers behind it. Batched, each transaction is short and the table stays writable between them; `SKIP LOCKED` steps over rows another transaction is already holding rather than queueing on them.

```sql
-- BAD: Updates all rows in one transaction (locks table)
UPDATE users SET normalized_email = LOWER(email);

-- GOOD: Batch update with progress
DO $$
DECLARE
  batch_size INT := 10000;
  rows_updated INT;
BEGIN
  LOOP
    UPDATE users
    SET normalized_email = LOWER(email)
    WHERE id IN (
      SELECT id FROM users
      WHERE normalized_email IS NULL
      LIMIT batch_size
      FOR UPDATE SKIP LOCKED
    );
    GET DIAGNOSTICS rows_updated = ROW_COUNT;
    RAISE NOTICE 'Updated % rows', rows_updated;
    EXIT WHEN rows_updated = 0;
    COMMIT;
  END LOOP;
END $$;
```

The stopping condition is the `EXIT WHEN` above — a backfill whose predicate does not narrow as it runs loops forever on the rows it keeps re-selecting.

## Anti-patterns

| Anti-Pattern | Why It Fails | Better Approach |
|-------------|-------------|-----------------|
| Manual SQL in production | No audit trail, unrepeatable | Always use migration files |
| Editing deployed migrations | Causes drift between environments | Create new migration instead |
| NOT NULL without default | Locks table, rewrites all rows | Add nullable, backfill, then add constraint |
| Inline index on large table | Blocks writes during build | CREATE INDEX CONCURRENTLY |
| Schema + data in one migration | Hard to rollback, long transactions | Separate migrations |
| Dropping column before removing code | Application errors on missing column | Remove code first, drop column next deploy |

Five of the six pass every test suite: the migration applies, the schema is correct afterwards, and the damage is a lock held or a drift opened rather than a wrong result. Reviewing the statement alone therefore catches none of them — what the review reads is the size of the table it runs against and the deploy standing between it and the code.
