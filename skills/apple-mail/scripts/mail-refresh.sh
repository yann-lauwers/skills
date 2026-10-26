#!/bin/bash
set -euo pipefail

usage() {
	cat >&2 <<'USAGE'
usage: mail-refresh.sh [--account <name>] [--timeout <seconds>]

Asks Apple Mail to fetch new mail, then waits until Mail's index stops growing,
so mail-search.sh sees what just arrived. Prints the newest indexed message and
how many arrived while it waited.

--account  an account name from mail-accounts.sh. Omitted, every account.
--timeout  the longest wait. Default 60.
USAGE
	exit 2
}

ACCOUNT="" TIMEOUT="60"
while [ $# -gt 0 ]; do
	case "$1" in
		--account) ACCOUNT="$2"; shift 2 ;;
		--timeout) TIMEOUT="$2"; shift 2 ;;
		-h|--help) usage ;;
		*) echo "mail-refresh: unknown argument $1" >&2; usage ;;
	esac
done
printf '%s' "$TIMEOUT" | grep -Eq '^[1-9][0-9]*$' || { echo "mail-refresh: --timeout must be a positive integer" >&2; exit 1; }
ls "$HOME/Library/Mail/" >/dev/null 2>&1 || { echo "mail-refresh: Operation not permitted on ~/Library/Mail/" >&2; exit 1; }

V="$(plutil -extract LastUsedVersionDirectoryName raw "$HOME/Library/Mail/PersistenceInfo.plist")"
INDEX="$HOME/Library/Mail/$V/MailData/Envelope Index"
newest() { sqlite3 -readonly "$INDEX" "SELECT max(ROWID) || ' ' || max(date_received) FROM messages"; }

before="$(newest)"
M_ACCOUNT="$ACCOUNT" osascript -l JavaScript <<'JXA' >/dev/null
ObjC.import("Foundation");
const name = ObjC.unwrap($.NSProcessInfo.processInfo.environment).M_ACCOUNT;
const Mail = Application("Mail");
const account = name ? ObjC.unwrap(name) : "";
if (account) Mail.checkForNewMail({ for: Mail.accounts.byName(account) });
else Mail.checkForNewMail();
JXA

last="$before" stable=0 waited=0
while [ "$waited" -lt "$TIMEOUT" ] && [ "$stable" -lt 5 ]; do
	sleep 1
	waited=$((waited + 1))
	now="$(newest)"
	if [ "$now" = "$last" ]; then stable=$((stable + 1)); else stable=0; last="$now"; fi
done

B_ROWID="${before%% *}" N_DATE="${last##* }" WAITED="$waited" STABLE="$stable" INDEX="$INDEX" python3 -I - <<'PY'
import json, os, sqlite3
from datetime import datetime, timezone
e = os.environ
db = sqlite3.connect(f"file:{e['INDEX']}?mode=ro", uri=True)
arrived = db.execute("SELECT count(*) FROM messages WHERE ROWID > ?", (int(e["B_ROWID"]),)).fetchone()[0]
print(json.dumps({
    "newest": datetime.fromtimestamp(int(e["N_DATE"]), timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
    "arrived": arrived,
    "settled": int(e["STABLE"]) >= 5,
    "waited_seconds": int(e["WAITED"]),
}, indent=2))
PY
