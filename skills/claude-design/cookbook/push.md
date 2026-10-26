# Publish

## The state a publish comes from

- Publish from one tree: the export replaces the system's files whole, so an older tree takes back what a later one changed.
- The tree is the tip of the branch the system mirrors, never a checkout as found; the calling skill names its exporter and the command that runs it.
- The export lands in the session's scratchpad as `<dir>/project/`, beside a list of every path it wrote.

## Steps

1. Resolve the target per `SKILL.md` § Project config.
   - `artifact` null → publish with the Design System type's `type_url` (`action: "list"`, `scope: "types"` names it), a `title` and no files, then carry the link it returns into the repo's config in the same change set.
   Done when a link is in hand.
2. Read the hosted index: `Artifact` `read` the link with `path: "project/design-system.json"`, saved to the scratchpad.
   - Its `lastChange.via` names the commit it was published from · that commit is no ancestor of the tree to publish → a newer tree published it: stop, and say which commit the system shows.
   - The exporter carries the saved index's `createdOnFiles` and the keys the page owns (`sections`, `blobs`, `docs`) into the new one.
   Done when the index is saved, or the system is new.
3. Export the tree with the calling skill's exporter.
   Done when the export lists `project/design-system.json`.
4. `Artifact` `list` the link with `scope: "files"`; every `project/` path it lists that the export lacks goes into the publish as `null`, except `project/api/…` and `project/manifest.json`, which the page writes.
   Done when each path to remove is named, or none is.
5. Publish: `url` the link, `root` the export's folder, `file_path` its `project/design-system.json`, `files` every other exported path mapped to itself and each step 4 path to `null`.
   - More than 255 paths → several publishes, the index only in the last.
   - Refused for want of edit access → stop, and name the account that owns the system.
   Done when the publish reports the index and the files it sent.
6. See it drawn: `node ~/.local/share/claude-login/examples/design-system-look.mjs <account> <link> --component <Name> …`, one `--component` per component the change touched, run as an account that can open the system.
   Done when its `RESULT` line reads `ok`, or the reply names each preview it reported `BLANK` or `ABSENT`.
