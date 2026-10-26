#!/usr/bin/env python3
"""One "has this actor loaded skill X since its last compaction" read, for any
guard that refuses an act until a skill is loaded.

TWO STORES DISAGREE ON "LOADED". `read-log/<session>` (written by
`record-loaded-context.py`) is archived at a compaction seam by
`precompact-capture.py`, so it goes stale exactly when the content leaves
context — the property that makes it honest to read. A skill the user typed as
`/<name>` does not reach it — it lands only in the transcript, as a
`<command-name>` record.

"RIGHT NOW" MEANS SINCE THE LAST SEAM. The read-log answers that directly for
the main session. When it does not — no line yet, or the read-log predates a
compaction that has since happened — the session's own transcript is the
second observable, and it is scanned only after the point its last
`"subtype":"compact_boundary"` record marks: content before that seam is gone
from context, whatever the file still says happened there.

SUBAGENTS SHARE THE PARENT'S session_id, so a guard reading the read-log would
credit every child with the parent's loads. A subagent therefore answers only
from its OWN transcript (`<parent-transcript-without-.jsonl>/subagents/agent-
<agent_id>.jsonl`), never through the parent's read-log — `held()` never even
opens it when `agent_id` is present.

THREE RETURNS, AND THE THIRD IS NOT THE SECOND. `True` and `False` are read
verdicts; `None` is "this file could not determine an answer" — a transcript
too large to scan safely, a read-log or transcript that raised on open. A
caller must never read `None` as `False`: the guard it feeds abstains and
allows, because a refusal must be clearable by an act the refused actor can
perform, and an unreadable observable clears nothing.

A payload field carrying no observable at all — `transcript_path` absent from
the hook payload, which every wired case here supplies but nothing enforces —
is a different fact from a real file that fails to open: it means no evidence
was offered, not that evidence exists and could not be read, so it resolves
like a miss (`False`) rather than an unknown (`None`). This is what lets a
caller whose payload carries no `transcript_path` keep denying on a bare read-log
miss instead of newly falling silent — see `references/hardening-cycle.md`,
moving an existing check onto a shared reader must not loosen it.

CONTRACT. `held(payload, name) -> True | False | None`. Pure: no environment
read but `HOOK_STATE_ROOT`/`~/.claude/state`, no write, no process spawned.
Every field is coerced at the entry point; a malformed payload or name is
`None`, never a crash — this module is imported into a PreToolUse gate's
decision path, and a raise there is read the same as any other crash: an
absent guard.

`held_detail(payload, name) -> (True | False | None, class | None)` carries
the same verdict plus WHICH feed credited a `True`, for a caller whose own
decision log distinguishes them (`managing-harness-unloaded`): `"readlog"` (the
main session's read-log), `"transcript"` (a `Skill` tool_use), `"typed"` (a
preloaded `<command-name>` block) or `"read"` (a whole `Read` of the skill's
own `SKILL.md`). `held()` is `held_detail()[0]` — its own contract and every
existing caller are unchanged.
"""

import json
import os
import re

MAX_TRANSCRIPT_BYTES = 256 * 1024 * 1024

# A nested subagent gets an extra directory level under `subagents/`; the walk
# that covers it is bounded so this reader never becomes the hang it exists to
# avoid.
MAX_SUBAGENT_DIRS = 64

# `agent_id` and `session_id` both become filename components, so each is
# validated rather than trusted — a rewritten id would read one actor's state
# under another's name. Real agent ids are hex-ish; real session ids are UUIDs.
SAFE_AGENT_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def _safe_session(value):
    if not isinstance(value, str) or not value:
        return None
    if "/" in value or "\\" in value or value.startswith("."):
        return None
    return value if re.fullmatch(r"[A-Za-z0-9._-]{1,128}", value) else None


PRELOAD_RE = re.compile(r"<command-name>([^<]+)</command-name>")
SKILL_MD_RE = re.compile(r"/([a-z0-9-]+)/SKILL\.md$")


def _state_root():
    return os.environ.get("HOOK_STATE_ROOT") or os.path.expanduser("~/.claude/state")


def _field(payload, key):
    v = payload.get(key)
    return v if isinstance(v, str) and v else ""


def _last_segment(name):
    """The identity a plugin-qualified name (`plugin:skill`) is credited
    under — its trailing half."""
    return name.rsplit(":", 1)[-1]


# ---------------------------------------------------------------------------
# The read-log
# ---------------------------------------------------------------------------

def _read_log_state(session, name):
    """True | False | None. A missing file is a real False — the recorder
    writes on the session's first Skill call, so absent means none has
    happened yet. A file that exists and cannot be opened (permission denied,
    a directory sitting where the file belongs) is a different fact and stays
    unknown rather than a negative."""
    path = os.path.join(_state_root(), "read-log", session)
    target = "skill:" + name
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if line.strip() == target:
                    return True
        return False
    except FileNotFoundError:
        return False
    except OSError:
        return None


# ---------------------------------------------------------------------------
# The transcript
# ---------------------------------------------------------------------------

