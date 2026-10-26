# Writing to a calendar

- `scripts/cal create` · `update <ref>` · `delete <ref>`; their flags → `scripts/cal help`.
- A request ambiguous about a date → run it with `--dry-run` first, which prints the event in the shape the real call returns, and show Yann that output rather than a description of it.
- Every mutation returns the event reread from the store → report from the returned JSON, never from the flags sent; a timezone or end date the store altered comes back altered.
- `create` without `--calendar` uses the system default and names it in the result.
- `--span this` changes one occurrence of a repeating event · `--span future` changes it and every later one · the default is `this`.
- A repeating event and a request that does not say how far → ask which span · "cancel the standup" almost always means `future`.

## Invitees

- EventKit and Calendar.app's scripting dictionary both expose attendees read-only, so neither `scripts/cal` nor `osascript` adds an invitee.
- The only other route talks CalDAV or Exchange directly, signing in again to accounts Calendar.app already holds → never take it.
- A request to invite someone → create the event with everything else in place, run `scripts/cal open <ref>`, and say in the reply that the invitees are the one part waiting for Yann in Calendar.app.
- A change to a recurrence rebuilds the whole `EKRecurrenceRule` in `bridge/Store.swift` (`buildRule`), never patches one.
