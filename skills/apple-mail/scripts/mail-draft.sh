#!/bin/bash
# requires: osascript (macOS), Apple Mail, Automation + Accessibility permission
# Composes a message in Apple Mail and leaves it open, unsent, for Yann to send.
#
# There is no send path in this script, by design. Apple Mail's `send` verb is
# never reached from here, so the only way a message leaves the machine is Yann
# clicking Send in the window this opens.
#
# The body is placed by pasting it into the compose window, never by assigning
# `content`. On a reply or a forward, `content` is the property that holds Mail's
# own quoted original, and assigning it replaces the quote with plain text —
# losing the attribution line, the blue quote bar, the sender's formatting and
# every inline image. Pasting leaves all of that standing and puts the new text
# above it, which is what Mail itself does when a person clicks Reply.
#
# The payload travels through a 0700 temp directory read back as UTF-8, so no
# address, subject or body text reaches argv or stdout. Prints "drafted".
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
	cat >&2 <<'USAGE'
usage: mail-draft.sh --to <addr[,addr]> --subject <s> (--body <text> | --body-file <path>)
                     [--from <addr>] [--cc <addr[,addr]>] [--bcc <addr[,addr]>]
                     [--html-file <path>] [--attach <path>]...
       mail-draft.sh --reply-to <message-id> [--all] (--body <text> | --body-file <path>)
                     [--from <addr>] [--html-file <path>] [--attach <path>]...
       mail-draft.sh --forward <message-id> --to <addr[,addr]>
                     (--body <text> | --body-file <path>) [--from <addr>]

Opens the composed message in Apple Mail as an unsent draft. Yann sends it.
--from must be an address Apple Mail already owns; mail-accounts.sh lists them.
--reply-to and --forward take an id from mail-list.sh or mail-search.sh, and keep Mail's own
quoted original untouched beneath the new text.

The body is plain text. A line starting with "- " becomes a real bulleted list
item, and a blank line a paragraph break; --html-file overrides that rendering
when a body needs markup this convention cannot express.
USAGE
	exit 2
}

TO="" CC="" BCC="" SUBJECT="" BODY="" FROM="" BODY_SET="false" HTML_FILE=""
REPLY_TO="" FORWARD="" REPLY_ALL="false"
ATTACHMENTS=()

while [ $# -gt 0 ]; do
	case "$1" in
		--to) TO="$2"; shift 2 ;;
		--cc) CC="$2"; shift 2 ;;
		--bcc) BCC="$2"; shift 2 ;;
		--from) FROM="$2"; shift 2 ;;
		--subject) SUBJECT="$2"; shift 2 ;;
		--reply-to) REPLY_TO="$2"; shift 2 ;;
		--forward) FORWARD="$2"; shift 2 ;;
		--all) REPLY_ALL="true"; shift ;;
		--body) BODY="$2"; BODY_SET="true"; shift 2 ;;
		--body-file)
			[ -r "$2" ] || { echo "mail-draft: cannot read $2" >&2; exit 1; }
			BODY="$(cat "$2")"; BODY_SET="true"; shift 2 ;;
		--html-file)
			[ -r "$2" ] || { echo "mail-draft: cannot read $2" >&2; exit 1; }
			HTML_FILE="$2"; shift 2 ;;
		--attach)
			[ -r "$2" ] || { echo "mail-draft: cannot read $2" >&2; exit 1; }
			ATTACHMENTS+=("$(cd "$(dirname "$2")" && pwd)/$(basename "$2")"); shift 2 ;;
		-h|--help) usage ;;
		*) echo "mail-draft: unknown argument $1" >&2; usage ;;
	esac
done

MODE="new"
[ -n "$REPLY_TO" ] && MODE="reply"
[ -n "$FORWARD" ] && MODE="forward"
if [ -n "$REPLY_TO" ] && [ -n "$FORWARD" ]; then
	echo "mail-draft: --reply-to and --forward are mutually exclusive" >&2; usage
fi

[ "$BODY_SET" = "true" ] || { echo "mail-draft: --body or --body-file is required" >&2; usage; }
case "$MODE" in
	new)
		[ -n "$TO" ] || { echo "mail-draft: --to is required" >&2; usage; }
		[ -n "$SUBJECT" ] || { echo "mail-draft: --subject is required" >&2; usage; }
		;;
	forward)
		[ -n "$TO" ] || { echo "mail-draft: --to is required with --forward" >&2; usage; }
		;;
esac

SOURCE_ID="${REPLY_TO}${FORWARD}"
if [ -n "$SOURCE_ID" ] && ! printf '%s' "$SOURCE_ID" | grep -Eq '^[0-9]+$'; then
	echo "mail-draft: message id must be numeric, got '$SOURCE_ID'" >&2
	exit 1