def subagent_transcript(parent, agent_id):
    """The subagent's own JSONL, laid out beside its parent's — `<parent-
    without-.jsonl>/subagents/agent-<agent_id>.jsonl`, one extra `subagents/`
    level per nesting depth. Returns "" when none is found; the caller reads
    that as "not proven", never as "unreadable". `agent_id` is trusted here —
    every caller validates it against `SAFE_AGENT_ID` first."""
    if not parent.endswith(".jsonl"):
        return ""
    root = os.path.join(parent[:-len(".jsonl")], "subagents")
    wanted = "agent-%s.jsonl" % agent_id
    direct = os.path.join(root, wanted)
    if os.path.isfile(direct):
        return direct
    queue, visited = [root], 0
    while queue and visited < MAX_SUBAGENT_DIRS:
        d = queue.pop(0)
        visited += 1
        try:
            entries = list(os.scandir(d))
        except OSError:
            continue
        for e in entries:
            if e.is_dir(follow_symlinks=False):
                queue.append(e.path)
            elif e.name == wanted:
                return e.path
    return ""


class _Unreadable(Exception):
    """The transcript names a real file, and it could not be scanned to a
    verdict — too large, or the open/read itself failed."""


BASE_DIR_RE = re.compile(r"^Base directory for this skill:\s*(\S+)")


def _read_credits(name, rec):
    """The credit CLASS this one transcript record, read alone, earns for
    `name` — `"typed"` (a real typed `/name`, or a preloaded
    `<command-name><name></command-name>` block, or the "Base directory for
    this skill: …/<name>" meta row that follows a typed command),
    `"transcript"` (a `Skill` tool_use whose last `:` segment matches) — or
    None. A whole `Read` of `.../<name>/SKILL.md` is NOT decided here: it is
    provisional until its own `tool_result` confirms no error, which
    `_read_pending_id`/`_tool_result_errors` below carry, since crediting
    straight off the `tool_use` block credited a FAILED Read the same as a
    successful one (finding 9).

    A REAL typed slash command is TWO records, neither shaped like the
    agent-file preload this used to be the only reader of: (1) `type:"user"`,
    `isMeta` ABSENT, `message.content` a STRING —
    `<command-message>x</command-message>\\n<command-name>/x</command-name>\\n
    <command-args>…</command-args>` (grepped from a live transcript,
    2026-09-19) — and (2) a SEPARATE `isMeta` row whose text starts
    `Base directory for this skill: <path>`, the skill's own preamble. Neither
    is a `list`-content `isMeta` block carrying a bare (no leading `/`) name,
    which is the AGENT-FILE preload shape (a different observable) — crediting only that shape left a typed
    `/managing-harness` (or `/house-style`) permanently uncredited in the main
    session, though every deny message says it counts.
    """
    if not isinstance(rec, dict):
        return None
    msg = rec.get("message")
    content = msg.get("content") if isinstance(msg, dict) else None
    if rec.get("type") == "user" and isinstance(content, str):
        for n in PRELOAD_RE.findall(content):
            if _last_segment(n.lstrip("/")) == name:
                return "typed"
    if not isinstance(content, list):
        return None
    if rec.get("type") == "user" and rec.get("isMeta"):
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "text":
                continue
            text = block.get("text") or ""
            for n in PRELOAD_RE.findall(text):
                if _last_segment(n.lstrip("/")) == name:
                    return "typed"
            m = BASE_DIR_RE.match(text)
            if m and os.path.basename(m.group(1).rstrip("/")) == name:
                return "typed"
    for block in content:
        if not isinstance(block, dict) or block.get("type") != "tool_use":
            continue
        inp = block.get("input") if isinstance(block.get("input"), dict) else {}
        tool = block.get("name")
        if tool == "Skill" and isinstance(inp.get("skill"), str):
            if _last_segment(inp["skill"]) == name:
                return "transcript"
    return None


def _read_pending_id(name, rec):
    """The `tool_use` id of a whole `Read` (no `offset`, no `limit`) of
    `.../<name>/SKILL.md` in this record, or None — a PROVISIONAL "read"
    credit, confirmed only once `_tool_result_errors` shows its matching
    result did not error."""
    if not isinstance(rec, dict):
        return None
    msg = rec.get("message")
    content = msg.get("content") if isinstance(msg, dict) else None
    if not isinstance(content, list):
        return None
    for block in content:
        if not isinstance(block, dict) or block.get("type") != "tool_use":
            continue
        if block.get("name") != "Read":
            continue
        inp = block.get("input") if isinstance(block.get("input"), dict) else {}
        fp = inp.get("file_path")
        if (isinstance(fp, str) and inp.get("offset") is None
                and inp.get("limit") is None):
            m = SKILL_MD_RE.search(fp.replace("\\", "/"))
            if m and m.group(1) == name and isinstance(block.get("id"), str):
                return block["id"]
    return None


