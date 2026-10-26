#!/bin/bash
# requires: bash, python3, cmux (the app's bundled CLI)
#
# Close the seat this session is sitting in, from inside it.
#
# A session cannot watch its own seat close: the close kills the shell that issued it, so
# whatever would have verified the result dies with the thing it was verifying. This script
# re-execs itself detached (reparented to PID 1) before touching anything, which is what makes
# the verification outlive the seat. Measured 2026-09-07: a nohup'd child of a closed cmux
# workspace keeps running with PPID 1.
#
# Three outcomes, never two. The seat is gone; the seat is still there; or the listing could
# not be read — and the third is not the first. A failed `workspace list` returns the same
# empty output as a successful close, so treating "no match" as proof would report success
# most confidently at the moment the CLI broke.
#
# The ref is resolved against the live listing before anything is armed — by ref or by UUID —
# because "the listing does not carry it" and "the seat is already closed" are the same reading,
# and the second one exits 0.
#
#   self-close.sh <workspace-ref|uuid> [--delay <s>] [--reason <text>] [--timeout <s>]
#
# Exit 0 close verified, or an EMPTY ref (a session in no seat: nothing to close) · 1 close failed
# or unverifiable (a problem seat was raised), or the listing could not be read · 2 usage, or a
# ref naming no live workspace.

set -uo pipefail

LOG="${SELF_CLOSE_LOG:-$HOME/.claude/logs/cmux-self-close.jsonl}"
REF=""; DELAY=8; REASON="work finished"; TIMEOUT=30

while [ $# -gt 0 ]; do
  case "$1" in
    --delay)   DELAY="$2"; shift 2 ;;
    --reason)  REASON="$2"; shift 2 ;;
    --timeout) TIMEOUT="$2"; shift 2 ;;
    --detached) DETACHED=1; shift ;;
    workspace:*|[0-9A-Fa-f]*-*) REF="$1"; shift ;;
    "") NO_SEAT=1; shift ;;
    *) echo "usage: self-close.sh <workspace-ref|uuid> [--delay s] [--reason text] [--timeout s]" >&2; exit 2 ;;
  esac
done
# An EMPTY ref is a session with no seat — `"$CMUX_WORKSPACE_ID"` expanded from an environment
# the terminal never exported into. That is "nothing to close", exit 0, so a caller passes the
# variable unguarded; a ref the listing does not carry stays a refusal below. No ref at all is
# still a usage error. It is decided before the CLI is resolved: a host with no seat is the one
# most likely to have no terminal wired either.
if [ -n "${NO_SEAT:-}" ] && [ -z "$REF" ]; then
  echo "self-close: no seat (empty ref) — nothing to close." >&2; exit 0
fi
[ -n "$REF" ] || { echo "self-close: no workspace ref given" >&2; exit 2; }

# The CLI is `cmux` on PATH; CMUX_BIN overrides it (the tests' stand-in).
C="${CMUX_BIN:-$(command -v cmux)}"
[ -n "$C" ] || { echo "$(basename "$0"): cmux is not on PATH — /Applications/cmux.app/Contents/Resources/bin is missing from it" >&2; exit 2; }

log() {  # log <event> <detail>
  mkdir -p "$(dirname "$LOG")"
  python3 - "$LOG" "$REF" "$1" "$2" "$REASON" <<'PY' 2>/dev/null || true
import json, sys, datetime
path, ref, event, detail, reason = sys.argv[1:6]
row = {"at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
       "ref": ref, "event": event, "detail": detail, "reason": reason}
with open(path, "a") as fh:
    fh.write(json.dumps(row) + "\n")
PY
}

