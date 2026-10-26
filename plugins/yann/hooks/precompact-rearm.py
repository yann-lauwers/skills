#!/usr/bin/env python3
"""UserPromptSubmit — deliver the compaction capture, once per seam.

Failure it prevents: a summary of a past state reads exactly like present context.
Nothing in the transcript marks where the seam is, so a value that was true when it
was read — a file's contents, a ticket's status, a check's result — is quoted
forward as though it were current, and the reading is wrong in the one direction
nobody checks. The message names the split the reader cannot see: the summary is
evidence of history, and evidence of no current value.

Second failure, same seam: the skills and glossaries loaded before it are
gone from context while every ledger still records them as read, so the session
resumes on canon it no longer holds and nothing says so.

It carries the session's own written files in the same message, for the mirror-image
failure: those outlive the summary, so a session told only that "the hook was
updated" rebuilds a file that is already on disk and correct.

Published pages are carried the same way and always as a PAIR. A page has a hosted
address and a served local one; both exist in the transcript the summary replaces,
and a session that resumes holding one of them hands the reader half an answer —
usually the hosted half, since that is what the tool returned and what the reply
quoted. The local address is the half that keeps working after the scratchpad is
cleaned and from an account that does not own the hosted page, so it is the half
that must not be the one lost.

Why the delivery lives here rather than at the seam itself: an injection emitted
at `PreCompact` lands in the material being summarised and can be discarded with
the context it warns about. `additionalContext` at `UserPromptSubmit` is the
documented channel, it arrives as a system reminder the user never sees in the
transcript, and it arrives when the session is about to act.

Two design points that failed elsewhere before they were fixed:

  The flag is set BEFORE the message is emitted. Emit-then-clear re-fires forever
  whenever the hook is killed in between.

  The flag is keyed on the compaction EPOCH, not the session. A session-keyed flag
  is spent at the first seam, so every later compaction in that session — the
  sessions that compact most — delivers nothing.

Contract (verified against hook-development references/events-and-contracts.md):
  UserPromptSubmit can block; this never does.
  exit 0 + hookSpecificOutput.additionalContext -> injected as context.
  exit 0 + no output -> nothing happens.
"""
import json
import os
import re
import sys

MAX_NAMED = 8          # per kind, in the message; the file holds the rest


def state_root():
    return os.environ.get("HOOK_STATE_ROOT") or os.path.expanduser("~/.claude/state")


def safe_session(value):
    if not isinstance(value, str) or not value:
        return None
    return value if re.fullmatch(r"[A-Za-z0-9._-]{1,128}", value) else None


def claim_once(session, key):
    """True the first time this (session, key) is claimed.

    Atomic via O_CREAT|O_EXCL, and claimed before anything is emitted. A store
    failure returns False: the worst case of not delivering is one missed re-read,
    while the worst case of delivering on every prompt is a reminder the reader
    learns to skip.
    """
    try:
        directory = os.path.join(state_root(), "precompact")
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, "%s.%s" % (session, key))
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
        return True
    except FileExistsError:
        return False
    except Exception:
        return False


def load_capture(session):
    path = os.path.join(state_root(), "precompact", session + ".json")
    try:
        with open(path, errors="replace") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def dedupe_pages(pages):
    """One entry per page, the most recent republish kept.

    `local` is the stable key: it is served from the store's group/slug and
    identical across every artifact id a page is republished under, where
    `hosted` changes on every republish. Pages already come in the list
    oldest-first, so the LAST occurrence of a key is the most recent republish
    and every earlier one under the same key is the page it superseded.
    `hosted` stands in when a page never got a local copy at all.
    """
    keyed, order = {}, []
    for page in pages:
        if not isinstance(page, dict):
            continue
        key = page.get("local") or page.get("hosted") or page.get("title")
        if not key:
            continue
        if key not in keyed:
            order.append(key)
        keyed[key] = page
    return [keyed[k] for k in order]


def name_list(items, limit=MAX_NAMED):
    shown = [str(i) for i in items[:limit]]
    extra = len(items) - len(shown)
    text = ", ".join(shown)
    return text + (" and %d more" % extra if extra > 0 else "")


def short_path(path):
    """`~/x/y.md` for a path under home, verbatim otherwise.

    An artifact line is read to decide whether to OPEN the file, so the path
    stays whole — a basename collides across directories and a truncated path
    cannot be acted on at all.
    """
    home = os.path.expanduser("~")
    if path.startswith(home + os.sep):
        return "~" + path[len(home):]
    return path


