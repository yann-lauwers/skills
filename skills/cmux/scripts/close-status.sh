#!/bin/bash
# requires: bash, python3, git, cmux (the app's bundled CLI); gh optional
#
# Everything a close decision needs about THIS seat, in one read.
#
# The seat this session sits in is named by CMUX_WORKSPACE_ID, exported into every workspace
# by cmux itself — so identifying the seat costs an env lookup, not a screen read. Where that
# variable is absent the session is not inside a cmux seat, and the script says so rather than
# guessing a ref: closing the wrong seat kills somebody else's work.
#
# Read-only. Every reading carries three outcomes, never two — the fact, its absence, and
# "could not read", which is not the same as absence and is printed as `unknown`.
#
#   close-status.sh [--no-pr]
#
# Exit 0 always: this reports, it does not decide. BLOCKERS is the caller's input, not a verdict.

set -uo pipefail

# The CLI is `cmux` on PATH; CMUX_BIN overrides it (the tests' stand-in).
C="${CMUX_BIN:-$(command -v cmux)}"
[ -n "$C" ] || { echo "$(basename "$0"): cmux is not on PATH — /Applications/cmux.app/Contents/Resources/bin is missing from it" >&2; exit 2; }
WANT_PR=1
[ "${1:-}" = "--no-pr" ] && WANT_PR=0

BLOCKERS=()
block() { BLOCKERS+=("$1"); }

# Bound a command's runtime without `timeout`, which is not installed here.
# Prints the command's stdout; empty output plus non-zero status means it was killed.
limit() {  # limit <seconds> <cmd...>
  local secs="$1"; shift
  local out rc
  out=$("$@" 2>/dev/null & pid=$!
       ( sleep "$secs"; kill -9 $pid 2>/dev/null ) >/dev/null 2>&1 &
       watcher=$!
       wait $pid; rc=$?
       kill -9 $watcher 2>/dev/null
       exit $rc)
  rc=$?
  printf '%s' "$out"
  return $rc
}

# ---------------------------------------------------------------- seat
SEAT_REF=""; SEAT_TITLE=""; SEAT_DIR=""; SEAT_GROUP=""; SIBLINGS=""; SEAT_ERR=""
if [ -z "${CMUX_WORKSPACE_ID:-}" ]; then
  echo "SEAT      not in a cmux workspace (CMUX_WORKSPACE_ID unset) — no seat to close"
else
  # Groups are a separate listing — `workspace list --json` carries no group field.
  eval "$(CMUX_BIN="$C" python3 -c '
import json,os,shlex,subprocess
C=os.environ["CMUX_BIN"]; me=os.environ.get("CMUX_WORKSPACE_ID","").lower()
def cmux(*a):
    try: return json.loads(subprocess.run([C,*a],capture_output=True,text=True,timeout=15).stdout)
    except Exception: return None
def q(k,v): print("%s=%s"%(k,shlex.quote(str(v if v is not None else ""))))
d=cmux("workspace","list","--json","--id-format","both")
if d is None:
    q("SEAT_ERR","cmux workspace list could not be read"); raise SystemExit(0)
