#!/bin/bash
# requires: osascript (macOS), python3, Apple Mail
# Lists the accounts configured in Apple Mail, as JSON.
# AppleScript only: needs Automation permission for Mail, never Full Disk Access.
set -euo pipefail

RS=$'\x1e'
FS=$'\x1f'

raw=$(osascript <<'APPLESCRIPT'
tell application "Mail"
	set rs to (ASCII character 30)
	set fs to (ASCII character 31)
	set out to ""
	repeat with a in accounts
		set AppleScript's text item delimiters to ","
		set addrs to (email addresses of a) as text
		set AppleScript's text item delimiters to ""
		set out to out & (name of a) & fs & addrs & fs & (account type of a as string) & fs & (enabled of a as string) & rs
	end repeat
	return out
end tell
APPLESCRIPT
)

RAW="$raw" MFS="$FS" MRS="$RS" python3 - <<'PY'
import json, os
raw, fs, rs = os.environ["RAW"], os.environ["MFS"], os.environ["MRS"]
out = []
for rec in raw.split(rs):
    rec = rec.strip("\n")
    if not rec:
        continue
    parts = rec.split(fs)
    name, emails, kind, enabled = parts[0], parts[1], parts[2], parts[3]
    out.append({
        "name": name,
        "emails": [e for e in emails.split(",") if e],
        "type": kind,
        "enabled": enabled == "true",
    })
print(json.dumps(out, indent=2, ensure_ascii=False))
PY
