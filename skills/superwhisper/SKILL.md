---
name: superwhisper
description: "Changes SuperWhisper's dictation config and finds why a change did not take. Started only by /superwhisper ."
disable-model-invocation: true
---

# SuperWhisper

- Dictation runs in two stages that share no data: the recogniser turns sound into words, the cleanup model rewrites them with the mode's prompt → fix a symptom at the stage that owns it; the vocabulary never reaches the prompt.
- The app reads its config only at launch and rewrites a file only when a setting changes in its own UI → an external write waits on disk until the next start, whoever restarts the app.
- `G` — the generator, `~/.local/bin/superwhisper-skills`.

## Routing

| If the request is | Read |
| --- | --- |
| Sync the slash-command listing, add vocabulary, edit a mode prompt | `cookbook/apply.md` |
| A change did not take effect, a name is still misheard, the app ignored a write | `cookbook/diagnose.md` |
| Which stage owns a symptom, what each stage can change, a symptom no row names | `references/layers.md` |
| How a write is lost, the traps that hide a failed write, a dictation in progress, the ingestion witnesses | `references/write-model.md` |
| The generator and its flags, the scheduled check, its daily notification, the sync's health, the cadence | `references/generator.md` |
| The iPhone — syncing the vocabulary or a mode to the phone, its restart, its witnesses | `references/iphone.md` |

## Project config

- `~/.claude/skills/agents-config/integrations/superwhisper.md` declares `role: dictation` and carries no value: the app's own files answer every one.
- A mode → its file key, `modes/<key>.json`, never its display name; the modes carrying the generated roster → `SW_MODES` in `$G`.
- The config folder → read it at the act, never as a literal: `<appFolderDirectory>/superwhisper`, the parent answered by `defaults read com.superduper.superwhisper appFolderDirectory`; a fresh install → `~/superwhisper`.
- Config absent → bootstrap it through /managing-harness , `references/skills.md` § A tool's skill and its config.

## Completion

- State which layer changed and its ingestion witness, per `references/write-model.md` § Witnesses.
- No witness yet → report it as written-not-confirmed, naming what would confirm it.