fi

for addr in $(printf '%s,%s,%s' "$TO" "$CC" "$BCC" | tr ',' '\n' | sed 's/^ *//;s/ *$//' | grep -v '^$'); do
	printf '%s' "$addr" | grep -Eq '^[^[:space:]@]+@[^[:space:]@]+\.[^[:space:]@]+$' || {
		echo "mail-draft: '$addr' is not a well-formed address" >&2
		exit 1
	}
done

dir="$(mktemp -d -t mail-draft)"
RESTORE_PB="false"
cleanup() {
	[ "$RESTORE_PB" = "true" ] && osascript -l JavaScript "$HERE/pasteboard.js" restore "$dir" >/dev/null 2>&1
	/bin/rm -r -f "$dir"
}
trap cleanup EXIT
chmod 700 "$dir"

# One field per file, so every value is read back as UTF-8 rather than decoded as MacRoman.
printf '%s' "$SUBJECT"    > "$dir/subject"
printf '%s' "$BODY"       > "$dir/body"
printf '%s' "$FROM"       > "$dir/from"
printf '%s' "$MODE"       > "$dir/mode"
printf '%s' "$SOURCE_ID"  > "$dir/source_id"
printf '%s' "$REPLY_ALL"  > "$dir/reply_all"
printf '%s' "$TO"  | tr ',' '\n' | sed 's/^ *//;s/ *$//' | grep -v '^$' > "$dir/to"  || true
printf '%s' "$CC"  | tr ',' '\n' | sed 's/^ *//;s/ *$//' | grep -v '^$' > "$dir/cc"  || true
printf '%s' "$BCC" | tr ',' '\n' | sed 's/^ *//;s/ *$//' | grep -v '^$' > "$dir/bcc" || true
printf '%s\n' ${ATTACHMENTS+"${ATTACHMENTS[@]}"} | grep -v '^$' > "$dir/attach" || true

python3 "$HERE/body-to-html.py" "$dir/body" "$dir/html" "$dir/text"
[ -n "$HTML_FILE" ] && cp "$HTML_FILE" "$dir/html"

# Mail builds the quote from a global preference. With it off, `reply` produces an
# empty body and the draft goes out with no thread behind it — which looks exactly
# like a working run, so say so rather than let it pass.
if [ "$MODE" != "new" ]; then
	quoting="$(osascript -e 'tell application "Mail" to return quote original message as string' 2>/dev/null || true)"
	if [ "$quoting" = "false" ]; then
		echo "mail-draft: Mail > Settings > Composing has quoting off, so this ${MODE} will carry no quoted original" >&2
	fi
fi

# The window is found by a nonce written into its own title, never by asking which
# window is frontmost: another process opening a compose window between the create
# and the paste would otherwise receive the keystroke, and the paste would land in
# somebody else's unsent draft.
NONCE="mail-draft-$$-${RANDOM}"
printf '%s' "$NONCE" > "$dir/nonce"

# 1. Create the message, park its real subject, title the window with the nonce.
REAL_SUBJECT_FILE="$dir/real_subject"
MAIL_PAYLOAD_DIR="$dir" osascript > "$dir/newid" <<'APPLESCRIPT'
on readText(p)
	try
		return (read (POSIX file p) as «class utf8»)
	on error
		return ""
	end try
end readText

on readLines(p)
	set raw to my readText(p)
	if raw is "" then return {}
	set AppleScript's text item delimiters to linefeed
	set parts to text items of raw
	set AppleScript's text item delimiters to ""
	set out to {}
	repeat with x in parts
		if (x as string) is not "" then set end of out to (x as string)
	end repeat
	return out
end readLines

on writeText(p, t)
	set f to open for access (POSIX file p) with write permission
	set eof f to 0
	write t to f as «class utf8»
	close access f
end writeText

set d to (system attribute "MAIL_PAYLOAD_DIR")
set theSubject to my readText(d & "/subject")
set theFrom to my readText(d & "/from")
set theMode to my readText(d & "/mode")
set sourceId to my readText(d & "/source_id")
set theNonce to my readText(d & "/nonce")
set replyAll to (my readText(d & "/reply_all")) is "true"
set theTo to my readLines(d & "/to")
set theCc to my readLines(d & "/cc")
set theBcc to my readLines(d & "/bcc")

