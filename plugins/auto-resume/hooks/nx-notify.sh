#!/usr/bin/env bash
# Desktop banner for scheduled Claude jobs. Posts a clickable macOS notification
# via terminal-notifier; clicking opens $3 (a file path or URL). No-ops silently
# if terminal-notifier isn't installed, so callers never need to guard.
#
# Usage: nx-notify.sh <title> <message> [open-target]
#   open-target — a local path (auto-wrapped as file://) or a URL.
#
# Banners go to Notification Center and persist there, so a job that fires while
# you're away from the keyboard still greets you when you sit down.
set -euo pipefail

title="${1:-Claude jobs}"
message="${2:-done}"
open_target="${3:-}"

tn="$(command -v terminal-notifier 2>/dev/null || true)"
[ -z "$tn" ] && exit 0

args=(-title "$title" -message "$message" -group "claude-jobs" -sound default)
if [ -n "$open_target" ]; then
  case "$open_target" in
    *://*) args+=(-open "$open_target") ;;
    /*)    args+=(-open "file://$open_target") ;;
    *)     args+=(-open "file://$PWD/$open_target") ;;
  esac
fi

"$tn" "${args[@]}" >/dev/null 2>&1 || true
