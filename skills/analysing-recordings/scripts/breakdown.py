#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Break a recording into the moments worth looking at: stills, contact sheets and what was said."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MODEL_DIR = Path.home() / ".local/share/whisper-models"
MODELS = ["ggml-large-v3.bin", "ggml-large-v3-turbo-q5_0.bin", "ggml-large-v3-turbo.bin"]
INSTALL = ("brew install ffmpeg whisper-cpp, and a multilingual model from "
           "https://huggingface.co/ggerganov/whisper.cpp/tree/main "
           f"(ggml-large-v3.bin) in {MODEL_DIR}")

SILENCE_FILTER = "silencedetect=noise=-35dB:d=0.5"
LONGEST_PIECE_WHISPER_HEARS_SECONDS = 28.0
MIN_SPEECH_SECONDS = 0.4

SPREAD_FRAMES = 40
SPREAD_MIN_STEP, SPREAD_MAX_STEP = 0.2, 5.0
FIT_WITHIN_2000_PX = ("scale='if(gte(iw,ih),min(2000,iw),-2)':'if(gte(iw,ih),-2,min(2000,ih))'"
               ":flags=lanczos")
SHEET_COLUMNS, SHEET_ROWS, SHEET_TILE_WIDTH = 4, 3, 496

Span = tuple[float, float]
Segment = tuple[float, float, str]


def die(message: str) -> None:
    print(f"breakdown: {message}", file=sys.stderr)
    raise SystemExit(2)


def run(command: list[str]) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        die(f"{command[0]} is not installed — {INSTALL}")


def seconds(text: str) -> float:
    total = 0.0
    for part in text.split(":"):
        total = total * 60 + float(part)
    return total


def clock(t: float) -> str:
    return f"{int(t // 60)}:{t % 60:04.1f}"


def probe(recording: Path) -> dict:
    done = run(["ffprobe", "-v", "error", "-show_entries",
                "format=duration:stream=codec_type,width,height", "-of", "csv=p=0",
                str(recording)])
    if done.returncode != 0:
        die(f"ffprobe cannot read it: {done.stderr.strip()}")
    info = {"duration": 0.0, "video": False, "audio": False, "size": "no picture"}
    for line in done.stdout.split():
        fields = line.split(",")
        if fields[0] == "video":
            info["video"], info["size"] = True, f"{fields[1]}x{fields[2]}"
        elif fields[0] == "audio":
            info["audio"] = True
        elif fields[0]:
            info["duration"] = float(fields[0])
    return info


def speech_spans(wav: Path, start: float, end: float) -> list[Span]:
    done = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(wav), "-af", SILENCE_FILTER,
                "-f", "null", "-"])
    silences = [(float(a), float(b)) for a, b in re.findall(
        r"silence_start: (-?[\d.]+)[\s\S]*?silence_end: ([\d.]+)", done.stderr)]
    trailing = re.findall(r"silence_start: (-?[\d.]+)", done.stderr)
    if len(trailing) > len(silences):
        silences.append((float(trailing[-1]), end))
    spans, cursor = [], start
    for quiet_from, quiet_to in silences:
        if quiet_from - cursor >= MIN_SPEECH_SECONDS:
            spans.append((cursor, min(quiet_from, end)))
        cursor = max(cursor, quiet_to)
    if end - cursor >= MIN_SPEECH_SECONDS:
        spans.append((cursor, end))
    return [(a, b) for a, b in spans if b > start and a < end]


def pieces(spans: list[Span]) -> list[Span]:
    out: list[Span] = []
    for a, b in spans:
        while b - a > LONGEST_PIECE_WHISPER_HEARS_SECONDS:
            out.append((a, a + LONGEST_PIECE_WHISPER_HEARS_SECONDS))
            a += LONGEST_PIECE_WHISPER_HEARS_SECONDS
        if out and b - out[-1][0] <= LONGEST_PIECE_WHISPER_HEARS_SECONDS and a - out[-1][1] < 2.0:
            out[-1] = (out[-1][0], b)
        else:
            out.append((a, b))
    return out


def parse_srt(srt: Path, offset: float) -> list[Segment]:
    segments = []
    for block in re.split(r"\n\s*\n", srt.read_text(encoding="utf-8").strip()):
        stamp = re.search(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", block)
        if not stamp:
            continue
        g = [int(x) for x in stamp.groups()]
        text = " ".join(line.strip() for line in block.splitlines()[2:] if line.strip())
        if text:
            segments.append((offset + g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000,
                             offset + g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000, text))
    return segments


def transcribe(recording: Path, out: Path, start: float, end: float,
               terms: str | None) -> tuple[list[Segment], str]:
    model = next((MODEL_DIR / m for m in MODELS if (MODEL_DIR / m).is_file()), None)
    if model is None:
        die(f"no speech model on disk — {INSTALL}")
    wav = out / "audio.wav"
    done = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(recording),
                "-vn", "-ac", "1", "-ar", "16000", str(wav)])
    if done.returncode != 0:
        die(f"ffmpeg cannot extract the audio: {done.stderr.strip()}")
    spans = pieces(speech_spans(wav, start, end))
    if not spans:
        return [], "none — the track is silent"

    language, segments = "auto", []
    for index, (a, b) in enumerate(sorted(spans, key=lambda s: s[0] - s[1])):
        cut = out / f"piece-{index:03d}.wav"
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{max(0, a - 0.2):.3f}",
             "-to", f"{b + 0.2:.3f}", "-i", str(wav), str(cut)])
        command = ["whisper-cli", "-m", str(model), "-f", str(cut), "-l", language,
                   "-osrt", "-of", str(cut.with_suffix("")), "-sns"]
        if terms:
            command += ["--prompt", terms]
        done = run(command)
        srt = cut.with_suffix(".srt")
        if done.returncode != 0 or not srt.exists():
            die(f"whisper-cli failed on {clock(a)}–{clock(b)}: {done.stderr.strip()[-300:]}")
        detected = re.search(r"auto-detected language: (\w+)", done.stderr)
        if language == "auto" and detected:
            language = detected.group(1)
        segments += parse_srt(srt, max(0, a - 0.2))
        cut.unlink()
        srt.unlink()
    wav.unlink()
    segments.sort()
    spoken = sum(b - a for a, b in spans)
    return segments, f"{len(segments)} sentences over {spoken:.0f} s, language {language}"


