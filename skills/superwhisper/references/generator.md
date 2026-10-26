# The Generator

## What it owns

- It builds the slash-command listing from the skills on disk and writes it to both layers in one pass: the recogniser's vocabulary and the mode prompt's roster.
- The Claude Code rules deciding which names are real — built-ins carry no `SKILL.md`, `skillOverrides` can switch one off, names collide across sources → live in the script; change them there.
- Drift is the generated listing against the live vocabulary, the ground truth for what was imported → keep no bookkeeping of your own.
- `$G --help` lists the flags.

## Flags

- Load now → `--apply --restart`; the restart yields to a dictation in flight or one that just ended, since the update is already on disk · load at the next start → `--apply` alone.
- `--auto` is the scheduled check's entry point → never run it by hand: a manual run spends the question it would have asked.
- `--prompt` — what the notification's click runs → run it to put the choice to the user now.
- `--check` → § Checking the sync · `--measure` → the near-miss rule's numbers, per `references/layers.md`; both write nothing the app reads.
- No flag → it writes its artifacts to disk for a manual import and changes nothing the app reads.

## The scheduled check

- The scheduled check — the launchd agent `com.yannlauwers.superwhisper-skills`, running `$G --auto` every quarter hour.
- It restarts the app itself only while nobody is using the machine; someone at it is ordinary, not a failure.
- The app quit → the pass never opens it; the update loads when the user does.
- A machine that never goes quiet → one notification a day, once the update has waited a day.
- Any failure — a refused roster write, a relaunch that did not come back, a dialog that could not appear → a notification whenever it happens.
- Clicking the day's notification offers apply now · ask again tomorrow · stop asking about these names, and carries out the chosen one.
- "Stop asking" covers the batch it was shown; a skill added afterwards asks again.
- No notification → the listing is current, the update has waited under a day, or the day's question is already answered.
- Asked to change the cadence → edit the scheduled check's plist in `~/Library/LaunchAgents/`.

## Checking the sync

- Asked whether the sync is healthy → run `$G --check`; its answer holds whatever did or did not appear on screen.
- `in sync` → it is working.
- `staged` → the update is on disk and the running app has not loaded it; any restart finishes it.
- Drifted — names missing from the live vocabulary, a stale roster, or entries a retired skill left → read the state file, `~/.local/share/superwhisper-skills/schedule.json`, absent while nothing is pending: `pending_since` dates the drift; `snoozed_until` and `muted` separate a question already answered from a window the job never gets.
