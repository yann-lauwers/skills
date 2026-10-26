# Writing

- Create, schedule, deadline, complete, move and delete all run through AppleScript; act on an existing item by its id, collected per `references/reading.md`.
- A title, notes or tag about to be written → word it per `references/wording.md` first.
- Create → `make new to do with properties {name:"…", notes:"…", tag names:"a,b"} at beginning of list "Inbox"`, with no deadline unless the request names one.
- `schedule` is when the item surfaces to work on, the common case · `due date` is the hard "finish by" date, the rare one.
- Schedule → `schedule t for (current date) + 1 * days`; `activation date` is read-only, so `schedule` is the only route.
- Deadline → `set due date of t to date "…"`, only when the user names a date the work must be finished by; a date for when to start on it is a schedule.
- `delete t` moves the item to Trash.
- Checklist items, project headings, the evening slot, appending rather than replacing notes or tags → `references/url-scheme.md`.
