#!/usr/bin/env python3
import os
import re
import subprocess

STANDALONE = re.compile(r"<!doctype\s+html|<html[\s>]", re.I)
TITLED = re.compile(r"<title[^>]*>|<h1[\s>]", re.I)
HTML_SUFFIX = (".html", ".htm")
EPHEMERAL_PREFIXES = ("/private/tmp/", "/tmp/", "/var/folders/", "/private/var/folders/")
READ_CAP = 400_000


def in_repo(path):
    d = os.path.dirname(os.path.abspath(path)) or "/"
    while not os.path.isdir(d):
        parent = os.path.dirname(d)
        if parent == d:
            return False
        d = parent
    try:
        out = subprocess.run(["git", "-C", d, "rev-parse", "--is-inside-work-tree"],
                             capture_output=True, text=True, timeout=5)
        return out.returncode == 0 and out.stdout.strip() == "true"
    except Exception:
        return False


def ephemeral(path):
    return os.path.realpath(path).startswith(EPHEMERAL_PREFIXES)


def homeless(path):
    return ephemeral(path) or not in_repo(path)


def page_text(tool, tool_input, path):
    if tool == "Write":
        content = tool_input.get("content")
        return content if isinstance(content, str) else ""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read(READ_CAP)
    except Exception:
        return ""
    old, new = tool_input.get("old_string"), tool_input.get("new_string")
    if isinstance(old, str) and isinstance(new, str):
        text = text.replace(old, new, -1 if tool_input.get("replace_all") else 1)
    return text


def is_page(text):
    return bool(STANDALONE.search(text) and TITLED.search(text))


def authored(payload):
    if not isinstance(payload, dict) or payload.get("tool_name") not in ("Write", "Edit"):
        return None
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    path = tool_input.get("file_path")
    if not isinstance(path, str) or not path.lower().endswith(HTML_SUFFIX):
        return None
    path = os.path.expanduser(path)
    text = page_text(payload["tool_name"], tool_input, path)
    if not is_page(text) or not homeless(path):
        return None
    return path, text
