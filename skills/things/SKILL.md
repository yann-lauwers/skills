---
name: things
description: "Reads, adds, schedules, completes and rewrites to-dos in Things 3 on this Mac. Started only by /things ."
allowed-tools: Bash(osascript:*), Bash(open:*), Bash(cat:*)
disable-model-invocation: true
---

- Lives at `/Applications/Things3.app`, driven by AppleScript with no credential.
- A class, property or command the references leave out → `cat /Applications/Things3.app/Contents/Resources/Things.sdef`, the app's own dictionary.
- Built-in list names stay English whatever the language of areas and projects: `Inbox` · `Today` · `Tomorrow` · `Anytime` · `Upcoming` · `Someday` · `Later Projects` · `Logbook` · `Trash`.
- One store holds every context, work included: a standing context is an area (`area "Nexus"`), a finite outcome a project; both are addressed by name.
- A name the user calls a project → enumerate `name of areas` and `name of projects` before choosing the class to query; both expose `to dos`, so the query shape is the same once the class is right.

## Routing

| IF                                                                                                       | THEN read                  |
| -------------------------------------------------------------------------------------------------------- | -------------------------- |
| reading, listing or finding to-dos, or collecting ids before acting on them                              | `references/reading.md`    |
| creating, scheduling, setting a deadline, completing, reopening, moving or deleting                      | `references/writing.md`    |
| writing or rewriting a title, notes or tag · reformulating a capture · merging duplicates                | `references/wording.md`    |
| checklist items, project headings, the evening slot, appending to notes or tags, or any `things:///` URL | `references/url-scheme.md` |

## Every use

- Deleting, completing or rescheduling an item the request did not name → confirm with the user first.
- Reporting back → state what changed and where it landed: the list or project name, and the scheduled date where one was set.
- A count of items read stays out of the reply; the items themselves go in.
