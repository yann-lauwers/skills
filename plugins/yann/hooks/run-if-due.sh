#!/usr/bin/env bash
# Power-off catch-up guard for scheduled Claude jobs.
#
# launchd calls this instead of the job script directly. Paired with
# RunAtLoad=true in the plist, it makes a job missed during a full shutdown run
# at the next login: StartCalendarInterval handles the normal on-time / on-wake
# case, and RunAtLoad handles the cold-boot case. The stamp guard ensures the
# job runs at most once per cadence window, so repeated logins/loads don't
# re-fire it.
#
# Usage: run-if-due.sh <job-id> <daily|weekly> <command> [args...]
#   job-id  — stamp file name under ~/.claude/.run-stamps/
#   cadence — daily: due once per calendar day; weekly: due once per 7 days
#
# The stamp is written only on a successful run, so a failed job retries on the
# next trigger instead of being marked done.
set -euo pipefail

[ "$#" -ge 3 ] || { echo "usage: run-if-due.sh <job-id> <daily|weekly> <command> [args...]" >&2; exit 64; }

job_id="$1"; cadence="$2"; shift 2

stamp_dir="$HOME/.claude/.run-stamps"
mkdir -p "$stamp_dir"
stamp="$stamp_dir/$job_id"

now_epoch=$(date +%s)
today=$(date +%Y-%m-%d)

due=1
if [ -f "$stamp" ]; then
  last=$(cat "$stamp" 2>/dev/null || echo 0)
  [ -z "$last" ] && last=0
  last_day=$(date -r "$last" +%Y-%m-%d 2>/dev/null || echo "")
  days=$(( (now_epoch - last) / 86400 ))
  case "$cadence" in
    daily)  [ "$last_day" = "$today" ] && due=0 ;;
    weekly) [ "$days" -lt 7 ] && due=0 ;;
    # <N>d — an arbitrary day interval, for cadences between daily and weekly.
    # The comparison is against elapsed days like `weekly`, not against the
    # calendar, so a job that ran late does not get a short next window.
    [1-9]*d)
            n=${cadence%d}
            case "$n" in
              *[!0-9]*) echo "ERROR: unknown cadence '$cadence'" >&2; exit 64 ;;
            esac
            [ "$days" -lt "$n" ] && due=0 ;;
    *)      echo "ERROR: unknown cadence '$cadence'" >&2; exit 64 ;;
  esac
fi

if [ "$due" -eq 0 ]; then
  echo "$(date -Iseconds) [$job_id] not due (cadence=$cadence, last=$(date -r "$last" -Iseconds 2>/dev/null || echo never)) — skip"
  exit 0
fi

echo "$(date -Iseconds) [$job_id] due — running"
if "$@"; then
  date +%s > "$stamp"
  echo "$(date -Iseconds) [$job_id] done — stamp updated"
else
  rc=$?
  echo "$(date -Iseconds) [$job_id] exited $rc — stamp NOT updated (will retry next trigger)"
  exit "$rc"
fi
