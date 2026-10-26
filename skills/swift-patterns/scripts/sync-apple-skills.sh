#!/bin/sh
# Install Apple's own agent skills, as shipped by the selected Xcode, as the plugin
# xcode-integration@skills-dir. Their names keep Apple's namespace
# (/xcode-integration:swiftui-specialist), which is how their own cross-references are written.
#
# usage: sync-apple-skills.sh [--dry-run]
# requires: Xcode 27 or later selected with xcode-select (xcrun agent), rsync.
# prints: one line per skill installed or removed, a "changed <skill>/<file>" line per file the copy
#         added, changed or deleted, a "not in this Xcode's pack" line per keep-list entry that
#         matched nothing, then the Xcode build it copied from; exit 0.
# exit 1: this Xcode ships no agent plugin, or the copy failed.
#
# Run it after every Xcode update: the pack is versioned with the Xcode build, and every skill
# not in this Xcode's pack is removed from the copy. The pack's .mcp.json (the xcode MCP server,
# which needs a running Xcode that has allowed external agents) is not copied.

set -eu

# Skills that serve a macOS SwiftUI/AppKit app and run on Read, Grep and Bash alone. A pattern ending
# in * matches the release-numbered skill of whichever Xcode is selected. Left out: iOS-only surfaces
# (UIKit, device and simulator driving, App Intents, document apps) and every skill that runs on
# Xcode's own MCP tools (security settings, translation).
KEEP="swiftui-specialist swiftui-whats-new-* modernize-tests
accessibility-voiceover-specialist accessibility-dynamic-type-specialist
accessibility-sufficient-contrast-specialist adopt-c-bounds-safety"

dry=
[ "${1:-}" = "--dry-run" ] && dry=1

src=$(xcrun agent plugin path --plugin-format claude) || { echo "this Xcode ships no agent plugin" >&2; exit 1; }
[ -f "$src/.claude-plugin/plugin.json" ] || { echo "no plugin manifest under $src" >&2; exit 1; }
build=$(xcodebuild -version | awk '/Build version/{print $3}')
dest="$HOME/.claude/skills/xcode-integration"

# Resolve the keep-list against this Xcode's pack.
# Word-split KEEP with globbing off, so a pattern is never expanded against the caller's directory.
wanted=
set -f
for pattern in $KEEP; do
  set +f
  found=
  for d in "$src"/skills/$pattern/; do
    [ -d "$d" ] || continue
    wanted="$wanted $(basename "$d")"
    found=1
  done
  [ -n "$found" ] || echo "not in this Xcode's pack: $pattern"
  set -f
done
set +f

if [ -n "$dry" ]; then
  for s in $wanted; do echo "would install xcode-integration:$s"; done
  for d in "$dest"/skills/*/; do
    [ -d "$d" ] || continue
    s=$(basename "$d")
    case " $wanted " in *" $s "*) ;; *) echo "would remove $s" ;; esac
  done
  echo "from Xcode build $build (dry run)"
  exit 0
fi

mkdir -p "$dest/.claude-plugin" "$dest/skills"
rsync -a "$src/.claude-plugin/plugin.json" "$dest/.claude-plugin/plugin.json"
for s in $wanted; do
  copied=$(rsync -a -c --delete -i "$src/skills/$s/" "$dest/skills/$s/")
  printf '%s\n' "$copied" |
    awk -v s="$s" 'NF >= 2 && $1 !~ /^\./ && $2 !~ /\/$/ { print "changed xcode-integration:" s "/" $2 }'
  echo "installed xcode-integration:$s"
done
for d in "$dest"/skills/*/; do
  [ -d "$d" ] || continue
  s=$(basename "$d")
  case " $wanted " in *" $s "*) ;; *) rm -rf "$d"; echo "removed $s" ;; esac
done
printf 'Copied by swift-patterns/scripts/sync-apple-skills.sh from Xcode %s (%s). Do not edit; re-run the script.\n' "$build" "$src" > "$dest/SOURCE"
echo "from Xcode build $build"
