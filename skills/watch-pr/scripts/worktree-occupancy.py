#!/usr/bin/env python3
"""Where a merged pull request's local worktree stands, for the closeout in cookbook/closeout.md.

Run from the session's own Bash, so the process ancestry that excludes the session's own
client and the cwd behind `session_inside` are the session's.

Usage: worktree-occupancy.py --repo OWNER/REPO --branch BRANCH
Prints one JSON object: worktree_path (or null), worktree_occupied (true, false or "unknown"),
session_inside. Exit 0; 2 on bad args.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def find_worktree(owner: str, repo: str, branch: str) -> str | None:
    """Path of the local worktree checked out on `branch`, from the cwd repo, ~/Code/<repo> or ~/Code/*/<repo>."""
    code = Path.home() / "Code"
    candidates = [Path.cwd(), code / repo, *sorted(code.glob(f"*/{repo}"))]
    for root in candidates:
        url = subprocess.run(["git", "-C", str(root), "remote", "get-url", "origin"],
                             capture_output=True, text=True)
        if url.returncode != 0 or f"{owner}/{repo}".lower() not in url.stdout.lower():
            continue
        wl = subprocess.run(["git", "-C", str(root), "worktree", "list", "--porcelain"],
                            capture_output=True, text=True)
        path = None
        for line in wl.stdout.splitlines():
            if line.startswith("worktree "):
                path = line[len("worktree "):]
            elif line.startswith("branch ") and line[len("branch "):] == f"refs/heads/{branch}":
                return path
    return None


def contains(parent: str, child: str) -> bool:
    """Whether `child` is `parent` or sits under it, by path SEGMENT.

    `startswith` answers the wrong question: `~/worktrees/nexus` already holds
    `nex-3734` beside `nex-3734-2`, and a prefix test reports the first as holding the
    second's occupant.
    """
    p, c = os.path.realpath(parent).rstrip("/"), os.path.realpath(child).rstrip("/")
    return c == p or c.startswith(p + os.sep)


def own_client_pids() -> set:
    """Every pid between this process and the session it runs inside.

    The self-exclusion that matters. This process is a `python3`, which the client
    pattern never matches, so excluding its own pid removes a row that could not have
    been admitted — while the client that SPAWNED it sits in the table with its cwd at
    the session's own worktree, and counting that one makes every session's own tree read
    as held by a peer. Walking the parent chain names it: the client is an ancestor.
    """
    pids, pid = set(), os.getpid()
    for _ in range(24):                     # bounded: a runaway chain answers nothing
        pids.add(pid)
        try:
            out = subprocess.run(["ps", "-o", "ppid=", "-p", str(pid)],
                                 capture_output=True, text=True, timeout=5)
        except Exception:
            break
        parent = out.stdout.strip()
        if not parent.isdigit() or int(parent) <= 1 or int(parent) == pid:
            break
        pid = int(parent)
    return pids


def client_in(path: str):
    """True, False, or "unknown" for a live Claude client launched inside `path`.

    The second occupancy reader, and the one a seat listing cannot supply: a session
    started at a worktree holds it whether or not a workspace was ever created there.
    Read from the process table, which reports each client's own working directory —
    its LAUNCH directory, since neither that nor a seat's recorded path follows a
    session that moves itself.

    Clients in this process's own ancestry are not occupants: they are the session
    running this script, whose own tree the closeout is there to remove.

    "unknown" when the table cannot be read. That is not the same as nobody being
    there, and this reader gates a `git wt remove -D`: an empty seat listing is a definite
    answer about seats and says nothing about processes, so the two failures do not
    cover for each other.
    """
    try:
        out = subprocess.run(
            ["lsof", "-a", "-d", "cwd", "-u", str(os.getuid()), "-Fpcn"],
            capture_output=True, text=True, timeout=10)
    except Exception:
        return "unknown"
    if out.returncode not in (0, 1):        # lsof exits 1 on partial reads
        return "unknown"
    target = os.path.realpath(path)
    mine, pid, comm = own_client_pids(), None, None
    for line in out.stdout.splitlines():
        if not line:
            continue
        tag, value = line[0], line[1:]
        if tag == "p":
            pid, comm = value, None
        elif tag == "c":
            comm = value
        elif tag == "n" and pid and comm and re.match(r"^(claude|\d+\.\d+\.\d+)", comm):
            if pid.isdigit() and int(pid) not in mine and contains(target, value):
                return True
    return False


def worktree_occupied(path: str):
    """True/False for a session OTHER than this one standing in the path;
    "unknown" when the seat listing is unreadable and no client answers.

    Two readers, because neither sees the whole picture: a seat at the path, and a
    client launched there. A session working in a worktree always has a workspace
    there, so counting its own seat would report every session's own tree as held by
    a peer. cmux puts the caller's workspace id in CMUX_WORKSPACE_ID, which joins to
    the listing's `id`; outside cmux it is unset and every workspace counts.

    This gates a `git wt remove -D`, so a client answering outranks an unreadable listing:
    a tree with a live session in it is occupied whatever cmux can say about it. And a
    process table that could not be read leaves the answer unknown rather than free,
    however definite the seat listing is — seats and processes are separate facts.
    """
    client = client_in(path)
    if client is True:
        return True
    try:
        proc = subprocess.run(["cmux", "workspace", "list", "--json"], capture_output=True, text=True, timeout=10)
        if proc.returncode != 0:
            return "unknown"
        data = json.loads(proc.stdout)
    except Exception:
        return "unknown"
    own = os.environ.get("CMUX_WORKSPACE_ID")
    for ws in data.get("workspaces") or []:
        if own and ws.get("id") == own:
            continue
        cd = ws.get("current_directory") or ""
        if cd and contains(path, cd):
            return True
    return "unknown" if client == "unknown" else False


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--repo", required=True, help="OWNER/REPO")
    ap.add_argument("--branch", required=True)
    args = ap.parse_args()
    owner, _, repo = args.repo.partition("/")
    if not owner or not repo:
        print("worktree-occupancy: --repo must be OWNER/REPO", file=sys.stderr)
        sys.exit(2)
    wt = find_worktree(owner, repo, args.branch)
    print(json.dumps({
        "worktree_path": wt,
        "worktree_occupied": worktree_occupied(wt) if wt else False,
        "session_inside": contains(wt, os.getcwd()) if wt else False,
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
