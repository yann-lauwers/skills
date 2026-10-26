#!/bin/bash
# requires: swiftc, codesign (both ship with the Xcode command line tools)
# Compiles bridge/*.swift into CalendarBridge.app and ad-hoc signs it.
#
# The executable lives inside an app bundle because macOS attributes a Calendars
# TCC grant to a bundle identity. A bare CLI gets attributed to whichever terminal
# launched it, which yields write-only access and no way to read events.
#
# The signature is ad-hoc, so a rebuild changes the binary's hash and TCC drops back
# to "not determined" — the next verb re-establishes it. That is why this script is a
# no-op when the binary is newer than the source.
set -euo pipefail

SKILL="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLIST="$SKILL/bridge/Info.plist"
APP="$SKILL/bridge/CalendarBridge.app"
BIN="$APP/Contents/MacOS/calendar-bridge"

force=0
[ "${1:-}" = "--force" ] && force=1

if ! command -v swiftc >/dev/null 2>&1; then
	echo "build-bridge: swiftc is not on PATH. Install the Xcode command line tools:" >&2
	echo "  xcode-select --install" >&2
	exit 1
fi

stale=0
for src in "$SKILL"/bridge/*.swift "$PLIST"; do [ "$src" -nt "$BIN" ] && stale=1; done
if [ "$force" -eq 0 ] && [ -x "$BIN" ] && [ "$stale" -eq 0 ]; then
	echo "build-bridge: $BIN is current; nothing rebuilt."
	exit 0
fi

mkdir -p "$APP/Contents/MacOS"
cp "$PLIST" "$APP/Contents/Info.plist"

swiftc -O "$SKILL"/bridge/*.swift -o "$BIN"

codesign --sign - --force --timestamp=none "$APP" >/dev/null 2>&1

echo "build-bridge: built $BIN"
"$SKILL/scripts/cal" access
