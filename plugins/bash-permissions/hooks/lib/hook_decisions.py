#!/usr/bin/env python3
import os, json, glob, re
from datetime import datetime, timezone

DETAIL_CAP = 200
TRANSCRIPT_TAIL = 262144
ASSISTANT_MODEL_RE = re.compile(rb'"model":"(claude-[A-Za-z0-9.\-\[\]]+)","id":"msg_')


def provider():
    value = os.environ.get("AGENT_HOOK_PROVIDER") or ""
    return value if value and value != "claude" else None


def state_root():
    return os.environ.get("HOOK_STATE_ROOT") or os.path.expanduser("~/.claude/state")


def _field(v):
    if v is None:
        return None
    return str(v).replace("\t", " ").replace("\n", " ").replace("\r", " ")


def _bump_health():
    try:
        path = os.path.join(state_root(), "hook-decisions.health")
        try:
            n = int(open(path).read().strip() or 0)
        except Exception:
            n = 0
        with open(path, "w") as fh:
            fh.write(str(n + 1))
    except Exception:
        pass


def session_model(session):
    if not session or not re.fullmatch(r"[A-Za-z0-9-]+", session):
        return None
    config = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
    try:
        for path in glob.glob(os.path.join(config, "projects", "*", session + ".jsonl")):
            with open(path, "rb") as fh:
                fh.seek(max(0, os.path.getsize(path) - TRANSCRIPT_TAIL))
                found = ASSISTANT_MODEL_RE.findall(fh.read())
            if found:
                return found[-1].decode()
    except Exception:
        pass
    return None


def log(check, verdict, detail="", session=None,
        event=None, mode=None, actor=None, outcome=None):
    try:
        root = state_root()
        os.makedirs(root, exist_ok=True)
        row = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "check": _field(check),
            "session": _field(session) or "unknown",
            "verdict": _field(verdict),
            "detail": _field(detail)[:DETAIL_CAP] if detail else "",
        }
        for key, value in (("event", event), ("mode", mode),
                           ("actor", actor), ("outcome", outcome),
                           ("model", session_model(session)),
                           ("provider", provider())):
            if value:
                row[key] = _field(value)
        with open(os.path.join(root, "hook-decisions.jsonl"), "a") as fh:
            fh.write(json.dumps(row) + "\n")
        return True
    except Exception:
        _bump_health()
        return False
