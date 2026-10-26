#!/usr/bin/env python3
"""PreCompact — write down what only exists right now, before the summary replaces it.

Failure it prevents: a compaction replaces the conversation with a summary, so the
skills this session loaded are gone from context while every
ledger still records them as read. The session then resumes editing files on canon
it no longer holds, and nothing after the seam can reconstruct what was lost —
this is the last moment that knowledge exists anywhere.

This hook only WRITES STATE. It emits nothing.

Two events deliver what it captures, and both are documented context channels:
`UserPromptSubmit` on the first prompt after the seam, and `SessionStart` with the
`compact` matcher. `PreCompact`'s own documented decision control is
`{"decision": "block"}` — carrying the payload out through this event instead would
put the obligation in the one place a compaction is free to discard.

Three feeds, every one of them already on disk:

  skills    $HOOK_STATE_ROOT/read-log/<session>, written by record-loaded-context.py
  artifacts the session's own transcript, for the files it wrote
  pages     the same transcript for what it PUBLISHED, resolved against the local
            artifact store's own registries for the second address

The first answers what the session FORGOT; the last two answer where its work
LIVES. A summary that describes an edit without naming the file it landed in sends
the resumed session to rebuild something that is already on disk and current.

A published page has TWO addresses and neither one substitutes for the other: the
hosted URL belongs to one account and reaches anyone, the served local URL reaches
every account on this machine and survives the scratchpad being cleaned. They exist
together in exactly one place before the seam — the tool response and the mirror
hook's message, both of which the summary replaces — so a page is captured as a
PAIR or not at all, and a missing half is recorded as missing rather than dropped.
The pairing itself is read from the store's registries rather than from the
transcript, because the store is the copy that is still true after the seam.

What the session was DOING needs no feed here either: the compaction summary is
the record of that, and this hook's own instructions say what a summary must
carry forward. Duplicating it into a second feed would put one fact in two homes
and leave the reader deciding which is current.

Contract (verified against hook-development references/events-and-contracts.md):
  PreCompact can block via {"decision": "block"}. This hook never does — a failed
  capture costs one re-read, and blocking a compaction costs the session.
  exit 0 always.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import published_pages

MAX_ITEMS_PER_KIND = 25

# Tools whose `file_path` names a file the session WROTE. Read carries the same
# key and is deliberately absent: a file that was only read is not this session's
# output, and listing it would bury the few paths that are.
WRITE_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")

# The session scratchpad, which is a temp root plus a `scratchpad` segment. Both
# halves are required: the segment alone would drop a project directory a user
# named `scratchpad/`, and the temp root alone would drop the tmpdir every test
# and every legitimate temp artifact lives in.
TEMP_ROOTS = ("/tmp/", "/private/tmp/", "/var/folders/", "/private/var/folders/")
SCRATCH_SEGMENT = "/scratchpad/"

def state_root():
    return os.environ.get("HOOK_STATE_ROOT") or os.path.expanduser("~/.claude/state")


def canon_ledger_dir():
    """Resolved exactly as `domain-canon.py` resolves it, from the same variable —
    a second spelling would archive a directory nothing writes to."""
    return os.environ.get("CANON_STATE_DIR") or os.path.expanduser(
        "~/.claude/state/domain-canon")


def safe_session(value):
    if not isinstance(value, str) or not value:
        return None
    return value if re.fullmatch(r"[A-Za-z0-9._-]{1,128}", value) else None


def stream_lines(path):
    """Every line of a file, one at a time, never all of them at once."""
    try:
        with open(path, errors="replace") as fh:
            for line in fh:
                yield line
    except Exception:
        return


def skills_loaded(session):
    path = os.path.join(state_root(), "read-log", session)
    out = []
    try:
        for line in open(path, errors="replace"):
            line = line.strip()
            if line.startswith("skill:") and line not in out:
                out.append(line)
    except Exception:
        pass
    return [s.split(":", 1)[1] for s in out]


def is_scratchpad(path):
    """A file the session wrote to be thrown away.

    Naming one is false on both halves of what the artifacts line claims — it is
    not work that outlived the summary, and reopening it teaches nothing. Against
    a list capped at MAX_ITEMS_PER_KIND it also displaces the paths that are.
    """
    return path.startswith(TEMP_ROOTS) and SCRATCH_SEGMENT in path


def artifacts_written(transcript):
    """Every file this session wrote, oldest first, deduped, still on disk.

    Read from the transcript because it is the only record that already exists.
    A PostToolUse recorder would answer for sessions started after it was
    installed and for no others, and the first compaction that matters is
    usually in a session already running.

    The existence filter is what keeps the list honest: a path written and then
    deleted, or one inside a worktree since removed, reads as a live artifact
    otherwise — and a resumed session sent to open it learns nothing except that
    this feed cannot be trusted.
    """
    if not transcript:
        return []
    out = []
    for line in stream_lines(transcript):
        if '"tool_use"' not in line or "file_path" not in line:
            continue                    # cheap reject before paying for a parse
        try:
            row = json.loads(line)
        except Exception:
            continue
        if not isinstance(row, dict):
            continue
        message = row.get("message")
        blocks = message.get("content") if isinstance(message, dict) else None
        if not isinstance(blocks, list):
            continue
        for block in blocks:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            if block.get("name") not in WRITE_TOOLS:
                continue
            data = block.get("input")
            path = data.get("file_path") if isinstance(data, dict) else None
            if isinstance(path, str) and path and path not in out:
                out.append(path)
    return [p for p in out if os.path.isfile(p) and not is_scratchpad(p)]


def epoch(session):
    """How many seams this session has already crossed, counted from the archives.

    The archive rename is the counter — one artifact serving both jobs, so there is
    no second file to fall out of step with it.
    """
    directory = os.path.join(state_root(), "read-log")
    try:
        prefix = session + ".pc"
        return sum(1 for n in os.listdir(directory) if n.startswith(prefix))
    except Exception:
        return 0


def archive_read_log(session):
    """Move the read-log aside so its gates re-arm, and advance the epoch.

    A read recorded before a compaction no longer means the content is in context,
    so a gate reading "already loaded" is answering about a session that no longer
    exists. Renaming is what makes the next load count as the first.

    A seam crossed with no read-log leaves an EMPTY archive, because this count is
    the epoch and the epoch keys the delivery flag. Skipping the archive holds the
    counter at a value already claimed, so the next seam's capture is written
    correctly, keyed to a spent flag, and delivered to nobody — the exact loss the
    epoch keying exists to prevent, reached through the other door. A session that
    loads its first skill after its first compaction is all it takes.
    """
    directory = os.path.join(state_root(), "read-log")
    os.makedirs(directory, exist_ok=True)
    live = os.path.join(directory, session)
    index = 0
    while os.path.exists("%s.pc%d" % (live, index)):
        index += 1
    target = "%s.pc%d" % (live, index)
    if os.path.exists(live):
        os.rename(live, target)
    else:
        open(target, "w").close()
    return os.path.basename(target)


def canon_facts(session):
    """Every canon path this session's ledger already recorded, read before the
    archive rename moves it aside — the same ordering invariant as the skills
    feed: read first, archive second, or the seam that owns this fact reads as
    having recorded nothing.
    """
    facts = []
    path = os.path.join(canon_ledger_dir(), session + ".txt")
    try:
        with open(path, errors="replace") as fh:
            for line in fh:
                kind, _, rel = line.strip().partition(" ")
                if kind and rel and rel not in facts:
                    facts.append(rel)
    except OSError:
        pass
    return facts


def archive_canon_ledger(session):
    """Move this session's canon ledger aside so `canon-read-gate` re-arms.

    The ledger records which glossaries and decision records the session read. A
    compaction replaces that content with a summary while every `read` line still
    stands, so the gate would keep opening on canon the session can no longer
    recall. Renaming makes the first edit past the seam demand the re-read.

    Only the session's own ledger. A subagent keys on its `agent_id` and its
    window is not what this seam replaced.
    """
    live = os.path.join(canon_ledger_dir(), session + ".txt")
    if not os.path.exists(live):
        return None
    index = 0
    while os.path.exists("%s.pc%d" % (live, index)):
        index += 1
    target = "%s.pc%d" % (live, index)
    os.rename(live, target)
    return os.path.basename(target)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    if not isinstance(payload, dict):
        return
    session = safe_session(payload.get("session_id"))
    if not session:
        return

    transcript_path = payload.get("transcript_path") or ""

    # Everything is read BEFORE the archive rename, because the skills feed lives in
    # the very file the rename moves. Computing it afterwards yields the empty set,
    # and an empty set here reads as "nothing was loaded" — a wrong answer that
    # announces itself nowhere.
    captured = {
        "session": session,
        "epoch": epoch(session) + 1,
        "trigger": payload.get("trigger") or payload.get("matcher") or "unknown",
        "cwd": payload.get("cwd") or "",
        "transcript_path": transcript_path,
        "skills": skills_loaded(session)[:MAX_ITEMS_PER_KIND],
        "canon": canon_facts(session)[:MAX_ITEMS_PER_KIND],
        # Sliced from the TAIL, unlike the two above. A long session's earliest
        # writes are its least relevant, and the work a compaction interrupts is
        # always at the recent end — a head slice hands back the opening moves and
        # drops the file that was being edited when the window filled.
        "artifacts": artifacts_written(
            transcript_path)[-MAX_ITEMS_PER_KIND:],
        # Tail-sliced for the same reason as the artifacts above: a long session's
        # most recent page is the one being worked on when the window filled.
        "pages": published_pages.pages_published(
            transcript_path, stream_lines)[-MAX_ITEMS_PER_KIND:],
    }

    try:
        directory = os.path.join(state_root(), "precompact")
        os.makedirs(directory, exist_ok=True)
        # Two destinations, written the same way. `<session>.json` is the LIVE
        # one `precompact-rearm.py` reads at the very next prompt; it is
        # overwritten at every seam by design, since only the latest seam is
        # ever owed a delivery. `<session>.pc<epoch>.json` is never overwritten
        # — the epoch is unique per seam — so a session that crosses more than
        # one compaction keeps every earlier seam's own snapshot on disk,
        # rather than only the one rearm happened to deliver.
        live = os.path.join(directory, session + ".json")
        per_epoch = os.path.join(directory, "%s.pc%d.json" % (session, captured["epoch"]))
        for target in (live, per_epoch):
            # Written whole then moved: a reader arriving mid-write would otherwise
            # get a truncated file and treat a parse failure as "nothing was captured".
            tmp = target + ".tmp"
            with open(tmp, "w") as fh:
                json.dump(captured, fh)
            os.replace(tmp, target)
    except Exception:
        pass

    try:
        archive_read_log(session)
    except Exception:
        pass

    try:
        archive_canon_ledger(session)
    except Exception:
        pass

    try:
        sys.path.insert(0, os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "lib"))
        import hook_decisions
        hook_decisions.log(
            "precompact-capture", "captured",
            "epoch=%d skills=%d artifacts=%d pages=%d" % (
                captured["epoch"], len(captured["skills"]),
                len(captured["artifacts"]), len(captured["pages"])),
            session=session, event="PreCompact")
    except Exception:
        pass


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
    sys.exit(_run("precompact-capture", main, event="PreCompact"))
