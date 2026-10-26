---
name: resurrect
description: >-
  Rebuilds a dead session's state from disk, re-verifies every claim live, and writes one handoff.
  Use on "resurrect", "that session died", "it hit the context wall", "pick up where that one left
  off", "recover that session", or a session id to continue; fires when a dead session's transcript
  is about to be read to carry its work on. Not for a brief from the live session — /handoff-yann ;
  not for a live session near its limit — `/compaction fire`; not for a dead account
  — /relogin .
argument-hint: "[session-id]"
---

# Resurrect

- Every fact in the handoff is verified on disk or by a live call before it is written.
- Read `cookbook/resurrect.md` whole before acting; it names each reference at the step that reads it.

## Routing

| IF the invocation… | THEN |
| --- | --- |
| carries a session id (`/resurrect <uuid>`) | Read `cookbook/resurrect.md`, start at Step 1 |
| arrives bare ( /resurrect ) | Read `cookbook/resurrect.md`, start at Step 0 — list recent sessions, let the user pick |
| needs the transcript's on-disk shape, artifact dirs, or death-marker signatures | Read `references/transcript-forensics.md` |
| needs the handoff document's sections or the task-restore block | Read `references/handoff-shape.md` |
