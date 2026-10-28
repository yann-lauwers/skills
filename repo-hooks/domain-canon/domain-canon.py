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
    BASH_TOOL, GREP_NAME_ONLY_MODES, GREP_TOOL, READ_TOOL, as_edits, command_of, coerce_str, cwd_of, read_payload, session_of,
    target_path, tool_of,
)
from domain_canon.trace_shell_command import (
    SLICE_READERS, WHOLE_FILE_READERS, over_parse_cap, reached_files,
    whole_reads_naming_no_file, written_files,
)

CHECK_ID_GATE = "canon-read-gate"
CHECK_ID_GATE_SHELL = "canon-read-gate-shell"
CHECK_ID_READ_FIRST = "canon-read-first"
CHECK_ID_UNPLACED = "canon-unplaced-read"
CHECK_ID_REMINDER = "canon-read-reminder"
CHECK_ID_CREDIT = "canon-read-credit"
CHECK_ID_MAP = "canon-map-injection"
MAX_MAP_CHARS = 9000


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


def grep_touched(payload):
    where = place(target_path(payload))
    if not where or not os.path.isfile(where[1]):
        return []
    tool_input = payload.get("tool_input")
    mode = coerce_str(tool_input.get("output_mode")) if isinstance(tool_input, dict) else None
    return [(where[0], where[1], False, GREP_TOOL,
             (mode or "files_with_matches") not in GREP_NAME_ONLY_MODES)]


def touched(payload, unplaced=None):
    tool = tool_of(payload)
    if tool == GREP_TOOL:
        return grep_touched(payload)
    if tool != BASH_TOOL:
        where = place(target_path(payload))
        return [(where[0], where[1], tool == READ_TOOL, tool, True)] if where else []
    command = command_of(payload)
    return reached_files(command, cwd_of(payload), unplaced) if command else []


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


def log_whole_reads_naming_no_file(payload, reached):
    command = command_of(payload)
    if not command:
        return
    missed = whole_reads_naming_no_file(command, cwd_of(payload), {r[1] for r in reached})
    if missed:
        log(payload, CHECK_ID_CREDIT, "unresolved", "enforcing",
            "%d operand(s) named no file :: %s" % (len(missed), " ".join(missed[:4])))


def credit_whole_reads(key, reached):
    for root, abs_path, credited, _verb, _opens in reached:
        rel = os.path.relpath(abs_path, root)
        if credited and is_owed_canon(rel):
            remember_reads.record(key, "read", remember_reads.canon_fact(root, rel))


def log_read_credit(payload, reached):
    if tool_of(payload) != BASH_TOOL:
        return
    classes = {}
    for root, abs_path, credited, verb, _opens in reached:
        rel = os.path.relpath(abs_path, root)
        if not is_owed_canon(rel):
            continue
        if credited:
            verdict = "credited"
        elif verb in WHOLE_FILE_READERS or verb in SLICE_READERS:
            verdict = "slice"
        else:
            verdict = "unknown-verb"
        classes.setdefault((verdict, verb), []).append(rel)
    for (verdict, verb), rels in classes.items():
        log(payload, CHECK_ID_CREDIT, verdict, "enforcing", "verb=%s n=%d %s" % (verb, len(rels), rels[0]))


def remind_of_unread_canon(payload, key, reached):
    facts = remember_reads.facts(key)
    fresh, subjects = [], []
    for root, abs_path, _credited, _verb, _opens in reached:
        missing = [c for c in required_canon(root, abs_path)
                   if ("reminded", remember_reads.canon_fact(root, c)) not in facts
                   and ("read", remember_reads.canon_fact(root, c)) not in facts
                   and (root, c) not in fresh]
        missing = owed_unless_ignored(root, abs_path, missing)
        if missing:
            fresh.extend((root, c) for c in missing)
            subjects.append(os.path.relpath(abs_path, root))
    if not fresh:
        return
    for root, c in fresh:
        remember_reads.record(key, "reminded", remember_reads.canon_fact(root, c))
    subject = subjects[0] if len(subjects) == 1 else "%s (+%d more)" % (subjects[0], len(subjects) - 1)
    log(payload, CHECK_ID_REMINDER, "warn", "enforcing", "%s :: %d named" % (subject, len(fresh)))
    emit_context("PostToolUse", word_refusals.reminder(CHECK_ID_REMINDER, subject, [c for _r, c in fresh]))


