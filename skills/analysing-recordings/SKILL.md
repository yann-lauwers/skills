---
name: analysing-recordings
description: >-
  Reads what a video or audio recording shows and says, and settles whether a recording handed over
  needs reading at all. Use when one is handed over — 'what does this show', 'watch this', 'here is
  a recording of the bug', 'transcribe this .m4a', 'summarise the call' — or when asked whether
  Claude understands a video. Also fires on a .mp4, .mov or .m4a arriving with a question or a bare
  note, and on a recording handed over to store, attach or upload.
---

# Analysing Recordings

- Read the file the routing table names before acting.

## Does this recording get analysed?

- Answering needs what is inside the file → analyse it · a recording named as a fact, a payload or a destination → handle it as a file, and run no breakdown.

| The task is | Route |
| --- | --- |
| "what does this show", "watch this", "what did I say" | Analyse |
| A recording attached with a question about its content | Analyse |
| "here is a recording of the bug" | Analyse |
| "summarise the call", "transcribe this" | Analyse — audio-only takes the same path |
| Store it in the vault, a repo, or a workspace | Handle as a file — move it, name it, record where it went |
| Attach it to a ticket, a PR, or a message | Handle as a file |
| Rename, copy, upload, check its size | Handle as a file |
| A recording mentioned in passing ("we recorded a demo") | Answer the sentence — nothing is being handed over |

- Stored and analysed → store it at the destination the user named first, then analyse the copy there, per `cookbook/analyse-recording.md` step 3.

## Routing table

| If the task is | Read |
| --- | --- |
| Reading what a recording shows or says | `cookbook/analyse-recording.md` |
| Choosing a frame rate, scene mode, or handling a recording over ~10 minutes | `references/sampling.md` |
| `ffmpeg`, `whisper-cli` or the model file is missing, the script fails on tooling, which speech model, the typed command | `references/toolchain.md` |
| Anything else, or the analyse-versus-file call is unclear | `cookbook/analyse-recording.md` |

## The one command

```
${CLAUDE_SKILL_DIR}/scripts/breakdown.py <recording>
```

- It writes `<recording>-breakdown/` beside the recording, holding `frames/`, `transcript.srt` and `MANIFEST.md` — the entry point: one row per frame, carrying the frame's path and what was spoken around it.
- Run it with `--help` before reaching for an option.
