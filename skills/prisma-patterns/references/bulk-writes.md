# Bulk writes — `updateMany`, `deleteMany`, and what they skip

The three ways a bulk write does something other than what the call site reads like: it returns a count instead of rows, it leaves `@updatedAt` stale, and it wipes the table when `where` is omitted. Read before any `updateMany` or `deleteMany`.

## `updateMany` returns a count, not records

```ts
// BAD: result is { count: 2 } — users[0] is undefined
const users = await prisma.user.updateMany({ where: { role: 'GUEST' }, data: { role: 'USER' } });

// GOOD: capture IDs first, then update, then fetch only the affected rows
const targets = await prisma.user.findMany({
  where: { role: 'GUEST' },
  select: { id: true },
});
const ids = targets.map((u) => u.id);
await prisma.user.updateMany({ where: { id: { in: ids } }, data: { role: 'USER' } });
const updated = await prisma.user.findMany({ where: { id: { in: ids } } });
```

`deleteMany` behaves the same way — `{ count: n }`, never the deleted rows.

## `@updatedAt` does not fire on `updateMany`

Prisma sets it on `update` and `upsert` only. A bulk write leaves the old timestamp in place.

```ts
// BAD: updatedAt stays at its old value
await prisma.post.updateMany({ where: { authorId }, data: { published: true } });

// GOOD
await prisma.post.updateMany({
  where: { authorId },
  data: { published: true, updatedAt: new Date() },
});
```

## `deleteMany` without `where` deletes every row

```ts
// BAD: silently wipes the table
await prisma.post.deleteMany();

// GOOD
await prisma.post.deleteMany({ where: { authorId: userId } });
```

Every `deleteMany` carries a `where`. The empty-argument form is valid TypeScript and valid Prisma, so nothing upstream of production reports it.
