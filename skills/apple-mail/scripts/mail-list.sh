#!/bin/bash
# requires: osascript (macOS), python3, Apple Mail
# Lists recent messages from Apple Mail as JSON, newest first.
# AppleScript only: needs Automation permission for Mail, never Full Disk Access.
#
# Each message comes back with the numeric `id` that mail-read.sh, mail-draft.sh
# --reply-to and mail-trash.sh take.
set -euo pipefail

usage() {
	cat >&2 <<'USAGE'
usage: mail-list.sh [--account <name>] [--mailbox <name>] [--limit <n>] [--unread-only]

--account   an account name from mail-accounts.sh. Omitted, the unified inbox is read.
--mailbox   a mailbox of that account. Requires --account. Default: that account's inbox.
--limit     how many messages, newest first. Default 20.

Reading properties over the Apple event bridge costs seconds, not milliseconds.
Ask for the smallest --limit that answers the question.
USAGE
	exit 2
}

ACCOUNT="" MAILBOX="" LIMIT="20" UNREAD_ONLY="false"

while [ $# -gt 0 ]; do
	case "$1" in
		--account) ACCOUNT="$2"; shift 2 ;;
		--mailbox) MAILBOX="$2"; shift 2 ;;
		--limit) LIMIT="$2"; shift 2 ;;
		--unread-only) UNREAD_ONLY="true"; shift ;;
		-h|--help) usage ;;
		*) echo "mail-list: unknown argument $1" >&2; usage ;;
	esac
done

printf '%s' "$LIMIT" | grep -Eq '^[1-9][0-9]*$' || { echo "mail-list: --limit must be a positive integer" >&2; exit 1; }
if [ -n "$MAILBOX" ] && [ -z "$ACCOUNT" ]; then
	echo "mail-list: --mailbox needs --account, because mailbox names repeat across accounts" >&2
	exit 1
fi

RS=$'\x1e'
FS=$'\x1f'

raw=$(M_ACCOUNT="$ACCOUNT" M_MAILBOX="$MAILBOX" M_LIMIT="$LIMIT" M_UNREAD="$UNREAD_ONLY" osascript -l JavaScript <<'JXA'
ObjC.import("Foundation");
const env = ObjC.unwrap($.NSProcessInfo.processInfo.environment);
const get = (k) => (env[k] === undefined ? "" : ObjC.unwrap(env[k]));

const accountName = get("M_ACCOUNT");
const mailboxName = get("M_MAILBOX");
const limit = parseInt(get("M_LIMIT"), 10);
const unreadOnly = get("M_UNREAD") === "true";

const Mail = Application("Mail");

function resolveBox() {
  if (!accountName) return Mail.inbox();
  const account = Mail.accounts.whose({ name: accountName })[0];
  if (!account.exists()) throw new Error(`no account named "${accountName}"`);
  if (!mailboxName) return account.mailboxes.whose({ name: "INBOX" })[0].exists()
    ? account.mailboxes.whose({ name: "INBOX" })[0]
    : account.mailboxes.whose({ name: "Inbox" })[0];
  const box = account.mailboxes.whose({ name: mailboxName })[0];
  if (!box.exists()) throw new Error(`account "${accountName}" has no mailbox "${mailboxName}"`);
  return box;
}

const box = resolveBox();
const source = unreadOnly ? box.messages.whose({ readStatus: false }) : box.messages;

// One Apple event per property across the whole collection beats one event per
// message: the round trip, not the row count, is what costs.
const ids = source.id();
const take = Math.min(limit, ids.length);
if (take === 0) {
  "";
} else {
  const subjects = source.subject();
  const senders = source.sender();
  const dates = source.dateReceived();
  const reads = source.readStatus();
  const mailboxes = source.mailbox.name();
  const accounts = source.mailbox.account.name();

  const RS = String.fromCharCode(30);
  const FS = String.fromCharCode(31);
  const rows = [];
  for (let i = 0; i < take; i++) {
    rows.push([
      ids[i],
      dates[i] ? dates[i].toISOString() : "",
      reads[i],
      senders[i] || "",
      (subjects[i] || "").replace(/[\x1e\x1f]/g, " "),
      mailboxes[i] || "",
      accounts[i] || "",
    ].join(FS));
  }
  rows.join(RS);
}
JXA
)

RAW="$raw" MFS="$FS" MRS="$RS" M_ACCOUNT="$ACCOUNT" python3 - <<'PY'
import json, os, re
raw, fs, rs = os.environ["RAW"], os.environ["MFS"], os.environ["MRS"]
account = os.environ["M_ACCOUNT"]

def split_sender(s):
    m = re.match(r'^\s*"?(.*?)"?\s*<([^>]+)>\s*$', s)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return "", s.strip()

out = []
for rec in raw.split(rs):
    rec = rec.strip("\n")
    if not rec:
        continue
    parts = rec.split(fs)
    if len(parts) < 7:
        continue
    mid, date, read, sender, subject, mailbox, acct = parts[:7]
    name, address = split_sender(sender)
    out.append({
        "id": int(mid),
        "date": date,
        "read": read == "true",
        "from_name": name,
        "from_address": address,
        "subject": subject,
        "mailbox": mailbox,
        "account": acct or account,
    })
print(json.dumps(out, indent=2, ensure_ascii=False))
PY
