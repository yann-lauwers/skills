---
name: redis
description: "Connects `redis-cli` to the project's Redis — host, auth, container — and names a new key by the project's key pattern. Use to inspect a key, its TTL or live traffic, or to check what the cache holds. Also fires on the ACT — before `redis-cli` runs, and when code introduces a new Redis key."
user-invocable: false
---

# Redis

Needs: `REDISCLI_AUTH` — the instance's password, where it has one; `redis-cli` reads it itself, and unset means no auth.

## The project's Redis

- Connection, container, key pattern and the repo's own rules → as the project's instructions state them; none stated → ask the user.
- No key pattern stated → derive it from the live keys (`redis-cli --scan`) and state the convention inferred.

| Fact | What it answers |
| --- | --- |
| connection | a `redis://host:port` URI, only where the instance is not on `127.0.0.1:6379` |
| container | the Docker container the instance runs in, where it runs in one |
| key pattern | the segment order new keys follow |

## Connecting

- No connection → `redis-cli` with no host flags, which reaches `127.0.0.1:6379`.
- A connection → `redis-cli -u <connection>`; `-u` refuses a value without the `redis://` scheme.
- No `redis-cli` on the host, or the port unpublished → `docker exec <container> redis-cli …`.