ws=d.get("workspaces") or []
mine=next((w for w in ws if str(w.get("id","")).lower()==me), None)
if mine is None:
    q("SEAT_ERR","this session'"'"'s workspace id is not in the listing"); raise SystemExit(0)
ref=mine.get("ref")
q("SEAT_REF",ref)
q("SEAT_TITLE",mine.get("custom_title") or mine.get("title"))
q("SEAT_DIR",mine.get("current_directory"))
groups=((cmux("workspace-group","list","--json") or {}).get("groups") or [])
g=next((g for g in groups if ref in (g.get("member_workspace_refs") or [])), None)
if g:
    q("SEAT_GROUP","%s (%s, %d members)"%(g.get("name"),g.get("ref"),g.get("member_count") or 0))
    byref={w.get("ref"):w for w in ws}
    sibs=[byref.get(r) for r in (g.get("member_workspace_refs") or []) if r!=ref]
    q("SIBLINGS"," · ".join("%s %s"%(s.get("ref"),(s.get("custom_title") or s.get("title") or "")[:40]) for s in sibs if s))
')"
  if [ -n "${SEAT_ERR:-}" ]; then
    echo "SEAT      unknown — $SEAT_ERR"
    block "seat ref unresolved: $SEAT_ERR"
  else
    echo "SEAT      $SEAT_REF · ${SEAT_TITLE:-(untitled)}${SEAT_GROUP:+ · folder: $SEAT_GROUP}"
    echo "CWD       ${SEAT_DIR:-unknown}"
    [ -n "$SIBLINGS" ] && echo "SIBLINGS  $SIBLINGS"
  fi
fi

# ---------------------------------------------------------------- repo
DIR="${SEAT_DIR:-$PWD}"
[ -d "$DIR" ] || DIR="$PWD"
GITDIR=$(git -C "$DIR" rev-parse --git-dir 2>/dev/null)
if [ -z "$GITDIR" ]; then
  echo "REPO      none — $DIR is not a git repository"
else
  COMMON=$(git -C "$DIR" rev-parse --git-common-dir 2>/dev/null)
  KIND="checkout"; [ "$GITDIR" != "$COMMON" ] && KIND="worktree"
  BRANCH=$(git -C "$DIR" rev-parse --abbrev-ref HEAD 2>/dev/null)
  DIRTY=$(git -C "$DIR" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
  UPSTREAM=$(git -C "$DIR" rev-parse --abbrev-ref '@{u}' 2>/dev/null)
  if [ -n "$UPSTREAM" ]; then
    AHEAD=$(git -C "$DIR" rev-list --count "$UPSTREAM"..HEAD 2>/dev/null)
  else
    AHEAD="no upstream"
  fi
  STASH=$(git -C "$DIR" stash list 2>/dev/null | wc -l | tr -d ' ')
  echo "REPO      $KIND · branch $BRANCH · ${DIRTY} uncommitted · ${AHEAD} unpushed · ${STASH} stashed"
  [ "$DIRTY" != "0" ]  && block "$DIRTY uncommitted file(s) in $DIR"
  [ "$AHEAD" = "no upstream" ] && [ "$KIND" = "worktree" ] && block "branch $BRANCH has no upstream — nothing was pushed"
  [ "$AHEAD" != "no upstream" ] && [ "${AHEAD:-0}" != "0" ] && block "$AHEAD commit(s) not pushed on $BRANCH"
  [ "$STASH" != "0" ] && block "$STASH stash entry/entries on this repo — refs/stash is shared by every worktree"

  # ------------------------------------------------------------- PR
  if [ "$WANT_PR" = "1" ] && command -v gh >/dev/null 2>&1 && [ -n "$BRANCH" ]; then
    PRJSON=$(cd "$DIR" && limit 20 gh pr view --json number,state,isDraft,mergedAt,mergeStateStatus,statusCheckRollup)
    if [ -z "$PRJSON" ]; then
      echo "PR        none open for $BRANCH (or gh could not read it)"
    else
      printf '%s' "$PRJSON" | python3 -c '
import json,sys
d=json.load(sys.stdin)
rollup=d.get("statusCheckRollup") or []
bad=[c for c in rollup if (c.get("conclusion") or c.get("state") or "") in ("FAILURE","ERROR","CANCELLED","TIMED_OUT")]
pend=[c for c in rollup if (c.get("status") or "")=="IN_PROGRESS" or (c.get("state") or "")=="PENDING"]
print("PR        #%s %s%s · %s · checks: %d failing, %d pending, %d total"%(
  d.get("number"), d.get("state"),
  " (DRAFT)" if d.get("isDraft") else "",
  d.get("mergeStateStatus") or "?", len(bad), len(pend), len(rollup)))
' 2>/dev/null || echo "PR        unknown — could not parse gh output"
      STATE=$(printf '%s' "$PRJSON" | python3 -c 'import json,sys;d=json.load(sys.stdin);print(d.get("state",""))' 2>/dev/null)
      DRAFT=$(printf '%s' "$PRJSON" | python3 -c 'import json,sys;d=json.load(sys.stdin);print(d.get("isDraft"))' 2>/dev/null)
      [ "$STATE" = "OPEN" ] && block "PR is still open — not merged"
      [ "$DRAFT" = "True" ] && block "PR is a draft — a draft runs no CI"
    fi
  fi
fi

# ---------------------------------------------------------------- verdict input
echo
if [ ${#BLOCKERS[@]} -eq 0 ]; then
  echo "BLOCKERS  none found by this script"
else
  echo "BLOCKERS"
  for b in "${BLOCKERS[@]}"; do echo "  - $b"; done
fi
echo
echo "CLOSE     ~/.claude/skills/cmux/scripts/self-close.sh ${SEAT_REF:-<ref-unresolved>} --delay 60 --reason \"<why>\""
exit 0
