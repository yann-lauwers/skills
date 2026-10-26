#!/usr/bin/env python3
"""PostToolUse + InstructionsLoaded — record what this session loaded, and the canon
it started under.

Failure it prevents: after a compaction, a skill's content is gone from context
while nothing on disk says it was ever loaded, so the re-read obligation the
PreCompact capture writes cannot name what to re-read. It covers skills invoked
through the Skill tool; one the user typed is not recorded here.

Contract (verified against hook-development references/events-and-contracts.md):
  PostToolUse and InstructionsLoaded cannot block, and carry no decision. Side
  effects only. exit 0 always — a crash here would be an absent recorder, and every
  field is coerced at the entry point rather than wrapped in a blanket try/except.

Writes one line per skill to $HOOK_STATE_ROOT/read-log/<session>. The file is the
compaction epoch counter's substrate too: the PreCompact capture archives it to
`<session>.pc<n>`, so the count of those archives is how many seams this session
has crossed.

Second write, same validated fields: one JSON line per invocation, appended to
$HOOK_STATE_ROOT/skill-invocations.jsonl — cumulative across every session, never
archived or truncated by the compaction seam above. The per-session read-log answers
"has this session invoked X through the Skill tool" for the PreCompact obligation; this file answers a
different question the read-log structurally cannot, because it is overwritten per
session and carries no timestamp: "was skill X invoked through the Skill tool
anywhere, and when" — the question a routing-reliability check greps for. A `/<skill>`
the user types expands without a Skill call, so it reaches neither file; the transcript
alone carries it. `{"ts", "session", "skill"}` per line; append-only, same race
tolerance as the read-log (dedup, if wanted, happens on read).

The canon stamp, on InstructionsLoaded: the same read-log carries which version of
the always-loaded canon the session started under, so a session can be placed before
or after a canon change. Two fields, each a line; a reader takes the LAST line of
each key:

  canon:<sha>                 the commit of the installed yann plugin this hook runs from,
                              or `canon:unknown` when it cannot be read. Written once
                              per record.
  always-loaded-bytes:<n>     the summed size of every always-loaded instruction file,
                              or `always-loaded-bytes:unknown` when one of them could
                              not be sized — never a silent undercount.

Always-loaded is a `session_start` or `compact` load, plus an `include` whose parent is
itself always-loaded (AGENTS.md imported by CLAUDE.md). A `compact` reload lands in
the fresh record the compaction seam leaves, and stamps it the same way. The evidence
behind the total is one `instructions:<json>` line per file, first load wins, so a
resume re-reporting the same files counts each once. Every stamp line sits outside
the `skill:` namespace, which is the only one this file's other readers keep.

The load events of one session start arrive as parallel processes, so the stamp is
written under an exclusive lock and the total is recomputed from the whole record on
every write: the last line written has seen every load before it, and an include that
lands before its parent is counted once the parent does.
"""
import fcntl
import json
import os
import re
import sys
from datetime import datetime, timezone

SLUG = re.compile(r"[a-z0-9][a-z0-9-]{0,63}$")
SHA = re.compile(r"[0-9a-f]{40}([0-9a-f]{24})?")

ALWAYS_LOADED = {"session_start", "compact"}
INCLUDED = {"include"}
RECORDED = ALWAYS_LOADED | INCLUDED
UNKNOWN = "unknown"


def state_root():
    return os.environ.get("HOOK_STATE_ROOT") or os.path.expanduser("~/.claude/state")


def installed_plugins_path():
    return os.environ.get("CLAUDE_INSTALLED_PLUGINS") or os.path.expanduser("~/.claude/plugins/installed_plugins.json")


def safe_session(value):
    """A session id is a path segment here, so anything that could climb out of the
    directory is refused rather than sanitised — a rewritten id would silently split
    one session's log in two."""
    if not isinstance(value, str) or not value:
        return None
    if "/" in value or "\\" in value or value.startswith("."):
        return None
    return value if re.fullmatch(r"[A-Za-z0-9._-]{1,128}", value) else None


def skill_name(tool_input):
    if not isinstance(tool_input, dict):
        return None
    name = tool_input.get("skill")
    if not isinstance(name, str):
        return None
    name = name.strip().lower()
    # A plugin skill arrives as `plugin:skill`; the pair is the identity, so both
    # halves are kept and each is checked against the same shape.
    parts = name.split(":")
    if len(parts) > 2 or not all(SLUG.fullmatch(p) for p in parts if p):
        return None
    return name or None


def instruction_path(value):
    """An absolute path on one line, or None."""
    if not isinstance(value, str) or not os.path.isabs(value):
        return None
    return None if "\n" in value or "\r" in value else value


