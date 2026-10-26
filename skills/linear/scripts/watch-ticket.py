#!/usr/bin/env python3
"""Watch one Linear ticket until it completes or is canceled, or until enough matching comments land; print one JSON line, then exit.

Lines: COMPLETED | CANCELED | COMMENTS_IN (each carries `then`) · COMMENTED (`rearm` carries --seen) ·
GONE (two consecutive not-found reads) · WATCHER_ERROR (auth | duplicate | blind | unknown).
Exit: 0 verdict or --once | 2 bad args | 3 duplicate | 4 auth | 5 not found on --once | 7 no read landed for --blind-after seconds | 1 traceback, no line
"""
import argparse
import fcntl
import json
import re
import subprocess
import sys
import time
from pathlib import Path

QUERY = "query($id: String!) { issue(id: $id) { identifier state { name type } } }"
QUERY_WITH_COMMENTS = (
    "query($id: String!, $after: String) { issue(id: $id) { identifier state { name type } "
    "comments(first: 250, after: $after) { nodes { id body } pageInfo { hasNextPage endCursor } } } }"
)
MAX_BACKOFF = 600
EXIT_ARGS, EXIT_DUPLICATE, EXIT_AUTH, EXIT_NOT_FOUND, EXIT_BLIND = 2, 3, 4, 5, 7


class Unknown(Exception):
    pass


class Auth(Exception):
    pass


class NotFound(Exception):
    pass


def log(msg):
    sys.stderr.write(f"{msg}\n")
    sys.stderr.flush()