# ── Detach before acting. Without this the close kills us mid-verify. ─────────────────────
if [ -z "${DETACHED:-}" ]; then
  # Resolve the argument against the live listing, and refuse to arm on anything it does not
  # name. A ref the listing does not carry reads as "already gone" to the detached watcher,
  # which then exits 0 without ever issuing a close — a success report for a seat still
  # standing. Measured 2026-09-07: a `workspace:<uuid>` argument took exactly that path.
  RESOLVED=$(CMUX_BIN="$C" SC_REF="$REF" python3 -c '
import json,os,subprocess
C=os.environ["CMUX_BIN"]; want=os.environ["SC_REF"]
key=want.split(":",1)[1] if want.startswith("workspace:") else want
try:
    d=json.loads(subprocess.run([C,"workspace","list","--json","--id-format","both"],
                                capture_output=True,text=True,timeout=15).stdout)
except Exception:
    print("UNREADABLE"); raise SystemExit(0)
for w in d.get("workspaces") or []:
    if w.get("ref")==want or str(w.get("id","")).lower()==key.lower():
        print(w.get("ref")); raise SystemExit(0)
print("ABSENT")
' 2>/dev/null)
  case "$RESOLVED" in
    workspace:*) REF="$RESOLVED" ;;
    ABSENT)
      log "arm-refused" "$REF names no live workspace"
      echo "self-close: $REF names no live workspace — nothing armed." >&2; exit 2 ;;
    *)
      log "arm-refused" "workspace listing unreadable; existence unconfirmed"
      echo "self-close: cannot read the workspace listing, so $REF is unconfirmed — nothing armed." >&2
      exit 1 ;;
  esac

  log "arming" "delay=${DELAY}s timeout=${TIMEOUT}s"
  # `nohup ... &` only. There is no setsid on macOS, and the earlier version called it: the
  # exec failed, the child never ran, and the parent still printed "armed" — an arming message
  # that was an announcement rather than evidence. Measured 2026-09-07: a plain nohup'd child
  # survives its cmux seat closing and reparents to PID 1, which is all the detach this needs.
  nohup "$0" "$REF" --detached --delay "$DELAY" --reason "$REASON" \
        --timeout "$TIMEOUT" >/dev/null 2>&1 &
  child=$!
  # Prove it is alive before claiming it. A child that died on exec looks exactly like one
  # doing its job, and the seat then stays open with nothing watching it.
  sleep 0.5
  if ! kill -0 "$child" 2>/dev/null; then
    log "arm-failed" "detached child $child did not start"
    echo "self-close: FAILED to arm for $REF — the detached watcher did not start. Seat untouched." >&2
    exit 1
  fi
  echo "self-close armed for $REF in ${DELAY}s (pid $child, log $LOG)"
  exit 0
fi

# ── Detached from here. The seat may die under us at any point. ───────────────────────────
sleep "$DELAY"

# seat_state -> "present" | "absent" | "unknown". Never collapses unknown into absent.
seat_state() {
  local out
  out=$("$C" workspace list --json 2>/dev/null) || { echo unknown; return; }
  [ -n "$out" ] || { echo unknown; return; }
  printf '%s' "$out" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
    refs = {w.get("ref") for w in d.get("workspaces", [])}
except Exception:
    print("unknown"); sys.exit()
print("present" if sys.argv[1] in refs else "absent")
' "$REF" 2>/dev/null || echo unknown
}

before=$(seat_state)
if [ "$before" = "absent" ]; then
  log "noop" "seat already gone before the close"
  exit 0
fi

log "closing" "state_before=$before"
close_err=$("$C" workspace close "$REF" --force 2>&1 >/dev/null)
rc=$?

# Corroborate: one reading is not a verdict. Require two consecutive "absent" before
# calling it closed, and never accept "unknown" as either answer.
deadline=$(( $(date +%s) + TIMEOUT ))
streak=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  case "$(seat_state)" in
    absent)  streak=$((streak+1)); [ "$streak" -ge 2 ] && { log "closed" "close_rc=$rc"; exit 0; } ;;
    present) streak=0 ;;
    unknown) streak=0 ;;
  esac
  sleep 1
done

# ── Failure. Raise a seat that says so, carrying the log. ─────────────────────────────────
final=$(seat_state)
log "failed" "close_rc=$rc close_err=${close_err:-none} final_state=$final timeout=${TIMEOUT}s"

if "$C" workspace create --name "⚠️ self-close failed" --cwd "$HOME" --focus false \
     --command "printf '%s\n' 'self-close could not verify that $REF closed.' \
       'close exit code: $rc   ·   last read state: $final' \
       'Reason the session gave: $REASON' '' \
       'Recent decisions:' ; tail -5 '$LOG' ; printf '%s\n' '' \
       'Close it by hand:  $C workspace close $REF --force' ; exec \$SHELL" >/dev/null 2>&1
then
  log "raised" "problem seat created"
else
  # The alarm runs on the same CLI that just failed, so it can fail for the same reason.
  # A breadcrumb on disk is the one channel that does not depend on cmux answering.
  crumb="$HOME/.claude/logs/cmux-self-close-FAILED.txt"
  { echo "[$(date '+%F %T')] self-close could not close $REF and could not raise a seat."
    echo "close exit code: $rc   ·   last read state: $final   ·   reason: $REASON"
    echo "cmux binary: $C"
    echo "close it by hand once cmux answers:  cmux workspace close $REF --force"
  } >> "$crumb" 2>/dev/null
  log "raise-failed" "cmux unreachable; breadcrumb at $crumb"
fi

exit 1
