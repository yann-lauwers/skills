#!/bin/bash
set -u
out=${1:?usage: scan.sh <output-dir>}
D=/System/Volumes/Data
H=$D$HOME
mkdir -p "$out/parts"
rm -f "$out"/parts/*

{
  find "$D" -mindepth 1 -maxdepth 1 -type d ! -path "$D/Users" ! -path "$D/private" ! -path "$D/System"
  find "$D/Users" -mindepth 1 -maxdepth 1 -type d ! -path "$H"
  find "$D/private" -mindepth 1 -maxdepth 1 -type d
  find "$H" -mindepth 1 -maxdepth 1 -type d ! -path "$H/Library"
  find "$H/Library" -mindepth 1 -maxdepth 1 -type d
} 2>/dev/null > "$out/roots.txt"

export out
scan_root() {
  local f
  f="$out/parts/$(printf '%s' "$1" | shasum | cut -c1-12)"
  du -xk "$1" 2>>"$f.err" | awk -v root="$1" '$1 >= 1048576 || substr($0, index($0, "\t") + 1) == root' > "$f.txt"
}
export -f scan_root
tr '\n' '\0' < "$out/roots.txt" | xargs -0 -P 12 -I{} bash -c 'scan_root "$1"' _ {}

cat "$out"/parts/*.txt | sort -t$'\t' -k2 > "$out/scan.txt"
cat "$out"/parts/*.err 2>/dev/null | sed -n 's/^du: \(.*\): Operation not permitted$/\1/p' | sort -u > "$out/unreadable.txt"
python3 -I "$(dirname "$0")/render.py" "$out/scan.txt" "$out/roots.txt" > "$out/tree.txt"
df -k "$D" | awk 'NR == 2 { printf "volume used %.1f GB, free %.1f GB\n", $3 / 1048576, $4 / 1048576 }'
head -2 "$out/tree.txt" | tail -1 | awk '{ printf "scanned %s GB; the gap is what unreadable.txt hides plus local snapshots\n", $2 }'
