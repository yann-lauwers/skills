#!/usr/bin/env python3
"""One scan of the decision log, written down so no session start has to repeat it.

Two facts are read out of the log by more than one reader — which ids write
verdicts, and which handlers crashed — and the log is the wrong thing to hand any
of them. It
passed 46 MB and grows about a megabyte a day. So the daily review job scans it
once and writes this summary.

**A crash is recent by one definition, and it lives here.** The drift report and the
daily notifier both answer "what crashed lately". The report had no
window, so 170 rows of a `NameError` fixed three weeks earlier read exactly like a
crash from this morning — which is noise nobody acts on, and it hid the crash that
was still happening. Recency is judged at READ time against `recent_ts`, never at
write time: a summary made at 09:00 and read at 08:00 the next day would otherwise
call a day-old crash fresh.

**A crash row names a MODULE, not a check.** `lib/hook_run.py` records `verdict=error`
under the handler's own id, because a raising handler never reached the check that
would have named itself. Those rows are kept apart from `logged_ids`, for the reason
`hook-decisions --drift` already states: counted as verdicts, a guard crashing on
every call is indistinguishable from one running clean.

Usage:

    python3 ~/.claude/hooks/lib/hook_log_summary.py --write   # scan and write
    python3 ~/.claude/hooks/lib/hook_log_summary.py --recent  # print last-day crashes
"""
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hook_decisions import state_root  # noqa: E402  (the sink owns where state lives)

SCHEMA = 1
LOG_NAME = "hook-decisions.jsonl"

# What "recent" means for a crash, everywhere it is asked.
RECENT = timedelta(hours=24)
# A summary older than this is a finding. The writer runs daily and catches up at
# login, so two days means the job itself stopped — a missed day is not staleness.
STALE = timedelta(hours=48)
# Timestamps kept per crashed id. A crash storm writes a row per call, and the
# summary must stay a file a session start can read in milliseconds.
RECENT_CAP = 200
# Only timestamps young enough to still be recent at a stale read are worth keeping.
KEEP_FOR = RECENT + STALE
DETAIL_CAP = 200


# `hook_run` records `why=<repr(exc)>`, so an unmarked row from before the mark shows
# the exception's class name followed by its argument list.
_RAISED_DETAIL = re.compile(r"^why=[A-Z]\w*(?:Error|Exception|Exit|Interrupt|Warning)?\(")


def is_crash(row):
    """True when a row records a handler that RAISED.

    `verdict=error` alone does not say so. `hook_run` writes it when a handler raises,
    and marks it `outcome=raised`; other writers use the same verdict for a condition
    they detected and handled — no terminal owns the session, the payload was empty.
    Those handlers decided something. Rows written before the mark are recognised by
    the exception repr `hook_run` has always written.
    """
    if not isinstance(row, dict) or row.get("verdict") != "error":
        return False
    if row.get("outcome") == "raised":
        return True
    return bool(_RAISED_DETAIL.match(str(row.get("detail") or "")))


def log_path():
    return os.path.join(state_root(), LOG_NAME)


def _parse_ts(value):
    """An aware datetime, or None. A row's time is written by the sink as ISO 8601
    UTC; anything else is unreadable and must never read as recent."""
    try:
        t = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


class _Crashes:
    """Accumulates crash rows into the map every reader shares."""

    def __init__(self, now):
        self.now = now
        self.map = {}

    def add(self, row):
        cid = row.get("check")
        if not cid or not is_crash(row):
            return
        entry = self.map.setdefault(cid, {"rows": 0, "last_ts": None,
                                          "last_detail": "", "recent_ts": []})
        entry["rows"] += 1
        ts = str(row.get("ts") or "")
        when = _parse_ts(ts)
        last = _parse_ts(entry["last_ts"]) if entry["last_ts"] else None
        if entry["last_ts"] is None or (when and (last is None or when >= last)):
            entry["last_ts"] = ts
            entry["last_detail"] = str(row.get("detail") or "")[:DETAIL_CAP]
        if when and self.now - when <= KEEP_FOR:
            entry["recent_ts"].append(ts)

    def result(self):
        for entry in self.map.values():
            entry["recent_ts"] = sorted(entry["recent_ts"],
                                        key=lambda t: _parse_ts(t))[-RECENT_CAP:]
        return self.map


def summarize_rows(rows, now=None):
    """One pass over parsed rows: the summary `scan` writes, from rows in any form.

    The drift report already holds the whole log as a list; `scan` streams it from the
    file. Both classify each row here, once, so neither can drift from the other.
    """
    now = now or datetime.now(timezone.utc)
    acc = _Crashes(now)
    logged, count = set(), 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        count += 1
        if is_crash(row):
            acc.add(row)
        elif row.get("check"):
            logged.add(row["check"])
    return {
        "schema": SCHEMA,
        "generated_at": now.isoformat(),
        "log_rows": count,
        "malformed": 0,
        "logged_ids": sorted(logged),
        "crashes": acc.result(),
    }


def scan(path=None, now=None):
    """Read the log once, streaming. Never raises: a missing log is an empty one."""
    bad = [0]

    def parsed(fh):
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except Exception:
                bad[0] += 1
                continue
            if isinstance(row, dict):
                yield row
            else:
                bad[0] += 1

    try:
        fh = open(path or log_path(), errors="replace")
    except OSError:
        return summarize_rows((), now)
    with fh:
        summary = summarize_rows(parsed(fh), now)
    summary["malformed"] = bad[0]
    return summary


def recent_crashes(crashes, now=None, window=RECENT):
    """Crashed ids with a row inside `window` of `now`, newest first.

    Each item: {"check", "rows" (inside the window), "last_ts", "last_detail"}.
    """
    now = now or datetime.now(timezone.utc)
    out = []
    for cid, entry in (crashes or {}).items():
        # Strictly inside the window: a row exactly one day old belongs to yesterday.
        # A row a little AFTER `now` still counts — a reader and the writer on one
        # machine disagree by seconds, and dropping the newest crash is the one
        # direction this must never fail in.
        inside = [t for t in entry.get("recent_ts", [])
                  if _parse_ts(t) is not None and now - _parse_ts(t) < window]
        if inside:
            out.append({"check": cid, "rows": len(inside),
                        "last_ts": entry.get("last_ts"),
                        "last_detail": entry.get("last_detail", "")})
    out.sort(key=lambda c: _parse_ts(c["last_ts"]) or datetime.min.replace(
        tzinfo=timezone.utc), reverse=True)
    return out


