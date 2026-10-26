# Rate limiting

How a limit counts, and which counter shape holds it. Read when limiting how often a caller may do something.

| Shape | Take it when | How |
| --- | --- | --- |
| Fixed window | Low traffic, a burst at the window edge is acceptable | A key carrying the caller and `now // window` as its last segment; `INCR` and `EXPIRE window` in one `MULTI`/`EXEC` block; limited when the count exceeds the limit. The window number in the key is what makes the counter reset; `EXPIRE` only garbage-collects it, and a key without the window number never resets |
| Sliding window | The limit has to hold at every instant — per-user throttling | A sorted set of request timestamps, trimmed and counted in one Lua script |

Fixed window allows up to twice the limit across a window boundary; that is what sliding window buys.

## The sliding-window script

The script is the atomic unit: trim, count and add in two round trips is a race that admits over the limit.

```lua
local key, now, window, limit, nonce = KEYS[1], tonumber(ARGV[1]), tonumber(ARGV[2]), tonumber(ARGV[3]), ARGV[4]
redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
if redis.call('ZCARD', key) < limit then
  redis.call('ZADD', key, now, now .. '-' .. nonce)
  redis.call('EXPIRE', key, math.ceil(window / 1000))
  return 1
end
return 0
```

`now` and `window` are milliseconds; `EXPIRE` takes seconds, hence the division. The member is `now-nonce` rather than `now`, with the nonce supplied by the caller: two requests in the same millisecond with the same member collapse into one `ZADD` and the second is never counted. Every key the script touches is in `KEYS`: on Cluster a script reaching a key outside them fails with a cross-slot error. Load the script once at startup and call it by SHA rather than sending its body per call.