tell application "Mail"
	activate
	if theMode is "new" then
		set msg to make new outgoing message with properties {subject:theNonce, visible:true}
		set realSubject to theSubject
	else
		set src to missing value
		repeat with acct in every account
			try
				set src to (first message of (first mailbox of acct whose name is "INBOX") whose id is (sourceId as integer))
			end try
			if src is not missing value then exit repeat
		end repeat
		if src is missing value then
			repeat with acct in every account
				repeat with box in every mailbox of acct
					try
						set src to (first message of box whose id is (sourceId as integer))
					end try
					if src is not missing value then exit repeat
				end repeat
				if src is not missing value then exit repeat
			end repeat
		end if
		if src is missing value then error "message " & sourceId & " was not found in Apple Mail"
		if theMode is "reply" then
			set msg to reply src opening window true reply to all replyAll
		else
			set msg to forward src opening window true
		end if
		delay 1
		set realSubject to subject of msg
		if theSubject is not "" then set realSubject to theSubject
	end if

	tell msg
		if theFrom is not "" then set sender to theFrom
		repeat with a in theTo
			make new to recipient at end of to recipients with properties {address:(a as string)}
		end repeat
		repeat with a in theCc
			make new cc recipient at end of cc recipients with properties {address:(a as string)}
		end repeat
		repeat with a in theBcc
			make new bcc recipient at end of bcc recipients with properties {address:(a as string)}
		end repeat
	end tell
	set subject of msg to theNonce
	set visible of msg to true
	my writeText(d & "/real_subject", realSubject)
	return (id of msg) as string
end tell
APPLESCRIPT
NEWID="$(cat "$dir/newid")"

restore_subject() {
	MAIL_PAYLOAD_DIR="$dir" MAIL_MSG_ID="$NEWID" osascript >/dev/null 2>&1 <<'APPLESCRIPT' || true
on readText(p)
	try
		return (read (POSIX file p) as «class utf8»)
	on error
		return ""
	end try
end readText
set d to (system attribute "MAIL_PAYLOAD_DIR")
set wanted to (system attribute "MAIL_MSG_ID") as integer
set realSubject to my readText(d & "/real_subject")
tell application "Mail"
	repeat with m in (every outgoing message)
		try
			if (id of m) is wanted then set subject of m to realSubject
		end try
	end repeat
end tell
APPLESCRIPT
}
# Mail autosaves an open compose window to Drafts every few seconds, so a window
# that wore the nonce while that happened leaves a saved draft titled with it.
# Restoring the subject does not rename the copy already on disk; only this does.
sweep_nonce_drafts() {
	MAIL_NONCE="$NONCE" MAIL_TRASH_NAMES="$(cat "$HERE/trash-names")" osascript -l JavaScript "$HERE/sweep-drafts.js" >/dev/null 2>&1 || true
}
trap 'restore_subject; sweep_nonce_drafts; cleanup' EXIT

# 2. Wait for the compose window to carry the nonce and have a rendered body, then raise it.
raised=""
for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
	raised="$(MAIL_NONCE="$NONCE" osascript 2>"$dir/raise_err" <<'APPLESCRIPT' || true
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
tell application "Mail" to activate
tell application "System Events" to tell process "Mail"
	set w to first window whose name is nonce
	perform action "AXRaise" of w
	set focused of w to true
	set wa to my findWeb(w, 0)
	if wa is missing value then error "no body web area in the compose window"
	-- A forward opens with the caret in the To: field, so a blind paste types the
	-- body into the address line. Focusing the body is what makes all three modes
	-- behave the same; on a reply it is a no-op.
	set value of attribute "AXFocused" of wa to true
	return "raised"
end tell
APPLESCRIPT
)"
	[ "$raised" = "raised" ] && break
	sleep 0.25
done
discard_message() {
	MAIL_MSG_ID="$NEWID" osascript >/dev/null 2>&1 <<'APPLESCRIPT' || true
set wanted to (system attribute "MAIL_MSG_ID") as integer
tell application "Mail"
	repeat with i from (count of outgoing messages) to 1 by -1
		if (id of outgoing message i) is wanted then delete outgoing message i
	end repeat
end tell
APPLESCRIPT
}
if [ "$raised" != "raised" ]; then
	discard_message
	echo "mail-draft: the compose window could not be reached, so the message was discarded: $(tail -n 1 "$dir/raise_err")" >&2
	exit 1
fi

