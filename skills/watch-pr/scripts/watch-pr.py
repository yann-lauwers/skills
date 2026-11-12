#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Watch one pull request; print one JSON line when its verdict is news, then exit 0.

Reads GitHub through `gh api` and git through the local checkout, never writes to either.
Each cycle reads uncached, classifies (pr_classify.py), and sleeps --interval; the line is
printed once `verdict:key` differs from --seen. WAITING is never printed except by --once.

Verdicts: MERGED CLOSED DRAFT CONFLICT HUMAN_COMMENTS BOT_THREADS CI_RED BASE_ADVANCED CLEAN
          WAITING WATCHER_ERROR (auth | duplicate | pr_not_found | gh_missing | blind)
Every non-terminal line carries `rearm`: the whole argument list of the next arm.

Usage: watch-pr.py [--pr N|URL] [--repo OWNER/REPO] [--seen VERDICT:KEY] [--once]
       No --pr: the pull request of the branch checked out in the current folder.
Exit:  0 verdict or --once | 1 traceback | 2 bad args | 3 duplicate | 4 auth or gh missing
       | 5 PR not found | 7 blind (no read landed for --blind-after)
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import pr_reads
from pr_classify import classify
from pr_reads import Auth, GhError, GhMissing, NotFound, RateLimited, Reader

EXIT_OK, EXIT_ARGS, EXIT_DUPLICATE, EXIT_AUTH, EXIT_NOT_FOUND, EXIT_BLIND = 0, 2, 3, 4, 5, 7
TERMINAL = {"MERGED", "CLOSED"}
BACKOFF_CEILING = 600
SHA_WIDTH = 12
MAX_ITEMS = 10
PR_URL = re.compile(r"github\.com/([^/\s]+)/([^/\s]+)/pull/(\d+)")
LOCK_ROOT = Path.home() / ".local" / "state" / "watch" / "pr"


def emit(line: dict) -> None:
    print(json.dumps(line, separators=(",", ":")), flush=True)


def note(msg: str) -> None:
    print(f"watch-pr: {msg}", file=sys.stderr, flush=True)


def fail(error: str, detail: str, code: int, pr=None) -> None:
    emit({"verdict": "WATCHER_ERROR", "reason": detail, "error": error, "pr": pr})
    sys.exit(code)


def gh_view(cmd: list[str], what: str) -> dict:
    try:
        proc = subprocess.run(["gh", *cmd], capture_output=True, text=True, timeout=pr_reads.GH_TIMEOUT)
    except FileNotFoundError:
        fail("gh_missing", "gh is not installed or not on PATH", EXIT_AUTH)
    except subprocess.TimeoutExpired:
        fail("pr_not_found", f"{what}: gh exceeded {pr_reads.GH_TIMEOUT:.0f}s", EXIT_NOT_FOUND)
    if proc.returncode != 0:
        fail("pr_not_found", f"{what}: {proc.stderr.strip()[:200]}", EXIT_NOT_FOUND)
    return json.loads(proc.stdout)


def resolve_target(pr_arg: str | None, repo_arg: str | None) -> tuple[str, str, int]:
    """(owner, repo, number) from a URL, from a number plus --repo or the current folder's
    repo, or from the current folder's branch."""
    url = PR_URL.search(pr_arg or "")
    if url:
        return url.group(1), url.group(2), int(url.group(3))
    if pr_arg and not pr_arg.isdigit():
        note("--pr must be a number or a pull request URL")
        sys.exit(EXIT_ARGS)
    if repo_arg:
        owner, _, name = repo_arg.partition("/")
        if not owner or not name:
            note("--repo must be OWNER/REPO")
            sys.exit(EXIT_ARGS)
    else:
        found = gh_view(["repo", "view", "--json", "owner,name"], "no repo in the current folder and no --repo")
        owner, name = found["owner"]["login"], found["name"]
    if pr_arg:
        return owner, name, int(pr_arg)
    found = gh_view(["pr", "view", "--repo", f"{owner}/{name}", "--json", "number"]
                    if repo_arg else ["pr", "view", "--json", "number"],
                    "no pull request for the current branch and no --pr")
    return owner, name, int(found["number"])


