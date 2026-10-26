---
name: superwhisper
description: "Changes SuperWhisper's dictation config and finds why a change did not take — the recogniser's vocabulary, a mode's prompt, and the spoken slash-command listing kept in sync with the skills on disk. Use on \"superwhisper\", \"dictation\", \"vocabulary\", \"mode prompt\", \"slash commands are misheard\", a dictated name that keeps coming out wrong, `superwhisper-skills`, a file under its `settings/` or `modes/` folder, its iPhone app, or its launchd sync job. Not for its public feedback board or roadmap — the feedback board's skill."
---

# SuperWhisper

- Dictation runs in two stages that share no data: the recogniser turns sound into words, the cleanup model rewrites them with the mode's prompt → fix a symptom at the stage that owns it; the vocabulary never reaches the prompt.
- The app reads its config only at launch and rewrites a file only when a setting changes in its own UI → an external write waits on disk until the next start, whoever restarts the app.
- `G` — the generator, `~/.local/bin/superwhisper-skills`.
- Match the request against § Routing, then read the matched file and every reference it names.

## Routing

| If the request is | Read |
| --- | --- |
| Sync the slash-command listing, add vocabulary, edit a mode prompt | `cookbook/apply.md` |
| A change did not take effect, a name is still misheard, the app ignored a write | `cookbook/diagnose.md` |
| Which stage owns a symptom, what each stage can change | `references/layers.md` |
| How a write is lost, the traps that hide a failed write, a dictation in progress, the ingestion witnesses | `references/write-model.md` |
| Running the generator or choosing its flag, the scheduled check, the day's notification, whether the sync is healthy, the cadence | `references/generator.md` |
| A symptom no row names | `references/layers.md` classifies it, then route back here |

## Project config

- `~/.claude/skills/agents-config/integrations/superwhisper.md` declares `role: dictation` and carries no value: the app's own files answer every one.
- A mode → its file key, `modes/<key>.json`, never its display name; the modes carrying the generated roster → `SW_MODES` in `$G`.
- The config folder → read it at the act, never as a literal: `<appFolderDirectory>/superwhisper`, the parent answered by `defaults read com.superduper.superwhisper appFolderDirectory`; a fresh install → `~/superwhisper`.
- Config absent → bootstrap it through /managing-harness , `references/skills.md` § A tool's skill and its config.

## The iPhone

- Sync runs one way, computer → phone, carrying the vocabulary and the modes; the phone keeps its own `modeKeys` and `favoriteModelIDs`, each synced mode's key appended.
- The phone app, `com.superduper.superwhisper-ios`, keeps the same `settings/` and `modes/` under `/Documents/superwhisper/`, reached on a paired iPhone, by cable or Wi-Fi sync, through `uvx --from pymobiledevice3 pymobiledevice3 apps pull|push --documents com.superduper.superwhisper-ios`; `push` takes the local file first, `pull` the phone path first.
- Provenance: 2026-10-12, cable, pull and push read back byte for byte on iOS app 2.24.
- Back up the phone's files before a push.
- A phone mode carries fewer fields than the Mac's → fill a phone mode's shape from the Mac mode, folding `promptExamples` into the prompt as the Mac sends them: `EXAMPLES OF CORRECT BEHAVIOR:`, then `User:` / `Assistant:` pairs.
- A mode on a local model or on system audio stays on the Mac.
- No remote restart reaches the phone → the user force-quits and reopens the app, changing no setting in between.
- Witnesses → the Vocabulary screen, and a phone recording's `meta.json`.

## Completion

- State which layer changed and its ingestion witness, per `references/write-model.md` § Witnesses.
- No witness yet → report it as written-not-confirmed, naming what would confirm it.
