#!/usr/bin/env python3
import hashlib
import json
import os
import shlex
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

import hook_decisions
import hook_mode
import hook_shell
from hook_run import run

CHECK_READ_FIRST = "canon-read-first"
CHECK_CREDIT = "canon-read-credit"
CHECK_MAP = "canon-map-injection"
FILE_TOOLS = frozenset(("Read", "Edit", "Write", "NotebookEdit"))
SEARCH_TOOLS = frozenset(("Grep", "Glob"))
WHOLE_FILE_READERS = frozenset(("cat", "bat"))
EXPANSION_CHARS = "$`*?["
GLOSSARY = "GLOSSARY.md"
MAP_FILE = "GLOSSARY-MAP.md"
ADR_DIR = os.path.join("docs", "adr")
MAX_MAP_CHARS = 9000
PATHS_PER_CAT = 40
STATE_DIR = os.environ.get("CANON_STATE_DIR") or os.path.expanduser("~/.claude/state/domain-canon")
REPO_COPIES = (os.path.join(".agents", "hooks", "domain-canon.py"),
               os.path.join(".claude", "hooks", "domain-canon.py"))


def text(value):
    return value if isinstance(value, str) and value else None


def repo_root(path):
    while path and path != os.path.dirname(path):
        if os.path.exists(os.path.join(path, ".git")):
            return path
        path = os.path.dirname(path)
    return None


def is_canon(path):
    name = os.path.basename(path)
    return name in (GLOSSARY, MAP_FILE) or (name.endswith(".md") and os.path.dirname(path).endswith(ADR_DIR))


def canon_above(root, directory):
    rel = os.path.relpath(directory, root)
    parts = [] if rel == "." else rel.split(os.sep)
    found = []
    for depth in range(len(parts) + 1):
        here = os.path.join(root, *parts[:depth])
        if os.path.isfile(os.path.join(here, GLOSSARY)):
            found.append(os.path.relpath(os.path.join(here, GLOSSARY), root))
        try:
            records = sorted(n for n in os.listdir(os.path.join(here, ADR_DIR)) if n.endswith(".md") and n != "README.md")
        except OSError:
            records = []
        found.extend(os.path.relpath(os.path.join(here, ADR_DIR, n), root) for n in records)
    return found


def fact(root, rel):
    return "%s:%s" % (hashlib.sha1(os.fsencode(root)).hexdigest()[:12], rel)


def ledger_path(payload):
    key = text(payload.get("agent_id")) or text(payload.get("session_id")) or "nosession"
    return None if "/" in key or ".." in key else os.path.join(STATE_DIR, key + ".txt")


def read_facts(path):
    try:
        with open(path) as fh:
            return {line.strip().partition(" ")[2] for line in fh if line.startswith("read ")}
    except OSError:
        return set()


def literal_path(word, here):
    literal = word[:min((word.find(c) for c in EXPANSION_CHARS if c in word), default=len(word))]
    if not literal or here is None and not os.path.isabs(os.path.expanduser(literal)):
        return None
    return os.path.normpath(os.path.join(here or "/", os.path.expanduser(literal)))


def words(statement):
    try:
        return shlex.split(statement, posix=True)
    except ValueError:
        return statement.split()


def reads_only_canon(statement, here):
    if hook_shell.command_word(statement) not in WHOLE_FILE_READERS:
        return False
    paths = [literal_path(w, here) for w in hook_shell.operands(statement)]
    return bool(paths) and all(p and os.path.isfile(p) and is_canon(p) for p in paths)


def touched_paths(payload, tool, tool_input, cwd):
    if tool in FILE_TOOLS:
        return [literal_path(text(tool_input.get("file_path")) or text(tool_input.get("notebook_path")) or "", cwd)]
    if tool in SEARCH_TOOLS:
        return [literal_path(text(tool_input.get("path")) or cwd, cwd)]
    command = text(tool_input.get("command")) if tool == "Bash" else None
    paths = []
    for statement, at in hook_shell.statements_with_cwd(command or "", cwd):
        here = at or cwd
        if reads_only_canon(statement, here):
            continue
        paths.append(here)
        for word in words(statement):
            for candidate in {word, word.partition("=")[2], word.lstrip("0123456789<>&|")}:
                path = literal_path(candidate, here)
                if path and not os.path.exists(path):
                    path = os.path.dirname(path)
                if path and os.path.exists(path):
                    paths.append(path)
    return paths


def governed_places(paths):
    places = {}
    for path in filter(None, paths):
        if os.path.isfile(path) and is_canon(path):
            continue
        directory = path if os.path.isdir(path) else os.path.dirname(path)
        root = repo_root(directory)
        if root and ".git" not in os.path.relpath(directory, root).split(os.sep):
            places.setdefault(directory, root)
    return places.items()


