import hashlib
import os

from domain_canon.parse_event import coerce_str

STATE_DIR = os.environ.get("CANON_STATE_DIR") or os.path.expanduser("~/.claude/state/domain-canon")


def key_of(payload):
    key = coerce_str(payload.get("agent_id")) or coerce_str(payload.get("session_id")) or "nosession"
    return None if ("/" in key or ".." in key) else key


def _path(key):
    os.makedirs(STATE_DIR, exist_ok=True)
    return os.path.join(STATE_DIR, key + ".txt")


def facts(key):
    found = set()
    try:
        with open(_path(key)) as fh:
            for line in fh:
                kind, _, rel = line.strip().partition(" ")
                if kind and rel:
                    found.add((kind, rel))
    except OSError:
        pass
    return found


def record(key, kind, fact):
    try:
        with open(_path(key), "a") as fh:
            fh.write("%s %s\n" % (kind, fact))
    except OSError:
        pass


def canon_fact(root, rel):
    return "%s:%s" % (hashlib.sha1(os.fsencode(root)).hexdigest()[:12], rel)


def unread(key_facts, root, canon):
    return [c for c in canon if ("read", canon_fact(root, c)) not in key_facts]
