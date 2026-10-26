---
name: prisma-patterns
description: "Writes and reviews Prisma ORM code in a TypeScript backend — models, relations, ids, indexes, `include` / `select` reads, cursor pagination, soft delete, transactions, `PrismaClient` setup, `P2002` / `P2025` / `P2003`. Use on 'add a model', 'write this query', 'wrap it in a transaction', 'paginate this', 'Transaction already closed', 'too many connections in serverless', or a `.prisma` file or `prisma.$transaction` under edit. Not for the Prisma CLI — /prisma ; not for a live schema change — /database-migrations ; not for the Nest service — /nestjs-patterns ."
paths:
  - "**/schema.prisma"
  - "**/*.prisma"
metadata:
  origin: ECC
  source: https://github.com/affaan-m/ECC/blob/main/skills/prisma-patterns/SKILL.md
---

# Prisma Patterns

Router over Prisma's production patterns and its non-obvious traps. Each intent pulls one reference; the traps live beside the pattern they break, so the file that answers "how do I bulk update" is the file carrying "updateMany returns a count".

Fires while designing or changing models and relations, writing queries, transactions or pagination, reaching for `updateMany` / `deleteMany` or any bulk op, implementing soft delete or multi-tenant row filtering, and deploying to a serverless runtime.

The API surface moved across major releases — package name, whether `PrismaClient` needs a driver adapter, where `datasource.url` lives, `relationJoins`, the `omit` field modifier, the Client Extensions API. `references/client-setup.md § Version check` settles which shape this install is on before any pattern is applied.

## Routing table

| Intent | Read |
| --- | --- |
| IF designing a model, choosing an id strategy, placing indexes, or adding a soft-delete column | THEN `references/schema-design.md` |
| IF writing a read — `include` vs `select`, relations in a loop, pagination, filtering soft-deleted rows, shaping an API response | THEN `references/queries.md` |
| IF wrapping writes in an interactive or array transaction, or one timed out with "Transaction already closed" | THEN `references/transactions.md` |
| IF instantiating `PrismaClient`, hitting duplicate instances on hot reload, or exhausting connections on a serverless runtime | THEN `references/client-setup.md` |
| IF catching a Prisma error, translating `P2002` / `P2025` / `P2003`, or choosing between `findUnique` and `findFirst` and their `*OrThrow` forms | THEN `references/errors.md` |
| IF calling `updateMany` or `deleteMany`, or a bulk write left `updatedAt` stale | THEN `references/bulk-writes.md` |
| IF creating, editing or deploying a migration, or running any Prisma CLI command | THEN /prisma |
| IF reviewing Prisma code before it ships, or auditing an existing service | THEN `references/review-checklist.md` |
| IF the request matches none of the above | THEN `references/review-checklist.md`, say which row was closest |

## Neighbouring skills

The NestJS service layer that wraps these calls is /nestjs-patterns ; multi-step migration planning against a live production database is /database-migrations , which owns the sequencing.
