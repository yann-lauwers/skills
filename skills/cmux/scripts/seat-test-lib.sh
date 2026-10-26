# requires: bash, python3
#
# The half every contract test in this directory shares: a private temp tree, the stand-in cmux
# wired to it (seat-test-stub.py beside this file), the pass/fail counters, the workspace fixture
# and the summary trailer. Sourced by seat-test.sh and self-close-test.sh, never run.
#
#   . "$(dirname "$0")/seat-test-lib.sh"     # sets HERE, T (removed on exit), $T/cmux, PASS, FAIL
#   ws <n> <dir>                              # one workspace object for a state.json fixture
#   finish                                    # prints "<PASS> passed, <FAIL> failed"; exits 1 on any failure

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
printf '#!/bin/bash\nT=%s exec python3 %s/seat-test-stub.py "$@"\n' "$T" "$HERE" > "$T/cmux"
chmod +x "$T/cmux"

PASS=0; FAIL=0
ws() { printf '{"ref":"workspace:%s","current_directory":"%s","custom_color":null}' "$1" "$2"; }
finish() {
  echo
  echo "$PASS passed, $FAIL failed"
  [ "$FAIL" -eq 0 ]
}
