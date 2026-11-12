---
name: watch-pr
description: Watches one pull request until it merges, acting on its watcher's verdicts. Use on 'merge once green', 'watch the pr'; also once a pull request is opened or pushed to land.
---

# Watch PR

1. Start the watcher as a background Bash task, `description: "PR <N> watcher"`:
   `scripts/watch-pr.py`
   It takes the current folder's branch; from elsewhere add `--pr <url>`.
2. Report the PR and end the turn: the watcher's exit wakes the session.
3. The last `{` line of its output is the verdict. Handle it, then start the watcher again with the line's `rearm`.

Done on `MERGED` or `CLOSED`: report it and stop.

## What the verdict leaves to you

- `integration_base` true → take the base by merge · false → rebase, push `--force-with-lease`.
- `BOT_THREADS` → fix each, or refute it quoting the line or output that disproves it; reply, then resolve.
- `HUMAN_COMMENTS` → fix what is asked and push; report each item with a suggested answer. The reply and the resolve are the user's.
- `CI_RED` with no code root (infra, a flake) → `gh run rerun <run_id> --failed` while `attempt` is under 3 · then pause.
- Pause = report and start nothing: on the 6th fix in a row without a `CLEAN`, or a verdict unnamed here.
- A harness with no wake on exit → run the watcher in the foreground.
