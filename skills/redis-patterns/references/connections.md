# Connections and the instance

Sizing the pool, choosing eviction, and what shares an instance. Read when sizing a pool, choosing an eviction policy, or deciding what shares an instance.

## Pool

One pool per process, built at startup, sized to the process's concurrency — a request-per-thread server needs roughly its thread count, an async one its in-flight ceiling. Set a connect timeout and a per-command timeout explicitly; a client whose default for either is none — redis-py for both — stalls every request behind a dead instance instead of failing one. A blocking consumer — `SUBSCRIBE`, `XREADGROUP … BLOCK`, `BLPOP` — holds its connection for its lifetime and takes one outside the request pool.

Cluster and Sentinel clients are the library's own; take their construction from its documentation. In Cluster mode a multi-key command or script touches one hash slot only, so keys that must be operated on together share a `{hash-tag}`, and numbered databases do not exist.

## Eviction

`maxmemory-policy` in `redis.conf`:

| Policy | Take it for |
| --- | --- |
| `allkeys-lru` | A pure cache |
| `allkeys-lfu` | A cache with a skewed hot set |
| `volatile-lru` / `volatile-ttl` | A mixed store where only TTL'd keys may go |
| `noeviction` | A queue, a lock, anything whose loss is a defect — writes fail loudly when full |

## What shares an instance

A cache and a queue on one instance share one `maxmemory` and one eviction policy, so the cache's eviction can drop queue entries, or the queue's `noeviction` can fail cache writes. Numbered databases separate the keyspace and nothing else. Anything whose loss is a defect takes its own instance.
