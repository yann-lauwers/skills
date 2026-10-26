# What the Apple event bridge costs, and what it lies about

- Take a command's shape from `/System/Applications/Mail.app/Contents/Resources/Mail.sdef`; its parameter names do not follow the shapes AppleScript usually reads as natural.
- Fetch each property across the whole collection in one call, never one call per message — `mail-list.sh` is the pattern.
- Pass text through a temp file read `as «class utf8»`, or through JXA's ObjC bridge; `system attribute` decodes as MacRoman, so only ASCII crosses it intact.
- Move or remove a message, a draft included, by assigning its `mailbox` property, the target matched by name across providers — the name list lives in `scripts/trash-names`.
- `delete` (`Mail.sdef`, Standard Suite) — `delete message 1 of box` does not compile (`Expected end of line, etc. but found number`); `delete outgoing message i` removes an unsent message opened in a window, as `mail-draft.sh`'s discard does; on a stored message its effect is untested.

## Done when

The new call compiles against `Mail.sdef` and passes text through a file or the ObjC
bridge.
