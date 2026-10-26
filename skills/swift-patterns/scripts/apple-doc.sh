#!/bin/sh
# Fetch one page of Apple's developer documentation as Markdown and print where it landed.
#
# usage: apple-doc.sh <page> [out-dir]
#   <page> is any of:
#     https://developer.apple.com/documentation/swiftui/menubarextra
#     doc://com.apple.documentation/documentation/SwiftUI/View/opacity(_:)
#     swiftui/menubarextra            (a path under documentation/)
#     updates/swiftui                 (the dated "what's new" page for a framework)
#   [out-dir] defaults to $TMPDIR.
# prints: the file path and its byte count; exit 0.
# exit 1: no Markdown page at that path. A symbol's path is not guessable — an overload carries a
#         hash suffix (View/body-8kl5o) — so fetch the parent type's page and pass one of its links.
# exit 2: bad usage, no network, or [out-dir] not writable.
#
# A page links as /documentation/... or doc://com.apple.documentation/documentation/...; pass
# either back to this script as it stands. The page opens with a JSON comment whose
# "availability" lists the OS floor; the compiler (sil-check.sh) outranks it when the two disagree.

set -u
[ $# -ge 1 ] || { sed -n '2,18p' "$0" >&2; exit 2; }

page=$1
out=${2:-${TMPDIR:-/tmp}}

page=${page#doc://com.apple.documentation/}
page=${page#https://developer.apple.com/}
page=${page#http://developer.apple.com/}
page=${page#/}
page=${page%.md}
page=${page%/}
case $page in
  documentation/*) ;;
  *) page=documentation/$page ;;
esac

url="https://developer.apple.com/$page.md"
file="$out/apple-doc-$(printf '%s' "${page#documentation/}" | tr -c 'A-Za-z0-9._-' '_').md"

code=$(curl -sSL -g -o "$file" -w '%{http_code} %{content_type}' "$url") || { echo "fetch failed for $url (no network, or [out-dir] is not a writable directory)" >&2; exit 2; }
case $code in
  "200 text/markdown"*) printf '%s %s bytes\n' "$file" "$(wc -c < "$file" | tr -d ' ')" ;;
  *) rm -f "$file"; echo "no Markdown page at $url ($code) — fetch the parent page instead" >&2; exit 1 ;;
esac
