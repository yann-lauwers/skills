#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Watch one Slack conversation for a reply to a question; print one JSON line, then exit.

The token is read from $SLACK_TOKEN, injected by `keyless run`. It is never printed, logged
or passed to the classifier child; only len() of it reaches stderr.

Lines: ANSWERED | QUESTION_BACK | NEW_MESSAGE (terminal, a fresh watch follows) ·
STALE (nothing for --nudge-after seconds; `rearm` carries the flags for the next arm) ·
WATCHER_ERROR (auth | channel_not_found | duplicate | blind | unknown).
Swallowed, stderr only: ACK, UNRELATED, the configured user's own messages.
A classifier failure emits NEW_MESSAGE, never silence.

Usage: watch-reply.py --channel D0123 [--after TS] [--from U0123 ...] [--question TEXT|@file]
                      [--thread TS] [--interval S] [--nudge-after S] [--seen V:K] [--once]
Exit:  0 verdict or --once | 2 bad args | 3 duplicate | 4 auth | 5 channel not found
       | 7 no read landed for --blind-after seconds | 1 traceback, no line
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = os.environ.get("SLACK_API_BASE", "https://slack.com/api")
TOKEN_ENV = "SLACK_TOKEN"
KIND = "slack"
DEFAULT_INTERVAL = 120
DEFAULT_NUDGE_AFTER = 4 * 3600
DEFAULT_BLIND_AFTER = 3600
MAX_BACKOFF = 600
CLASSIFY_TIMEOUT = 90
DEFAULT_MODEL = "haiku"
RATE_LIMIT_FALLBACK = 60

EXIT_ARGS, EXIT_DUPLICATE, EXIT_AUTH, EXIT_NOT_FOUND, EXIT_BLIND = 2, 3, 4, 5, 7

AUTH_ERRORS = ("invalid_auth", "not_authed", "token_revoked", "token_expired", "account_inactive")
NOT_FOUND_ERRORS = ("channel_not_found", "not_in_channel")

CLASSIFY_SCHEMA = json.dumps({
    "type": "object",
    "properties": {
        "summary": {"type": "string", "description": "one line: what the reply gives or asks, without naming a label"},
        "verdict": {"type": "string", "enum": ["UNRELATED", "ACK", "QUESTION_BACK", "ANSWERED"]},
    },
    "required": ["summary", "verdict"],
    "additionalProperties": False,
})


def iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg: str) -> None:
    sys.stderr.write(f"[{iso()}] {msg}\n")
    sys.stderr.flush()


def emit(verdict: str, reason: str, rearm: str | None = None, **fields) -> None:
    line = {"verdict": verdict, "reason": reason, **({"rearm": rearm} if rearm else {}), **fields}
    sys.stdout.write(json.dumps(line, ensure_ascii=False) + "\n")
    sys.stdout.flush()


class RateLimited(Exception):
    def __init__(self, retry_after: float):
        super().__init__(f"rate limited, retry after {retry_after}s")
        self.retry_after = retry_after


class SlackError(Exception):
    pass


class AuthError(SlackError):
    pass


class NotFound(SlackError):
    pass


