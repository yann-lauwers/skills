---
name: simplify-comments
description: "Sweeps a codebase's comments: each one deleted, filed as an issue or moved to a decision record, then held at that count by lint. Started only by /simplify-comments ."
argument-hint: [path]
disable-model-invocation: true
---

# Simplify Comments

A sweep leaves the scope with no comment but tool lines, every hack a comment excused on the tracker, every decision a comment held in a record, and a lint check that lets the count only fall.

- Scope → the argument's path; none → the whole repo.
- Before step 1, read the repo's coding standard, where its decision records live and how its tracker takes an issue.

## Steps

1. **Inventory.** `node scripts/inventory.mjs <repo> [--under <path>] --json <file>` lists every comment and the whole lines each fills; `--help` says what it reads. A file type it skips → read those files. Done when every tracked code file type in scope is counted.
2. **Verdict.** Read each comment on the code it sits on and give it one verdict from `references/verdicts.md`. A verdict of `recorded` or `stale` names the doc line or the code that proves it. Done when every inventory entry has one.
3. **Excuse → issue.** Search the tracker for a ticket already covering the hack; none → file one issue per hack, stating what the code does, what the repo's rule says and when it is fixed. The comment goes once the issue exists; a tool line the build needs stays and enters the ratchet. Done when every `excuse` names its issue.
4. **Decision → record.** Group the `decision` comments by the thing they govern, one record per group, in the repo's own record format, carrying each comment's why in full. A doc the code now contradicts is corrected in the same pass. Done when every `decision` names its record.
5. **Delete.** Remove every comment but the tool lines, and rerun the inventory. Done when it lists tool lines only.
6. **Ratchet.** Add the lint check from `references/ratchet.md`, or extend the one the repo has. Done when lint passes on the tree, and fails on one probe comment per language, since removed.
7. **Verify.** Run the repo's formatter, lint and the tests of what changed. Done when each passes; one the repo lacks is named as not run.
8. **Report.** One table of every comment group — file, lines, verdict, what became of it — then the issues, the records, and the lines shed: whole lines deleted in this pass, whole lines left with why each stays, taken from the inventory before and after.

## Guardrails

- Behaviour-preserving: a deletion changes no line a tool reads; a rename that would carry a comment stays inside its file.
- A why is moved, never guessed: a comment whose reason the code and docs do not show goes into a record in its own words.
- A filed issue and a published record are outward-facing: the repo's tracker and record rules decide whether to ask first.
