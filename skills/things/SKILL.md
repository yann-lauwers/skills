---
name: things
description: "Reads, adds, schedules, completes, moves and rewrites to-dos in the Things 3 app on this Mac, and carries the house wording for a to-do's title, notes and the tag marking one unclear. Use on \"things\", \"todo list\", \"add a task\", \"what's on today\", \"inbox\", \"schedule this\", \"mark it done\", \"rewrite this task\", \"check for duplicates\", a Things area or project, `osascript` targeting Things3, or a `things:///` URL. Not for a timed calendar event — the calendar's skill; not for a repository's tickets — the tracker's skill."
allowed-tools: Bash(osascript:*), Bash(open:*), Bash(cat:*)
---

# Things 3

- Things 3 lives at `/Applications/Things3.app`, driven by AppleScript with no credential.
- A class, property or command the references leave out → `cat /Applications/Things3.app/Contents/Resources/Things.sdef`, the app's own dictionary.
- Built-in list names stay English whatever the language of areas and projects: `Inbox` · `Today` · `Tomorrow` · `Anytime` · `Upcoming` · `Someday` · `Later Projects` · `Logbook` · `Trash`.
- One store holds every context, work included: a standing context is an area (`area "Nexus"`), a finite outcome a project; both are addressed by name.
- A name the user calls a project → enumerate `name of areas` and `name of projects` before choosing the class to query; both expose `to dos`, so the query shape is the same once the class is right.

## Project config

- `~/.claude/skills/agents-config/integrations/things.md` (`role: tasks`) → `secret`, the item holding the URL scheme's `auth-token`.
- One store per machine, so a user floor and no project layer → a `docs/agents/integrations/things.md` inside a repo is a misplacement to report, never a file to read.
- Config absent or `secret: null` → drive the app anyway; URL-scheme updates stay unavailable until the user enables the token.

## Routing

| IF | THEN read |
| --- | --- |
| reading, listing or finding to-dos, or collecting ids before acting on them | `references/reading.md` |
| creating, scheduling, setting a deadline, completing, reopening, moving or deleting | `references/writing.md` |
| writing or rewriting a title, notes or tag · reformulating a capture · merging duplicates | `references/wording.md` |
| checklist items, project headings, the evening slot, appending to notes or tags, or any `things:///` URL | `references/url-scheme.md` |

## Every use

- Deleting, completing or rescheduling an item the request did not name → confirm with the user first.
- Reporting back → state what changed and where it landed: the list or project name, and the scheduled date where one was set.
- A count of items read stays out of the reply; the items themselves go in.
