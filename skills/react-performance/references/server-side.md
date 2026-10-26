# Server-side cost — RSC, Server Actions, API routes

What a request costs on the server: auth on every action, per-request and cross-request caching, what crosses the serialization boundary, and what must never live at module scope.

## Authenticate Server Actions like API routes

Every `"use server"` function is a public endpoint. Authenticate AND authorize inside the action — never rely on the calling Client Component's gating.

```ts
"use server";
export async function deleteUser(formData: FormData) {
  const session = await getSession();
  if (!session?.user) throw new Error("Unauthorized");
  const targetId = String(formData.get("id"));
  if (session.user.role !== "admin" && session.user.id !== targetId) {
    throw new Error("Forbidden");
  }
  await db.user.delete({ where: { id: targetId } });
}
```

## `React.cache()` for per-request deduplication

```ts
import { cache } from "react";

export const getUser = cache(async (id: string) => {
  return db.user.findUnique({ where: { id } });
});
```

`React.cache` dedupes within a single request. Calling `getUser("1")` from three Server Components in the same render = one DB query.

## LRU cache for cross-request data

For data that does NOT change per request (config, lookup tables), cache outside React with an LRU cache, or the framework's cross-request cache — in Next.js, the one the installed version's docs give; where they live — /nextjs-patterns .

## Avoid duplicate serialization in RSC props

When a Server Component renders the same data into multiple Client Components, the data is serialized once per consumer. Lift the Client Component up and pass children.

## Hoist static I/O to module scope

```ts
// CORRECT — runs once at module load
const fontData = readFileSync(fontPath);

export async function Page() {
  return <Banner font={fontData} />;
}
```

## No mutable module-level state in RSC/SSR

Module state on the server is shared across all requests — a race condition between users. Use request-scoped storage (`headers()`, `cookies()`, async context) instead.

## Minimize data passed to Client Components

Only serialize what the Client needs. Strip fields, paginate, project columns at the DB layer.

## Parallelize nested fetches with Promise.all per item

```ts
const users = await getUsers();
const enriched = await Promise.all(
  users.map(async (u) => ({ ...u, posts: await getPostsFor(u.id) })),
);
```

## Use `after()` for non-blocking work

Next.js 15.1+ `after()` runs work after the response is sent — logging, cache warming, analytics.

```ts
import { after } from "next/server";
export async function GET() {
  const data = await getData();
  after(() => logAnalytics(data));
  return Response.json(data);
}
```
