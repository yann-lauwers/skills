#!/usr/bin/env python3
"""Close out a merged pull request: remove its local worktree and branch once nothing is lost.

Run from the session's own Bash, so the process ancestry that excludes the session's own
client and the cwd behind the session-inside check are the session's.

Usage: closeout.py --repo OWNER/REPO --pr N [--dry-run]
Prints one JSON object. `closeout` is `removed`, `no_worktree`, `would_remove` (--dry-run)
or `refused` with a `reason`; a refusal leaves the tree untouched.
Exit 0 removed, no_worktree or would_remove; 1 refused; 2 bad args.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

LOCK_HELD = 75


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


def git(cwd: str, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, input=stdin)


def patch_id(cwd: str, *diff_args: str) -> str:
    diff = git(cwd, *diff_args).stdout
    return git(cwd, "patch-id", "--stable", stdin=diff).stdout.split(" ")[0].strip()


def unlanded(tree: str, base: str, merge_sha: str) -> str | None:
    """The reason the tree's work is not on the base, or None once it is."""
    dirty = git(tree, "status", "--porcelain").stdout.splitlines()
    if dirty:
        return "uncommitted: " + ", ".join(line[3:] for line in dirty[:5]) + (" …" if len(dirty) > 5 else "")
    if git(tree, "fetch", "origin", base).returncode != 0:
        return f"cannot fetch origin/{base}"
    cherry = git(tree, "cherry", f"origin/{base}", "HEAD")
    if cherry.returncode != 0:
        return "git cherry failed: " + cherry.stderr.strip()[-160:]
    if not any(line.startswith("+") for line in cherry.stdout.splitlines()):
        return None
    fork = git(tree, "merge-base", f"origin/{base}", "HEAD").stdout.strip()
    branch_id = patch_id(tree, "diff", fork, "HEAD")
    if branch_id and branch_id == patch_id(tree, "show", merge_sha):
        return None
    return "unmerged local work: the branch diff differs from the merge commit"


def finish(closeout: str, code: int = 0, **fields) -> None:
    print(json.dumps({"closeout": closeout, **fields}, separators=(",", ":")))
    sys.exit(code)


def refuse(reason: str, **fields) -> None:
    finish("refused", 1, reason=reason, **fields)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--repo", required=True, help="OWNER/REPO")
    ap.add_argument("--pr", required=True, type=int)
    ap.add_argument("--dry-run", action="store_true", help="run every check, remove nothing")
    args = ap.parse_args()
    owner, _, repo = args.repo.partition("/")
    if not owner or not repo:
        print("closeout: --repo must be OWNER/REPO", file=sys.stderr)
        sys.exit(2)
    try:
        proc = subprocess.run(["gh", "api", f"repos/{owner}/{repo}/pulls/{args.pr}"],
                              capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        refuse(f"cannot read the pull request: {e}")
    if proc.returncode != 0:
        refuse("cannot read the pull request: " + proc.stderr.strip()[-160:])
    pull = json.loads(proc.stdout)
    if not pull.get("merged"):
        refuse(f"pull request is {pull.get('state')}, not merged")
    branch, base, merge_sha = pull["head"]["ref"], pull["base"]["ref"], pull["merge_commit_sha"]
    merged = {"pr": args.pr, "merged_by": (pull.get("merged_by") or {}).get("login"), "base": base,
              "merge_commit_sha": merge_sha[:12]}
    tree = find_worktree(owner, repo, branch)
    if not tree:
        finish("no_worktree", **merged)
    occupied = worktree_occupied(tree)
    if occupied is True:
        refuse("another session holds the worktree", worktree=tree)
    if occupied == "unknown":
        refuse("occupancy unreadable: the seat listing or the process table did not answer", worktree=tree)
    common = git(tree, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip()
    checkout = str(Path(common).parent)
    if contains(tree, os.getcwd()):
        refuse("this session stands inside the worktree: cd to the base checkout and rerun",
               worktree=tree, cd=checkout)
    lost = unlanded(tree, base, merge_sha)
    if lost:
        refuse(lost, worktree=tree)
    if args.dry_run:
        finish("would_remove", worktree=tree, branch=branch, **merged)
    rm = subprocess.run(["git", "wt", "-C", checkout, "-y", "remove", branch, "-D", "--foreground"],
                        capture_output=True, text=True)
    if rm.returncode == LOCK_HELD:
        refuse("another start or stop holds the tree's lock: rerun once it frees", worktree=tree)
    if rm.returncode != 0:
        refuse("git wt remove failed: " + (rm.stderr or rm.stdout).strip()[-300:], worktree=tree)
    if tree in git(checkout, "worktree", "list", "--porcelain").stdout.split():
        refuse("git wt remove left the worktree on disk", worktree=tree)
    if git(checkout, "branch", "--list", branch).stdout.strip():
        git(checkout, "branch", "-D", branch)
    finish("removed", worktree=tree, branch=branch, **merged)


if __name__ == "__main__":
    main()
