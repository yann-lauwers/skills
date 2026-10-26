---
name: redis-patterns
description: "Designs a Redis key before it is written — structure and TTL, a cache and its invalidation, a lock, a rate limiter, a pub/sub channel or Stream consumer — and sizes the connection pool and eviction policy behind it. Use on 'add a cache', 'rate limit this endpoint', 'distributed lock', 'cache invalidation', 'hash or string', or code calling `SETEX`, `SET NX`, `INCR`, `XADD`, `XREADGROUP` or `PUBLISH`. Not for naming a key by project convention or inspecting an instance — /redis ; not for `X-RateLimit-*` headers — /api-design ."
metadata:
  origin: ECC
  source: https://github.com/affaan-m/ECC/blob/main/skills/redis-patterns/SKILL.md
---

# Redis Patterns

Router over the design decisions taken before a Redis key exists — which structure holds it, how it goes stale, who may hold a lock, how a limit counts, whether a message may be lost, and how many connections sit behind it. Two premises hold across every reference: every cache, counter, session, token and lock key carries a TTL, while a key that holds the work itself rather than a copy of it — a Stream used as a queue — carries none, is capped by `MAXLEN` and sits on a `noeviction` instance; and a multi-step operation is atomic only inside one Lua script or one `MULTI`/`EXEC` block — a pipeline alone batches and is not atomic, and two round trips are a race. The client library's own calls and options are its documentation's, not this skill's.

## Routing table

| Intent | Read |
| --- | --- |
| IF caching a value, invalidating one, or a cached value is stale or stampeded | THEN `references/caching.md` |
| IF limiting how often a caller may do something | THEN `references/rate-limiting.md` |
| IF one worker at a time may hold a resource | THEN `references/locks.md` |
| IF fanning an event out to consumers, or queueing work that must not be lost | THEN `references/messaging.md` |
| IF choosing a structure or picking its TTL — the key's name follows the convention /redis resolves | THEN `references/key-design.md` |
| IF sizing a pool, choosing an eviction policy, or deciding what shares an instance | THEN `references/connections.md` |
| IF naming a key by the project's convention, reading, scanning or watching keys on a running instance, or resolving a project's connection target | THEN /redis |
| IF the request matches none of the above | THEN `references/key-design.md`, say which row was closest |

## Done when

The key's structure, its name by the convention /redis resolves, its TTL or the reason it has none, and the atomic unit that writes it are each stated in one line, the reference for the matched intent has been read, and the trap it names for that intent is answered in the code rather than left to a comment.
