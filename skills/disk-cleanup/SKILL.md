---
name: disk-cleanup
description: >-
  Frees disk space on this Mac, cleaning only the candidates the owner picks. Started only by
  /disk-cleanup .
argument-hint: "[area to focus on]"
disable-model-invocation: true
---

# Disk cleanup

- Deletion waits for the owner to name the ID.
- Read `cookbook/cleanup.md` whole before acting; it names each script and reference at the step that uses it.

## Routing

| IF the invocation… | THEN |
| --- | --- |
| arrives bare, or names the whole disk | Read `cookbook/cleanup.md`, start at Step 1 |
| names an area ("just `~/Library`") | Read `cookbook/cleanup.md`, run Steps 1–2, then Step 3 with only that area's brief and the Explorer |
| holds a size map from earlier in this session | Read `cookbook/cleanup.md`, start at Step 3 |
| needs the research agents' briefs | Read `references/agent-briefs.md` |
