#!/bin/bash
# requires: bash, python3, git
#
# Contract tests for seat.sh's folder derivation, against a stateful stand-in for the cmux CLI
# (seat-test-stub.py beside this file). Nothing here touches the real sidebar.
#
#   bash seat-test.sh            run every case; exit 1 on any failure
#   SEAT=<path> bash seat-test.sh   run against another copy — how a mutation is proved red
#
# Each case builds the sidebar it needs, runs seat.sh once, and asserts the exit code and the
# folder the new seat landed in.

set -u
. "$(dirname "$0")/seat-test-lib.sh"
S="${SEAT:-$HERE/seat.sh}"
mkdir -p "$T/repoA" "$T/repoB" "$T/plain" "$T/elsewhere"
git -C "$T/repoA" init -q && git -C "$T/repoA" commit -q --allow-empty -m x
git -C "$T/repoA" worktree add -q "$T/repoA-wt" -b wt
git -C "$T/repoB" init -q

reset() { printf '{"groups":[%s],"workspaces":[%s]}' "$1" "$2" > "$T/state.json"; : > "$T/calls.log"; }
grp() { printf '{"ref":"workspace_group:%s","name":"%s","custom_color":"%s","anchor_workspace_ref":"workspace:%s","member_workspace_refs":["workspace:%s"]}' "$1" "$2" "$3" "$1" "$1"; }
grpm() {  # grpm <n> <name> <hex> <member n> — a folder whose anchor is workspace:<n> and which holds one member seat besides it
  printf '{"ref":"workspace_group:%s","name":"%s","custom_color":"%s","anchor_workspace_ref":"workspace:%s","member_workspace_refs":["workspace:%s","workspace:%s"]}' "$1" "$2" "$3" "$1" "$1" "$4"; }
folders() {  # folders <value> — repoA's own seat_folders setting; `-` removes it so the floor governs
  local f="$T/repoA/docs/agents/integrations/cmux.md"
  if [ "$1" = "-" ]; then rm -f "$f"; return; fi
  mkdir -p "$(dirname "$f")"
  printf -- '---\ntool: cmux\nrole: terminal\ndefaults:\n  seat_folders: %s\n---\n' "$1" > "$f"
}
landed() {  # the folder name the most recently created seat is a member of, or UNGROUPED
  python3 - "$T" <<'PY'
import json, sys
st = json.load(open(sys.argv[1] + "/state.json"))
seat = st["workspaces"][-1]["ref"]
print(next((g["name"] for g in st["groups"] if seat in g["member_workspace_refs"]), "UNGROUPED"))
PY
}
check() {  # check <label> <want exit> <want folder or -> -- <seat.sh args...>
  local label="$1" want_rc="$2" want_folder="$3"; shift 4
  CMUX_BIN="$T/cmux" "$S" --name t "$@" >/dev/null 2>"$T/err"; local rc=$?
  local got="-"; [ "$rc" -eq 0 ] && got="$(landed)"
  if [ "$rc" = "$want_rc" ] && [ "$got" = "$want_folder" ]; then
    PASS=$((PASS + 1)); echo "  ok    $label"
  else
    FAIL=$((FAIL + 1)); echo "  FAIL  $label — exit $rc (want $want_rc), folder '$got' (want '$want_folder')"
    sed 's/^/        /' "$T/err"
  fi
}

reset "$(grp 1 RepoA '#167E31')" "$(ws 1 "$T/elsewhere")"
check "a fresh worktree finds the folder named for its repo, wherever that folder stands" 0 RepoA -- --cwd "$T/repoA-wt"

reset "$(grp 1 'Répo-A' '#167E31')" "$(ws 1 "$T/elsewhere")"
check "case, accents and punctuation are set aside when reading a name" 0 'Répo-A' -- --cwd "$T/repoA-wt"

reset "$(grp 1 RepoA '#167E31')" "$(ws 1 "$T/elsewhere")"
check "a repository with no folder of its own gets one, named for it" 0 repoB -- --cwd "$T/repoB"

reset "$(grp 1 'NEX-4714' '#9360EA')" "$(ws 1 "$T/repoA")"
check "an effort folder anchored in the repo is never the repo's folder" 0 repoA -- --cwd "$T/repoA-wt"

reset "$(grp 1 RepoA '#167E31'),$(grp 2 'repo a' '#9360EA')" "$(ws 1 "$T/elsewhere"),$(ws 2 "$T/elsewhere")"
check "two folders named for one repo is refused, nothing created" 5 - -- --cwd "$T/repoA-wt"

reset "$(grp 1 RepoA '#167E31')" "$(ws 1 "$T/elsewhere")"
check "a directory in no repository is refused without --group" 6 - -- --cwd "$T/plain"

reset "$(grp 1 RepoA '#167E31'),$(grp 2 'Effort' '#9360EA')" "$(ws 1 "$T/elsewhere"),$(ws 2 "$T/elsewhere")"
check "an explicit --group wins over the repository's folder" 0 Effort -- --cwd "$T/repoA-wt" --group workspace_group:2

reset "$(grp 1 'NEX-4714' '#9360EA'),$(grp 2 RepoA '#167E31')" "$(ws 1 "$T/repoA"),$(ws 2 "$T/elsewhere")"
check "an effort folder whose header stands in --cwd does not claim a seat there" 0 RepoA -- --cwd "$T/repoA"

folders per-effort
reset "$(grp 1 RepoA '#167E31'),$(grpm 2 'NEX-4714' '#9360EA' 3)" "$(ws 1 "$T/elsewhere"),$(ws 2 "$T/elsewhere"),$(ws 3 "$T/repoA-wt")"
check "per effort, a worktree joins the effort whose seat already stands in it" 0 NEX-4714 -- --cwd "$T/repoA-wt"

reset "$(grp 1 RepoA '#167E31'),$(grpm 2 'NEX-4714' '#9360EA' 3)" "$(ws 1 "$T/elsewhere"),$(ws 2 "$T/elsewhere"),$(ws 3 "$T/repoA")"
check "per effort, a base checkout joins the repository's folder, never an effort seated there" 0 RepoA -- --cwd "$T/repoA"

folders -
reset "$(grp 1 RepoA '#167E31'),$(grpm 2 'NEX-4714' '#9360EA' 3)" "$(ws 1 "$T/elsewhere"),$(ws 2 "$T/elsewhere"),$(ws 3 "$T/repoA-wt")"
check "per repository — the floor — a worktree joins the repository's folder even where an effort stands" 0 RepoA -- --cwd "$T/repoA-wt"

folders sideways
reset "$(grp 1 RepoA '#167E31')" "$(ws 1 "$T/elsewhere")"
check "a seat_folders value that is neither setting is refused, nothing created" 2 - -- --cwd "$T/repoA-wt"
folders -

finish
