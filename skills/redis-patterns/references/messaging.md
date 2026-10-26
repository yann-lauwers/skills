# Messaging

Pub/Sub or a Stream, and what each one owes. Read when fanning an event out to consumers, or queueing work that must not be lost.

| Shape | Take it when | What it does not do |
| --- | --- | --- |
| Pub/Sub — `PUBLISH` / `SUBSCRIBE` | Fire-and-forget broadcast: a live update, a cache-bust signal | A message with no subscriber at that instant is gone; no replay, no acknowledgement |
| Stream — `XADD` / `XREADGROUP` / `XACK` | Delivery must be guaranteed, consumers are grouped, or a late consumer replays | Nothing, at the cost of trimming and reclaiming |

## What a Stream consumer owes

- `XGROUP CREATE … MKSTREAM` once at startup, tolerating `BUSYGROUP` — that error, not every exception.
- `XACK` after the work succeeds. An entry read and never acked sits in the pending list forever.
- A reclaim loop: `XAUTOCLAIM` (or `XPENDING` + `XCLAIM`) takes entries a dead consumer read and never acked. At-least-once delivery holds only with this loop; without it a crashed consumer's entries are never redelivered.
- A cap: `XADD … MAXLEN ~ <n>` — approximate. Exact `MAXLEN` trims on every add and is O(N).

The subscriber side of Pub/Sub blocks the connection it runs on; it takes its own connection, in its own thread or process, never one borrowed from the request pool.
