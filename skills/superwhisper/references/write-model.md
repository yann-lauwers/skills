# Write Model

## The app owns the file

- The app keeps its config in memory and watches no file under `settings/` or `modes/`.
- Its UI rewrites a file whole; a dictation rewrites nothing.
- A UI change made before the next launch saves the in-memory state over the write → make the write again.
- The app never flushes on quit → what is on disk is already current; merge into it, and never quit the app to make it save first.
- Config is `settings.json` and the mode JSON files only; the app's SQLite database holds recordings and migrations, with no settings table.
- Designing a file-write strategy against a new app version → first confirm the database still has no settings table; one appearing invalidates file writes.

## Traps

- `open -g -a` right after a quit races LaunchServices, fails with error `-600` and leaves the app down while the exit code reads success → drop `-g`, retry, and verify the process before reporting.
- The config folder may be cloud-synced — iCloud Drive syncs Desktop and Documents here — and the app signals nothing → keep a single automated writer; a second machine writing the same files leaves conflict copies the app ignores.
- Everything in a mode's prompt travels to the model verbatim, and is charged for, on every dictation → name the cost of anything added.
- Added prompt text competes with the prompt's own precedence rules → write it as prompt content, bounded on headings the prompt already has; never a machine marker.

## Detecting a dictation in progress

- A dictation creates a directory under the recordings folder, and its `meta.json` lands only once the transcript is final → a recordings directory without one is a dictation in flight.
- A dictation that ended in the last three minutes counts as in progress → defer the restart, to the next day if need be.
- Quitting mid-dictation loses the recording, and relaunching does not recover it → this check outranks an explicit instruction to restart.

## Witnesses

- An ingestion witness separates "the file changed" from "the app read it"; each layer has its own.
- A mode-prompt change → report it confirmed only after a dictation.

| Layer | Witness | How to read it |
| --- | --- | --- |
| Vocabulary | The SuperVocab phonetic cache under the app's support directory | A newly added word appears with a French and an English reading. It populates over several seconds after relaunch, so a reading taken too early looks like partial failure |
| Mode prompt | The `prompt` field of a recording's `meta.json` | Present only once a dictation has happened. Note the newest recording before the change, then compare after one |
| Either | `$G --check` | Per `references/generator.md` § Checking the sync |
