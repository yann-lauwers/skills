# Errors — codes, boundaries, and the `*OrThrow` forms

Translating Prisma's error codes into domain errors at the service boundary, and choosing the `*OrThrow` variant that actually enforces the condition. Read when catching a Prisma error, or when a lookup returned a row it should not have.

## Catch at the service boundary

```ts
import { Prisma } from '@prisma/client'; // or the generated client path for this setup

try {
  await prisma.user.create({ data: { email } });
} catch (e) {
  if (e instanceof Prisma.PrismaClientKnownRequestError) {
    if (e.code === 'P2002') throw new ConflictError('Email already exists');
    if (e.code === 'P2025') throw new NotFoundError('Record not found');
    if (e.code === 'P2003') throw new BadRequestError('Referenced record does not exist');
  }
  throw e;
}
```

Common codes: `P2002` unique violation · `P2025` not found · `P2003` foreign key violation.

Translate at the service boundary and never let a raw Prisma message reach an API consumer — the message carries column names, constraint names and the failing values.

## Soft delete leaks through `findUniqueOrThrow`

`findUniqueOrThrow` raises `P2025` only when the row is absent from the database. A soft-deleted row is still there, so it comes back without error.

`findUniqueOrThrow` also demands a unique-constraint field in `where`, so adding `deletedAt: null` beside `id` fails to typecheck — `{ id, deletedAt }` is not a compound unique constraint. `findFirstOrThrow` takes arbitrary conditions and is the correct call.

```ts
// BAD: returns the soft-deleted user
const user = await prisma.user.findUniqueOrThrow({ where: { id } });

// BAD: Prisma type error — { id, deletedAt } is not a unique constraint
const user = await prisma.user.findUniqueOrThrow({ where: { id, deletedAt: null } });

// GOOD: findFirstOrThrow supports arbitrary where conditions
const user = await prisma.user.findFirstOrThrow({ where: { id, deletedAt: null } });
```

Prefer an `*OrThrow` method over a manual null check — `P2025` arrives for free and the happy path stays unbranched. Filtering on anything but a unique constraint means `findFirstOrThrow`.
