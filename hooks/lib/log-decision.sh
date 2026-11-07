#!/usr/bin/env bash
# Shared decision-row sink for hook checks.
#
# One sink, one row shape, because the registry's per-check counts are only as true as
# the sink they read. A check that writes rows somewhere of its own is invisible to
# `scripts/check_inventory.py` and to every count built on the log — which reads as
# "never fired" rather than "logged elsewhere", and those two look identical.
#
# Row shape is the one REGISTRY.md documents:
#   {"ts","check","session","verdict","detail"}
#
# NEVER PRINTS a payload value: `detail` is a bounded 200-char fingerprint of the command
# or path that fired the check, so a row stays diagnostic without becoming a second copy
# of whatever the check was protecting.

# A write that fails is counted in its own file. Without the counter, "no rows" and
# "could not write" produce the same log, and every count read from it is a floor
# rather than a total — with nothing on disk saying so.
_bump_decision_health() {
  local health="${HOOK_STATE_ROOT:-$HOME/.claude/state}/hook-decisions.health"
  local n
  n=$(cat "$health" 2>/dev/null || echo 0)
  case "$n" in ''|*[!0-9]*) n=0 ;; esac
  # The braces carry the redirection: `cmd > file 2>/dev/null` silences the
  # command, while the shell reports a FAILED redirection itself, on its own
  # stderr, before the command ever runs. A guard that prints on every call in a
  # broken state is noise the host has no way to attribute.
  { printf '%s' "$((n + 1))" > "$health"; } 2>/dev/null || true
}


log_decision() { # <check_id> <verdict> <detail> [session_id] [mode]
  local sink="${HOOK_STATE_ROOT:-$HOME/.claude/state}/hook-decisions.jsonl"
  local detail mode_field=""
  # Every control character becomes a space before the value is quoted. A raw tab
  # or newline inside `detail` yields a line that is not JSON at all, so the row is
  # lost to every reader — and a newline does worse than corrupt one field: it
  # forges a second row that parses cleanly and names a check that never ran.
  detail=$(printf '%s' "$3" | head -c 200 \
    | tr '\n\r\t' '   ' | tr -d '\000-\010\013\014\016-\037' \
    | sed 's/\\/\\\\/g; s/"/\\"/g')
  [ -n "${5:-}" ] && mode_field=",\"mode\":\"$5\""
  case "${AGENT_HOOK_PROVIDER:-claude}" in
    claude) ;;
    *[!a-z]*) ;;
    *) mode_field="$mode_field,\"provider\":\"$AGENT_HOOK_PROVIDER\"" ;;
  esac
  mkdir -p "$(dirname "$sink")" 2>/dev/null || { _bump_decision_health; return 0; }
  { printf '{"ts":"%s","check":"%s","session":"%s","verdict":"%s","detail":"%s"%s}\n' \
      "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" "${4:-unknown}" "$2" "$detail" "$mode_field" \
      >> "$sink"; } 2>/dev/null || _bump_decision_health
}
