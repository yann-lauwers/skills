# Transactions — which form, and the 5-second wall

Choosing between the array and interactive forms of `$transaction`, and keeping external calls out of the one that times out. Read before wrapping writes in a transaction, or when one failed with "Transaction already closed".

## Form selection

| Situation | Use |
|---|---|
| Independent operations, no inter-dependency | Array form |
| Later step depends on an earlier result | Interactive form |
| External calls (email, HTTP) involved | Outside the transaction entirely |

```ts
// Array form — batched in one round trip
const [user, post] = await prisma.$transaction([
  prisma.user.update({ where: { id }, data: { name } }),
  prisma.post.create({ data: { title, authorId: id } }),
]);

// Interactive form — use the tx client only, never the outer prisma client
const post = await prisma.$transaction(async (tx) => {
  const user = await tx.user.findUniqueOrThrow({ where: { id } });
  if (user.role !== 'ADMIN') throw new Error('Forbidden');
  return tx.post.create({ data: { title, authorId: user.id } });
});
```

## The interactive form times out after 5 seconds

An external call inside the callback blows the default budget and the transaction closes under it.

```ts
// BAD: external call inside transaction exceeds 5s default → "Transaction already closed"
await prisma.$transaction(async (tx) => {
  const user = await tx.user.findUniqueOrThrow({ where: { id } });
  await sendWelcomeEmail(user.email); // external call
  await tx.user.update({ where: { id }, data: { emailSent: true } });
});

// GOOD: external calls outside the transaction
const user = await prisma.user.findUniqueOrThrow({ where: { id } });
await sendWelcomeEmail(user.email);
await prisma.user.update({ where: { id }, data: { emailSent: true } });

// Only raise the timeout where bulk processing genuinely needs it
await prisma.$transaction(async (tx) => { ... }, { timeout: 30_000 });
```

## Use the tx client, not the outer one

Inside the interactive form, every call goes through `tx`. A call on the outer `prisma` client runs on a different connection, outside the transaction, and commits even when the transaction rolls back.