def grab(recording: Path, frames: Path, times: list[float]) -> list[tuple[float, str]]:
    def one(t: float) -> tuple[float, str] | None:
        for at in (t, t - 0.5, t - 1.0, t - 2.0):
            at = max(0.0, at)
            name = f"t{at:08.2f}s.png"
            run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{at:.3f}",
                 "-i", str(recording), "-frames:v", "1", "-vf", FIT_WITHIN_2000_PX, str(frames / name)])
            if (frames / name).exists():
                return t, name
        return None

    with ThreadPoolExecutor(max_workers=4) as pool:
        return [hit for hit in pool.map(one, times) if hit]


def moments(segments: list[Segment], start: float, end: float) -> list[tuple[float, str]]:
    said = [((a + b) / 2, text) for a, b, text in segments]
    step = min(SPREAD_MAX_STEP, max(SPREAD_MIN_STEP, (end - start) / SPREAD_FRAMES))
    spread, t = [], start
    while t < end:
        if all(abs(t - at) > step / 2 for at, _ in said):
            spread.append((t, ""))
        t += step
    return sorted(said + spread)


def sheets(out: Path, stills: list[tuple[float, str]]) -> list[tuple[str, list[float]]]:
    folder = out / "sheets"
    folder.mkdir()
    per_sheet = SHEET_COLUMNS * SHEET_ROWS
    made = []
    for index in range(0, len(stills), per_sheet):
        batch = stills[index:index + per_sheet]
        listing = out / "sheet.txt"
        listing.write_text("".join(
            f"file '{out / 'frames' / name}'\nduration 1\n" for _, name in batch))
        name = f"sheet-{index // per_sheet + 1:02d}.png"
        done = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat",
                    "-safe", "0", "-i", str(listing), "-vf",
                    f"scale={SHEET_TILE_WIDTH}:-2,tile={SHEET_COLUMNS}x{SHEET_ROWS}:padding=4:margin=2",
                    "-frames:v", "1", str(folder / name)])
        listing.unlink()
        if done.returncode == 0:
            made.append((name, [t for t, _ in batch]))
    return made


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("recording", type=Path)
    parser.add_argument("--from", dest="start", type=seconds, default=0.0, metavar="M:SS",
                        help="read only from this moment")
    parser.add_argument("--to", dest="end", type=seconds, metavar="M:SS",
                        help="read only up to this moment")
    parser.add_argument("--terms", help="names and words the speaker uses, comma-separated, "
                                        "so they are spelled right")
    args = parser.parse_args()

    recording = args.recording.expanduser().resolve()
    if not recording.is_file():
        die(f"not a file: {recording}")
    info = probe(recording)
    if not info["video"] and not info["audio"]:
        die("the file carries neither picture nor sound")
    start = args.start
    end = min(args.end or info["duration"], info["duration"])
    if end <= start:
        die(f"nothing between {clock(start)} and {clock(end)}; the recording lasts {clock(info['duration'])}")

    tag = hashlib.sha1(f"{recording}{start}{end}".encode()).hexdigest()[:8]
    slug = re.sub(r"[^A-Za-z0-9]+", "-", recording.stem).strip("-")
    out = Path(os.environ.get("TMPDIR") or tempfile.gettempdir()) / "recordings" / f"{slug}-{tag}"
    shutil.rmtree(out, ignore_errors=True)
    (out / "frames").mkdir(parents=True)

    segments, speech = (transcribe(recording, out, start, end, args.terms)
                        if info["audio"] else ([], "none — the file has no sound"))
    rows = moments(segments, start, end)
    stills = grab(recording, out / "frames", [t for t, _ in rows]) if info["video"] else []
    names = dict(stills)
    made = sheets(out, stills) if stills else []

    lines = [
        f"# {recording.name}\n",
        f"- source: `{recording}`",
        f"- read: {clock(start)} to {clock(end)} of {clock(info['duration'])}, {info['size']}",
        f"- speech: {speech}",
        f"- stills: {len(stills)}, each under `{out}/frames/`\n",
        "| time | still | said |",
        "| --- | --- | --- |",
    ]
    lines += [f"| {clock(t)} | {'`' + names[t] + '`' if t in names else ''} | {text.replace('|', '/')} |"
              for t, text in rows]
    if made:
        lines += ["", "## Sheets", "",
                  f"Every still in order, left to right then top to bottom, under `{out}/sheets/`.", ""]
        lines += [f"- `{name}`: {' · '.join(clock(t) for t in times)}" for name, times in made]
    manifest = out / "MANIFEST.md"
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"speech   : {speech}")
    print(f"stills   : {len(stills)} on {len(made)} sheets")
    print(f"manifest : {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
