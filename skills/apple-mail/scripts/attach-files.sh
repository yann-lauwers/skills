#!/bin/bash
# requires: osascript (macOS), Apple Mail, Automation + Accessibility permission
# Attaches files to the compose window mail-draft.sh opened, found by its nonce title.
#
#   attach-files.sh <nonce> <path>...
#
# The files are pasted at the caret, which the body paste left under the new
# text, exactly as dropping them there would. `make new attachment` is not used: on a reply or a forward it
# replaces the whole body, quoted original included, with the attachment alone.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NONCE="$1"
shift

attached_names() {
	MAIL_NONCE="$NONCE" osascript 2>/dev/null <<'APPLESCRIPT' || true
global collected, visited, budget

on findWeb(el, depth)
	if depth > 8 then return missing value
	tell application "System Events"
		try
			set kids to every UI element of el
		on error
			return missing value
		end try
		repeat with k in kids
			set rr to ""
			try
				set rr to (role of k) as string
			end try
			if rr is "AXWebArea" then return k
			set v to my findWeb(k, depth + 1)
			if v is not missing value then return v
		end repeat
	end tell
	return missing value
end findWeb

on gather(el, depth)
	if depth > 12 then return
	if visited ≥ budget then return
	tell application "System Events"
		try
			set kids to every UI element of el
		on error
			return
		end try
		repeat with k in kids
			if visited ≥ budget then return
			set visited to visited + 1
			set rr to ""
			try
				set rr to (role of k) as string
			end try
			if rr is not "AXStaticText" then
				try
					set end of collected to ((description of k) as string)
				end try
			end if
			my gather(k, depth + 1)
		end repeat
	end tell
end gather

set collected to {}
set visited to 0
set budget to 200
set nonce to (system attribute "MAIL_NONCE")
tell application "System Events" to tell process "Mail"
	set w to first window whose name is nonce
	set wa to my findWeb(w, 0)
	if wa is missing value then error "no body web area in the compose window"
	my gather(wa, 0)
end tell
set AppleScript's text item delimiters to linefeed
set out to collected as string
set AppleScript's text item delimiters to ""
return out
APPLESCRIPT
}

paste_file() {
	MAIL_NONCE="$NONCE" MAIL_NEW_LINE="$1" osascript >/dev/null 2>&1 <<'APPLESCRIPT'
on findWeb(el, depth)
	if depth > 8 then return missing value
	tell application "System Events"
		try
			set kids to every UI element of el
		on error
			return missing value
		end try
		repeat with k in kids
			set rr to ""
			try
				set rr to (role of k) as string
			end try
			if rr is "AXWebArea" then return k
			set v to my findWeb(k, depth + 1)
			if v is not missing value then return v
		end repeat
	end tell
	return missing value
end findWeb

set nonce to (system attribute "MAIL_NONCE")
set newLine to (system attribute "MAIL_NEW_LINE") is "true"
tell application "Mail" to activate
tell application "System Events" to tell process "Mail"
	set w to first window whose name is nonce
	perform action "AXRaise" of w
	set focused of w to true
	set wa to my findWeb(w, 0)
	if wa is missing value then error "no body web area in the compose window"
	set value of attribute "AXFocused" of wa to true
	delay 0.3
	if newLine then
		keystroke return
		delay 0.2
	end if
	keystroke "v" using command down
end tell
APPLESCRIPT
}

# The file system and the accessibility tree do not agree on how an accented
# letter is composed, so both names are normalised before they are compared.
nfc() {
	python3 -c 'import sys, unicodedata; sys.stdout.write(unicodedata.normalize("NFC", sys.stdin.read()))'
}

# One file per paste: Mail takes only the first of several files pasted together.
# A paste that did not land is repeated, as the body paste is; one that landed is
# never repeated, so no file is attached twice.
new_line="true"
for path in "$@"; do
	wanted="$(basename "$path" | nfc)"
	landed="false"
	for attempt in 1 2 3; do
		osascript -l JavaScript "$HERE/pasteboard.js" load-files "$path" >/dev/null
		paste_file "$new_line" || true
		new_line="false"
		for _ in 1 2 3 4 5 6; do
			sleep 0.5
			if attached_names | nfc | grep -Fq -- "$wanted"; then
				landed="true"
				break
			fi
		done
		[ "$landed" = "true" ] && break
	done
	if [ "$landed" != "true" ]; then
		echo "mail-draft: $path did not attach after 3 attempts; the draft is open in Mail without it" >&2
		exit 1
	fi
done
