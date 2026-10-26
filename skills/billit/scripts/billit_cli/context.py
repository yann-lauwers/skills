import json
import os
import re
import shutil
import subprocess

from .errors import USAGE, Fail

MISSING = object()


class Context:
    def __init__(self, root, entity, party_id, item, block, register):
        self.root = root
        self.entity = entity
        self.party_id = party_id
        self.item = item
        self.block = block
        self.register = register

    @property
    def env_name(self):
        return re.sub(r"[^A-Za-z0-9]", "_", self.item).upper()


def dotted(obj, path):
    for part in path.split("."):
        if not isinstance(obj, dict) or part not in obj:
            return MISSING
        obj = obj[part]
    return obj


def find_root(rt, given):
    if given:
        return os.path.realpath(given)
    try:
        done = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=rt.cwd, capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, timeout=15)
    except (OSError, subprocess.SubprocessError):
        done = None
    if done is None or done.returncode != 0 or not done.stdout.strip():
        raise Fail(USAGE, "not inside a git repository; pass --root DIR")
    return done.stdout.strip()


def agents_config_path(rt):
    found = shutil.which("agents-config", path=rt.env.get("PATH", ""))
    if found:
        return found
    fallback = os.path.join(rt.home, ".agents", "bin", "agents-config")
    if os.access(fallback, os.X_OK):
        return fallback
    raise Fail(USAGE, "agents-config not found on PATH or in ~/.claude/skills/agents-config/scripts")


def read_register(rt, root):
    tool = agents_config_path(rt)
    done = subprocess.run([tool, "get", "billit", "--root", root], capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, env=rt.env, cwd=root, timeout=60)
    if done.returncode != 0:
        raise Fail(USAGE, "agents-config get billit failed: %s" % (done.stderr.strip() or done.returncode))
    try:
        register = json.loads(done.stdout)["defaults"]["register"]
    except (ValueError, KeyError, TypeError):
        raise Fail(USAGE, "agents-config get billit carries no defaults.register")
    for key in ("index", "block"):
        if not isinstance(register, dict) or not register.get(key):
            raise Fail(USAGE, "billit config sets no register.%s" % key)
    return register


def read_json(path, what):
    try:
        with open(path) as handle:
            return json.load(handle)
    except (OSError, ValueError) as error:
        raise Fail(USAGE, "cannot read %s %s: %s" % (what, path, error))


def resolve(rt, root_arg, entity_arg):
    root = find_root(rt, root_arg)
    register = read_register(rt, root)
    index_path = os.path.join(root, register["index"])
    index = read_json(index_path, "entity index")
    known = sorted(index.get("entities", {}))
    entity = entity_arg or index.get("default")
    if entity not in known:
        raise Fail(USAGE, "unknown entity %r; known: %s" % (entity, " ".join(known)))
    entity_file = os.path.join(os.path.dirname(index_path), index["entities"][entity]["path"])
    block = dotted(read_json(entity_file, "entity file"), register["block"])
    if block is MISSING or not isinstance(block, dict):
        raise Fail(USAGE, "entity %s has no %s block" % (entity, register["block"]))
    if not block.get("party_id"):
        raise Fail(USAGE, "entity %s: %s carries no party_id" % (entity, register["block"]))
    item = block.get("secret") or "%s-billit" % entity
    return Context(root, entity, block["party_id"], item, block, register)


def api_key(rt, ctx, argv):
    wrapped = rt.env.get("BILLIT_KEY_ITEM") == ctx.item
    key = rt.env.get("BILLIT_API_KEY")
    if wrapped and key:
        return key
    if wrapped:
        return None
    command = ["keyless", "run", "-s", "BILLIT_API_KEY=%s" % ctx.env_name, "--", "env",
               "BILLIT_KEY_ITEM=%s" % ctx.item, rt.entry, *argv]
    try:
        rt.execvp("keyless", command)
    except OSError:
        raise Fail(USAGE, "keyless not found on PATH; it injects the Billit key")
    return None