def emit(verdict, reason, rearm=None, **fields):
    line = {"verdict": verdict, "reason": reason, **({"rearm": rearm} if rearm else {}), **fields}
    sys.stdout.write(json.dumps(line, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def fail(error, detail, code, **fields):
    emit("WATCHER_ERROR", detail, error=error, detail=detail, **fields)
    sys.exit(code)


def read_page(secret, query, variables):
    payload = json.dumps({"query": query, "variables": variables})
    argv = [
        "keyless", "run", "-s", f"LINEAR_KEY={secret}", "--",
        "curl", "-sS", "--max-time", "60", "-X", "POST", "https://api.linear.app/graphql",
        "-H", "Content-Type: application/json",
        "--variable", "%LINEAR_KEY", "--expand-header", "Authorization: {{LINEAR_KEY}}",
        "-w", "\n%{http_code}",
        "--data", payload,
    ]
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=90)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Unknown(f"linear read did not land: {type(exc).__name__}")
    if proc.returncode != 0:
        raise Unknown(f"linear read exited {proc.returncode}")
    out = proc.stdout.rstrip("\n")
    head, _, tail = out.rpartition("\n")
    status = tail if re.fullmatch(r"\d{3}", tail) else None
    if status == "401":
        raise Auth("linear refused the credential: http 401")
    try:
        body = json.loads(head if status else out)
    except json.JSONDecodeError:
        raise Unknown("linear answered with something other than JSON")
    if not isinstance(body, dict):
        raise Unknown("linear answered with something other than an object")
    if body.get("errors"):
        errors = [e for e in body["errors"] if isinstance(e, dict)]
        messages = [e.get("message", "") for e in errors]
        if any("authentication" in (e.get("extensions") or {}).get("type", "").lower()
               or "authentication" in e.get("message", "").lower() for e in errors):
            raise Auth("; ".join(messages)[:200])
        if any("not found" in m.lower() for m in messages):
            raise NotFound(variables["id"])
        raise Unknown("; ".join(messages)[:200])
    issue = (body.get("data") or {}).get("issue")
    if not issue or not issue.get("state"):
        raise Unknown("linear returned no issue state")
    return issue


def first_line(text):
    lines = (text or "").strip().splitlines()
    return lines[0] if lines else ""


def read_ticket(ticket, secret, comments_matching):
    if not comments_matching:
        issue = read_page(secret, QUERY, {"id": ticket})
        return {"state": issue["state"]["name"], "state_type": issue["state"]["type"]}
    pattern = re.compile(comments_matching, re.MULTILINE)
    matching, after = [], None
    while True:
        issue = read_page(secret, QUERY_WITH_COMMENTS, {"id": ticket, "after": after})
        page = issue.get("comments") or {}
        nodes, info = page.get("nodes"), page.get("pageInfo")
        if nodes is None or info is None:
            raise Unknown("linear returned no comment page")
        matching += [{"id": c["id"], "first_line": first_line(c.get("body"))}
                     for c in nodes if pattern.search(c.get("body") or "")]
        if not info.get("hasNextPage"):
            break
        after = info.get("endCursor")
        if not after:
            raise Unknown("linear reported another comment page with no cursor")
    return {"state": issue["state"]["name"], "state_type": issue["state"]["type"], "matching_comments": matching}


def classify(args, facts):
    ticket, state, state_type = args.ticket, facts["state"], facts["state_type"]
    if state_type in ("canceled", "duplicate"):
        return "CANCELED", f"{ticket} is {state}", state_type, {}
    if args.comments_matching is not None:
        matching = facts["matching_comments"]
        listed = " · ".join(f"[{c['id']}] {c['first_line']}" for c in matching)
        ids = ",".join(c["id"] for c in matching)
        if len(matching) >= args.expect:
            return "COMMENTS_IN", f"{len(matching)} of {args.expect} matching comments on {ticket}: {listed}", ids, {"then": args.then}
        if matching:
            return "COMMENTED", f"{len(matching)} of {args.expect} matching comments on {ticket}: {listed}", ids, {}
    elif state_type == "completed":
        return "COMPLETED", f"{ticket} is {state}", state_type, {"then": args.then}
    return "OPEN", f"{ticket} is {state}", state, {}


def take_lock(ticket):
    d = Path.home() / ".local" / "state" / "watch" / "ticket"
    d.mkdir(parents=True, exist_ok=True)
    fh = open(d / f"{ticket}.lock", "a+")
    try:
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        fail("duplicate", f"lock held: {fh.name}", EXIT_DUPLICATE, ticket=ticket)
    return fh


def run(args):
    ticket = args.ticket
    last_ok, wait, gone = time.time(), args.interval, 0
    while True:
        try:
            facts = read_ticket(ticket, args.secret, args.comments_matching)
            gone = 0
        except Auth as exc:
            fail("auth", str(exc), EXIT_AUTH, ticket=ticket)
        except NotFound:
            gone += 1
            if args.once:
                fail("not_found", f"{ticket} is not in Linear", EXIT_NOT_FOUND, ticket=ticket)
            if gone >= 2:
                emit("GONE", f"{ticket} is not in Linear", ticket=ticket)
                return
            last_ok, wait = time.time(), args.interval
            time.sleep(args.interval)
            continue
        except Unknown as exc:
            if args.once:
                emit("WATCHER_ERROR", str(exc), error="unknown", detail=str(exc), ticket=ticket)
                return
            if time.time() - last_ok > args.blind_after:
                fail("blind", f"no read landed for {int(time.time() - last_ok)}s: {exc}", EXIT_BLIND, ticket=ticket)
            log(f"read failed: {exc}; backing off {wait}s")
            time.sleep(wait)
            wait = min(2 * wait, MAX_BACKOFF)
            continue
        last_ok, wait = time.time(), args.interval
        verdict, reason, key, extra = classify(args, facts)
        line_fields = {"ticket": ticket, "state": facts["state"], **extra}
        if args.once:
            emit(verdict, reason, f"--seen {verdict}:{key}", **line_fields)
            return
        if verdict != "OPEN" and f"{verdict}:{key}" != args.seen:
            emit(verdict, reason, f"--seen {verdict}:{key}" if verdict == "COMMENTED" else None, **line_fields)
            return
        time.sleep(args.interval)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ticket", required=True)
    parser.add_argument("--secret", required=True, help="the secrets-store item the linear config's `secret` names")
    parser.add_argument("--then", required=True, help="the act a woken session runs once the ticket completes; with --comments-matching, once --expect matching comments are in")
    parser.add_argument("--comments-matching", help="a regex over comment bodies; the watch reports each new matching comment")
    parser.add_argument("--expect", type=int, help="with --comments-matching, how many matching comments end the watch")
    parser.add_argument("--seen", help="VERDICT:KEY already acted on; not printed again")
    parser.add_argument("--interval", type=float, default=300)
    parser.add_argument("--blind-after", type=float, default=3600)
    parser.add_argument("--once", action="store_true", help="one read, no lock, print the current line")
    args = parser.parse_args()
    if (args.comments_matching is None) != (args.expect is None):
        parser.error("--comments-matching and --expect go together")
    if args.comments_matching is not None:
        if not args.comments_matching:
            parser.error("--comments-matching must not be empty")
        try:
            re.compile(args.comments_matching)
        except re.error as exc:
            parser.error(f"--comments-matching is not a valid regex: {exc}")
        if args.expect < 1:
            parser.error("--expect must be at least 1")
    lock = None if args.once else take_lock(args.ticket)
    try:
        run(args)
    finally:
        if lock:
            lock.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
