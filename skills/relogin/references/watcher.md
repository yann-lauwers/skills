# The watcher

`scripts/credential-watch.py` reads every slot every 10 minutes from launchd (`com.yann.credential-watch`, `~/Library/LaunchAgents/`) and acts on at most one slot per tick.

```
credential-watch tick [--dry-run]    one reading, one act at most
credential-watch status              the state, the attempts, the last reading
launchctl kickstart -k gui/$(id -u)/com.yann.credential-watch    run a tick now
```

| Verdict | Read from | Act |
| --- | --- | --- |
| `DEAD` | `cswap list --json` reading `relogin_required` on the same slot on every tick across 15 min — covered by readings, never by elapsed time, so a failed source or a sleeping Mac restarts the window | `oauth.py --email <slot's email>`, then `SKILL.md` § Validate, then record, in that section's own step order |
| `WAITING` | that reading, with the window not yet covered | nothing |
| `LIVE` | none of those | nothing |
| `UNKNOWN` (exit 2) | a read that failed | nothing; the next tick re-reads |
| anything else | — | not emitted; the state file is the raw reading, read it before acting |

- A failed read is never a verdict.
- The backstop is per account → one attempt per 6 h, two per 24 h; past it the watcher stops on that account and DMs once a day with the by-hand line.
- Every act, proven or failed, arrives as a Slack DM from the bot; the log is `~/.local/state/credential-watch/log`.
- `oauth.py` exit 3 → the run waited on Yann in a visible window and closed unfinished: a "closed unfinished" DM, never FAILED, the attempt still counted by the backstop.
- A tick holds the lock for its whole run, up to 160 min while a window waits on Yann; a relogin run by hand outside a tick holds `~/.local/state/credential-watch/tick.lock` too, or the next tick's act collides on the global account.
- It survives session ends and reboots, so nothing re-arms it; `launchctl list | grep credential-watch` says it is loaded.