def handle_post_tool_use(payload, key):
    reached = touched(payload)
    log_whole_reads_naming_no_file(payload, reached)
    if not reached:
        return
    credit_whole_reads(key, reached)
    log_read_credit(payload, reached)
    remind_of_unread_canon(payload, key, reached)


def refuse_unread(payload, check_id, root, rel, missing):
    emit_deny(word_refusals.unread_canon(check_id, tool_of(payload) or "call", root, rel, missing))


def handle_read_first(payload, key):
    mode = mode_of(CHECK_ID_READ_FIRST)
    command = command_of(payload) if tool_of(payload) == BASH_TOOL else None
    if command and over_parse_cap(command, cwd_of(payload)):
        if mode == "observe":
            log(payload, CHECK_ID_READ_FIRST, "would-deny", mode, "over parse cap")
            return
        log(payload, CHECK_ID_READ_FIRST, "over-cap", mode, "over parse cap")
        emit_deny(word_refusals.over_parse_cap(CHECK_ID_READ_FIRST))
        return True

    facts = remember_reads.facts(key)
    unplaced = []
    for root, abs_path, _credited, _verb, opens in touched(payload, unplaced):
        required = required_canon(root, abs_path) if opens else []
        if not required:
            continue
        missing = remember_reads.unread(facts, root, required)
        if missing and is_ignored(root, abs_path):
            continue
        rel = os.path.relpath(abs_path, root)
        glossary = nearest_glossary(root, abs_path)
        first_in_context = ("scored", glossary) not in facts
        if first_in_context:
            remember_reads.record(key, "scored", glossary)
            facts.add(("scored", glossary))
        if not missing:
            if first_in_context:
                log(payload, CHECK_ID_READ_FIRST, "preloaded", mode, rel)
            continue
        detail = "%s :: %d unread" % (rel, len(missing))
        if mode == "observe":
            log(payload, CHECK_ID_READ_FIRST, "would-deny", mode, detail)
            return
        log(payload, CHECK_ID_READ_FIRST, "deny", mode, detail)
        refuse_unread(payload, CHECK_ID_READ_FIRST, root, rel, missing)
        return True
    return handle_unplaced_reads(payload, unplaced, facts)


def handle_unplaced_reads(payload, unplaced, facts):
    mode = mode_of(CHECK_ID_UNPLACED)
    for directory, operand, verb in unplaced:
        where = place(os.path.join(directory, "unplaced-operand"))
        if not where:
            continue
        root, probe = where
        missing = remember_reads.unread(facts, root, required_canon(root, probe))
        if not missing:
            continue
        rel_dir = os.path.relpath(directory, root)
        detail = "verb=%s %s :: %d unread" % (verb, rel_dir, len(missing))
        if mode == "observe":
            log(payload, CHECK_ID_UNPLACED, "would-deny", mode, detail)
            return False
        log(payload, CHECK_ID_UNPLACED, "deny", mode, detail)
        emit_deny(word_refusals.unplaced_read(
            CHECK_ID_UNPLACED, tool_of(payload) or "call", root, rel_dir, operand, missing))
        return True
    return False


def handle_shell_write_gate(payload, key):
    command = command_of(payload)
    targets = written_files(command, cwd_of(payload)) if command else []
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
        refuse_unread(payload, CHECK_ID_GATE_SHELL, root, rel, missing)
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
    refuse_unread(payload, CHECK_ID_GATE, root, rel, missing)
    return True


def handle_pre_tool_use(payload, key):
    tool = tool_of(payload)
    if tool == BASH_TOOL:
        return handle_shell_write_gate(payload, key) or handle_read_first(payload, key)
    if tool in (READ_TOOL, GREP_TOOL):
        return handle_read_first(payload, key)
    return handle_tool_write_gate(payload, key)


def main():
    payload = read_payload()
    if payload is None:
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
