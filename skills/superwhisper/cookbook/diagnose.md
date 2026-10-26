# Diagnose a change that did not take

- Run the checks in order; the evidence, not the order, names the cause.
- Read `references/write-model.md` and `references/layers.md` before step 1.
- Suspect a correct write the app never read, or a correct change on the wrong layer, before a broken write.

## Process

1. Reproduce the symptom: the exact spoken phrase and the exact text produced, never a remembered symptom.
2. The symptom is "the notification did nothing" → compare the app's process id and the live vocabulary against what they were before the click. Changed → the action ran and only its confirmation was lost: a reporting defect, not a broken button. A command launched from a notification click inherits a bare environment, so a binary resolved by name is missing there — the reporter first.
3. Read the file. The change absent → the app saved a UI change over it before its next launch; rerun `cookbook/apply.md`. The change present → continue.
4. Check the app is running: a failed relaunch leaves the config correct and the app down, while every earlier step looks clean.
5. Check ingestion per `references/write-model.md` § Witnesses. Written but not ingested → the app has not launched since the write; restart it, then read the witness again.
6. Check the layer per `references/layers.md` § Which stage owns the symptom, on a recording's raw transcript against its final text. The name already in the live vocabulary → its bias lost to an ordinary phrase that sounds like it: count that phrase across the corpus's raw transcripts — meant as the name, meant as speech, and how often the final text kept it — before choosing between a replacement and a prompt line.
7. Check for a competing entry: a literal replacement matching the same phrase rewrites the transcript before the model sees it, and overrides whatever the prompt says.
8. Report the cause and the layer, then run `cookbook/apply.md` against the correct one.
