#!/bin/bash
# Compile one Swift file to SIL so region-isolation diagnostics run (-typecheck skips them),
# and print the command, every diagnostic line, and the exit status.
# requires: xcrun (Xcode or its command line tools)
# usage: sil-check.sh <file.swift> [--target <macOS version, default 14.0>] [extra swiftc flags...]
# swiftc prints nothing for an unrecognised -enable-upcoming-feature name, so a misspelled feature
# reads as "enabled". A claim that a feature is on needs a paired probe whose result flips between
# the run with the flag and the run without it (or with a bogus name as the control).
# Pass the target the project's build settings name; 14.0 is a default, not a finding.
# e.g.   sil-check.sh probe.swift --target 14.0 -swift-version 6
#        sil-check.sh probe.swift -swift-version 6 -enable-upcoming-feature NonisolatedNonsendingByDefault
set -u
[ $# -ge 1 ] || { echo "usage: $0 <file.swift> [--target <version>] [swiftc flags...]" >&2; exit 2; }
f="$1"; shift
target="14.0"
if [ "${1:-}" = "--target" ]; then target="$2"; shift 2; fi
arch="$(uname -m)"; [ "$arch" = "x86_64" ] || arch="arm64"
cmd=(xcrun swiftc -emit-sil -o /dev/null -target "${arch}-apple-macos${target}" "$@" "$f")
echo "\$ ${cmd[*]}"
out="$("${cmd[@]}" 2>&1)"; rc=$?
if [ -z "$out" ]; then
  echo "(no diagnostics)"
else
  printf '%s\n' "$out" | grep -E '^[^ |].*:[0-9]+:[0-9]+: (error|warning|note):' || true
fi
# A code diagnostic carries a file:line:col prefix. A non-zero exit with none is a compiler that
# never ran the file — a bad flag, a missing SDK — never evidence about the code.
if [ "$rc" -ne 0 ] && ! printf '%s\n' "$out" | grep -qE '^[^ |].*:[0-9]+:[0-9]+: (error|warning|note):'; then
  echo "DID NOT COMPILE: $(printf '%s\n' "$out" | head -1)"
fi
echo "exit=$rc"
exit "$rc"
