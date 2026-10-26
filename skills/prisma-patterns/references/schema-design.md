# Schema design — ids, defaults, indexes

What a model declares at creation: which id strategy, which columns exist from day one, and which indexes carry the queries that will be written against it. Read before adding or reshaping a model.

## ID strategy

| Strategy | Use when | Avoid when |
|---|---|---|
| `@default(cuid())` | Default choice — URL-safe, sortable, no collisions | Sequential IDs needed for external systems |
| `@default(uuid())` | Interoperability with non-Prisma systems required | High-write tables (random UUIDs fragment B-tree indexes) |
| `@default(autoincrement())` | Internal join tables, audit logs | Public-facing IDs (exposes record count) |

## The default model shape

```prisma
model User {
  id        String    @id @default(cuid())
  email     String    @unique  // @unique already creates an index — no @@index needed
  name      String
  role      Role      @default(USER)
  posts     Post[]
  createdAt DateTime  @default(now())
  updatedAt DateTime  @updatedAt
  deletedAt DateTime?

  @@index([createdAt])
  @@index([deletedAt, createdAt]) // composite for soft-delete + sort queries
}
```

Add `@@index` on every foreign key and every column used in `WHERE` or `ORDER BY`.

Declare `deletedAt DateTime?` upfront where soft delete is a foreseeable requirement — adding it later takes a migration against a live table.

`updatedAt @updatedAt` is set by Prisma on `update` and `upsert` only. Bulk writes leave it stale: `bulk-writes.md § @updatedAt does not fire on updateMany`.

## Nullability, referential actions, enums

- `Type?` → nullable, no default · `Type? @default(x)` → nullable, new rows get `x` · `Type @default(x)` → `NOT NULL`, new rows get `x`.
- A relation with no `onDelete` → `Restrict` when required, `SetNull` when optional; `onUpdate` defaults to `Cascade` on both.
- An enum's values in application code → imported from the generated client, never hardcoded.
