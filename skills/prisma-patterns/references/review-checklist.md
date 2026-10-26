# Review checklist — what to check before Prisma code ships

The one-screen pass over a diff or an existing service: each rule with the failure it prevents, and the file carrying the worked form. Read when reviewing Prisma code, auditing a service, or when a request matched no other route.

| Rule | Reason | Depth |
|---|---|---|
| `migrate deploy` in CI/CD, `migrate dev` only locally | `migrate dev` is interactive and builds migrations against a shadow database | /prisma |
| Map entities to response DTOs | Prevents leaking internal fields | `queries.md` |
| Catch `PrismaClientKnownRequestError` at the service boundary | Translates to domain errors | `errors.md` |
| Prefer `*OrThrow` over a manual null check | Raises `P2025` automatically; `findFirstOrThrow` where the filter is not a unique constraint | `errors.md` |
| `connection_limit=1` + an external pooler on serverless | Prevents connection exhaustion | `client-setup.md` |
| Always provide `where` on `deleteMany` | Prevents an accidental table wipe | `bulk-writes.md` |
| Set `updatedAt: new Date()` manually in `updateMany` | `@updatedAt` skips bulk writes | `bulk-writes.md` |
| One `PrismaClient`, held on `globalThis` in development | Each instance opens its own pool; hot reload multiplies them | `client-setup.md` |
| A unique field as the secondary `orderBy` on any cursor page | Rows sharing a timestamp shuffle between pages | `queries.md` |
| `@@index` on every foreign key and every `WHERE` / `ORDER BY` column | Sequential scans on the queries that matter | `schema-design.md` |
| External calls outside `$transaction` | The interactive form closes after 5s | `transactions.md` |
| Explicit `deletedAt: null` at each call site, no middleware | Middleware hides the filter from the reader and the yann:debugger | `queries.md` |
