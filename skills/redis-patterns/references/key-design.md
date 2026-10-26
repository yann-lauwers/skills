# Key design

Which structure holds a value, and how long it lives. Read when choosing a structure or picking its TTL — and as the closest row for anything the table does not match.

## Structure

| Use case | Structure |
| --- | --- |
| One serialised value | String |
| A record read and written by field | Hash |
| Ranked scores, pagination by rank | Sorted set |
| Membership, exact unique count | Set |
| Approximate unique count at fixed memory | HyperLogLog |
| A capped recent-items feed | List |
| An event log with consumer groups | Stream |
| Counter, rate-limit bucket | String with `INCR` |

A Bloom filter is the RedisBloom module, not HyperLogLog: HyperLogLog counts distinct members and cannot answer whether one member is present.

A value over about 100KB is stored elsewhere and the key holds its reference; serialising and evicting large blobs is what makes an instance slow.

The key's name follows the project's own convention, which /redis resolves. Application code never enumerates keys with `KEYS`; it blocks the instance for the whole scan. `SCAN` with a cursor and a `MATCH` pattern is the enumeration.

## TTL

Every cache, counter, session, token and lock key carries one. A key without a TTL is a leak that shows up as memory pressure months later, and `volatile-*` eviction policies never touch it. The exception is a key that holds the work itself rather than a copy of it — a Stream used as a queue — which carries none and is bounded by `MAXLEN` on a `noeviction` instance instead (`references/messaging.md`, `references/connections.md`).

| Data | TTL |
| --- | --- |
| Session | 24h |
| API response cache | 5–15 min |
| Rate-limit bucket | the window length |
| Short-lived token | 5–10 min |
| Leaderboard | 1h–24h |
| Reference data | 1h–1 week |
