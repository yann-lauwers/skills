#!/bin/bash
# requires: bash, python3, cmux (the app's bundled CLI)
#
# Create one seat and give it its folder's colour, as a single act.
#
# `workspace create` carries no colour flag and cmux runs no inheritance from a folder to its
# members, so the colour is always a second call — and a second call a session has to remember
# is a call a session eventually forgets. This script is that pair, so forgetting is not one of
# the outcomes.
#
# Resolving the folder's hex repairs the folder on the way past: a group carrying no colour
# adopts the hue its own members already wear, and every colourless member is filled with it.
# A member wearing a different non-null colour is left alone and reported — that mark was set
# deliberately, and overwriting it is a decision no script gets to take.
#
#   seat.sh --name <title> --cwd <path> [--group <ref>] [--command <text>] [--hex '#RRGGBB']
#
# Every seat lands in a folder. Without `--group` the folder is DERIVED from the repository's
# `seat_folders` setting, read from the config holding `role: terminal` at the repo's base
# checkout. `per-effort`, and --cwd is a linked worktree: a group with a member standing in
# --cwd itself. Otherwise, and as the fallback: the repository's own folder — the one named for
# the repo — else a folder created for that repository, coloured, before the seat. Pass
# `--group` to place a seat in an effort's folder — a session seated for a ticket tree — or where
# the derivation is ambiguous.
#
# Prints one line per act, then `SEAT <ref> <hex>`.
#
# Exit 0 seat created, in its folder, and coloured
#      2 bad arguments, the named group is not in the listing, or the repository's
#        `seat_folders` setting cannot be read or is neither `per-repository` nor `per-effort`
#      3 the group and every member are colourless and no --hex was given, or every palette
#        and overflow hue is already worn: pick one no neighbouring folder wears, pass --hex
#      4 the seat or the folder was created and the colour did not stick, or a create failed
#      5 the folder is ambiguous: two groups have members in --cwd, two are named for its repository,
#        or --group disagrees with the group already standing there. Nothing is created.
#      6 no folder stands in --cwd and it belongs to no git repository, so nothing can be
#        derived: name one with --group. Nothing is created.

set -uo pipefail

# The CLI is `cmux` on PATH; CMUX_BIN overrides it (the tests' stand-in).
C="${CMUX_BIN:-$(command -v cmux)}"
[ -n "$C" ] || { echo "$(basename "$0"): cmux is not on PATH — /Applications/cmux.app/Contents/Resources/bin is missing from it" >&2; exit 2; }

NAME=""; CWD=""; GROUP=""; COMMAND=""; HEX=""
while [ $# -gt 0 ]; do
  case "$1" in
    --name)    NAME="${2:-}"; shift 2 ;;
    --cwd)     CWD="${2:-}"; shift 2 ;;
    --group)   GROUP="${2:-}"; shift 2 ;;
    --command) COMMAND="${2:-}"; shift 2 ;;
    --hex)     HEX="${2:-}"; shift 2 ;;
    *) echo "seat.sh: unknown argument: $1" >&2; exit 2 ;;
  esac
done

[ -n "$NAME" ] || { echo "seat.sh: --name is required" >&2; exit 2; }
[ -n "$CWD"  ] || { echo "seat.sh: --cwd is required" >&2; exit 2; }
if [ -n "$HEX" ] && ! printf '%s' "$HEX" | grep -qE '^#[0-9A-Fa-f]{6}$'; then
  echo "seat.sh: --hex must be #RRGGBB, got: $HEX" >&2; exit 2
fi

