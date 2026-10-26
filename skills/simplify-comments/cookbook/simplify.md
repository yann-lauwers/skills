# Simplify Workflow

1. Resolve the target: the argument's path; none → `git diff --name-only` plus staged and untracked files. Done when the list is named in the reply.
2. Read the whole file. Done when every line has been read, never a range.
3. Inventory every comment and docstring with its line and the code it sits on. Done when the entry count equals the file's comment count from a full scan.
4. Give each entry one verdict from `references/decision-rules.md` and print `L<line>: <verdict> — <reason>`, the reason naming what the code does or does not show. Done when every entry has one.
5. Apply every `carry` and `cut` in one pass; leave each `stays` line; delete each `hand back` comment only after its text is copied into the report. Done when the file holds no comment but `stays` lines.
6. Verify behaviour: the file's formatter, typecheck and the tests covering it pass, and no exported name changed. A failure → undo that one edit, then delete the comment once its text is in the report. A check the repo lacks is named as not run. Done when every check the repo has passes.
7. Report: `Simplified <file> — <carried> carried, <cut> cut, <handed> handed back, <kept> tool lines kept.` Under it, each handed-back comment with its line, its text and the rename, type or test that would carry it; the commit that deletes a handed-back comment quotes its text in its message where the tree has git; else the report names the tool's doc (its `CLAUDE.md`, its skill, or the row that registers it) and the constraint line to add there, and the entry is handed back.
