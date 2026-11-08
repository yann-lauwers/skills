---
name: things
description: Reads, adds, schedules, completes and rewrites to-dos in Things 3.
allowed-tools: Bash(osascript:*), Bash(open:*)
disable-model-invocation: true
---

## Driving it

- An area or project goes in the properties: `tell application "Things3" to make new to do with properties {name:"…", area:area "Nexus"}`; `at beginning of area|project` silently files it in neither.
- A container name → look it up in both `name of areas` and `name of projects` before addressing it.
- A date the user gives → `schedule t for <date>` (`activation date` is read-only); `due date` only for a stated finish-by deadline.
- A to-do scheduled for today sits in both `Today` and `Anytime` → dedupe by id when reading across lists.
- Checklist items, the evening slot and headings exist only in the URL scheme's `add` (`open "things:///add?…"`); `update` needs an auth token this setup lacks, so on an existing to-do they are out of reach → tell the user.

## Wording

- French whatever the request's language, in the user's franglais: English tech words keep their English root (`checker` · `updater` · `PR` · `hook` · `commit`).
- Title: infinitive verb first, 3–8 words, one action, no trailing punctuation.
- Notes: only the facts the action needs (link, number, address, dimensions, candidate dates, a message draft, the options still open).
- A rambling capture → keep the user's words, drop the thinking-out-loud, move every fact into the notes.
- A to-do that cannot be started as written → tag `À clarifier`, notes naming the one question that unblocks it.
- One outcome, one to-do: merge duplicates into the richer one; alternative approaches go in its notes.
- ❌ `Update test setup` · ✅ `Regrouper les tests dans des dossiers _test_`
- ❌ `Checker pour créer skill billit qui utilise l'interface (opensource ?) qui utilise l'interface ?` · ✅ title `Créer un skill Billit`, notes `À vérifier : Billit expose-t-il une API publique, ou faut-il piloter l'interface ?`, tag `À clarifier`
