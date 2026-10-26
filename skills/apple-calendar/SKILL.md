---
name: apple-calendar
description: >-
  Reads the calendars signed in on this Mac, answers questions about them, and creates, moves or
  deletes events. Use when the request says "what's on my calendar", "am I free", "when is my next
  meeting", "add an event", "book a slot", "move that meeting", "find a time for", "invite them", or
  names a day, meeting or attendee and asks what is happening. Also fires before reaching a calendar
  through Google Calendar, CalDAV, an ICS file or a connector, and before an `osascript` call
  targeting Calendar. Not for a to-do with no time on it — the task list's skill.
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/*)
---

# Apple Calendar

- `${CLAUDE_SKILL_DIR}/scripts/cal <verb> [flags]` reaches every calendar configured on this Mac, with no credential.
- It prints JSON on stdout, a diagnostic on stderr, and exits non-zero on failure.
- Every verb and flag → `scripts/cal help`; read it before naming a flag · a verb's own `--help` runs the verb, never the help.
- Every read and write goes through `scripts/cal`, never the binary inside `bridge/CalendarBridge.app` run directly, nor `osascript` against Calendar.app.

## Route

| IF | THEN read |
| --- | --- |
| which calendars exist, which are writable, which is the default | `scripts/cal calendars` |
| what is on a day, a week or a range · one event in full · where the open slots are | `references/reading.md` |
| adding, moving, retitling, rescheduling, deleting · inviting someone | `references/writing.md` |
| opening an event in Calendar.app | `scripts/cal open <ref>` |
| a permission error · an empty result that looks wrong · `cal` exiting 70 · rebuilding the bridge | `references/permission-and-bundle.md` |
| editing `bridge/*.swift` | `references/permission-and-bundle.md`; rebuild with `scripts/build-bridge.sh --force` |
| creating a calendar, adding an account, a subscription | Calendar.app's own territory: `scripts/cal open` an event and let Yann do it there, or read `/System/Applications/Calendar.app/Contents/Resources/iCal.sdef` |

## Every use

- `--calendar` takes a title or an id, matched exactly first and then as a substring, against the title only, never the account.
- An event that belongs to work or to a shared calendar → pass the id from `scripts/cal calendars`, never a title.
- A ref (`identifier@occurrence`, as `events` prints it) → act on it in the same turn it was read · a later turn re-runs the query; an id changes when its event is edited.
