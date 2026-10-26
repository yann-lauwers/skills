# Locks

One holder at a time for one resource. Read when one worker at a time may hold a resource, or a cache rebuild must run once.

Acquire with `SET <the lock's key, carrying the resource id> <token> NX PX <ttl>` where the token is a fresh UUID. Release only through a script that compares the token before deleting:

```lua
if redis.call('GET', KEYS[1]) == ARGV[1] then return redis.call('DEL', KEYS[1]) end
return 0
```

A plain `DEL` on release deletes a lock another worker now holds whenever this one ran past its TTL — the compare is the whole point, and `GET` then `DEL` as two calls reopens the same window.

The TTL exceeds the longest the job can run, and the release sits in a `finally`. A job that can outrun any TTL needs a heartbeat that extends the lock, or a split into shorter jobs.

`SET NX PX` on one instance is safe until that instance fails over: a replica promoted before the key replicated hands the lock to a second holder. Where that matters, the Redlock algorithm over several independent instances, taken from the project's client ecosystem, is the answer, and where it does not, the lock's key sits on an instance that fails over into nothing, and the reference names why.