# ---- derive the folder from the location ---------------------------------------------------
#
# `--group` is an OPTIONAL argument, and forgetting it was once a silent success: the seat was
# created, coloured, reported, and landed at the sidebar's top level beside the folder its
# effort already owned. Measured 2026-09-09 — `workspace_group:15 Codeine` existed, a seat
# for codeine work was created without `--group`, and nothing failed.
#
# Two things make that the DEFAULT outcome rather than an unlucky one. A workspace row
# carries no group field at all — membership is readable only from the group's side, as
# `member_workspace_refs` — so "which folder is this seat in?" cannot be asked of the seat.
# And the cookbook's own step 1 is a listing a caller has to remember to run, which is the
# shape of check that decays.
#
# So the folder is DERIVED here instead of trusted to the caller, the way `docker compose`
# derives its project name from the working directory rather than requiring `-p`
# (https://docs.docker.com/compose/how-tos/project-name/, precedence: `-p`, then the env
# var, then the file's `name:`, then the base directory). Same precedence, one addition:
# a `--group` that DISAGREES with the derivation is refused rather than silently winning,
# because Compose has no case where a flag and a derivation can both be right and differ.
#
# The match is an EXACT directory equality against each group's members, never its anchor.
# Anything looser — a prefix, a parent walk — would sort a fresh worktree into whichever
# folder happens to sit above it, and a misfiled seat reads as correct. The fallback below
# looks only for the REPOSITORY'S OWN folder, marked by its name, and never for a folder that
# merely holds or anchors one of the repo's seats — that is how an effort's folder looks too,
# and a seat filed there reads as correct.

derive_group() {  # derive_group <cwd> -> "<group-ref>" | "" ; exit 5 when two folders claim it
  { $C workspace-group list --json; echo '---SPLIT---'; $C workspace list --json; } |
  CWD="$1" python3 -c '
import json, os, sys
raw = sys.stdin.read().split("---SPLIT---")
if len(raw) != 2:
    print("ERR could not read the cmux listings", file=sys.stderr); sys.exit(2)
groups = json.loads(raw[0])["groups"]
by_ref = {w["ref"]: w for w in json.loads(raw[1])["workspaces"]}
want = os.path.realpath(os.environ["CWD"]).rstrip("/")

def stands_here(ref):
    w = by_ref.get(ref)
    if not w or not w.get("current_directory"):
        return False
    return os.path.realpath(w["current_directory"]).rstrip("/") == want

hits = []
for g in groups:
    # Members only: the anchor is the folder header and stands at whatever root the folder was
    # made at, so an effort folder anchored at a base checkout would otherwise claim every seat there.
    refs = [r for r in (g.get("member_workspace_refs") or []) if r != g.get("anchor_workspace_ref")]
    if any(stands_here(r) for r in refs):
        hits.append(g)
if len(hits) > 1:
    names = ", ".join("%s (%s)" % (g["ref"], g["name"]) for g in hits)
    print("ERR two folders already stand in " + want + ": " + names +
          " — name one with --group", file=sys.stderr)
    sys.exit(5)
print(hits[0]["ref"] if hits else "")
'
}

# ---- which folder this repository's seats join ---------------------------------------------
#
# The exact-directory rung above answers "which effort is this seat part of", and only a repo
# whose seats fold per effort asks that question. Where every seat joins the repository's
# folder, a member standing in --cwd names at best that same folder and at worst an effort folder
# left over from an earlier arrangement, so the rung is not run at all.
#
# Even per effort, it runs only inside a linked worktree. A base checkout is where every kind of
# seat stands — a plain session, a person's own shell — so a member standing there says nothing
# about which effort a new seat belongs to, and matching it filed a new seat into whichever
# effort's seat happened to share the path. A session seated for one unit stands in its own
# worktree, which is what makes the match mean something there.
#
# The setting is read at the base checkout rather than at --cwd, because it is the repository's
# answer and every worktree of it must get the same one.
AGENTS_CONFIG="${AGENTS_CONFIG:-$HOME/.claude/skills/agents-config/scripts/agents-config}"
MODE=""; IN_WORKTREE=""
if COMMON=$(git -C "$CWD" rev-parse --path-format=absolute --git-common-dir 2>/dev/null); then
  COMMON=$(cd "$COMMON" && pwd -P)
  BASE="$COMMON"; [ "$(basename "$COMMON")" = ".git" ] && BASE="$(dirname "$COMMON")"
  GITDIR=$(cd "$(git -C "$CWD" rev-parse --path-format=absolute --git-dir)" && pwd -P)
  [ "$GITDIR" != "$COMMON" ] && IN_WORKTREE=1
  MODE=$("$AGENTS_CONFIG" get --role terminal seat_folders --root "$BASE" 2>&1) || {
    echo "seat.sh: cannot read this repository's seat_folders setting: $MODE" >&2; exit 2; }
  case "$MODE" in
    per-repository|per-effort) ;;
    *) echo "seat.sh: seat_folders reads '$MODE' for $BASE; want per-repository or per-effort" >&2; exit 2 ;;
  esac