def refusal(tool, root, directory, missing):
    rel = os.path.relpath(directory, root)
    subject = "this repository" if rel == "." else rel + "/"
    paths = [shlex.quote(os.path.join(root, c)) for c in missing]
    cats = "".join("  cat " + " ".join(paths[i:i + PATHS_PER_CAT]) + "\n" for i in range(0, len(paths), PATHS_PER_CAT))
    return (f"[{CHECK_READ_FIRST}] {subject} sits under {len(missing)} canon file{'s' if len(missing) != 1 else ''} "
            f"this session has not read:\n" + "".join(f"  {c}\n" for c in missing)
            + f"Read them, then retry this {tool}:\n" + cats
            + "Only a whole read counts: the Read tool with no offset or limit, or `cat` with no pipe or redirect.")


def gate(payload, tool, tool_input, cwd, session):
    facts = read_facts(ledger_path(payload) or "")
    mode = hook_mode.resolve(CHECK_READ_FIRST, "enforce")
    for directory, root in governed_places(touched_paths(payload, tool, tool_input, cwd)):
        missing = [c for c in canon_above(root, directory) if fact(root, c) not in facts]
        if not missing:
            continue
        verdict = "would-deny" if mode == "observe" else "deny"
        hook_decisions.log(CHECK_READ_FIRST, verdict, "tool=%s %s :: %d unread" % (tool, os.path.relpath(directory, root), len(missing)),
                           session=session, event="PreToolUse", mode=mode)
        if verdict == "deny":
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                     "permissionDecisionReason": refusal(tool, root, directory, missing)}}))
        return


def credited_paths(tool, tool_input, cwd):
    if tool == "Read":
        whole = tool_input.get("offset") is None and tool_input.get("limit") is None
        return [literal_path(text(tool_input.get("file_path")) or "", cwd)] if whole else []
    command = text(tool_input.get("command")) if tool == "Bash" else None
    return [literal_path(w, at) for statement, at in hook_shell.statements_with_cwd(command or "", cwd)
            if hook_shell.command_word(statement) in WHOLE_FILE_READERS and not hook_shell.has_pipe_or_redirect(statement)
            for w in hook_shell.operands(statement)]


def credit(payload, tool, tool_input, cwd, session):
    path = ledger_path(payload)
    for file in filter(None, credited_paths(tool, tool_input, cwd)):
        root = repo_root(os.path.dirname(file))
        if not (root and os.path.isfile(file) and is_canon(file)):
            continue
        rel = os.path.relpath(file, root)
        try:
            os.makedirs(STATE_DIR, exist_ok=True)
            with open(path, "a") as fh:
                fh.write("read %s\n" % fact(root, rel))
        except (OSError, TypeError):
            return
        hook_decisions.log(CHECK_CREDIT, "credited", "tool=%s %s" % (tool, rel), session=session,
                           event="PostToolUse", mode="enforce")


def inject_map(cwd, session):
    root = repo_root(cwd)
    try:
        with open(os.path.join(root or "", MAP_FILE)) as fh:
            body = fh.read().strip()
    except OSError:
        return
    if not body:
        return
    verdict = "truncated" if len(body) > MAX_MAP_CHARS else "injected"
    note = f"\n\n[truncated at {MAX_MAP_CHARS} of {len(body)} characters; the rest is in {MAP_FILE}]" if verdict == "truncated" else ""
    hook_decisions.log(CHECK_MAP, verdict, "%s :: %d chars" % (MAP_FILE, len(body)), session=session,
                       event="SessionStart", mode="enforce")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext":
                      f"{MAP_FILE}, at the root of this repository, in full:\n\n{body[:MAX_MAP_CHARS]}{note}"}}))


def stands_down(cwd):
    root = repo_root(cwd)
    here = os.path.realpath(__file__)
    try:
        with open(os.path.join(root or "", ".claude", "settings.json")) as fh:
            groups = json.load(fh)["hooks"]["PreToolUse"]
        commands = [h["command"] for g in groups if "Bash" in g.get("matcher", "") and "Read" in g.get("matcher", "")
                    for h in g.get("hooks", []) if isinstance(h.get("command"), str)]
    except Exception:
        return False
    for copy in REPO_COPIES:
        path = os.path.join(root, copy)
        if os.path.realpath(path) != here and any("/" + copy in c for c in commands):
            try:
                with open(path, "rb") as theirs, open(here, "rb") as ours:
                    if theirs.read() == ours.read():
                        return True
            except OSError:
                pass
    return False


def main():
    try:
        payload = json.loads(sys.stdin.read())
    except (ValueError, TypeError):
        return
    if not isinstance(payload, dict):
        return
    cwd = text(payload.get("cwd")) or os.getcwd()
    if stands_down(cwd):
        return
    event = text(payload.get("hook_event_name"))
    session = text(payload.get("session_id")) or "unknown"
    tool = text(payload.get("tool_name")) or ""
    tool_input = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}
    if event == "SessionStart":
        inject_map(cwd, session)
    elif event == "PreToolUse":
        gate(payload, tool, tool_input, cwd, session)
    elif event == "PostToolUse":
        credit(payload, tool, tool_input, cwd, session)


if __name__ == "__main__":
    sys.exit(run("domain-canon", main))
