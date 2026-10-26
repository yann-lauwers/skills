# Caching

Which caching shape to take and how the value goes stale. Read when adding a cache, invalidating one, or a cached value is stale or stampeded.

## Which shape

| Shape | Take it when | The trap |
| --- | --- | --- |
| Cache-aside — read the key, on a miss read the source and `SETEX` it | Read-heavy, slight staleness tolerated — the default | Every miss hits the source; see stampede below |
| Delete-on-write — write the source, then `DEL` the key | A write must be visible on the next read | Deleting, never overwriting: two writers overwriting in a different order than they committed leave the cache wrong until TTL, and a delete costs one miss |
| Write-through — write the source, then `SETEX` the new value | Only when the value is expensive to rebuild and a single writer owns it | The reorder race above |

Key on every input that changes the value — for a response cache, the request parameters that reach the query, never the whole URL with its noise.

## Invalidating a group

One key per value plus a tag set keyed by the group: `SADD <tag key> <member key>` in the same `MULTI`/`EXEC` block as the `SETEX`, and invalidation is `SMEMBERS` then `DEL` of the members and the tag. The tag's TTL is at least the longest member TTL, refreshed on every add, or the tag expires while its members live on and the group can no longer be cleared.

## Stampede

A cold or just-expired hot key sends every concurrent reader to the source at once. Two answers, both in code rather than a comment:

- A per-key lock — `references/locks.md` — so one reader rebuilds while the rest wait and re-read. An in-process mutex covers one process only; a multi-process deployment takes the Redis lock.
- Probabilistic early expiry: each reader rebuilds with a small chance that grows as the TTL runs out, so the rebuild lands before the miss.
