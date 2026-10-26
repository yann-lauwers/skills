#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Turn a recording into frames, a timestamped transcript, and a MANIFEST.md joining them.

Stdlib only — ffmpeg/ffprobe/whisper-cli are external binaries, called via subprocess.
Reads no credentials and prints none.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# 24 frames keeps a whole recording readable in one pass: each frame is an image the
# reader opens, and past ~30 the useful ones sit buried in near-duplicates.
DEFAULT_MAX_FRAMES = 24
# 0.15 is ffmpeg's practical floor for "the screen changed" on UI captures; lower
# thresholds fire on cursor movement alone.
DEFAULT_SCENE_THRESHOLD = 0.15
# A request carrying more than 20 images rejects any image over 2000 px on its long
# edge, and a recording's frames are read in one conversation. Menu-bar text on a
# Retina capture stays legible at this size.
FRAME_SCALE = ("scale='if(gte(iw,ih),min(2000,iw),-2)':'if(gte(iw,ih),-2,min(2000,ih))'"
               ":flags=lanczos")
# Multilingual models only: an .en model transcribes non-English speech as the
# literal string "(speaking in foreign language)" rather than failing. Ordered
# most accurate first; the first one present on disk wins. large-v3 leads by
# owner preference: on clean speech it ties the turbo build, and the margin it
# holds in reserve is for hard audio, where the distilled turbo gives ground.
MODEL_DIR = Path.home() / ".local/share/whisper-models"
MODEL_PREFERENCE = [
    "ggml-large-v3.bin",
    "ggml-large-v3-turbo-q5_0.bin",
    "ggml-large-v3-turbo.bin",
    "ggml-small.bin",
    "ggml-base.bin",
    "ggml-base.en.bin",
]


def resolve_model() -> Path | None:
    for name in MODEL_PREFERENCE:
        candidate = MODEL_DIR / name
        if candidate.is_file():
            return candidate
    return None


def die(msg: str) -> None:
    print(f"breakdown: {msg}", file=sys.stderr)
    raise SystemExit(2)


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        die(f"{cmd[0]} is not installed — run the tooling check")


def probe(video: Path) -> dict:
    cp = run(["ffprobe", "-v", "error", "-print_format", "json",
              "-show_format", "-show_streams", str(video)])
    if cp.returncode != 0:
        die(f"ffprobe failed: {cp.stderr.strip()}")
    data = json.loads(cp.stdout or "{}")
    streams = data.get("streams", [])
    video_s = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio_s = next((s for s in streams if s.get("codec_type") == "audio"), None)
    return {
        "duration": float(data.get("format", {}).get("duration") or 0.0),
        "width": (video_s or {}).get("width"),
        "height": (video_s or {}).get("height"),
        "has_video": video_s is not None,
        "has_audio": audio_s is not None,
    }


def extract_frames(video: Path, out: Path, duration: float, fps: float | None,
                   scene: float | None, max_frames: int) -> list[tuple[float, str]]:
    fdir = out / "frames"
    fdir.mkdir(parents=True, exist_ok=True)
    for old in fdir.glob("*.png"):
        old.unlink()

    if scene is None:
        if fps is None:
            fps = min(1.0, max_frames / duration) if duration > 0 else 1.0
        count = max(1, int(duration * fps)) if duration > 0 else 1
        return grab_at(video, fdir, [i / fps for i in range(count)])

    # Scene detection has to compare every frame, so this mode alone decodes the whole file.
    ptslog = out / "pts.log"
    vf = f"select='gt(scene,{scene})',metadata=print:file={ptslog},{FRAME_SCALE}"
    cp = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(video),
              "-vf", vf, "-fps_mode", "vfr", str(fdir / "raw_%04d.png")])
    if cp.returncode != 0:
        die(f"ffmpeg frame extraction failed: {cp.stderr.strip()}")

    # A scene filter fires on change, so the opening state produces no frame.
    # Grab it separately, and name it raw_0000 so it sorts first.
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video),
         "-frames:v", "1", "-vf", FRAME_SCALE, str(fdir / "raw_0000.png")])

    raws = sorted(fdir.glob("raw_*.png"))
    times: list[float] = []
    if ptslog.exists():
        times = [0.0] + [float(m) for m in re.findall(r"pts_time:([0-9.]+)", ptslog.read_text())]
    if len(times) != len(raws):
        times = [float(i) for i in range(len(raws))]

    frames: list[tuple[float, str]] = []
    for raw, t in zip(raws, times):
        name = "t%08.3fs.png" % t
        raw.rename(fdir / name)
        frames.append((t, name))
    return frames


def grab_at(video: Path, fdir: Path, times: list[float]) -> list[tuple[float, str]]:
    # -ss before -i seeks to the nearest keyframe and decodes only from there, so
    # the cost follows the frame count rather than the recording's length.
    # A seek near the end of a stream whose last frames reference ones it cannot decode
    # exits 0 and writes nothing, so a missing file steps back half a second and retries.
    def grab(t: float) -> tuple[float, str]:
        for at in (t, t - 0.5, t - 1.0, t - 2.0):
            at = max(0.0, at)
            name = "t%08.3fs.png" % at
            cp = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{at:.3f}",
                      "-i", str(video), "-frames:v", "1", "-vf", FRAME_SCALE, str(fdir / name)])
            if cp.returncode == 0 and (fdir / name).exists():
                return at, name
        die(f"ffmpeg frame extraction failed at {t:.3f}s: {cp.stderr.strip()}")

    with ThreadPoolExecutor(max_workers=4) as pool:
        return list(pool.map(grab, times))


