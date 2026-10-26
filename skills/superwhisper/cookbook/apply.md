# Apply a config change

- Run the steps in order and skip none.
- Before the first write → read `references/write-model.md`.
- The request is the slash-command listing → `$G` is the writer, per `references/generator.md`: `--check` shows the drift, `--apply` is step 5's write, `--restart` its restart; every other step still holds, except step 1's split — one pass covers both layers.

## Process

1. Name the layer: vocabulary (recogniser) or mode prompt (cleanup model), per `references/layers.md`. A request naming both → two passes through this workflow.
2. Back up the file being changed, outside the config folder.
3. Decide when it loads. The user asked for it to land now → restart after writing, unless a dictation is in flight or just ended, per `references/write-model.md` § Detecting a dictation in progress. Otherwise → write, and report that it loads at the next restart, one the user makes included.
4. Dry-run the merge: read the file fresh, build the new content — add what is missing, carry everything else through untouched — and diff it against the file. Confirm the untouched part is byte-identical — the vocabulary holds entries put there for other reasons, and a mode prompt is handwritten outside its generated roster. A mode-prompt edit → handwritten text lands above the roster's rule 24, per `references/layers.md` § Layer 2 — the cleanup model, and the cost of anything added is named, per `references/write-model.md` § Traps.
5. Write, whether or not the app is running, and record that the write waits for a launch. Step 3 said restart → restart, then confirm the process is up by a process check, never by the launch command's exit code.
6. Confirm ingestion per `references/write-model.md` § Witnesses; a mode prompt → ask the user for one short dictation.
7. Report per `SKILL.md` § Completion.
