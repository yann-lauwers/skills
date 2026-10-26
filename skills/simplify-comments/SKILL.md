---
name: simplify-comments
description: "Carries a file's comments into its code and deletes them — each becomes a name or a type where the file can hold it, goes where the code already says it, or is handed back where only a cross-file rename or a test could carry it. Works one named file, or the working tree's changed files. Use on \"simplify the comments\", \"clean up the comments\", \"remove the comments\", \"comment diet\", or the /simplify-comments command. Behaviour-preserving. Also answers, without running a pass, which comment lines a build, lint or run reads and must stay. Not for reviewing changed code for reuse and quality — `/simplify`."
argument-hint: [file-path]
---

# Simplify Comments

- This pass leaves one file with no comment but the lines a tool reads, without changing what it does.
- One file at a time; no argument → the working tree's changed files, worked in turn and named in the reply.
- The per-comment steps → `cookbook/simplify.md`; the verdicts and what stays → `references/decision-rules.md`; read both before touching the file.

## Guardrails

- Behaviour-preserving: a rename or a narrowed type stays inside the file and changes no exported name; anything wider is handed back.
- Never invent a meaning: a comment asserting a why the code does not show is handed back with its text, never rewritten into a guess.
- A line a tool reads stays → `references/decision-rules.md` § Lines a tool reads; asked only which lines those are → answer from it and run no pass.
- Names written by this pass use the terms the file's `GLOSSARY.md` defines — reached through the root `GLOSSARY-MAP.md` when present, else the one nearest the file — never a synonym it avoids.
