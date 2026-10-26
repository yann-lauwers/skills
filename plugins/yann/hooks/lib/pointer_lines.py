import os
import re
import subprocess

from git_reads import GIT_TIMEOUT

LINE_LIMIT_BYTES = 1_000_000
BINARY_SNIFF_BYTES = 8000


def blob_contents(top, specs):
    out = {s: None for s in specs}
    specs = [s for s in specs if "\n" not in s]
    if not specs:
        return out
    try:
        sizes = subprocess.run(("git", "-C", top, "cat-file", "--batch-check"), input="\n".join(specs) + "\n",
                               capture_output=True, text=True, timeout=GIT_TIMEOUT).stdout.splitlines()
        small = [s for s, row in zip(specs, sizes)
                 if len(row.split()) == 3 and row.split()[1] == "blob" and int(row.split()[2]) <= LINE_LIMIT_BYTES]
        if not small:
            return out
        body = subprocess.run(("git", "-C", top, "cat-file", "--batch"), input=("\n".join(small) + "\n").encode(),
                              capture_output=True, timeout=GIT_TIMEOUT).stdout
        at = 0
        for s in small:
            end = body.index(b"\n", at)
            size = int(body[at:end].split()[2])
            out[s] = body[end + 1:end + 1 + size]
            at = end + 1 + size + 1
    except Exception:
        return {s: None for s in out}
    return out


def as_text(raw):
    return None if raw is None or b"\0" in raw[:BINARY_SNIFF_BYTES] else raw.decode("utf-8", "replace")


def matching_lines(text, rule):
    return {l.strip() for l in text.splitlines() if re.search(rule.pattern, l)}


def worktree_bytes(top, path):
    full = os.path.join(top, path)
    try:
        if os.path.islink(full) or os.path.getsize(full) > LINE_LIMIT_BYTES:
            return None
        with open(full, "rb") as fh:
            return fh.read()
    except OSError:
        return None


def added_pointers(top, rule, paths, from_worktree, in_head, in_merge):
    in_index = blob_contents(top, [":" + p for p in paths if p not in from_worktree])
    found = {}
    for p in paths:
        raw = worktree_bytes(top, p) if p in from_worktree else in_index.get(":" + p)
        text = as_text(raw)
        if text is not None and matching_lines(text, rule):
            found[p] = (text, matching_lines(text, rule))
    if not found:
        return {}

    def earlier_copies(p):
        return (["HEAD:" + p] if p in in_head else []) \
            + (["MERGE_HEAD:" + p] if rule.merge_exempt and p in in_merge else [])

    before = blob_contents(top, [spec for p in found for spec in earlier_copies(p)])
    added = {}
    for p, (text, now) in sorted(found.items()):
        copies = [as_text(before.get(spec)) for spec in earlier_copies(p)]
        if None in copies:
            continue
        kept = set().union(*(matching_lines(c, rule) for c in copies))
        if now <= kept:
            continue
        added[p] = [n for n, l in enumerate(text.splitlines(), 1)
                    if re.search(rule.pattern, l) and l.strip() not in kept]
    return added