class Slack:
    def __init__(self, token: str):
        self._token = token

    def call(self, method: str, **params) -> dict:
        data = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None}).encode()
        req = urllib.request.Request(
            f"{API}/{method}", data=data,
            headers={"Authorization": f"Bearer {self._token}",
                     "Content-Type": "application/x-www-form-urlencoded"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                raise RateLimited(float(exc.headers.get("Retry-After", RATE_LIMIT_FALLBACK)))
            if exc.code == 401:
                raise AuthError(f"{method}: http 401")
            raise SlackError(f"http {exc.code} on {method}")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise SlackError(f"{method}: {type(exc).__name__}")
        if not isinstance(body, dict):
            raise SlackError(f"{method}: unexpected body")
        if body.get("ok"):
            return body
        err = body.get("error", "unknown")
        if err == "ratelimited":
            raise RateLimited(RATE_LIMIT_FALLBACK)
        if err in AUTH_ERRORS:
            raise AuthError(f"{method}: {err}")
        if err in NOT_FOUND_ERRORS:
            raise NotFound(f"{method}: {err}")
        raise SlackError(f"{method}: {err}")


def classify(question: str, reply: str, model: str) -> tuple[bool, dict | str]:
    claude_bin = None
    for d in os.environ.get("PATH", "").split(os.pathsep):
        cand = Path(d) / "claude"
        if cand.is_file() and os.access(cand, os.X_OK):
            claude_bin = str(cand)
            break
    if not claude_bin:
        return False, "claude CLI not on PATH"
    prompt = (
        "Classify one Slack reply against the question it may answer. Decide in this order and "
        "stop at the first that fits:\n"
        "1. UNRELATED — the reply is about something else; it neither answers, defers, nor "
        "questions the ask. Example: asked for a tool, reply 't'as vu le bug sur staging ?'.\n"
        "2. ACK — the reply only acknowledges or defers: 'ok', 'je regarde', 'haha ok je regarde "
        "ce soir', 'top', a reaction-like one-liner. Nothing asked for has arrived yet.\n"
        "3. QUESTION_BACK — the reply asks the asker something that must be answered first. "
        "Example: 'tu veux la version avec ou sans le hook ?'.\n"
        "4. ANSWERED — the reply delivers what was asked (a link, a file, the facts, a yes) OR a "
        "definitive refusal ('non, je peux pas le partager'). Only this verdict means the asker "
        "can act now.\n\n"
        "The `verdict` field carries exactly one of those four labels. The `summary` field is one "
        "line on what the reply gives or asks, and never restates the label.\n\n"
        f"QUESTION ASKED:\n{question}\n\nREPLY RECEIVED:\n{reply}\n"
    )
    cmd = [claude_bin, "-p", prompt, "--model", model, "--output-format", "json",
           "--json-schema", CLASSIFY_SCHEMA, "--no-session-persistence", "--setting-sources", ""]
    env = {k: v for k, v in os.environ.items() if k != TOKEN_ENV}
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=CLASSIFY_TIMEOUT, env=env)
    except subprocess.TimeoutExpired:
        return False, f"claude -p timed out after {CLASSIFY_TIMEOUT}s"
    except OSError as exc:
        return False, f"claude -p spawn failed: {exc}"
    if proc.returncode != 0:
        return False, f"claude -p exit {proc.returncode}: {proc.stderr.strip()[:200]}"
    try:
        envelope = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return False, "claude -p json envelope not parseable"
    out = envelope.get("structured_output") if isinstance(envelope, dict) else None
    if not isinstance(out, dict) or out.get("verdict") not in {"ANSWERED", "QUESTION_BACK", "ACK", "UNRELATED"}:
        return False, f"no structured_output (subtype={envelope.get('subtype') if isinstance(envelope, dict) else '?'})"
    return True, out


class Conversation:
    def __init__(self, args, token: str):
        self.a = args
        self.slack = Slack(token)
        self.self_id: str | None = None
        self.names: dict[str, str] = {}
        self.question_permalink: str | None = None
        self.last_ts = args.after

    def name_of(self, uid: str) -> str:
        if uid not in self.names:
            try:
                u = self.slack.call("users.info", user=uid)["user"]
                self.names[uid] = u.get("profile", {}).get("display_name") or u.get("real_name") or uid
            except (SlackError, RateLimited):
                self.names[uid] = uid
        return self.names[uid]

    def permalink(self, ts: str) -> str | None:
        try:
            return self.slack.call("chat.getPermalink", channel=self.a.channel, message_ts=ts)["permalink"]
        except (SlackError, RateLimited):
            return None

    def fetch_new(self, oldest: str) -> list[dict]:
        if self.a.thread:
            body = self.slack.call("conversations.replies", channel=self.a.channel,
                                   ts=self.a.thread, oldest=oldest, inclusive="false", limit=200)
            msgs = [m for m in body.get("messages", []) if m.get("ts") != self.a.thread]
        else:
            body = self.slack.call("conversations.history", channel=self.a.channel,
                                   oldest=oldest, inclusive="false", limit=200)
            msgs = body.get("messages", [])
        msgs = [m for m in msgs if m.get("type") == "message" and not m.get("subtype")
                and float(m.get("ts", "0")) > float(oldest)]
        return sorted(msgs, key=lambda m: float(m["ts"]))

    def open(self) -> None:
        me = self.slack.call("auth.test")
        self.slack.call("conversations.history", channel=self.a.channel, limit=1)
        self.self_id = me.get("user_id")
        if self.a.after_is_question and self.a.after != "0":
            self.question_permalink = self.permalink(self.a.after)

    def consider(self, msg: dict) -> tuple[str, str, dict] | None:
        uid = msg.get("user") or msg.get("bot_id") or "?"
        text = msg.get("text", "")
        who = self.name_of(uid) if uid.startswith("U") else uid
        if uid == self.self_id and uid not in self.a.from_users:
            log(f"swallow own message ts={msg['ts']}")
            return None
        if self.a.from_users and uid not in self.a.from_users:
            log(f"swallow {who} (not watched) ts={msg['ts']}")
            return None
        fields = {"from": who, "from_id": uid, "ts": msg["ts"], "text": text,
                  "permalink": self.permalink(msg["ts"]),
                  "files": [f.get("name") for f in msg.get("files", []) if f.get("name")]}
        if self.a.no_classify or not self.a.question:
            return "NEW_MESSAGE", f"message from {who}", fields
        ok, res = classify(self.a.question, text or "(no text; files: %s)" % fields["files"], self.a.model)
        if not ok:
            log(f"classifier failed: {res}; emitting NEW_MESSAGE")
            return "NEW_MESSAGE", f"message from {who}; classifier failed: {res}", {**fields, "classifier_error": str(res)}
        if res["verdict"] in ("ACK", "UNRELATED"):
            log(f"swallow {res['verdict']} from {who}: {res['summary']}")
            return None
        return res["verdict"], res["summary"], {**fields, "classifier": res["verdict"]}

    def stale_origin(self) -> float:
        try:
            origin = float(self.a.after)
            if origin > 0:
                return origin
        except (TypeError, ValueError):
            pass
        return self.a.armed_at

    def read(self, seen: str | None) -> tuple[str, str, dict] | None:
        if self.self_id is None:
            self.open()
        for m in self.fetch_new(self.last_ts):
            self.last_ts = m["ts"]
            hit = self.consider(m)
            if hit is not None and f"{hit[0]}:{m['ts']}" != seen:
                return hit
        if self.a.nudge_after > 0 and time.time() - self.stale_origin() >= self.a.nudge_after:
            if seen != "STALE:stale":
                return "STALE", f"no reply for {int(self.a.nudge_after // 3600)}h", {}
        return None

    def common(self) -> dict:
        return {"id": slug(self.a), "channel": self.a.channel, "thread": self.a.thread,
                "after": self.a.after, "last_ts": self.last_ts,
                "watching": self.a.from_users or "anyone",
                "question_permalink": self.question_permalink}


def slug(a) -> str:
    return f"{a.channel}-{a.after.replace('.', '_')}"


def take_lock(a):
    d = Path.home() / ".local" / "state" / "watch" / KIND
    d.mkdir(parents=True, exist_ok=True)
    fh = open(d / f"{slug(a)}.lock", "a+")
    try:
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        emit("WATCHER_ERROR", "another watcher holds this conversation", error="duplicate",
             detail=f"lock held: {fh.name}")
        sys.exit(EXIT_DUPLICATE)
    return fh


def fail(error: str, detail: str, code: int, **fields) -> None:
    emit("WATCHER_ERROR", detail, error=error, detail=detail, **fields)
    sys.exit(code)


def rearm_for(verdict: str, last_ts: str) -> str:
    return f"--after {last_ts} --nudge-after 0" if verdict == "STALE" else f"--after {last_ts}"


def run(a, token: str) -> int:
    convo = Conversation(a, token)
    last_ok = time.time()
    wait = a.interval
    while True:
        try:
            hit = convo.read(a.seen)
        except AuthError as exc:
            fail("auth", str(exc), EXIT_AUTH, channel=a.channel)
        except NotFound as exc:
            fail("channel_not_found", str(exc), EXIT_NOT_FOUND, channel=a.channel)
        except (SlackError, RateLimited) as exc:
            if a.once:
                emit("WATCHER_ERROR", str(exc), error="unknown", detail=str(exc), channel=a.channel)
                return 0
            if time.time() - last_ok > a.blind_after:
                fail("blind", f"no read landed for {int(time.time() - last_ok)}s: {exc}", EXIT_BLIND,
                     channel=a.channel)
            log(f"read failed: {exc}; backing off {wait}s")
            time.sleep(max(getattr(exc, "retry_after", 0), wait))
            wait = min(2 * wait, MAX_BACKOFF)
            continue
        last_ok = time.time()
        wait = a.interval
        if hit is not None:
            verdict, reason, fields = hit
            rearm = None if verdict != "STALE" else rearm_for(verdict, convo.last_ts)
            emit(verdict, reason, rearm, **{**convo.common(), **fields})
            return 0
        if a.once:
            emit("WAITING", "nothing new", rearm_for("WAITING", convo.last_ts), **convo.common())
            return 0
        time.sleep(a.interval)


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--channel", required=True, help="D…/C…/G… id to watch")
    p.add_argument("--after", default=None,
                   help="Slack ts of the question you sent; only later messages count (default: now)")
    p.add_argument("--from", dest="from_users", action="append", default=[],
                   help="U… id whose messages count; repeatable (default: anyone but you)")
    p.add_argument("--question", default=None,
                   help="the question asked, as text or @path to a file; enables the classifier")
    p.add_argument("--thread", default=None, help="parent ts: watch that thread's replies instead")
    p.add_argument("--interval", type=int, default=DEFAULT_INTERVAL)
    p.add_argument("--nudge-after", type=int, default=DEFAULT_NUDGE_AFTER, help="seconds; 0 disables STALE")
    p.add_argument("--blind-after", type=int, default=DEFAULT_BLIND_AFTER,
                   help="seconds with no read landing before the run ends")
    p.add_argument("--seen", default=None, help="VERDICT:KEY already acted on; not printed again")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--no-classify", action="store_true", help="wake on every watched message")
    p.add_argument("--once", action="store_true", help="one read, no lock, print the current line")
    a = p.parse_args(argv)
    a.after_is_question = a.after is not None
    a.armed_at = time.time()
    if a.after is None:
        a.after = f"{a.armed_at:.6f}"
    if a.question and a.question.startswith("@"):
        try:
            a.question = Path(a.question[1:]).expanduser().read_text().strip()
        except OSError as exc:
            p.error(f"--question file unreadable: {exc}")
    return a


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    token = os.environ.get(TOKEN_ENV, "")
    if not token:
        fail("auth", f"${TOKEN_ENV} is empty; launch under keyless run", EXIT_AUTH, channel=args.channel)
    lock = None if args.once else take_lock(args)
    log(f"token present ({len(token)} chars); channel={args.channel} after={args.after} "
        f"from={args.from_users or 'anyone'} classify={'on' if args.question and not args.no_classify else 'off'}")
    try:
        return run(args, token)
    finally:
        if lock:
            lock.close()


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        sys.exit(0)
