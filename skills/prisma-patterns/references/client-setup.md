# Client setup — version, singleton, connection pool

Which Prisma shape this install is on, how the client is instantiated exactly once, and how the pool is capped so a serverless runtime does not exhaust the database. Read before writing `new PrismaClient()`, or when connections run out under load.

## Version check

The API surface moved across major releases, so the install decides which patterns apply: the version /prisma derives.

What differs across versions:

- `relationJoins` loads relations by JOIN rather than by separate queries — faster, but it can explode rows on a large 1:N relation or a deep `include`. Benchmark both.
- The `omit` field modifier and the `prisma.$extends` Client Extensions API were added.
- Newer installs: the package may be named `prisma` rather than `@prisma/client`; `PrismaClient` may require a driver adapter (`@prisma/adapter-pg`); `datasource.url` may live in `prisma.config.ts` rather than `schema.prisma`.

## Singleton

Each `PrismaClient` opens its own connection pool. Instantiate once.

```ts
// lib/prisma.ts

// Option A — adapter-based initialization (required by newer Prisma installs)
import { PrismaClient } from '@prisma/client'; // or the generated client path for this setup
import { PrismaPg } from '@prisma/adapter-pg';

function createPrismaClient() {
  const adapter = new PrismaPg({
    connectionString: process.env.DATABASE_URL!,
  });
  return new PrismaClient({
    adapter,
    log: process.env.NODE_ENV === 'development' ? ['query', 'error'] : ['error'],
  });
}

const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient };

export const prisma = globalForPrisma.prisma ?? createPrismaClient();

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;

// Option B — direct initialization (older installs, no adapter needed)
// import { PrismaClient } from '@prisma/client';
// export const prisma = globalForPrisma.prisma ?? new PrismaClient({ ... });
```

Option A where the constructor demands an `adapter` argument, Option B where `new PrismaClient()` compiles with no arguments. The compiler settles it — do not guess from the version number.

The `globalThis` assignment is what prevents duplicate instances across a hot reload (Next.js, nodemon, ts-node-dev), which is the usual source of a connection count that climbs while nothing else changed.

## Connection pool on serverless

Cap the pool to one connection per instance. Embed the params in `DATABASE_URL` — concatenating them in code breaks the moment the URL already carries a query string (`?schema=public`).

```bash
# .env — embed params in the URL
DATABASE_URL="postgresql://user:pass@host/db?connection_limit=1&pool_timeout=20"

# With an external pooler (PgBouncer, Supabase pooler)
DATABASE_URL="postgresql://user:pass@host/db?pgbouncer=true&connection_limit=1"
```

```ts
// Vercel, AWS Lambda and similar runtimes: pool capped to 1 per instance,
// connection_limit and pool_timeout carried by DATABASE_URL.

// Adapter-based setup:
import { PrismaClient } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';

const prisma = new PrismaClient({
  adapter: new PrismaPg({ connectionString: process.env.DATABASE_URL }),
});

// Direct setup (install that needs no adapter):
// const prisma = new PrismaClient();
```
