---
name: superwhisper
description: "Tunes SuperWhisper dictation — vocabulary, replacements and mode prompts — so spoken names and slash commands come out spelled right, on the Mac and the iPhone."
disable-model-invocation: true
---

# SuperWhisper

- Config folder → `$(defaults read com.superduper.superwhisper appFolderDirectory)/superwhisper`: `settings/settings.json` holds the vocabulary and replacements of every mode, `modes/<key>.json` one mode's prompt; `~/Documents/superwhisper` is a dead copy.
- The app loads config at launch only → a write to those files takes effect at the next restart.
- Restart → once the newest directory under `recordings/` holds a `meta.json` more than three minutes old — one without is a dictation in flight, and quitting loses it; then quit, `open -a superwhisper`, `pgrep -x superwhisper`.
- Done → the change's witness, read from the app per the file routed below; none yet → report written-not-confirmed and what would confirm it.
- The vendor's docs → `https://superwhisper.com/docs/llms.txt`.

## Slash-command sync

- `scripts/sync-slash-commands.py` keeps every Claude Code skill name in the vocabulary and in the roster that ends each mode prompt `SW_MODES` names; the launchd agent `com.yannlauwers.superwhisper-skills` runs it every quarter hour and restarts the app while the machine sits idle.
- Is it healthy → `--check` · write and load now → `--apply --restart` · the rest → `--help`.
- A machine without the agent (`launchctl print gui/$(id -u)/com.yannlauwers.superwhisper-skills` fails) → copy `scripts/com.yannlauwers.superwhisper-skills.plist` to `~/Library/LaunchAgents/`, then `launchctl bootstrap gui/$(id -u)` on that copy.

## Routing

| The request | Read |
| --- | --- |
| A name or a command comes out wrong · adding a vocabulary word or a replacement | `references/wrong-name.md` |
| Editing a mode's prompt by hand | `references/mode-prompt.md` |
| Anything on the iPhone | `references/iphone.md` |
