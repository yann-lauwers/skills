#!/bin/bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
	cat >&2 <<'USAGE'
usage: mail-search.sh [--from <text>] [--after <YYYY-MM-DD>] [--before <YYYY-MM-DD>]
                      [--text <text>] [--limit <n>] [--scan <n>]

--from    matches the sender's address or display name, case-insensitive.
--after   received on or after this day.
--before  received before this day.
--text    matches the subject or the decoded body, case-insensitive.
--limit   how many matches, newest first. Default 20.
--scan    with --text, how many of the newest candidates are opened. Default 5000.

Mail writes new messages into its index as it syncs; run mail-refresh.sh first
when the answer depends on what arrived in the last minutes.
USAGE
	exit 2
}

FROM="" AFTER="" BEFORE="" TEXT="" LIMIT="20" SCAN="5000"

while [ $# -gt 0 ]; do
	case "$1" in
		--from) FROM="$2"; shift 2 ;;
		--after) AFTER="$2"; shift 2 ;;
		--before) BEFORE="$2"; shift 2 ;;
		--text) TEXT="$2"; shift 2 ;;
		--limit) LIMIT="$2"; shift 2 ;;
		--scan) SCAN="$2"; shift 2 ;;
		-h|--help) usage ;;
		*) echo "mail-search: unknown argument $1" >&2; usage ;;
	esac
done

for n in "$LIMIT" "$SCAN"; do
	printf '%s' "$n" | grep -Eq '^[1-9][0-9]*$' || { echo "mail-search: --limit and --scan must be positive integers" >&2; exit 1; }
done
for d in "$AFTER" "$BEFORE"; do
	[ -z "$d" ] || printf '%s' "$d" | grep -Eq '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' || { echo "mail-search: dates are YYYY-MM-DD, got '$d'" >&2; exit 1; }
done

ls "$HOME/Library/Mail/" >/dev/null 2>&1 || { echo "mail-search: Operation not permitted on ~/Library/Mail/" >&2; exit 1; }

ACCOUNTS="$(osascript -l JavaScript <<'JXA'
const Mail = Application("Mail");
Mail.accounts().map((a) => `${a.id()}\t${a.name()}`).join("\n");
JXA
)"

M_FROM="$FROM" M_AFTER="$AFTER" M_BEFORE="$BEFORE" M_TEXT="$TEXT" M_LIMIT="$LIMIT" M_SCAN="$SCAN" M_ACCOUNTS="$ACCOUNTS" M_TRASH="$HERE/trash-names" python3 -I - <<'PY'
import email, html, json, os, plistlib, re, sqlite3, sys
from datetime import datetime, timezone
from email import policy
from urllib.parse import unquote, urlparse

env = os.environ
mail_root = os.path.expanduser("~/Library/Mail")
with open(os.path.join(mail_root, "PersistenceInfo.plist"), "rb") as f:
    base = os.path.join(mail_root, plistlib.load(f)["LastUsedVersionDirectoryName"])

accounts = dict(line.split("\t", 1) for line in env["M_ACCOUNTS"].splitlines() if "\t" in line)
trash_names = {l.strip() for l in open(env["M_TRASH"]) if l.strip()}
text = env["M_TEXT"].lower()
limit, scan = int(env["M_LIMIT"]), int(env["M_SCAN"])

def day(s):
    return int(datetime.strptime(s, "%Y-%m-%d").timestamp())

where, args = ["1=1"], []
if env["M_FROM"]:
    where.append("(addresses.address LIKE ? OR addresses.comment LIKE ?)")
    args += [f"%{env['M_FROM']}%"] * 2
if env["M_AFTER"]:
    where.append("messages.date_received >= ?"); args.append(day(env["M_AFTER"]))
if env["M_BEFORE"]:
    where.append("messages.date_received < ?"); args.append(day(env["M_BEFORE"]))

db = sqlite3.connect(f"file:{base}/MailData/Envelope Index?mode=ro", uri=True)
rows = db.execute(f"""
    SELECT messages.ROWID, messages.date_received, messages.read, addresses.address,
           addresses.comment, subjects.subject, mailboxes.url
    FROM messages
    LEFT JOIN addresses ON addresses.ROWID = messages.sender
    LEFT JOIN subjects  ON subjects.ROWID = messages.subject
    LEFT JOIN mailboxes ON mailboxes.ROWID = messages.mailbox
    WHERE messages.deleted = 0 AND {' AND '.join(where)}
    ORDER BY messages.date_received DESC""", args)

files = None
def emlx_path(rowid):
    global files
    if files is None:
        files = {}
        for root, _, names in os.walk(base):
            for n in names:
                if n.endswith(".emlx"):
                    files[n.split(".")[0]] = os.path.join(root, n)
    return files.get(str(rowid))

def body_text(path):
    raw = open(path, "rb").read()
    nl = raw.index(b"\n")
    msg = email.message_from_bytes(raw[nl + 1 : nl + 1 + int(raw[:nl])], policy=policy.default)
    parts = []
    for part in msg.walk():
        if part.get_content_type() in ("text/plain", "text/html"):
            try:
                c = part.get_content()
            except Exception:
                continue
            if part.get_content_type() == "text/html":
                c = html.unescape(re.sub(r"<[^>]+>", " ", c))
            parts.append(c)
    return "\n".join(parts).lower()

out, opened = [], 0
for rowid, received, read, address, name, subject, url in rows:
    u = urlparse(url or "")
    mailbox = unquote(u.path.rsplit("/", 1)[-1])
    if mailbox.lower() in trash_names:
        continue
    if text and text not in (subject or "").lower():
        if opened >= scan:
            reached = datetime.fromtimestamp(received).strftime("%Y-%m-%d")
            sys.stderr.write(f"mail-search: stopped after opening {scan} messages, back to {reached}; raise --scan or narrow --after/--before to go further\n")
            break
        path = emlx_path(rowid)
        opened += 1
        if not path or text not in body_text(path):
            continue
    out.append({
        "id": rowid,
        "date": datetime.fromtimestamp(received, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "read": bool(read),
        "from_name": name or "",
        "from_address": address or "",
        "subject": subject or "",
        "mailbox": mailbox,
        "account": accounts.get(u.netloc, u.netloc),
    })
    if len(out) >= limit:
        break
print(json.dumps(out, indent=2, ensure_ascii=False))
PY
