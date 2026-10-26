# Reading a calendar

- `scripts/cal events --from X --to Y` → events in a window, with attendees, recurrence and the video link · `scripts/cal show <ref>` → one event in full · `scripts/cal free --from X --to Y` → open slots.
- Omitted, the window is `today` to `+7d` → pass both whenever the question names another window.
- A question over several days → one call for the whole range, never one per day.
- `events` has no default cap: `--from` and `--to` bound a read, `--limit` applies only when passed.

## Filtering

- Declined and cancelled events are dropped by default → `--include-declined` puts them back.
- `--query` matches title, location and notes as a case-insensitive substring, with no stemming and no synonyms.
- Before reporting that something is not on the calendar → retry with two or three other terms: the organiser's surname · the project name · the room.

## Reading the JSON

- Any key with no value is absent from the event → read every key with `.get()`, never by index.
- `conferenceUrl` carries the video-call link found in the url, location or notes → read it there, never by parsing the notes.
- `status` is `none` on most personal events → "did I accept" is answered by `myStatus`.
- An all-day event ends at 23:59:59 on its own last day: `durationMinutes` reads 1439 per day, 1499 on a daylight-saving day → count days from `start` and `end`, never by dividing `durationMinutes`.

## Open slots

- A `free` slot means nothing is booked, never that the time suits.
- `free` reads every calendar, birthdays and holidays included → pass `--calendar` for the ones that block time.
- Working hours → `--between 09:00-18:00 --weekdays`.
