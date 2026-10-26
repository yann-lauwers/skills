# Lifecycle Config

- `autoStopInterval` — minutes idle before the sandbox stops. Stopped clears memory and keeps the filesystem, so `start()` (sub-second) resumes far cheaper than a fresh create (seconds, high-variance).
- `autoDeleteInterval` — minutes before a stopped sandbox is deleted; `-1` never deletes.
- `ephemeral: true` — the sandbox is deleted when it stops, so every turn after an idle stop cold-creates → only where nothing ever resumes.

## What the idle clock counts

- Idle is no events on the sandbox, counted server-side from API calls; work inside the container defers nothing.
- An open PTY session defers auto-stop indefinitely, with no traffic on it — undocumented by the vendor.
- Closing the PTY, by `disconnect()` or the shell exiting, re-arms the clock: the sandbox stops one interval later.
- `refreshActivity()` and any ordinary SDK call such as `executeCommand` reset the clock to a full window.
- `setAutostopInterval()` moves the threshold without resetting the counter: raising it mid-window buys the difference measured from creation, not a fresh window.
- Read-only state polls reset nothing, so a monitor cannot keep sandboxes alive.

## Keeping a sandbox alive

- Work the platform cannot see → `refreshActivity()` on an interval below `autoStopInterval`, stopped once the work ends; `setAutostopInterval()` only to change the threshold.
- A long-lived stream gets its own client: one client shared between an open PTY and a state poll answers the poll with `socket hang up`, which is client contention, not an unreachable sandbox.

## Tearing a sandbox down

- A driver deletes what it made when its work ends; every create still sets `autoStopInterval` and `autoDeleteInterval`, so a driver dying before cleanup leaks nothing.
- Verify a delete against the account listing, never the delete call's return, and pause first: deletion completes asynchronously, so an immediate listing still shows the sandbox.