def canon_commit():
    root = os.path.realpath(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    try:
        with open(installed_plugins_path()) as fh:
            records = json.load(fh).get("plugins", {})
    except (OSError, ValueError):
        return UNKNOWN
    for entries in records.values():
        for entry in entries:
            if os.path.realpath(entry.get("installPath", "")) == root:
                sha = entry.get("gitCommitSha", "")
                return sha if SHA.fullmatch(sha) else UNKNOWN
    return UNKNOWN


def file_size(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return None


def always_loaded_bytes(loads):
    """Sum over the always-loaded set, closing includes over their parents. None when
    nothing is always-loaded yet; UNKNOWN when a member could not be sized."""
    members = {p for p, row in loads.items() if row.get("reason") in ALWAYS_LOADED}
    grew = True
    while grew:
        grew = False
        for path, row in loads.items():
            if path not in members and row.get("reason") in INCLUDED \
                    and row.get("parent") in members:
                members.add(path)
                grew = True
    if not members:
        return None
    sizes = [loads[p].get("bytes") for p in members]
    if any(not isinstance(s, int) for s in sizes):
        return UNKNOWN
    return str(sum(sizes))


def read_record(fh):
    """The record's first load per path, the last byte total written, and whether a
    canon line exists."""
    loads, last_total, has_canon = {}, None, False
    fh.seek(0)
    for line in fh:
        line = line.rstrip("\n")
        key, sep, value = line.partition(":")
        if not sep:
            continue
        if key == "instructions":
            try:
                row = json.loads(value)
            except ValueError:
                continue
            if isinstance(row, dict) and isinstance(row.get("path"), str):
                loads.setdefault(row["path"], row)
        elif key == "canon":
            has_canon = True
        elif key == "always-loaded-bytes":
            last_total = value
    return loads, last_total, has_canon


def stamp(payload):
    reason = payload.get("load_reason")
    if not isinstance(reason, str) or reason not in RECORDED:
        return
    session = safe_session(payload.get("session_id"))
    path = instruction_path(payload.get("file_path"))
    if not session or not path:
        return          # an empty parse means "I don't know", never "nothing loaded"
    parent = instruction_path(payload.get("parent_file_path"))

    row = {"path": path, "reason": reason, "bytes": file_size(path), "parent": parent}
    directory = os.path.join(state_root(), "read-log")
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, session), "a+") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        loads, last_total, has_canon = read_record(fh)
        out = []
        if reason in ALWAYS_LOADED and not has_canon:
            out.append("canon:%s" % canon_commit())
        if path not in loads:
            loads[path] = row
            out.append("instructions:%s" % json.dumps(row, sort_keys=True))
        total = always_loaded_bytes(loads)
        if total is not None and total != last_total:
            out.append("always-loaded-bytes:%s" % total)
        if out:
            fh.write("".join(line + "\n" for line in out))
            fh.flush()


def record_skill(payload):
    session = safe_session(payload.get("session_id"))
    name = skill_name(payload.get("tool_input"))
    if not session or not name:
        return          # an empty parse means "I don't know", never "nothing loaded"

    line = "skill:%s\n" % name
    try:
        directory = os.path.join(state_root(), "read-log")
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, session)
        # Append-only and deduplicated on read, not on write: re-reading the log to
        # check for a duplicate would race every parallel tool call in the session.
        with open(path, "a") as fh:
            fh.write(line)
    except Exception:
        pass            # the recorder is advisory; a failed write costs one
                        # re-read prompt, never the tool call it observed

    try:
        row = json.dumps({
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "session": session,
            "skill": name,
        })
        with open(os.path.join(state_root(), "skill-invocations.jsonl"), "a") as fh:
            fh.write(row + "\n")
    except Exception:
        pass            # advisory, same as above — a failed write costs one
                        # missing row in the audit log, never the tool call itself


def parse(raw):
    try:
        payload = json.loads(raw)
    except Exception:
        return None
    # valid JSON that is not an object parses fine and then raises on .get —
    # shape is part of the contract
    return payload if isinstance(payload, dict) else None


def main(payload):
    if payload.get("hook_event_name") == "InstructionsLoaded":
        stamp(payload)
    elif payload.get("tool_name") == "Skill":
        record_skill(payload)


if __name__ == "__main__":
    # The recorder is optional by construction. A hook copied away from its lib
    # must still run: crashing on a missing import is the very failure this
    # wrapper exists to record, and it would fail closed on the one path where
    # nothing is left to write the row.
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
    try:
        from hook_run import run as _run
    except Exception:
        def _run(_check, fn, event=None):
            return fn() or 0
    try:
        _raw = sys.stdin.read()
    except Exception:
        _raw = ""
    _payload = parse(_raw)
    if _payload is None:
        sys.exit(0)
    _event = _payload.get("hook_event_name")
    sys.exit(_run("record-loaded-context", lambda: main(_payload),
                  event=_event if isinstance(_event, str) else "PostToolUse"))
