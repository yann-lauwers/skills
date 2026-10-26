# The bridge and its Calendars access

- macOS attributes a Calendars grant to the responsible process: a binary a shell spawns gets the terminal's grant, which is write-only · `bridge/CalendarBridge.app` launched through LaunchServices holds its own full grant.
- `scripts/cal` therefore launches the bundle with `open` and reads the result back from a temp file → call `scripts/cal`, never `bridge/CalendarBridge.app/Contents/MacOS/calendar-bridge`.
- Exit codes: 1 the bridge could not be built · 2 usage · 3 access · 4 not found · 5 rejected · 70 the bridge wrote no result in time.
- Exit 70 → a Calendars prompt may be waiting on screen; `CAL_TIMEOUT` sets the wait in seconds, default 120 · the prompt answered and 70 again → check the bundle is present and signed: `codesign -dv` on it.

## Read the status before believing a diagnosis

- `${CLAUDE_SKILL_DIR}/scripts/cal access` prints `status`, `canRead` and `canWrite`.
- `full` → permissions are fine; look elsewhere.
- `write-only` → the grant is the terminal's: something ran the binary directly → call `scripts/cal`.
- `not determined` → run any read verb; a prompt appears on screen.
- `denied` → `tccutil reset Calendar com.yannlauwers.claude.calendar-bridge`, then re-run a read verb.
- `restricted` → a device policy blocks the grant; nothing in the skill lifts it.
- `System Settings → Privacy & Security → Calendars` lists the app as Calendar Bridge; its toggle is the same switch.

## What survives what

- A rebuild resets the status to `not determined`, since the ad-hoc signature's hash changes with the binary → the next read verb re-establishes access; expect a prompt on screen.
- `build-bridge.sh` rebuilds only when a `bridge/*.swift` file or `bridge/Info.plist` is newer than the binary, or under `--force`.
- Changing `CFBundleIdentifier` in `bridge/Info.plist` loses the grant outright, and the app reappears in System Settings under its new name → leave it unchanged.

## The failure that reads as an empty calendar

- On macOS 14 and later `requestAccess(to: .event)` returns success and grants write-only, and every read then returns an empty array with exit 0.
- `openStore` in `bridge/Output.swift` checks `EKEventStore.authorizationStatus` after the request and refuses to read on anything short of full access → editing it, keep that check and never trust the `granted` boolean.
- An exit-0 empty result from `events` is therefore a calendar with nothing in that window; the permission case exits 3.

## Rebuilding from nothing

- `${CLAUDE_SKILL_DIR}/scripts/build-bridge.sh --force` rebuilds and ad-hoc signs the bundle, then prints `cal access`.
- It needs `swiftc` and `codesign` from the Xcode command line tools → `xcode-select --install`.
- `scripts/cal` runs the build itself when the binary is missing → a fresh machine needs only the permission prompt answered.
