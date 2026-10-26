#!/usr/bin/env python3
"""The files that decide permissions, as they appear in command text.

`auto-allow-bash.sh` withholds a grant from a command that names one of the files;
`permission-request.py` withholds it from a command whose text writes to one.
"""
import re

# The basenames as they appear in command text. `settings.json` is NOT written bare:
# every project has one, and matching those would fire on ordinary repo work — the
# same reason the shell guard qualifies it with `.claude/`.
NAME_RE = re.compile(
    r"(\.claude/settings(\.local)?\.json"
    r"|(^|[^A-Za-z0-9_.-])auto-allow-bash\.sh"
    r"|(^|[^A-Za-z0-9_.-])permission-request\.py)")

WRITE_SHAPE_RE = re.compile(
    r"(>>?\s*[^\s|;&]*"
    r"|(^|[;&|(){}]|\s(do|then|else)\s)\s*(sed\s+-i|tee|mv|cp|rm|chmod|install|perl\s+-i)\s+[^;|&]*)"
    + NAME_RE.pattern, re.M)


def writes_permission_file(command):
    return WRITE_SHAPE_RE.search(command) is not None