def transcribe(video: Path, out: Path, model: Path, lang: str = "auto",
               prompt: str | None = None) -> list[tuple[float, float, str]]:
    wav = out / "audio.wav"
    cp = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video),
              "-vn", "-ac", "1", "-ar", "16000", str(wav)])
    if cp.returncode != 0:
        print(f"audio    : extraction failed: {cp.stderr.strip()}")
        return []
    # No segment length cap: a character cap cuts sentences and words mid-way and
    # strips the punctuation, while whisper's own segments run a sentence, ~6s.
    cmd = ["whisper-cli", "-m", str(model), "-f", str(wav),
           "-osrt", "-of", str(out / "transcript"), "-np"]
    if prompt:
        cmd += ["--prompt", prompt]
    # An .en model takes no language; only a multilingual model does.
    if ".en." not in model.name:
        cmd += ["-l", lang]
    cp = run(cmd)
    srt = out / "transcript.srt"
    if cp.returncode != 0 or not srt.exists():
        print(f"audio    : whisper failed: {cp.stderr.strip()[:300]}")
        return []
    return parse_srt(srt)


def parse_srt(srt: Path) -> list[tuple[float, float, str]]:
    segs: list[tuple[float, float, str]] = []
    for block in re.split(r"\n\s*\n", srt.read_text(encoding="utf-8").strip()):
        m = re.search(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", block)
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        start = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        end = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        text = " ".join(line.strip() for line in block.splitlines()[2:] if line.strip())
        if text:
            segs.append((start, end, text))
    return segs


def write_manifest(out: Path, video: Path, info: dict,
                   frames: list[tuple[float, str]],
                   segs: list[tuple[float, float, str]]) -> Path:
    size = f"{info['width']}x{info['height']}" if info["has_video"] else "audio only"
    lines = [
        "# Recording breakdown\n",
        "| field | value |",
        "| --- | --- |",
        f"| source | `{video}` |",
        f"| duration | {info['duration']:.1f} s |",
        f"| resolution | {size} |",
        f"| frames | {len(frames)} |",
        f"| transcript | {'transcript.srt' if segs else 'none'} |",
        "",
        "Open each frame below as an image. One row is one moment in the recording.",
        "",
        "| time | frame | spoken around it |",
        "| --- | --- | --- |",
    ]
    for i, (t, name) in enumerate(frames):
        nxt = frames[i + 1][0] if i + 1 < len(frames) else info["duration"] or t + 1
        said = " ".join(s[2] for s in segs if s[1] > t and s[0] < nxt)
        lines.append(f"| {t:.1f}s | `frames/{name}` | {said.replace('|', '/')} |")
    if segs:
        lines.append("\n## Full transcript\n")
        lines += [f"- **{s:.1f}s–{e:.1f}s** {text}" for s, e, text in segs]
    path = out / "MANIFEST.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> int:
    p = argparse.ArgumentParser(description="Break a recording into frames + transcript.")
    p.add_argument("video", type=Path)
    p.add_argument("--out", type=Path, help="output dir (default: <video>-breakdown beside it)")
    p.add_argument("--fps", type=float, help="frames per second; overrides --max-frames")
    p.add_argument("--scene", nargs="?", type=float, const=DEFAULT_SCENE_THRESHOLD,
                   help="sample on scene change instead of a fixed rate")
    p.add_argument("--max-frames", type=int, default=DEFAULT_MAX_FRAMES)
    p.add_argument("--no-audio", action="store_true")
    p.add_argument("--model", type=Path, default=None,
                   help="whisper model; defaults to the best one present in ~/.local/share/whisper-models")
    p.add_argument("--lang", default="auto",
                   help="spoken language code, or auto to detect (default: auto)")
    p.add_argument("--prompt",
                   help="names and terms the speaker uses, comma-separated, so whisper spells them right")
    args = p.parse_args()

    model = args.model or resolve_model()

    video = args.video.expanduser().resolve()
    if not video.is_file():
        die(f"not a file: {video}")

    out = (args.out or video.parent / f"{video.stem}-breakdown").expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)

    info = probe(video)
    if not info["has_video"] and not info["has_audio"]:
        die("file carries neither a video nor an audio stream")

    print(f"source   : {video}")
    print(f"duration : {info['duration']:.1f}s")

    frames: list[tuple[float, str]] = []
    if info["has_video"]:
        frames = extract_frames(video, out, info["duration"], args.fps,
                                args.scene, args.max_frames)
        mode = f"scene>{args.scene}" if args.scene is not None else (
            f"fps={args.fps}" if args.fps else f"<={args.max_frames} spread over the run")
        print(f"frames   : {len(frames)} ({mode})")

    segs: list[tuple[float, float, str]] = []
    if info["has_audio"] and not args.no_audio:
        if model is None or not model.is_file():
            print(f"audio    : skipped - no model in {MODEL_DIR}")
        else:
            segs = transcribe(video, out, model, args.lang, args.prompt)
            print(f"audio    : {len(segs)} segments ({model.name}, lang={args.lang})")
    elif not info["has_audio"]:
        print("audio    : none in this file")

    manifest = write_manifest(out, video, info, frames, segs)
    print(f"manifest : {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
