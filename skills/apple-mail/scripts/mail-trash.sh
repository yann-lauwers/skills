#!/bin/bash
# requires: osascript (macOS), Apple Mail
# Moves one message to its account's Trash mailbox.
# AppleScript only: needs Automation permission for Mail, never Full Disk Access.
#
# Recoverable: the message sits in Trash until Mail's own retention empties it,
# and can be dragged back. Nothing here empties the Trash.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
	cat >&2 <<'USAGE'
usage: mail-trash.sh --id <message-id> [--account <name>] [--mailbox <name>]

Prints the account and the trash mailbox the message landed in.
--account and --mailbox narrow the hunt; without them every mailbox is walked.
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
		*) echo "mail-trash: unknown argument $1" >&2; usage ;;
	esac
done

[ -n "$ID" ] || { echo "mail-trash: --id is required" >&2; usage; }
printf '%s' "$ID" | grep -Eq '^[0-9]+$' || { echo "mail-trash: --id must be numeric, got '$ID'" >&2; exit 1; }

M_ID="$ID" M_ACCOUNT="$ACCOUNT" M_MAILBOX="$MAILBOX" M_TRASH_NAMES="$(cat "$HERE/trash-names")" osascript -l JavaScript <<'JXA'
ObjC.import("Foundation");
const env = ObjC.unwrap($.NSProcessInfo.processInfo.environment);
const get = (k) => (env[k] === undefined ? "" : ObjC.unwrap(env[k]));

const wantId = parseInt(get("M_ID"), 10);
const accountName = get("M_ACCOUNT");
const mailboxName = get("M_MAILBOX");

const Mail = Application("Mail");

// Mail names its trash differently per provider, so the mailbox is matched by
// what it is called rather than assumed to be "Trash".
const TRASH_NAMES = get("M_TRASH_NAMES").split("\n").filter(Boolean);

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

const current = found.box.name();
if (TRASH_NAMES.includes(current.toLowerCase())) {
  JSON.stringify({ id: wantId, account: found.account.name(), mailbox: current, moved: false, reason: "already in trash" }, null, 2);
} else {
  const trash = found.account.mailboxes().find((b) => TRASH_NAMES.includes(b.name().toLowerCase()));
  if (!trash) throw new Error(`account "${found.account.name()}" has no trash mailbox`);
  const subject = found.message.subject();
  found.message.mailbox = trash;
  JSON.stringify({ id: wantId, account: found.account.name(), subject, from: current, mailbox: trash.name(), moved: true }, null, 2);
}
JXA
