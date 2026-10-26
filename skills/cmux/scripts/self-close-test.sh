#!/bin/bash
# requires: bash, python3
#
# Contract tests for self-close.sh, against the stateful stand-in for the cmux CLI
# (seat-test-stub.py beside this file). Nothing here touches the real sidebar.
#
#   bash self-close-test.sh              run every case; exit 1 on any failure
#   SELF_CLOSE=<path> bash self-close-test.sh   run against another copy — how a mutation is proved red
#
# Each case builds the sidebar it needs, runs the helper as a session in a seat would, waits for the detached watcher, and asserts the exit code, the seat's presence in the
# stub's own listing, and the events the helper logged. The detached half is real: the watcher
# reparents to PID 1 and is waited on through its log rather than its pid.

set -u
. "$(dirname "$0")/seat-test-lib.sh"
S="${SELF_CLOSE:-$HERE/self-close.sh}"

reset() {  # reset <workspaces-json>
  printf '{"groups":[],"workspaces":[%s]}' "$1" > "$T/state.json"
  : > "$T/calls.log"; : > "$T/log.jsonl"; rm -f "$T/close-noop"
}
field_eq() {  # field_eq <value> <field> — True when any listed workspace carries <field> == <value>
  python3 -c 'import json,sys; print(any(w.get(sys.argv[3])==sys.argv[2] for w in json.load(open(sys.argv[1]))["workspaces"]))' "$T/state.json" "$1" "$2"
}
present() { field_eq "$1" ref; }
titled() { field_eq "$1" title; }
events() { sed -nE 's/.*"event": "([^"]+)".*/\1/p' "$T/log.jsonl" | paste -sd, -; }
await_event() {  # await_event <event> <seconds> — the detached watcher's word, read off its log
  local deadline=$(( $(date +%s) + $2 ))
  while [ "$(date +%s)" -lt "$deadline" ]; do
    grep -q "\"event\": \"$1\"" "$T/log.jsonl" && return 0
    sleep 0.5
  done
  return 1
}
run() {  # run <args...> — the helper, wired to the stub and a private log; prints its exit code
  CMUX_BIN="$T/cmux" SELF_CLOSE_LOG="$T/log.jsonl" "$S" "$@" >"$T/out" 2>"$T/err"; echo $?
}
verdict() {  # verdict <label> <ok-bool> <detail>
  if [ "$2" = true ]; then PASS=$((PASS + 1)); echo "  ok    $1"
  else FAIL=$((FAIL + 1)); echo "  FAIL  $1 — $3"; sed 's/^/        /' "$T/err" 2>/dev/null; fi
}

# ── an empty ref — a session in no seat — is nothing to close ─────────────────────────────
reset "$(ws 1 "$T")"
rc=$(run "" --delay 0)
ok=false; [ "$rc" = 0 ] && [ -z "$(events)" ] && [ "$(present workspace:1)" = True ] && ok=true
verdict "an empty ref: exit 0, nothing armed, nothing logged, the listed seat untouched" $ok "exit $rc, events '$(events)'"

# ── the same, on a host with no terminal wired at all ─────────────────────────────────────
reset "$(ws 1 "$T")"
mkdir -p "$T/nohome"
rc=$( CMUX_BIN= PATH=/usr/bin:/bin HOME="$T/nohome" SELF_CLOSE_LOG="$T/log.jsonl" "$S" "" --delay 0 >"$T/out" 2>"$T/err"; echo $? )
ok=false; [ "$rc" = 0 ] && [ -z "$(events)" ] && ok=true
verdict "an empty ref where cmux is not on PATH: still exit 0 — no seat needs no CLI" $ok "exit $rc, events '$(events)', err '$(cat "$T/err")'"

# ── a ref the listing does not carry arms nothing ─────────────────────────────────────────
reset "$(ws 1 "$T")"
rc=$(run workspace:9 --delay 0)
ok=false; [ "$rc" = 2 ] && [ "$(events)" = "arm-refused" ] && [ "$(present workspace:1)" = True ] && ok=true
verdict "a ref naming no live workspace: exit 2, arm-refused, the listed seat untouched" $ok "exit $rc, events '$(events)'"

# ── an unreadable listing arms nothing, and is not read as absent ─────────────────────────
reset "$(ws 1 "$T")"; rm -f "$T/state.json"
rc=$(run workspace:1 --delay 0)
ok=false; [ "$rc" = 1 ] && [ "$(events)" = "arm-refused" ] && ok=true
verdict "an unreadable listing: exit 1, arm-refused — unknown is not absent" $ok "exit $rc, events '$(events)'"

# ── the success path: armed, closed, confirmed twice ──────────────────────────────────────
reset "$(ws 1 "$T"),$(ws 2 "$T")"
rc=$(run workspace:1 --delay 0 --reason "NEX-0 merged")
armed=false; grep -q "self-close armed for workspace:1" "$T/out" && armed=true
await_event closed 15
ok=false; [ "$rc" = 0 ] && [ "$armed" = true ] && [ "$(present workspace:1)" = False ] && [ "$(present workspace:2)" = True ] \
  && [ "$(events)" = "arming,closing,closed" ] && ok=true
verdict "the success path: exit 0 on arming, the seat gone from the listing, its neighbour standing, arming→closing→closed logged" $ok "exit $rc, armed=$armed, seat present=$(present workspace:1), events '$(events)'"

# ── a seat closed by somebody else first is no failure ────────────────────────────────────
reset "$(ws 1 "$T")"
rc=$(run workspace:1 --delay 2)
printf '{"groups":[],"workspaces":[]}' > "$T/state.json"   # another seat's close lands first
await_event noop 15
ok=false; [ "$rc" = 0 ] && [ "$(events)" = "arming,noop" ] && ok=true
verdict "a seat already gone when the watcher fires: noop, no close issued, no problem seat" $ok "exit $rc, events '$(events)'"

# ── the forced failure: the close lands and removes nothing ───────────────────────────────
reset "$(ws 1 "$T")"; touch "$T/close-noop"
rc=$(run workspace:1 --delay 0 --timeout 3 --reason "forced")
await_event raised 20
ok=false; [ "$rc" = 0 ] && [ "$(present workspace:1)" = True ] && [ "$(titled '⚠️ self-close failed')" = True ] \
  && [ "$(events)" = "arming,closing,failed,raised" ] && ok=true
verdict "the forced failure: the seat still listed after the timeout, a '⚠️ self-close failed' seat raised, arming→closing→failed→raised logged" $ok "exit $rc, seat present=$(present workspace:1), problem seat=$(titled '⚠️ self-close failed'), events '$(events)'"

finish