def build_message(capture, capture_path):
    """The message for one seam. Always non-empty: the summary itself is the
    stale object, so a session that loaded nothing and wrote nothing is owed the
    staleness contract exactly like one that did."""
    skills = capture.get("skills") or []
    canon = capture.get("canon") or []
    artifacts = capture.get("artifacts") or []
    pages = dedupe_pages(capture.get("pages") or [])

    out = ["[PC-REARM] A compaction ended this session's context at epoch %d."
           % capture.get("epoch", 0)]

    # Governs how everything else above the seam is read. The split is history
    # versus current value: a summary is evidence of what was decided and
    # cannot be evidence of what a file, ticket or process now holds.
    out.append(
        "Everything above the seam is a summary written at the moment the "
        "compaction ran, so it describes a past state of this session. It is "
        "authoritative for history — the objective, the steps taken, the "
        "decisions and their reasons, the corrections given — and for no current "
        "value. File contents, a ticket's status, a PR's checks, a branch, a "
        "running service, a test result: each was true when it was read, and the "
        "summary carries no evidence that it still is. A value quoted out of it "
        "is a claim about the past, so re-read from the source anything the next "
        "action depends on, and say which reading a claim rests on when the two "
        "could differ.")

    parts = []
    if skills:
        parts.append("%d skill(s) — %s" % (len(skills), name_list(skills)))
    if canon:
        parts.append("%d glossary/ies — %s" % (len(canon), name_list(canon)))
    if parts:
        out.append(
            "Loaded before it, and no longer present: %s. "
            "The record that each was read survives the summary while its content "
            "does not, so a gate reading \"already loaded\" is answering about a "
            "context that is gone. "
            "Re-read the ones the next action needs before taking it."
            % "; ".join(parts))

    if artifacts:
        out.append(
            "This session's own output was on disk in %d file(s) at the seam — %s. "
            "Those outlive the summary, so rebuilding one from the summary's "
            "description writes over work already on disk: open the file before "
            "writing anything it may already hold."
            % (len(artifacts), name_list([short_path(a) for a in artifacts])))

    if pages:
        lines = []
        for page in pages:
            if not isinstance(page, dict):
                continue
            title = page.get("title") or "untitled"
            hosted = page.get("hosted") or ""
            local = page.get("local") or ""
            lines.append("%s — hosted %s · local %s" % (
                title, hosted or "none", local or "NO LOCAL COPY"))
        out.append(
            "This session published %d page(s), each with two addresses: %s. "
            "Both belong together in anything said about a page — the hosted URL "
            "reaches anyone and belongs to one account, the local URL is served "
            "from this machine's artifact store and survives the scratchpad being "
            "cleaned and the account being switched. A page reported with one "
            "address gives the reader no way to reach the other, and this message "
            "is the only place the pairing survives the summary. \"NO LOCAL COPY\" "
            "means the mirror did not run for that page."
            % (len(lines), "; ".join(lines)))

    if skills or canon or artifacts or pages:
        out.append(
            "The full lists are at %s. "
            "Already re-read since the compaction, and the next action enters none "
            "of their scope? Take no action and do not mention this."
            % capture_path)
    else:
        out.append(
            "Nothing was loaded or written before the seam, so nothing is owed "
            "beyond reading the summary as history. Take no action and do not "
            "mention this.")

    return " ".join(out)


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

    capture = load_capture(session)
    if not capture:
        return

    epoch = capture.get("epoch")
    if not isinstance(epoch, int):
        return

    message = build_message(
        capture, os.path.join(state_root(), "precompact", session + ".json"))

    if not claim_once(session, "rearm-%d" % epoch):
        return          # this seam has already been delivered

    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": message}}))

    try:
        sys.path.insert(0, os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "lib"))
        import hook_decisions
        hook_decisions.log(
            "precompact-rearm", "warn",
            "epoch=%d skills=%d canon=%d artifacts=%d pages=%d" % (
                epoch, len(capture.get("skills") or []),
                len(capture.get("canon") or []),
                len(capture.get("artifacts") or []),
                len(capture.get("pages") or [])),
            session=session, event="UserPromptSubmit")
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
    sys.exit(_run("precompact-rearm", main, event="UserPromptSubmit"))
