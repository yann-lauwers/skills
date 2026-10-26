#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Watch one pull request; print one JSON line when its verdict is news, then exit 0.

Reads GitHub through `gh api` and git through the local checkout, never writes to either.
Each cycle reads uncached, classifies (pr_classify.py), and sleeps --interval; the line is
printed once `verdict:key` differs from --seen. WAITING is never printed except by --once.

Verdicts: MERGED CLOSED DRAFT CONFLICT NEW_COMMENTS CI_RED BASE_ADVANCED CLEAN WAITING
          WATCHER_ERROR (auth | duplicate | pr_not_found | gh_missing | blind)
Every non-terminal line carries `rearm`: the flags that replace their namesakes on the next arm.

Usage: watch-pr.py --repo OWNER/REPO --pr N [--seen VERDICT:KEY] [--once]
Exit:  0 verdict or --once | 1 traceback | 2 bad args | 3 duplicate | 4 auth or gh missing
       | 5 PR not found | 7 blind (no read landed for --blind-after)
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
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
LOCK_ROOT = Path.home() / ".local" / "state" / "watch" / "pr"


def emit(line: dict) -> None:
    print(json.dumps(line, separators=(",", ":")), flush=True)


def note(msg: str) -> None:
    print(f"watch-pr: {msg}", file=sys.stderr, flush=True)


def fail(error: str, detail: str, code: int, pr=None) -> None:
    emit({"verdict": "WATCHER_ERROR", "reason": detail, "error": error, "detail": detail, "pr": pr})
    sys.exit(code)


def resolve_repo(arg: str | None) -> tuple[str, str]:
    if arg:
        owner, _, name = arg.partition("/")
        if not owner or not name:
            note("--repo must be OWNER/REPO")
            sys.exit(EXIT_ARGS)
        return owner, name
    try:
        proc = subprocess.run(["gh", "repo", "view", "--json", "owner,name"], capture_output=True,
                              text=True, timeout=pr_reads.GH_TIMEOUT)
    except subprocess.TimeoutExpired:
        note(f"cannot resolve repo from cwd: gh exceeded {pr_reads.GH_TIMEOUT:.0f}s")
        sys.exit(EXIT_ARGS)
    if proc.returncode != 0:
        note(f"cannot resolve repo from cwd: {proc.stderr.strip()[:200]}")
        sys.exit(EXIT_ARGS)
    d = json.loads(proc.stdout)
    return d["owner"]["login"], d["name"]


def resolve_pr(arg: str | None) -> int:
    if arg:
        return int(arg)
    try:
        proc = subprocess.run(["gh", "pr", "view", "--json", "number"], capture_output=True,
                              text=True, timeout=pr_reads.GH_TIMEOUT)
    except subprocess.TimeoutExpired:
        note(f"no PR for the current branch and no --pr: gh exceeded {pr_reads.GH_TIMEOUT:.0f}s")
        sys.exit(EXIT_ARGS)
    if proc.returncode != 0:
        note(f"no PR for the current branch and no --pr: {proc.stderr.strip()[:200]}")
        sys.exit(EXIT_ARGS)
    return int(json.loads(proc.stdout)["number"])


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
    head = facts["head_sha"]
    if verdict == "DRAFT":
        return head
    if verdict == "BASE_ADVANCED":
        return f"{head}|{facts.get('base_tip_sha')}"
    return f"{head}|{facts['unresolved_bot_threads']}"


def rewrite_answer(owner: str, repo: str, head_ref: str) -> tuple[str, str]:
    """(answer, reason) from the rewrite rule for the watched branch, in a local checkout of
    this repository. No checkout, or no rule module, is `unknown`, which routes the
    conflict to the merge."""
    policy = pr_reads.pr_policy()
    if policy is None:
        return "unknown", "the rewrite rule could not be loaded"
    checkout = pr_reads.find_repo_checkout(owner, repo)
    if not checkout:
        return "unknown", "no local checkout of this repository"
    try:
        verdict = policy.may_rewrite(checkout, head_ref, forge=(owner, repo))
    except Exception as exc:
        return "unknown", f"the rewrite rule raised {type(exc).__name__}"
    return verdict.answer, verdict.reason


def build_line(owner: str, repo: str, pr: int, pull: dict, facts: dict) -> dict:
    v = facts["verdict"]
    key = dedupe_key(v, facts)
    line = {
        "verdict": v, "reason": facts["reason"], "pr": pr, "repo": f"{owner}/{repo}",
        "url": pull.get("html_url"), "branch": pull["head"]["ref"], "base": pull["base"]["ref"],
        "head_sha": facts["head_sha"], "ci": facts["ci"],
        "unresolved_bot_threads": facts["unresolved_bot_threads"], "bots": facts["bots"],
        "integration_base": facts["integration_base"], "base_tip_sha": facts["base_tip_sha"],
    }
    if v in ("CONFLICT", "BASE_ADVANCED"):
        line.update(behind_by=facts["behind_by"], base_changed_files=facts["base_changed_files"],
                    conflict_source=facts["conflict_source"])
    if v == "CONFLICT":
        line["rewrite"], line["rewrite_reason"] = rewrite_answer(owner, repo, pull["head"]["ref"])
    if v == "MERGED":
        line.update(merged_by=(pull.get("merged_by") or {}).get("login"),
                    merge_commit_sha=pull.get("merge_commit_sha"), merged_at=pull.get("merged_at"))
    if v not in TERMINAL:
        line["rearm"] = f"--seen {v}:{key}"
    return line


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--repo", help="OWNER/REPO (default: the cwd's repo)")
    ap.add_argument("--pr", help="PR number (default: the current branch's PR)")
    ap.add_argument("--seen", default="", help="VERDICT:KEY already acted on; print only a different one")
    ap.add_argument("--once", action="store_true", help="one read, print the current line whatever the verdict, exit 0; no lock")
    ap.add_argument("--interval", type=int, default=60, help="seconds between reads (default 60)")
    ap.add_argument("--blind-after", type=int, default=3600, help="seconds with no read landing before WATCHER_ERROR blind, exit 7 (default 3600; 0 disables)")
    ap.add_argument("--fresh-window", type=int, default=420)
    ap.add_argument("--bot-pending-timeout", type=int, default=1800)
    return ap


def main() -> None:
    args = build_parser().parse_args()
    owner, repo = resolve_repo(args.repo)
    pr = resolve_pr(args.pr)
    if not args.once:
        lock_fd = take_lock(f"{owner}-{repo}-{pr}", pr)
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
        facts = classify(read)
        v = facts["verdict"]
        if args.once:
            emit(build_line(owner, repo, pr, read["pull"], facts))
            sys.exit(EXIT_OK)
        if v != "WAITING" and f"{v}:{dedupe_key(v, facts)}" != args.seen:
            emit(build_line(owner, repo, pr, read["pull"], facts))
            sys.exit(EXIT_OK)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
