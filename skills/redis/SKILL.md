---
name: redis
description: "Inspects a local Redis instance — connecting with `redis-cli`, finding, reading and watching keys — and names a new key by the convention the project's config declares. Use on 'inspect redis', 'redis-cli', 'check the cache', 'watch a redis key', 'name a redis key'. Also fires before `redis-cli`, `--scan`, `GET`, `TTL` or `MONITOR` runs against an instance, and when a new key is named in code. Not for designing a key, a cache-invalidation rule, a lock or a limiter — /redis-patterns ."
user-invocable: false
---

# Redis

## Project config

- Read the merged config first: `~/.claude/skills/agents-config/scripts/agents-config get redis <key> --root "$CLAUDE_PROJECT_DIR"`.
- Read the project file's body for the repo's own rules.
- No `docs/agents/integrations/redis.md` in the repo → ask the user; on their yes, write it through `references/setup.md`, then continue.
- No `key_pattern` → derive it from the live keys (`redis-cli --scan`) and state the convention inferred.

| Key | What it answers |
| --- | --- |
| `connection` | a `redis://host:port` URI, only where the instance is not on `127.0.0.1:6379` |
| `container` | the Docker container the instance runs in, where it runs in one |
| `secret` | the vault item holding the password; `null` → no auth |
| `key_pattern` | the segment order new keys follow |

## Connecting

- No `connection` → `redis-cli` with no host flags, which reaches `127.0.0.1:6379`.
- A `connection` value → `redis-cli -u <connection>`; `-u` refuses a value without the `redis://` scheme.
- A `secret` → `keyless run -s REDISCLI_AUTH=<SECRET> -- redis-cli …`, `<SECRET>` being `secret` uppercased, every non-alphanumeric as `_`.
- No `redis-cli` on the host, or the port unpublished → `docker exec <container> redis-cli …`.
