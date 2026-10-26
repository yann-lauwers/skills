# Planning a schema change

How one schema change splits into migrations, what ships before what, and the checklist a migration passes before it is applied. Read before writing any statement; the statements themselves are `references/postgres-ddl.md`.

The act sequence — expand, backfill, switch, contract, each shipped before the next begins — holds whether the deploy is a fleet or a single process restarting. This file is what that sequence looks like on a real column: which deploy sits between two migrations, and what the application writes while both shapes exist.

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

A rename is this plan and never one statement — `references/postgres-ddl.md § Renaming a column` carries the four steps as SQL.

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
