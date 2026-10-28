#!/usr/bin/env python3
import json
import os
import sys

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HOOKS_DIR, os.path.join(HOOKS_DIR, "lib")]

import hook_decisions
import hook_mode
from hook_run import run

from domain_canon import remember_reads, word_refusals
from domain_canon.find_governing_canon import (
    MAP_FILE, is_ignored, is_owed_canon, nearest_glossary, owed_unless_ignored, place, repo_root,
    required_canon,
)
from domain_canon.parse_event import (
    as_edits, coerce_str, cwd_of, read_payload, session_of, target_path, tool_of,
)
from domain_canon import places
from domain_canon.places import READ_TOOLS, credited_reads, places_of, written_files

CHECK_ID_GATE = "canon-read-gate"
CHECK_ID_GATE_SHELL = "canon-read-gate-shell"
CHECK_ID_READ_FIRST = "canon-read-first"
CHECK_ID_REMINDER = "canon-read-reminder"
CHECK_ID_CREDIT = "canon-read-credit"
CHECK_ID_MAP = "canon-map-injection"
MAX_MAP_CHARS = 9000
REPO_COPIES = (os.path.join(".agents", "hooks", "domain-canon.py"),
               os.path.join(".claude", "hooks", "domain-canon.py"))


def log(payload, check_id, verdict, mode, detail):
    hook_decisions.log(check_id, verdict, detail, session=session_of(payload), mode=mode)


def mode_of(check_id):
    return hook_mode.resolve(check_id, "enforce")


def emit_context(event, text):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}))


def emit_deny(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))


def deferred_to_repo_copy(payload):
    root = repo_root(cwd_of(payload))
    if not root:
        return False
    here = os.path.realpath(__file__)
    return any(os.path.realpath(os.path.join(root, c)) != here and _same_bytes(os.path.join(root, c), here)
               and _wired(root, c) for c in REPO_COPIES)


def _same_bytes(a, b):
    try:
        with open(a, "rb") as fa, open(b, "rb") as fb:
            return fa.read() == fb.read()
    except OSError:
        return False


def _wired(root, copy):
    try:
        with open(os.path.join(root, ".claude", "settings.json")) as fh:
            hooks = json.load(fh).get("hooks", {})
    except (OSError, ValueError, AttributeError):
        return False
    return any(copy in h.get("command", "") for g in hooks.get("PreToolUse", []) for h in g.get("hooks", []))


def handle_session_start(payload):
    root = repo_root(cwd_of(payload))
    if not root:
        log(payload, CHECK_ID_MAP, "silent", "enforcing", "no repo root above cwd")
        return
    try:
        with open(os.path.join(root, MAP_FILE)) as fh:
            body = fh.read().strip()
    except OSError:
        log(payload, CHECK_ID_MAP, "silent", "enforcing", "no %s at repo root" % MAP_FILE)
        return
    if not body:
        log(payload, CHECK_ID_MAP, "silent", "enforcing", "%s is empty" % MAP_FILE)
        return
    full = len(body)
    note = ""
    if full > MAX_MAP_CHARS:
        body = body[:MAX_MAP_CHARS]
        note = (f"\n\n[truncated at {MAX_MAP_CHARS} of {full} characters — "
                f"the rest is in {MAP_FILE} at the repo root]")
        log(payload, CHECK_ID_MAP, "truncated", "enforcing",
            "%s :: %d of %d chars" % (MAP_FILE, MAX_MAP_CHARS, full))
    else:
        log(payload, CHECK_ID_MAP, "injected", "enforcing", "%s :: %d chars" % (MAP_FILE, full))
    emit_context("SessionStart", f"{MAP_FILE}, at the root of this repository, in full:\n\n{body}{note}")


def credit_whole_reads(payload, key):
    for root, abs_path in credited_reads(payload):
        rel = os.path.relpath(abs_path, root)
        if is_owed_canon(rel):
            remember_reads.record(key, "read", remember_reads.canon_fact(root, rel))
            log(payload, CHECK_ID_CREDIT, "credited", "enforcing", "verb=%s %s" % (tool_of(payload), rel))


