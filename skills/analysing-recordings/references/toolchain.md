# Toolchain

- `ffmpeg` + `ffprobe` (frames, audio, probing) and `whisper-cli` (`brew install ffmpeg whisper-cpp`) must resolve on `PATH`; `whisper-cli` missing → run with `--no-audio` and say the transcript is absent, `ffmpeg` or `ffprobe` missing → stop.
- Models are `ggml-*.bin` from `https://huggingface.co/ggerganov/whisper.cpp/tree/main`, kept in `~/.local/share/whisper-models/`. The script takes the first one on disk in its `MODEL_PREFERENCE` order, so installing a better one moves the default; `--model` overrides. Short clip → `--lang <code>` beats `auto`.

| Model | Size | Fits |
| --- | --- | --- |
| `ggml-large-v3.bin` | 2.9 GB | most accurate on accents, noise, overlap, rare vocabulary |
| `ggml-large-v3-turbo-q5_0.bin` | 547 MB | ties `large-v3` on clean speech, faster |
| `ggml-small.bin` | 465 MB | fallback when disk is tight |
| `ggml-base.bin` | 141 MB | last resort, garbles ordinary words |

- An `.en` model returns `(speaking in foreign language)` for non-English speech → emergency fallback only.
- Download a model over ~100 MB in the background.
- Homebrew's `ffmpeg` has no `drawtext`, and `-vsync` is gone → `-fps_mode`.
- A person outside a session runs `~/.local/bin/recording-breakdown`, an absolute-target symlink to `scripts/breakdown.py`; a session never needs it.
