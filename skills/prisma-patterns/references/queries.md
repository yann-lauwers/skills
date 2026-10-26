# Reads — projection, relations, pagination, soft delete

How a read is shaped: which fields cross the wire, how relations are loaded without N+1, how a feed pages, and how soft-deleted rows stay out of the result. Read before writing or reviewing a `findMany` / `findUnique` / `findFirst`.

## `include` vs `select`

| | `include` | `select` |
|---|---|---|
| Returns | All scalar fields + specified relations | Only specified fields |
| Use when | Most fields plus a relation are needed | Hot paths, large tables, avoiding over-fetch |
| Performance | May over-fetch on wide tables | Minimal payload, faster on large datasets |
| Relation loading | Uses JOIN where `relationJoins` is on | Same |

```ts
// include — all columns + relation
const user = await prisma.user.findUnique({
  where: { id },
  include: { posts: { select: { id: true, title: true } } },
});

// select — explicit allowlist
const user = await prisma.user.findUnique({
  where: { id },
  select: { id: true, email: true, name: true },
});
```

## Never return a raw entity

Map to a response DTO so the exposed field set is explicit.

```ts
// BAD: leaks passwordHash, deletedAt, internal fields
return await prisma.user.findUniqueOrThrow({ where: { id } });

// GOOD: explicit DTO mapping
const user = await prisma.user.findUniqueOrThrow({ where: { id } });
return { id: user.id, name: user.name, email: user.email };
```

## N+1

Loading a relation inside a loop issues one query per row.

```ts
// BAD: N+1 — one extra query per user
const users = await prisma.user.findMany();
for (const user of users) {
  const posts = await prisma.post.findMany({ where: { authorId: user.id } });
}

// GOOD: single query
const users = await prisma.user.findMany({ include: { posts: true } });
```

With `relationJoins` on, the `include` form resolves in one JOIN — which can explode the result set on a large 1:N relation or a deep `include`, since every parent row repeats per child. Benchmark both shapes where a relation can return many rows per parent.

## Cursor pagination

Preferred for feeds and large datasets.

```ts
async function getPosts(cursor?: string, limit = 20) {
  const items = await prisma.post.findMany({
    where: { published: true },
    orderBy: [
      { createdAt: 'desc' },
      { id: 'desc' }, // secondary sort prevents unstable pagination on duplicate timestamps
    ],
    take: limit + 1,
    ...(cursor && { cursor: { id: cursor }, skip: 1 }),
  });

  const hasNextPage = items.length > limit;
  if (hasNextPage) items.pop();

  return { items, nextCursor: hasNextPage ? items[items.length - 1].id : null };
}
```

Fetch `limit + 1` and pop — that is how `hasNextPage` is known without a second count query. Always carry a unique field (`id`) as a secondary `orderBy`, or rows sharing a timestamp shuffle between pages. Offset pagination is for admin tables where a user jumps to an arbitrary page, and nowhere else.

## Soft delete

Filter explicitly at each call site. Middleware hides the behaviour and is hard to debug.

```ts
const activeUsers = await prisma.user.findMany({ where: { deletedAt: null } });

await prisma.user.update({ where: { id }, data: { deletedAt: new Date() } });
await prisma.user.update({ where: { id }, data: { deletedAt: null } }); // restore
```

A soft-deleted row still exists, so `findUniqueOrThrow` returns it without error — `errors.md § Soft delete leaks through findUniqueOrThrow` carries the fix.