fi

# An ambiguous cwd is the case `--group` exists for, and its own message says "name one with
# --group" — so a caller that named one must not be refused by the check that asked for it.
# Exiting here unconditionally made that remedy unreachable: every folder standing at a shared
# repo root (eight of them at the nexus checkout) refused the create however it was invoked.
# The message is held back rather than printed, so a run --group resolved reports no error.
DERIVED=""
if [ "$MODE" = "per-effort" ] && [ -n "$IN_WORKTREE" ]; then
  DERIVE_ERR=$(mktemp)
  DERIVED=$(derive_group "$CWD" 2>"$DERIVE_ERR"); RC=$?
  if [ $RC -eq 5 ] && [ -n "$GROUP" ]; then
    DERIVED=""
  elif [ $RC -ne 0 ]; then
    cat "$DERIVE_ERR" >&2; rm -f "$DERIVE_ERR"; exit $RC
  fi
  rm -f "$DERIVE_ERR"
fi

# ---- nothing stands in --cwd: the repository's own folder, found or created -----------------
#
# A seat never lands at the sidebar's top level. The exact-directory match above finds nothing
# for a fresh worktree — nobody stands there yet — and that is the common case for a session
# seated for one unit. So
# the fallback is the REPOSITORY'S OWN folder, and its mark is its NAME: the folder whose name
# reads as the repo's basename once case, accents and punctuation are set aside ("Personal OPS"
# for personal-ops, "Les Gîtes du Haras" for les-gites-du-haras). The repo is found from --cwd by
# its git common dir, so every worktree of one repo reaches the same folder.
#
# The name, and not where the anchor stands, because position marks nothing here: an effort's
# folder is anchored in the repo too — the nexus checkout anchors six — and a folder the person
# made by hand stands wherever it was made. Two earlier shapes of this rung keyed on position,
# members then anchors, and each misfiled on the live sidebar (2026-09-13). A name is the one
# mark the person sets and reads, and an effort's folder is named for a ticket, never a repo.
#
# Two folders named for the repo → exit 5, naming them. None → one is created, named for the
# repo, anchored at its base checkout, before the seat exists — so a folder the person renamed
# away from the repo's name is not found, and a second one is made beside it.
#
# Measured 2026-09-13: a session for the first immo ticket was seated with no --group, no folder
# stood in its fresh worktree, and it landed at the top level with no colour.
#
# A created folder's hue is the first categorical palette slot nothing in the sidebar wears —
# folder or seat, since a colourless folder adopts its members' hue — then the first free
# overflow hue. The palette is solved for eight series side by side and this sidebar carries
# more, so the overflow list is the tail it already wears plus a few spares. The CREATED line
# names the closest hue already worn, so a near pair is reported rather than discovered.

PALETTE="#167E31 #9360EA #209FA3 #D03915 #1981D3 #6A7313 #E052AC #A27918"
OVERFLOW="#5C6BC0 #3E4B5E #7B3F00 #AD1457 #283593 #E8833A #F1C40F #C0392B #196F3D #7CB342 #00838F #F06292 #6D4C41 #8E24AA #546E7A"

repo_group() {  # repo_group <cwd> -> "found\t<ref>" | "none\t<root>\t<name>\t<hex>\t<nearest worn>" ; exit 3 | 5 | 6
  { $C workspace-group list --json; echo '---SPLIT---'; $C workspace list --json; } |
  CWD="$1" HEX="$HEX" PALETTE="$PALETTE" OVERFLOW="$OVERFLOW" python3 -c '
import json, os, subprocess, sys, unicodedata
raw = sys.stdin.read().split("---SPLIT---")
groups = json.loads(raw[0])["groups"]
spaces = json.loads(raw[1])["workspaces"]
by_ref = {w["ref"]: w for w in spaces}
cache = {}
def common_dir(path):
    if not path or not os.path.isdir(path):
        return None
    if path not in cache:
        r = subprocess.run(["git", "-C", path, "rev-parse", "--path-format=absolute",
                            "--git-common-dir"], capture_output=True, text=True)
        cache[path] = os.path.realpath(r.stdout.strip()) if r.returncode == 0 else None
    return cache[path]
def norm(s):
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s.lower() if c.isalnum())
want = common_dir(os.environ["CWD"])
if want is None:
    print("ERR no folder stands in " + os.environ["CWD"] + " and it belongs to no git repository, "
          "so no folder can be derived — name the effort folder with --group, creating it first "
          "if it does not exist", file=sys.stderr)
    sys.exit(6)
