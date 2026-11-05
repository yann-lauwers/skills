---
name: simplify-comments
description: "Carries a file's comments into its code and deletes them. Started only by /simplify-comments ."
argument-hint: [file-path]
disable-model-invocation: true
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
