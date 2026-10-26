---
name: disk-cleanup
description: >-
  Frees disk space on this Mac: maps every folder of 1 GB or more on the data volume, has research
  agents sort what is stale, merged, rebuildable or temporary into safe and risky candidates, and
  cleans the ones the owner picks. Use when the request says "disk full", "free up disk", "what is
  taking space", "System Data is huge", "no space left". Also fires on a write, build or test
  failing on "No space left on device" or ENOSPC, or `df` showing the data volume past 90%. Not for
  removing one named worktree — /worktrunk .
argument-hint: "[area to focus on]"
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
