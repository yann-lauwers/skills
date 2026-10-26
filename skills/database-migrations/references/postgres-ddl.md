# PostgreSQL statements and the locks they take

The statement per act — add a column, add an index, rename, drop, backfill at size — each with the form that takes no meaningful lock and the form that rewrites the table. Read while writing the SQL.

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
