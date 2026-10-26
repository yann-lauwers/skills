#!/bin/bash
# requires: osascript (macOS), Apple Mail
# Reads one message out of Apple Mail as JSON — headers, body text, attachment names.
# AppleScript only: needs Automation permission for Mail, never Full Disk Access.
#
# Takes the numeric id mail-list.sh prints. Ids are Apple Mail's own and are not
# stable across a re-index, so read the id in the same session you act on it.
set -euo pipefail

usage() {
	cat >&2 <<'USAGE'
usage: mail-read.sh --id <message-id> [--account <name>] [--mailbox <name>]

--account and --mailbox narrow the hunt. Without them every mailbox of every
account is walked, which is correct and slower.
USAGE
	exit 2
}

ID="" ACCOUNT="" MAILBOX=""

while [ $# -gt 0 ]; do
	case "$1" in
		--id) ID="$2"; shift 2 ;;
		--account) ACCOUNT="$2"; shift 2 ;;
		--mailbox) MAILBOX="$2"; shift 2 ;;
		-h|--help) usage ;;
		*) echo "mail-read: unknown argument $1" >&2; usage ;;
	esac
done

[ -n "$ID" ] || { echo "mail-read: --id is required" >&2; usage; }
printf '%s' "$ID" | grep -Eq '^[0-9]+$' || { echo "mail-read: --id must be numeric, got '$ID'" >&2; exit 1; }

M_ID="$ID" M_ACCOUNT="$ACCOUNT" M_MAILBOX="$MAILBOX" osascript -l JavaScript <<'JXA'
ObjC.import("Foundation");
const env = ObjC.unwrap($.NSProcessInfo.processInfo.environment);
const get = (k) => (env[k] === undefined ? "" : ObjC.unwrap(env[k]));

const wantId = parseInt(get("M_ID"), 10);
const accountName = get("M_ACCOUNT");
const mailboxName = get("M_MAILBOX");

const Mail = Application("Mail");

function findMessage() {
  const accounts = accountName ? [Mail.accounts.whose({ name: accountName })[0]] : Mail.accounts();
  for (const account of accounts) {
    const boxes = mailboxName ? [account.mailboxes.whose({ name: mailboxName })[0]] : account.mailboxes();
    for (const box of boxes) {
      try {
        const hit = box.messages.whose({ id: wantId })[0];
        if (hit.exists()) return { message: hit, box, account };
      } catch (e) {
        // A mailbox that refuses the query is one this message is not in.
      }
    }
  }
  return null;
}

const found = findMessage();
if (!found) throw new Error(`message ${wantId} was not found in Apple Mail`);

const m = found.message;
const addresses = (list) => {
  try {
    return list().map((r) => r.address());
  } catch (e) {
    return [];
  }
};

let attachments = [];
try {
  attachments = m.mailAttachments().map((a) => ({ name: a.name(), size: a.fileSize() }));
} catch (e) {
  attachments = [];
}

JSON.stringify({
  id: m.id(),
  account: found.account.name(),
  mailbox: found.box.name(),
  subject: m.subject(),
  from: m.sender(),
  to: addresses(() => m.toRecipients),
  cc: addresses(() => m.ccRecipients),
  reply_to: (() => { try { return m.replyTo(); } catch (e) { return ""; } })(),
  date_sent: (() => { const d = m.dateSent(); return d ? d.toISOString() : ""; })(),
  date_received: (() => { const d = m.dateReceived(); return d ? d.toISOString() : ""; })(),
  read: m.readStatus(),
  message_id: (() => { try { return m.messageId(); } catch (e) { return ""; } })(),
  attachments,
  body: m.content(),
}, null, 2);
JXA
