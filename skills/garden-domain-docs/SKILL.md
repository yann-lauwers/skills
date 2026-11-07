---
name: garden-domain-docs
description: "Walks the decision records and glossaries against today's code and applies only what the user picks. Started only by /garden-domain-docs , with a folder or a record to narrow it."
disable-model-invocation: true
---

# Garden Domain Docs

- Run /domain-modeling first; every proposal meets its bar.
- The repo's domain docs name where its records and glossaries live; none provided → the user runs `/setup-matt-pocock-skills`.

## Process

### 1. Read

- Scope — the folder or record passed, else every records folder and every glossary.
- Read each record whole and test its claims against the code it names, as it stands today.

### 2. Classify

Each record takes one verdict:

- Keep — it meets domain-modeling's ADR bar and every clause holds.
- Update — the decision holds, a clause doesn't; each stale clause gets its replacement, checked at `path:line`.
- Supersede — a later decision replaced it and the road between them is worth knowing; mark it per domain-modeling's ADR format, its text left as written.
- Fold into code — it fails the bar because a reader of the code would not wonder why; name what will carry it; a rule a check could enforce becomes the check.
- Merge — two records hold one decision; the survivor carries both, the other's lessons in its _Considered options_.
- Move — it sits outside the folder domain-modeling's file structure and the repo's domain docs give it; name that folder.

Each glossary term takes one: keep · update · cut — it fails domain-modeling's glossary rules, or nothing in the code or the records uses it · move — to the glossary the file structure names.

### 3. Present

- One table per folder — record or term · verdict · one-line reason · change — with the folder's numbering after the changes beneath it.
- Calls only the user can make → one round of questions per /grilling ; then wait.

### 4. Apply what the user picked

Make the picked changes, renumber each touched folder, and rewrite every citation of a number that moved. Done when, in every records folder:

- the numbers run 0001, 0002, … with no gap and none twice, superseded records included;
- every path a record names exists, and every record number cited in the repo names the record it meant.