root = os.path.dirname(want) if os.path.basename(want) == ".git" else want
named = [g for g in groups if norm(g["name"]) == norm(os.path.basename(root))]
if len(named) == 1:
    print("found\t" + named[0]["ref"]); sys.exit(0)
if named:
    names = ", ".join("%s (%s)" % (g["ref"], g["name"]) for g in named)
    print("ERR several folders are named for this repository: " + names +
          " — name one with --group", file=sys.stderr)
    sys.exit(5)
worn = {c.upper() for c in [g.get("custom_color") for g in groups] + [w.get("custom_color") for w in spaces] if c}
hexv = os.environ["HEX"] or next((h for h in os.environ["PALETTE"].split() + os.environ["OVERFLOW"].split()
                                  if h.upper() not in worn), "")
if not hexv:
    print("ERR every palette and overflow hue is worn — pass --hex", file=sys.stderr); sys.exit(3)
rgb = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
dist = lambda a, b: sum((x - y) ** 2 for x, y in zip(rgb(a), rgb(b))) ** 0.5
nearest = min(worn, key=lambda w: dist(w, hexv)) if worn else "-"
print("\t".join(["none", root, os.path.basename(root), hexv, nearest]))
'
}

if [ -z "$GROUP" ] && [ -z "$DERIVED" ]; then
  REPO=$(repo_group "$CWD"); RC=$?
  [ $RC -eq 0 ] || exit $RC
  IFS=$'\t' read -r KIND F1 F2 F3 F4 <<<"$REPO"
  case "$KIND" in
    found) DERIVED="$F1" ;;
    none)
      ROOT="$F1"; RNAME="$F2"; RHEX="$F3"; NEAREST="$F4"
      GOUT=$($C workspace-group create --name "$RNAME" --cwd "$ROOT" 2>&1)
      DERIVED=$(printf '%s' "$GOUT" | grep -oE 'workspace_group:[0-9]+' | head -1)
      [ -n "$DERIVED" ] || { echo "seat.sh: folder create failed: $GOUT" >&2; exit 4; }
      $C workspace-group set-color "$DERIVED" --hex "$RHEX" >/dev/null
      # Read the folder's colour back, as the seat's is below: set-color answers about the
      # request, and only the listing answers about the folder.
      GGOT=$($C workspace-group list --json | REF="$DERIVED" python3 -c '
import json, os, sys
for g in json.load(sys.stdin)["groups"]:
    if g["ref"] == os.environ["REF"]:
        print(g.get("custom_color") or ""); break
')
      if [ "$GGOT" != "$RHEX" ]; then
        echo "seat.sh: folder $DERIVED was created but reads custom_color=${GGOT:-null}, wanted $RHEX" >&2
        exit 4
      fi
      HEX="$RHEX"
      echo "CREATED $DERIVED $RNAME $RHEX at $ROOT (closest hue already worn: $NEAREST)"
      ;;
  esac
fi

if [ -z "$GROUP" ]; then
  GROUP="$DERIVED"
  [ -n "$GROUP" ] && echo "DERIVED $GROUP from $CWD"
elif [ -n "$DERIVED" ]; then
  # Both answered. Resolve the caller's argument to a ref before comparing — `--group`
  # accepts a name, and a name that matches the derived group is agreement, not conflict.
  GIVEN_REF=$($C workspace-group list --json | GROUP="$GROUP" python3 -c '
import json, os, sys
want = os.environ["GROUP"]
for g in json.load(sys.stdin)["groups"]:
    if g["ref"] == want or g["name"] == want:
        print(g["ref"]); break
')
  if [ -n "$GIVEN_REF" ] && [ "$GIVEN_REF" != "$DERIVED" ]; then
    echo "seat.sh: --group $GROUP resolves to $GIVEN_REF, but $DERIVED already stands in $CWD." >&2
    echo "seat.sh: one of the two is wrong; nothing was created." >&2
    exit 5
  fi
fi

# ---- resolve the folder's hex, repairing the folder if it has none -------------------------

resolve_hex() {  # resolve_hex <group-ref> <hex-or-empty>  -> "<hex>\t<members to fill, space separated>"
  local group="$1" fallback="$2"
  { $C workspace-group list --json; echo '---SPLIT---'; $C workspace list --json; } |
  GROUP="$group" FALLBACK="$fallback" python3 -c '
import json, os, sys
raw = sys.stdin.read().split("---SPLIT---")
if len(raw) != 2:
    print("ERR could not read the cmux listings", file=sys.stderr); sys.exit(2)
groups = json.loads(raw[0])["groups"]
by_ref = {w["ref"]: w for w in json.loads(raw[1])["workspaces"]}
want = os.environ["GROUP"]
g = next((g for g in groups if g["ref"] == want or g["name"] == want), None)
if g is None:
    print("ERR no such group: " + want, file=sys.stderr); sys.exit(2)
anchor = g.get("anchor_workspace_ref")
members = [r for r in g.get("member_workspace_refs", []) if r != anchor]
worn = [by_ref[r]["custom_color"] for r in members if r in by_ref and by_ref[r]["custom_color"]]
hexv = g.get("custom_color") or (max(set(worn), key=worn.count) if worn else "") or os.environ["FALLBACK"]
if not hexv:
    print("ERR colourless: " + g["ref"] + " " + g["name"], file=sys.stderr); sys.exit(3)
blank = [r for r in members if r in by_ref and not by_ref[r]["custom_color"]]
other = [r for r in members if r in by_ref and by_ref[r]["custom_color"] and by_ref[r]["custom_color"] != hexv]
print("\t".join([g["ref"], hexv, " ".join(blank), " ".join(other)]))
'
}

HEXV=""; GROUP_REF=""
if [ -n "$GROUP" ]; then
  RESOLVED=$(resolve_hex "$GROUP" "$HEX"); RC=$?
  [ $RC -eq 0 ] || exit $RC
  GROUP_REF=$(printf '%s' "$RESOLVED" | cut -f1)
  HEXV=$(printf '%s' "$RESOLVED" | cut -f2)
  BLANK=$(printf '%s' "$RESOLVED" | cut -f3)
  OTHER=$(printf '%s' "$RESOLVED" | cut -f4)

  $C workspace-group set-color "$GROUP_REF" --hex "$HEXV" >/dev/null && echo "GROUP $GROUP_REF $HEXV"
  for m in $BLANK; do
    $C workspace-action --action set-color --workspace "$m" --color "$HEXV" >/dev/null && echo "FILLED $m $HEXV"
  done
  for m in $OTHER; do echo "LEFT $m wears a different colour, not overwritten"; done
else
  HEXV="$HEX"
fi

# ---- create the seat, then colour it ------------------------------------------------------

set -- workspace create --name "$NAME" --cwd "$CWD" --focus false
[ -n "$GROUP_REF" ] && set -- "$@" --group "$GROUP_REF" --group-placement end
[ -n "$COMMAND" ] && set -- "$@" --command "$COMMAND"

OUT=$($C "$@" 2>&1) || { echo "seat.sh: create failed: $OUT" >&2; exit 4; }
REF=$(printf '%s' "$OUT" | grep -oE 'workspace:[0-9]+' | head -1)
[ -n "$REF" ] || { echo "seat.sh: create returned no ref: $OUT" >&2; exit 4; }

$C workspace-action --action set-color --workspace "$REF" --color "$HEXV" >/dev/null

# The colour is read back off the seat rather than off the call that set it: set-color answers
# about the request, and only the listing answers about the seat.
GOT=$($C workspace list --json | REF="$REF" python3 -c '
import json, os, sys
for w in json.load(sys.stdin)["workspaces"]:
    if w["ref"] == os.environ["REF"]:
        print(w["custom_color"] or ""); break
')
if [ "$GOT" != "$HEXV" ]; then
  echo "seat.sh: $REF was created but reads custom_color=${GOT:-null}, wanted $HEXV" >&2
  exit 4
fi
echo "SEAT $REF $HEXV"