# Reads the TOP of the composed body only. A whole-body walk costs one Apple event
# per element, so a long quoted original turns the check into a minute of round
# trips; the new text sits at the top, so the first few lines answer the question.
read_body_head() {
	MAIL_NONCE="$NONCE" osascript 2>/dev/null <<'APPLESCRIPT' || true
global collected, budget

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
	if (count of collected) ≥ budget then return
	tell application "System Events"
		try
			set kids to every UI element of el
		on error
			return
		end try
		repeat with k in kids
			if (count of collected) ≥ budget then return
			set rr to ""
			try
				set rr to (role of k) as string
			end try
			if rr is "AXStaticText" then
				try
					set end of collected to ((value of k) as string)
				end try
			end if
			my gather(k, depth + 1)
		end repeat
	end tell
end gather

set collected to {}
set budget to 8
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

# 3. Paste, then read the body back and check the first line of it arrived. The
#    pasteboard is machine-wide, so a concurrent copy can win the race; re-assert
#    and paste again rather than leaving a draft carrying somebody else's clipboard.
FIRSTLINE="$(grep -v '^[[:space:]]*$' "$dir/text" | head -1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
osascript -l JavaScript "$HERE/pasteboard.js" save "$dir" >/dev/null 2>&1 && RESTORE_PB="true"

pasted="false"
for attempt in 1 2 3; do
	osascript -l JavaScript "$HERE/pasteboard.js" load "$dir/html" "$dir/text" >/dev/null
	MAIL_NONCE="$NONCE" osascript >/dev/null 2>&1 <<'APPLESCRIPT'
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
tell application "Mail" to activate
tell application "System Events" to tell process "Mail"
	set w to first window whose name is nonce
	perform action "AXRaise" of w
	set focused of w to true
	set wa to my findWeb(w, 0)
	if wa is missing value then error "no body web area in the compose window"
	set value of attribute "AXFocused" of wa to true
	delay 0.3
	keystroke "v" using command down
end tell
APPLESCRIPT
	sleep 0.8
	# The FIRST line of the composed body must be our own first line. Searching the
	# whole body instead lets the quoted original answer for us: a reply to a mail
	# that happens to contain "Bonjour," reads as pasted when nothing was pasted.
	head_line="$(read_body_head | head -1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
	if [ -z "$FIRSTLINE" ] || [ "$head_line" = "$FIRSTLINE" ]; then
		pasted="true"
		break
	fi
	# Undo the wrong paste before trying again, so attempts cannot stack.
	MAIL_NONCE="$NONCE" osascript >/dev/null 2>&1 <<'APPLESCRIPT' || true
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
tell application "System Events" to tell process "Mail"
	set w to first window whose name is nonce
	perform action "AXRaise" of w
	set focused of w to true
	set wa to my findWeb(w, 0)
	if wa is not missing value then set value of attribute "AXFocused" of wa to true
	keystroke "z" using command down
end tell
APPLESCRIPT
	sleep 0.4
done

if [ "$pasted" != "true" ]; then
	echo "mail-draft: the body did not reach the compose window after 3 attempts" >&2
	exit 1
fi

# 4. Give the window its real subject back, then attach.
restore_subject

sweep_nonce_drafts
trap 'sweep_nonce_drafts; cleanup' EXIT

if [ -s "$dir/attach" ]; then
	MAIL_PAYLOAD_DIR="$dir" MAIL_MSG_ID="$NEWID" osascript >/dev/null <<'APPLESCRIPT'
on readText(p)
	try
		return (read (POSIX file p) as «class utf8»)
	on error
		return ""
	end try
end readText

on readLines(p)
	set raw to my readText(p)
	if raw is "" then return {}
	set AppleScript's text item delimiters to linefeed
	set parts to text items of raw
	set AppleScript's text item delimiters to ""
	set out to {}
	repeat with x in parts
		if (x as string) is not "" then set end of out to (x as string)
	end repeat
	return out
end readLines

-- Apple Mail resolves an attachment through an HFS alias, not a POSIX file:
-- the POSIX form is accepted and silently attaches nothing.
on toHFS(posixPath)
	set AppleScript's text item delimiters to "/"
	set parts to text items of posixPath
	set AppleScript's text item delimiters to ":"
	set hfs to "Macintosh HD" & (parts as string)
	set AppleScript's text item delimiters to ""
	return hfs
end toHFS

set d to (system attribute "MAIL_PAYLOAD_DIR")
set wanted to (system attribute "MAIL_MSG_ID") as integer
set theAttachments to my readLines(d & "/attach")

tell application "Mail"
	set msg to missing value
	repeat with m in (every outgoing message)
		try
			if (id of m) is wanted then set msg to m
		end try
	end repeat
	if msg is missing value then error "the draft went away before its attachments landed"
	tell msg
		repeat with p in theAttachments
			try
				make new attachment with properties {file name:((my toHFS(p as string)) as alias)} at after last paragraph
				delay 1
			on error errText
				error "attachment failed for " & (p as string) & ": " & errText
			end try
		end repeat
	end tell
end tell
APPLESCRIPT
fi

osascript -e 'tell application "Mail" to activate' >/dev/null
echo "drafted"