def take_lock(slug: str, pr: int):
    LOCK_ROOT.mkdir(parents=True, exist_ok=True)
    fd = os.open(LOCK_ROOT / f"{slug}.lock", os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        holder = os.read(fd, 32).decode().strip()
        fail("duplicate", f"another watcher holds {slug}" + (f" (pid {holder})" if holder else ""),
             EXIT_DUPLICATE, pr)
    os.ftruncate(fd, 0)
    os.write(fd, str(os.getpid()).encode())
    return fd


def dedupe_key(verdict: str, facts: dict) -> str:
    head = facts["head_sha"][:SHA_WIDTH]
    if verdict == "DRAFT":
        return head
    if verdict == "HUMAN_COMMENTS":
        return str(facts["human_items"][-1]["at"])
    if verdict == "BASE_ADVANCED":
        return f"{head}|{str(facts.get('base_tip_sha'))[:SHA_WIDTH]}"
    if verdict == "CI_RED":
        attempt = max((job["attempt"] or 1 for job in facts["failed_jobs"]), default=1)
        return f"{head}|{facts['unresolved_bot_threads']}|{attempt}"
    return f"{head}|{facts['unresolved_bot_threads']}"


def build_line(pr: int, pull: dict, facts: dict, humans_after: int) -> dict:
    v = facts["verdict"]
    line = {"verdict": v, "reason": facts["reason"], "pr": pr}
    if v in ("CONFLICT", "BASE_ADVANCED"):
        line.update(branch=pull["head"]["ref"], base=pull["base"]["ref"],
                    integration_base=facts["integration_base"])
    if v == "CI_RED":
        repo_path = pull["base"]["repo"]["full_name"]
        line["failed_jobs"] = [
            {"name": job["name"], "run_id": job["run_id"], "attempt": job["attempt"],
             "logs": f"repos/{repo_path}/actions/jobs/{job['job_id']}/logs" if job["job_id"] else None}
            for job in facts["failed_jobs"][:MAX_ITEMS]]
    if v == "HUMAN_COMMENTS":
        line["items"] = [{k: item[k] for k in ("author", "kind", "url")}
                         for item in facts["human_items"][-MAX_ITEMS:]]
        humans_after = facts["human_items"][-1]["at"]
    if facts["bots"]["stalled_checks"]:
        line["stalled_checks"] = facts["bots"]["stalled_checks"]
    if v not in TERMINAL:
        line["rearm"] = f"--pr {pull['html_url']} --seen {v}:{dedupe_key(v, facts)}" + (
            f" --humans-after {humans_after}" if humans_after else "")
    return line


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--pr", help="PR number or URL (default: the current branch's PR)")
    ap.add_argument("--repo", help="OWNER/REPO for a bare number (default: the current folder's repo)")
    ap.add_argument("--humans-after", type=int, default=0,
                    help="epoch seconds; human comments up to it are already handled")
    ap.add_argument("--seen", default="", help="VERDICT:KEY already acted on; print only a different one")
    ap.add_argument("--once", action="store_true",
                    help="one read, print the current line whatever the verdict, exit 0; no lock")
    ap.add_argument("--interval", type=int, default=60, help="seconds between reads (default 60)")
    ap.add_argument("--blind-after", type=int, default=3600,
                    help="seconds with no read landing before WATCHER_ERROR blind, exit 7 (default 3600; 0 disables)")
    ap.add_argument("--fresh-window", type=int, default=420)
    ap.add_argument("--bot-pending-timeout", type=int, default=1800)
    return ap


def main() -> None:
    args = build_parser().parse_args()
    owner, repo, pr = resolve_target(args.pr, args.repo)
    if not args.once:
        take_lock(f"{owner}-{repo}-{pr}", pr)
    reader = Reader(owner, repo, pr, args.fresh_window, args.bot_pending_timeout)
    last_ok, wait, read_once = time.monotonic(), args.interval, False
    while True:
        try:
            read = reader.read()
        except Auth as e:
            fail("auth", str(e), EXIT_AUTH, pr)
        except GhMissing as e:
            fail("gh_missing", str(e), EXIT_AUTH, pr)
        except (NotFound, RateLimited, GhError) as e:
            if isinstance(e, NotFound) and not read_once:
                fail("pr_not_found", f"PR {pr} or repo not found (404)", EXIT_NOT_FOUND, pr)
            if args.once:
                fail("unknown", str(e), 1, pr)
            if args.blind_after and time.monotonic() - last_ok > args.blind_after:
                fail("blind", f"no read landed for {args.blind_after}s; last: {e}", EXIT_BLIND, pr)
            pause = max(e.retry_after if isinstance(e, RateLimited) else 0, wait)
            note(f"read failed ({e}); retrying in {pause:.0f}s")
            time.sleep(pause)
            wait = min(2 * wait, BACKOFF_CEILING)
            continue
        read_once, last_ok, wait = True, time.monotonic(), args.interval
        facts = classify({**read, "humans_after": args.humans_after})
        v = facts["verdict"]
        if args.once:
            emit(build_line(pr, read["pull"], facts, args.humans_after))
            sys.exit(EXIT_OK)
        if v != "WAITING" and f"{v}:{dedupe_key(v, facts)}" != args.seen:
            emit(build_line(pr, read["pull"], facts, args.humans_after))
            sys.exit(EXIT_OK)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
