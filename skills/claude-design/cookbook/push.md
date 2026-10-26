# Push

## The state a push comes from

- Push from one state: concurrent pushers overwrite each other, and the read-back stays green either way.
- No calling skill names the project, and `~/.claude/skills/agents-config/scripts/agents-config get claude-design mirror --root <repo>` answers a path → export that state from a commit's tree, never a checkout as found:

  ```sh
  git -C <repo> fetch origin <sha>            # a merge commit is not local until fetched
  mkdir -p <dir> && git -C <repo> archive <sha>:<mirror> | tar -x -C <dir>
  ```

- Export the whole mirror, never the plan's paths; the scope lives in step 3's plan alone, and a pathspec naming a path the commit deleted exits 128.
- `<dir>` is the session's scratchpad; `localDir=<dir>` resolves every plan path mirror-relative.
- A calling skill names the project, or no mirror is declared → push the build output its owning skill names, whole.

## Steps

1. `list_files` → what is there now, so the plan names real writes and deletes.
   Done when the listing is in hand.
2. Rebuild the pane's card index, `_ds_manifest.json`, carrying the hosted one forward.
   - The pane compiles the index itself only for `/design-sync` uploads → a push that adds, removes or renames a card carries the index, or the files land and the pane shows nothing.
   - Every push replaces the index whole → `get_file _ds_manifest.json` into the scratchpad first, then build from the tree plus that file, dropping only what this change deletes across all its plans.
   - Shape → `references/manifest.md`; a repo declaring this medium keeps a script that writes it from the `@dsCard` markers and carries the hosted index through it.
   Done when the new index holds every hosted card this change does not delete.
3. `finalize_plan` → the exact paths to write and to delete (both keys, `deletes: []` when none) and `localDir`.
   - One plan carries one piece of the caller's system, every path named, no glob; what a piece is → the calling skill's push lines.
   - Several pieces → several plans: steps 1 and 3–5 once per piece, the index (step 2) with the last.
   - A bundle the project pushes itself → a piece of its own, since it replaces every component in the pane at once.
   - The plan shows the owner the paths and the source directory · whether a push waits for his answer there → the calling skill's push lines.
   - Every card in the plan carries the first-line marker and loads nothing remote → `references/card.md`.
   Done when the tool returns a `planId`.
4. `write_files` → each file as a `localPath` under `localDir`, never inline, 256 per call; then `delete_files` for every path under `deletes`, same `planId`.
   - `mimeType: "text/plain"` → only a file no page fetches: a `.py`, a `.sh`, a README, `_ds_manifest.json`.
   - A file a page fetches — `.js`, `.mjs`, `.css`, `.svg`, a font, an image, any JSON a card reads at runtime → its own type, never `text/plain`; under `nosniff` the browser refuses it and the card draws nothing while every signal here stays green.
   - The tool refuses a page-fetched file under its own type → stop and report the refusal verbatim; never fall back to `text/plain`.
   Done when every planned write and delete has been called.
5. Read back: `list_files` again, `get_file` on one path the push changed, and on one it deleted where the plan deleted anything.
   - The read-back proves the bytes landed · the write's own answer and the project's `updatedAt` prove nothing.
   - `delete_files` answering `403 permission_denied — bulk delete requires project ownership…` can still have deleted every path → read the project, never the status.
   Done when the read-back matches the plan; bytes landed is not a push confirmed.
6. Reconcile the host's bundle against the index.
   - Cards import a component bundle → `get_file _ds_bundle.js` and read its first line.
   - It opens `/* @ds-bundle:` → the host's own, carrying its component list; compare it with `_ds_manifest.json`'s · a component the index declares and the bundle lacks → the push is finished, and the reply names each blank card and the components the bundle lacks.
   - Any other first line → a bundle pushed from outside, which stays at that path; the counts cannot judge it → the project's own design skill says how it is rebuilt, when, and how an older one is caught.
   - A bundle pushed from outside and no project design skill → the push is unfinished; the reply names each blank card, the components the pane check in `cookbook/troubleshoot.md` Step 2 reports missing and the bundle's first line, and says that path needs the project's own build.
   - Cards import no bundle, every card self-contained → say so in one line.
   Done when the reply names what renders and what does not.