def _tool_result_errors(rec):
    """{tool_use_id: is_error} for every `tool_result` block this record
    carries. A tool's result always arrives as its own record, separate from
    the `tool_use` that requested it — this is the OTHER half of the pair
    `_read_pending_id` starts."""
    if not isinstance(rec, dict):
        return {}
    msg = rec.get("message")
    content = msg.get("content") if isinstance(msg, dict) else None
    if not isinstance(content, list):
        return {}
    out = {}
    for block in content:
        if isinstance(block, dict) and block.get("type") == "tool_result":
            tid = block.get("tool_use_id")
            if isinstance(tid, str):
                out[tid] = bool(block.get("is_error"))
    return out


def _scan_since_last_boundary(path, name):
    """The credit CLASS `name` earns anywhere after the transcript's LAST
    `"subtype":"compact_boundary"` record, or None — a credit earlier in the
    file is gone from context, whatever the line still says. A file with no
    boundary at all is scanned whole, because nothing has been dropped from
    it yet.

    One pass, one line held in memory at a time (plus the small set of
    `Read` tool_use ids still awaiting their own result): the credited class
    resets to None on every boundary crossed, so only what survives to
    end-of-file reflects the LAST one, with no second pass needed to find it
    first. `os.path.getsize` settles the size cap before a single byte is
    read, so an oversized file is never opened at all — the cost this
    function owes is bounded by that check, not by how much of the file it
    might otherwise stream.

    A `Read` credit is PROVISIONAL until its matching `tool_result` confirms
    it did not error — a stale offset or a skill moved since the transcript
    started would otherwise credit a Read that never actually delivered the
    file (finding 9). One still pending when the scan ends (or a boundary
    crosses) never credits: the discharge is a Read that SUCCEEDED, not one
    merely attempted.
    """
    try:
        size = os.path.getsize(path)
    except OSError:
        raise _Unreadable("missing")
    if size > MAX_TRANSCRIPT_BYTES:
        raise _Unreadable("too-large")
    credited = None
    pending_reads = {}                  # tool_use_id -> True, awaiting its result
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(rec, dict):
                    continue
                if rec.get("type") == "system" and rec.get("subtype") == "compact_boundary":
                    credited = None
                    pending_reads = {}
                    continue
                cls = _read_credits(name, rec)
                if cls:
                    credited = cls
                read_id = _read_pending_id(name, rec)
                if read_id:
                    pending_reads[read_id] = True
                for tool_use_id, is_error in _tool_result_errors(rec).items():
                    if tool_use_id in pending_reads:
                        if not is_error:
                            credited = "read"
                        pending_reads.pop(tool_use_id, None)
    except OSError:
        raise _Unreadable("unreadable")
    return credited


def _scan_transcript_detail(path, name):
    """(True | False | None, class | None). An empty `path` means the caller
    offered no transcript to check at all — a real miss, not an unknown, so a
    bare read-log negative still stands on its own (a payload missing the
    field is not evidence the field would have disagreed). A
    `path` that names a real file which cannot be scanned IS an unknown."""
    if not path:
        return False, None
    try:
        cls = _scan_since_last_boundary(path, name)
    except _Unreadable:
        return None, None
    return bool(cls), cls


def _scan_transcript(path, name):
    """True | False | None — `_scan_transcript_detail`'s bool half, the
    contract every caller before `held_detail` already relies on."""
    return _scan_transcript_detail(path, name)[0]


# ---------------------------------------------------------------------------
# held() / held_detail()
# ---------------------------------------------------------------------------

def _held_main_detail(payload, name):
    session = _safe_session(payload.get("session_id"))
    if session is None:
        return None, None
    rl = _read_log_state(session, name)
    if rl is True:
        return True, "readlog"
    tc, cls = _scan_transcript_detail(_field(payload, "transcript_path"), name)
    if tc is True:
        return True, cls
    if rl is None or tc is None:
        return None, None
    return False, None


def _held_subagent_detail(payload, agent_id, name):
    if not SAFE_AGENT_ID.match(agent_id):
        return None, None
    parent = _field(payload, "transcript_path")
    if not parent:
        return None, None
    path = subagent_transcript(parent, agent_id)
    if not path:
        return None, None
    return _scan_transcript_detail(path, name)


def held_detail(payload, name):
    """(True | False | None, class | None) — `held()`'s verdict, plus which
    feed credited a `True`: `"readlog"`, `"transcript"`, `"typed"` or
    `"read"` (see the module docstring). The class is always None when the
    bool is not True."""
    if not isinstance(payload, dict) or not isinstance(name, str) or not name:
        return None, None
    agent_id = _field(payload, "agent_id")
    if agent_id:
        return _held_subagent_detail(payload, agent_id, name)
    return _held_main_detail(payload, name)


def held(payload, name):
    """True | False | None — does this actor hold skill `name` in its context
    right now, meaning since its last compaction seam? A subagent (`agent_id`
    present in the payload) answers only from its own transcript; the parent's
    read-log is never opened for it. `None` is an abstain, never a negative —
    a caller wired to this must allow the act it gates on `None`."""
    return held_detail(payload, name)[0]
