---
name: garden-domain-docs
description: Walk the decision records and glossaries against today's code, propose what to keep, update, supersede, fold into code or move, and apply only what the user picks. Started only by the user typing /garden-domain-docs , with a folder or a record to narrow it.
disable-model-invocation: true
---

# Garden Domain Docs

Decision records and glossaries drift: the code moves on and the docs keep describing the app as it was. This command walks them against today's code and **proposes** one change per record and per term. Nothing changes until the user picks.

Call the Skill tool with "domain-modeling" first. It owns what a record and a term are, where they live and how they're written; every proposal here meets its bar.

Where this repo keeps its records and glossaries should have been provided to you (its domain docs). If not, tell the user to run `/setup-matt-pocock-skills`.

## Process

### 1. Read

Take the scope the user passed, a folder or a record; otherwise every records folder and every glossary. Read each record whole, open the code it names, and judge it against today's code: the record's own claims are what is under test.

### 2. Classify

Give each record one verdict:

- **Keep**: it still meets domain-modeling's bar for an ADR, and every clause holds.
- **Update**: the decision holds but a clause doesn't. _Use when_ a path is gone, the code changed the behaviour, or a sentence only tells how an implementation that no longer exists worked. Give each stale clause its replacement, checked at `path:line`.
- **Supersede**: a later decision replaced it, and the road from one to the other is worth knowing. Mark it superseded as domain-modeling's ADR format says, and leave its text as written: it tells the next reader why the old way was left, so nobody walks back to it.
- **Fold into code**: it no longer meets the bar, because a reader of the code would not wonder why. Name what will carry it: a type, a name, a test titled by the failure. A rule a check could enforce becomes the check.
- **Merge**: two records hold one decision. The survivor carries both, and the other's lessons go into its _Considered options_.
- **Move**: it sits somewhere other than where domain-modeling's file structure and the repo's domain docs put it. Name the right folder.

Give each glossary term one: **keep**, **update**, **cut** (it fails domain-modeling's glossary rules, or nothing in the code or the records uses it), or **move** (to the glossary where the file structure puts it).

### 3. Present

One table per folder: record or term, verdict, a one-line reason, the change. Under it, each folder's numbering after the changes. Put the calls only the user can make (a record that fails the bar but may matter to them, a lesson that might go) as one round of questions, worded the way `/grilling` words them, each with your recommended answer. Then wait.

### 4. Apply what the user picked

Make the picked changes, renumber each touched folder, and rewrite every citation of a number that moved. Done when, in every records folder:

- the numbers run 0001, 0002, … with no gap and none twice, superseded records included;
- every path a record names exists, and every record number cited in the repo names the record it meant.
