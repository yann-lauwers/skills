#!/usr/bin/env python3
import argparse
import hashlib
import math
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
VIDEO_SUFFIXES = {".webm", ".mp4", ".mov"}
AGENTS_CONFIG = Path.home() / ".claude/skills/agents-config/scripts/agents-config"


class Refused(Exception):
    pass


def run(argv: list[str], cwd: Path | None = None, env: dict | None = None, stdin: bytes | None = None) -> str:
    completed = subprocess.run(argv, cwd=cwd, env=env, input=stdin, capture_output=True)
    if completed.returncode != 0:
        raise Refused(f"{' '.join(argv[:3])} exited {completed.returncode}: {completed.stderr.decode().strip()}")
    return completed.stdout.decode().strip()


def frame_size(path: Path) -> tuple[int, int]:
    width, height = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(path)]).split(",")[:2]
    return int(width), int(height)


def captures(scenario: Path, fps: float, scratch: Path) -> list[Path]:
    frames: list[Path] = []
    for entry in sorted(scenario.rglob("*")):
        suffix = entry.suffix.lower()
        if suffix in IMAGE_SUFFIXES:
            frames.append(entry)
        elif suffix in VIDEO_SUFFIXES:
            folder = scratch / f"video-{len(frames):04d}"
            folder.mkdir()
            run(["ffmpeg", "-loglevel", "error", "-i", str(entry), "-vf", f"fps={fps}", str(folder / "%04d.png")])
            frames.extend(sorted(folder.glob("*.png")))
    return frames


def sheet(scenario: Path, out: Path, columns: int | None, width: int, fps: float) -> Path:
    if not scenario.is_dir():
        raise Refused(f"{scenario} is not a scenario directory")
    with tempfile.TemporaryDirectory() as scratch_name:
        scratch = Path(scratch_name)
        frames = captures(scenario, fps, scratch)
        if not frames:
            raise Refused(f"{scenario} holds no image or video")
        first_width, first_height = frame_size(frames[0])
        cell_width = min(width, first_width)
        cell_height = round(first_height * cell_width / first_width / 2) * 2
        cells = scratch / "cells"
        cells.mkdir()
        fit = f"scale={cell_width}:{cell_height}:force_original_aspect_ratio=decrease,pad={cell_width}:{cell_height}:(ow-iw)/2:(oh-ih)/2:color=white"
        for index, frame in enumerate(frames):
            run(["ffmpeg", "-loglevel", "error", "-i", str(frame), "-vf", fit, str(cells / f"{index:04d}.png")])
        across = columns or min(len(frames), 4)
        down = math.ceil(len(frames) / across)
        out.parent.mkdir(parents=True, exist_ok=True)
        run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(cells / "%04d.png"), "-vf", f"tile={across}x{down}:padding=8:margin=8:color=white", "-frames:v", "1", str(out)])
    return out


def evidence_branch(repo: Path) -> str:
    value = run([str(AGENTS_CONFIG), "get", "git", "evidence_branch", "--root", str(repo)])
    if value in ("", "null", "None"):
        raise Refused("the git config's evidence_branch is null: this repo publishes no evidence")
    return value


def forge_repository(repo: Path) -> str:
    try:
        return run(["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"], cwd=repo)
    except Refused as refusal:
        raise Refused(f"no GitHub repository answers for {repo}: {refusal}") from None


def remote_tip(repo: Path, branch: str) -> str | None:
    listed = run(["git", "ls-remote", "origin", f"refs/heads/{branch}"], cwd=repo)
    if not listed:
        return None
    tip = listed.split()[0]
    run(["git", "fetch", "-q", "origin", f"refs/heads/{branch}"], cwd=repo)
    return tip


def publish(files: list[Path], repo: Path, attempts: int = 2) -> list[str]:
    for file in files:
        if not file.is_file():
            raise Refused(f"{file} is not a file")
    branch = evidence_branch(repo)
    repository = forge_repository(repo)
    placed = [(file, f"{hashlib.sha256(file.read_bytes()).hexdigest()[:12]}/{file.name}") for file in files]
    for attempt in range(attempts):
        tip = remote_tip(repo, branch)
        with tempfile.TemporaryDirectory() as scratch_name:
            env = {**os.environ, "GIT_INDEX_FILE": str(Path(scratch_name) / "index")}
            if tip:
                run(["git", "read-tree", tip], cwd=repo, env=env)
            for file, path in placed:
                blob = run(["git", "hash-object", "-w", str(file)], cwd=repo)
                run(["git", "update-index", "--add", "--cacheinfo", f"100644,{blob},{path}"], cwd=repo, env=env)
            tree = run(["git", "write-tree"], cwd=repo, env=env)
        parents = ["-p", tip] if tip else []
        commit = run(["git", "commit-tree", tree, *parents, "-m", f"Evidence: {', '.join(file.name for file in files)}"], cwd=repo)
        try:
            run(["git", "push", "-q", "origin", f"{commit}:refs/heads/{branch}"], cwd=repo)
        except Refused:
            if attempt + 1 == attempts:
                raise
            continue
        return [f"![{file.stem}](https://github.com/{repository}/blob/{commit}/{path}?raw=true)" for file, path in placed]
    raise Refused("the push never landed")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="evidence.py",
        description="Turn a run directory's captures into images a pull request body embeds.",
        epilog=(
            "example:\n"
            "  evidence.py sheet .proof-runs/after/slash-menu --out /tmp/after.png\n"
            "  evidence.py publish /tmp/before.png /tmp/after.png --repo .\n"
            "publish prints one Markdown image line per file, linked at the pushed commit so it never changes."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    verbs = parser.add_subparsers(dest="verb", required=True)
    tiled = verbs.add_parser("sheet", help="tile every image of one scenario directory, in name order, into one PNG; a video is cut into frames first")
    tiled.add_argument("scenario", type=Path, help="one scenario directory of a run directory")
    tiled.add_argument("--out", type=Path, help="the PNG to write; default <scenario>.sheet.png beside the scenario")
    tiled.add_argument("--columns", type=int, help="frames per row; default up to 4")
    tiled.add_argument("--width", type=int, default=640, help="the widest a frame is drawn, in pixels (default 640)")
    tiled.add_argument("--fps", type=float, default=4, help="frames taken per second of a video (default 4)")
    posted = verbs.add_parser("publish", help="commit the files onto the git config's evidence_branch, push it, print the image lines")
    posted.add_argument("files", type=Path, nargs="+", help="the images to publish")
    posted.add_argument("--repo", type=Path, default=Path.cwd(), help="the checkout whose origin receives them (default: here)")
    parsed = parser.parse_args(argv)
    try:
        if parsed.verb == "sheet":
            out = parsed.out or parsed.scenario.with_name(f"{parsed.scenario.name}.sheet.png")
            print(sheet(parsed.scenario, out, parsed.columns, parsed.width, parsed.fps))
        else:
            for line in publish(parsed.files, parsed.repo.resolve()):
                print(line)
    except Refused as refusal:
        print(f"evidence: {refusal}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    if not shutil.which("ffmpeg") and len(sys.argv) > 1 and sys.argv[1] == "sheet":
        print("evidence: sheet needs ffmpeg on PATH", file=sys.stderr)
        sys.exit(1)
    sys.exit(main(sys.argv[1:]))
