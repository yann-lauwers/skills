import json
import os
import re
import sys

READ_TOOL = "Read"
BASH_TOOL = "Bash"
GREP_TOOL = "Grep"
GREP_NAME_ONLY_MODES = frozenset(("files_with_matches", "count"))


def coerce_str(value):
    return value if isinstance(value, str) and value else None


def read_payload():
    try:
        payload = json.loads(sys.stdin.read())
    except (ValueError, TypeError):
        return None
    return payload if isinstance(payload, dict) else None


def tool_of(payload):
    return coerce_str(payload.get("tool_name")) or ""


def session_of(payload):
    return coerce_str(payload.get("session_id")) or "unknown"


def cwd_of(payload):
    return coerce_str(payload.get("cwd")) or os.getcwd()


def command_of(payload):
    tool_input = payload.get("tool_input")
    return coerce_str(tool_input.get("command")) if isinstance(tool_input, dict) else None


def target_path(payload):
    tool_input = payload.get("tool_input")
    path = None
    if isinstance(tool_input, dict):
        path = coerce_str(tool_input.get("file_path")) or coerce_str(tool_input.get("notebook_path"))
        if tool_of(payload) == GREP_TOOL:
            path = coerce_str(tool_input.get("path"))
    path = path or coerce_str(payload.get("file_path"))
    if not path:
        return None
    if not os.path.isabs(path):
        cwd = coerce_str(payload.get("cwd"))
        if not cwd:
            return None
        path = os.path.join(cwd, path)
    return os.path.normpath(path)


PATCH_TOOL = "apply_patch"
PATCH_FILE_LINES = ("*** Add File: ", "*** Update File: ", "*** Delete File: ", "*** Move to: ")


def patch_paths(command):
    paths = []
    for line in (command or "").splitlines():
        line = line.strip()
        for head in PATCH_FILE_LINES:
            if line.startswith(head) and line[len(head):].strip():
                paths.append(line[len(head):].strip())
    return paths


LEADING_CD = re.compile(r"""^\s*cd\s+("[^"]*"|'[^']*'|[^\s;&|]+)\s*&&""")


def patch_folder(payload):
    cwd = cwd_of(payload)
    cd = LEADING_CD.match(command_of(payload) or "") if tool_of(payload) == BASH_TOOL else None
    if not cd:
        return cwd
    folder = os.path.expanduser(cd.group(1).strip("\"'"))
    return os.path.normpath(os.path.join(cwd, folder))


def as_edits(payload):
    tool = tool_of(payload)
    command = command_of(payload)
    folder = patch_folder(payload)
    edits = [dict(payload, tool_name="Edit", cwd=folder, tool_input={"file_path": path})
             for path in patch_paths(command)]
    if tool == PATCH_TOOL:
        return edits
    if tool == BASH_TOOL and PATCH_TOOL in (command or ""):
        return [payload] + edits
    return [payload]
