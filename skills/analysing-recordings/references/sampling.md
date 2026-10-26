# Sampling a recording

- Default: even spread, at most one frame per second and 24 in all (`--max-frames N` moves the ceiling, `--fps N` is uncapped). `--scene [threshold]` takes a frame per visual change; it decodes the whole file, so its cost grows with length.
- Frames near-identical with the change between two → `--fps 2` or `--scene 0.08`; the moment sits in a known window → trim it, then `--fps 4`.
- Names or jargon misspelled → `--prompt "Name1, Name2, …"`. Transcript reads `(speaking in foreign language)` → an English-only model met other speech; re-run with a multilingual model on disk. One segment spanning the whole run → the model produced no timings; check the model file.
- Past ~10 minutes the spread leaves whole screens unseen. Ask which minute matters; else `--max-frames 6` for a skeleton, find the moment in the transcript, then re-run on a window cut with `ffmpeg -ss <from> -to <to> -c copy`. Transcribe the whole recording once; re-run only windows.

## What a frame cannot carry

- The cursor: a few pixels, it reads as noise; where the user points comes from the transcript.
- Motion between two samples: a drag, a scroll or an animation.
- Anything shorter than the sampling interval: a 400 ms toast at one frame per second is invisible, and its absence is no evidence it never fired.