def remind_of_unread_canon(payload, key):
    facts = remember_reads.facts(key)
    fresh, subjects = [], []
    for root, directory in places_of(payload):
        probe = places.probe(directory)
        missing = [c for c in required_canon(root, probe)
                   if ("reminded", remember_reads.canon_fact(root, c)) not in facts
                   and ("read", remember_reads.canon_fact(root, c)) not in facts
                   and (root, c) not in fresh]
        missing = owed_unless_ignored(root, directory, missing)
        if missing:
            fresh.extend((root, c) for c in missing)
            subjects.append(_label(root, directory))
    if not fresh:
        return
    for root, c in fresh:
        remember_reads.record(key, "reminded", remember_reads.canon_fact(root, c))
    subject = subjects[0] if len(subjects) == 1 else "%s (+%d more)" % (subjects[0], len(subjects) - 1)
    log(payload, CHECK_ID_REMINDER, "warn", "enforcing", "%s :: %d named" % (subject, len(fresh)))
    emit_context("PostToolUse", word_refusals.reminder(CHECK_ID_REMINDER, subject, [c for _r, c in fresh]))


def handle_post_tool_use(payload, key):
    credit_whole_reads(payload, key)
    remind_of_unread_canon(payload, key)


def _label(root, directory):
    rel = os.path.relpath(directory, root)
    return "this repository" if rel == "." else rel + "/"


def refuse(payload, check_id, root, subject, missing):
    emit_deny(word_refusals.unread_canon(check_id, tool_of(payload) or "call", root, subject, missing))


def handle_read_first(payload, key):
    mode = mode_of(CHECK_ID_READ_FIRST)
    facts = remember_reads.facts(key)
    for root, directory in places_of(payload):
        probe = places.probe(directory)
        required = required_canon(root, probe)
        if not required:
            continue
        missing = remember_reads.unread(facts, root, required)
        if missing and is_ignored(root, directory):
            continue
        subject = _label(root, directory)
        glossary = nearest_glossary(root, probe)
        if ("scored", glossary) not in facts:
            remember_reads.record(key, "scored", glossary)
            facts.add(("scored", glossary))
            if not missing:
                log(payload, CHECK_ID_READ_FIRST, "preloaded", mode, subject)
        if not missing:
            continue
        detail = "verb=%s %s :: %d unread" % (tool_of(payload), subject, len(missing))
        if mode == "observe":
            log(payload, CHECK_ID_READ_FIRST, "would-deny", mode, detail)
            return False
        log(payload, CHECK_ID_READ_FIRST, "deny", mode, detail)
        refuse(payload, CHECK_ID_READ_FIRST, root, subject, missing)
        return True
    return False


def handle_shell_write_gate(payload, key):
    targets = written_files(payload)
    if not targets:
        return False
    facts = remember_reads.facts(key)
    mode = mode_of(CHECK_ID_GATE_SHELL)
    for root, abs_path in targets:
        missing = owed_unless_ignored(
            root, abs_path, remember_reads.unread(facts, root, required_canon(root, abs_path)))
        if not missing:
            continue
        rel = os.path.relpath(abs_path, root)
        detail = "%s :: %s" % (rel, ",".join(missing))
        if mode == "observe":
            log(payload, CHECK_ID_GATE_SHELL, "would-deny", mode, detail)
            return False
        log(payload, CHECK_ID_GATE_SHELL, "deny", mode, detail)
        refuse(payload, CHECK_ID_GATE_SHELL, root, rel, missing)
        return True
    return False


def handle_tool_write_gate(payload, key):
    where = place(target_path(payload))
    if not where:
        return False
    root, abs_path = where
    missing = owed_unless_ignored(
        root, abs_path, remember_reads.unread(remember_reads.facts(key), root, required_canon(root, abs_path)))
    if not missing:
        return False
    rel = os.path.relpath(abs_path, root)
    mode = mode_of(CHECK_ID_GATE)
    detail = "%s :: %s" % (rel, ",".join(missing))
    if mode == "observe":
        log(payload, CHECK_ID_GATE, "would-deny", mode, detail)
        return False
    log(payload, CHECK_ID_GATE, "deny", mode, detail)
    refuse(payload, CHECK_ID_GATE, root, rel, missing)
    return True


def handle_pre_tool_use(payload, key):
    tool = tool_of(payload)
    if tool == "Bash":
        return handle_shell_write_gate(payload, key) or handle_read_first(payload, key)
    if tool in READ_TOOLS:
        return handle_read_first(payload, key)
    return handle_tool_write_gate(payload, key)


def main():
    payload = read_payload()
    if payload is None or deferred_to_repo_copy(payload):
        return
    event = coerce_str(payload.get("hook_event_name")) or ""
    if event == "SessionStart":
        handle_session_start(payload)
        return
    key = remember_reads.key_of(payload)
    if key is None:
        return
    calls = as_edits(payload)
    if event == "PreToolUse":
        any(handle_pre_tool_use(call, key) for call in calls)
    elif event in ("PostToolUse", "PostToolUseFailure") and calls:
        handle_post_tool_use(calls[0], key)


if __name__ == "__main__":
    sys.exit(run("domain-canon", main))
