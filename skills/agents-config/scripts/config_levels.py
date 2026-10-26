#!/usr/bin/env python3
import hashlib
import os
import re
import subprocess
import sys
import unicodedata
from typing import Dict, NamedTuple, Optional

HOME = os.path.expanduser("~")
FLOOR_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "integrations")
PROJECT_PARTS = ("docs", "agents", "integrations")
FOREIGN_EXIT = 4
MAX_LINK_HOPS = 40
ROLE_HEAD_LINES = 12
REPO_LOCATION_ENV = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR", "GIT_CEILING_DIRECTORIES",
                     "GIT_DISCOVERY_ACROSS_FILESYSTEM")
ONLY_DOT_GIT_REPOSITORIES = ("-c", "safe.bareRepository=explicit")
OUTSIDE_ANY_REPOSITORY = ("not a git repository",)
OUTSIDE_ANY_WORK_TREE = OUTSIDE_ANY_REPOSITORY + ("must be run in a work tree", "cannot use bare repository")
TRACKED = "tracked by git, authored by this repo's committers"
COMMITTED = "untracked, but its bytes are what %s held in commit %s, authored by this repo's committers"
UNKNOWN_TRACKING = "is tracked"
UNKNOWN_HISTORY = "holds bytes a commit put at its path"
HISTORY_TIMEOUT = 10
NULL_BLOB = frozenset(("0" * 40, "0" * 64))
COMMITTERS_DECIDE = ("Its content came from the repository's committers: Yann reviews it and decides what happens "
                     "to it, and an agent never untracks, deletes or rewrites it to get past this refusal.")


class Local(NamedTuple):
    path: str


class Tracked(NamedTuple):
    repo: str
    entry: str

    @property
    def path(self):
        return os.path.join(self.repo, self.entry)


class Committed(NamedTuple):
    repo: str
    entry: str
    commit: str
    path: str


class Foreign(Exception):
    def __init__(self, path, reason, source=None, unknown=UNKNOWN_TRACKING):
        super().__init__(path, reason, source, unknown)
        self.path, self.reason, self.source, self.unknown = path, reason, source, unknown


class Project(NamedTuple):
    dir: Optional[str]
    configs: Dict[str, object]


class GitUnreadable(Exception):
    pass


def _git(cwd, *args, absent=OUTSIDE_ANY_REPOSITORY, timeout=None):
    env = {k: v for k, v in os.environ.items() if k not in REPO_LOCATION_ENV}
    env["LC_ALL"] = "C"
    try:
        r = subprocess.run(["git", *ONLY_DOT_GIT_REPOSITORIES, "-C", cwd, *args], capture_output=True,
                           encoding="utf-8", errors="surrogateescape", env=env, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise GitUnreadable("`git -C %s %s` did not answer within %ds" % (cwd, args[0], timeout))
    except OSError as e:
        raise GitUnreadable("git did not run: %s" % e)
    if r.returncode == 0:
        return r.stdout
    if any(s in r.stderr for s in absent):
        return None
    raise GitUnreadable("`git -C %s %s` exited %d: %s" % (
        cwd, args[0], r.returncode, r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "no message"))


def _toplevel(root):
    if not os.path.isdir(root):
        return None
    try:
        out = _git(root, "rev-parse", "--show-toplevel", absent=OUTSIDE_ANY_WORK_TREE)
    except GitUnreadable as e:
        raise Foreign(root, str(e))
    return out.strip() if out else None


def _chain(start, parts):
    entries, cur, pending, hops = [], start, list(parts), 0
    while pending:
        part = pending.pop(0)
        if part in ("", "."):
            continue
        if part == "..":
            cur = os.path.dirname(cur)
            continue
        nxt = os.path.join(cur, part)
        if not os.path.islink(nxt):
            cur = nxt
            continue
        hops += 1
        if hops > MAX_LINK_HOPS:
            raise GitUnreadable("%s is more than %d symlinks deep" % (nxt, MAX_LINK_HOPS))
        entries.append(nxt)
        target = os.readlink(nxt)
        if os.path.isabs(target):
            cur = os.sep
        pending = target.split(os.sep) + pending
    entries.append(cur)
    return entries


def _identity(path):
    try:
        st = os.lstat(path)
    except OSError:
        return None
    return st.st_dev, st.st_ino


def _own_repo():
    try:
        out = _git(os.path.dirname(os.path.realpath(__file__)), "rev-parse", "--show-toplevel")
    except GitUnreadable:
        return None
    return _identity(out.rstrip("\n")) if out else None


OWN_REPO = _own_repo()


def _containing_repos(d):
    tops, seen, cur = [], [], d
    while True:
        out = _git(cur, "rev-parse", "--show-toplevel")
        if out is None:
            return tops
        top = out.rstrip("\n")
        if top in seen:
            return tops
        seen.append(top)
        if OWN_REPO is None or _identity(top) != OWN_REPO:
            tops.append(top)
        if os.path.dirname(top) == top:
            return tops
        cur = os.path.dirname(top)


def _index_by_dir(repo):
    out = _git(repo, "ls-files", "-z")
    dirs, by_dir = {}, {}
    for entry in (out or "").split("\0"):
        if not entry:
            continue
        parent = os.path.dirname(entry)
        if parent not in dirs:
            dirs[parent] = _identity(os.path.join(repo, parent))
        by_dir.setdefault(dirs[parent], []).append(Tracked(repo, entry))
    return by_dir


def _tracked(entries):
    by_dir = {}
    for e in entries:
        by_dir.setdefault(os.path.dirname(e), set()).add(e)
    indexes, found, errors, repos_by_dir = {}, {}, {}, {}
    for d, here in sorted(by_dir.items()):
        try:
            repos = _containing_repos(d)
            for repo in repos:
                if repo not in indexes:
                    indexes[repo] = _index_by_dir(repo)
        except GitUnreadable as e:
            errors[d] = str(e)
            continue
        repos_by_dir[d] = repos
        wanted = {_identity(e): e for e in sorted(here)}
        wanted.pop(None, None)
        here_id = _identity(d)
        if here_id is None:
            continue
        for repo in repos:
            for t in indexes[repo].get(here_id, ()):
                e = wanted.get(_identity(t.path))
                if e is not None:
                    found.setdefault(e, t)
    return found, errors, repos_by_dir


def _held_name(parent, name):
    try:
        names = os.listdir(parent)
    except OSError:
        return name
    if name in names:
        return name
    want = _identity(os.path.join(parent, name))
    return next((n for n in sorted(names) if _identity(os.path.join(parent, n)) == want), name)


def _spellings(path, repo):
    top, asked, held, cur = _identity(repo), [], [], path
    while _identity(cur) != top:
        parent = os.path.dirname(cur)
        if parent == cur:
            return ()
        name = os.path.basename(cur)
        asked.insert(0, name)
        held.insert(0, _held_name(parent, name))
        cur = parent
    return tuple(dict.fromkeys(("/".join(asked), "/".join(held))))


def _blob_ids(data):
    framed = b"blob %d\0" % len(data) + data
    return {hashlib.sha1(framed).hexdigest(), hashlib.sha256(framed).hexdigest()}


def _working_blobs(repo, wanted):
    blobs, files = {}, []
    for e, spellings in wanted:
        try:
            if os.path.islink(e):
                blobs[e] = _blob_ids(os.readlink(os.fsencode(e)))
                continue
            with open(e, "rb") as fh:
                blobs[e] = _blob_ids(fh.read())
        except OSError as err:
            raise GitUnreadable("%s could not be read to hash it: %s" % (_shown(e), err.strerror))
        files.append((e, spellings[0]))
    if files:
        out = _git(repo, "hash-object", "--", *(rel for _, rel in files), absent=(), timeout=HISTORY_TIMEOUT)
        ids = out.split()
        if len(ids) != len(files):
            raise GitUnreadable("`git -C %s hash-object` answered %d ids for %d files" % (repo, len(ids), len(files)))
        for (e, _), blob in zip(files, ids):
            blobs[e].add(blob)
    return blobs


def _history(repo, wanted):
    blobs = _working_blobs(repo, wanted)
    specs = sorted({":(icase,literal)" + s for _, spellings in wanted for s in spellings})
    out = _git(repo, "log", "-m", "--all", "--format=%H", "--raw", "--no-abbrev", "--no-renames", "-z",
               "--", *specs, absent=(), timeout=HISTORY_TIMEOUT)
    identities = {e: _identity(e) for e, _ in wanted}
    tokens, held, commit, i = out.split("\0"), {}, None, 0
    while i < len(tokens):
        token = tokens[i].lstrip("\n")
        i += 1
        if not token.startswith(":"):
            commit = token or commit
            continue
        entry = tokens[i] if i < len(tokens) else ""
        i += 1
        ids = set(token.split()[2:4]) - NULL_BLOB
        here = _identity(os.path.join(repo, entry))
        for e, _ in wanted:
            if e not in held and ids & blobs[e] and here is not None and here == identities[e]:
                held[e] = Committed(repo, entry, commit, e)
    return held


def _committed(entries, repos_by_dir):
    by_repo = {}
    for e in sorted(entries):
        for repo in repos_by_dir.get(os.path.dirname(e), ()):
            spellings = _spellings(e, repo)
            if spellings:
                by_repo.setdefault(repo, []).append((e, spellings))
    found, errors = {}, {}
    for repo, wanted in sorted(by_repo.items()):
        try:
            held = _history(repo, wanted)
        except GitUnreadable as err:
            for e, _ in wanted:
                errors.setdefault(e, str(err))
            continue
        for e, hit in held.items():
            found.setdefault(e, hit)
    return found, errors


def project(root, floor_only=False):
    if floor_only:
        return Project(None, {})
    top = _toplevel(root)
    if top is None:
        return Project(None, {})
    pdir = os.path.join(top, *PROJECT_PARTS)
    try:
        names = sorted(f for f in os.listdir(pdir) if f.endswith(".md"))
    except OSError:
        return Project(pdir, {})
    configs, chains = {}, {}
    for name in names:
        tool, path = name[:-3], os.path.join(pdir, name)
        if not os.path.isfile(path):
            continue
        try:
            chains[tool] = (path, _chain(top, PROJECT_PARTS + (name,)))
        except GitUnreadable as e:
            configs[tool] = Foreign(path, str(e))
    found, errors, repos_by_dir = _tracked({e for _, chain in chains.values() for e in chain})
    untracked = {}
    for tool, (path, chain) in chains.items():
        hit = next((found[e] for e in chain if e in found), None)
        err = next((errors[os.path.dirname(e)] for e in chain if os.path.dirname(e) in errors), None)
        if hit:
            configs[tool] = Foreign(path, TRACKED, hit)
        elif err:
            configs[tool] = Foreign(path, err)
        else:
            untracked[tool] = (path, chain)
    held, faults = _committed({e for _, chain in untracked.values() for e in chain}, repos_by_dir)
    for tool, (path, chain) in untracked.items():
        hit = next((held[e] for e in chain if e in held), None)
        fault = next((faults[e] for e in chain if e in faults), None)
        if hit:
            configs[tool] = Foreign(path, COMMITTED % (_shown(hit.entry), hit.commit[:12]), hit)
        elif fault:
            configs[tool] = Foreign(path, fault, unknown=UNKNOWN_HISTORY)
        else:
            configs[tool] = Local(path)
    return Project(pdir, dict(sorted(configs.items())))


def declares(path, role):
    try:
        with open(path, encoding="utf-8") as fh:
            head = [next(fh, "") for _ in range(ROLE_HEAD_LINES)]
    except OSError:
        return False
    return any(re.match(r"^role:\s*%s\s*$" % re.escape(role), line) for line in head)


def floor_tools():
    if not os.path.isdir(FLOOR_DIR):
        return []
    return [f[:-3] for f in sorted(os.listdir(FLOOR_DIR))
            if f.endswith(".md") and os.path.isfile(os.path.join(FLOOR_DIR, f))]


class RoleUnresolved(Exception):
    def __init__(self, level, hits):
        super().__init__(level, hits)
        self.level, self.hits = level, hits


def pick_role(role, configs):
    level, hits = "project", sorted(t for t, c in configs.items() if declares(c.path, role))
    for t in hits:
        if isinstance(configs[t], Foreign):
            raise configs[t]
    if not hits:
        level, hits = "floor", sorted(t for t in floor_tools()
                                      if declares(os.path.join(FLOOR_DIR, t + ".md"), role))
    if len(hits) != 1:
        raise RoleUnresolved(level, hits)
    return hits[0]


def _unprintable(text):
    return any(unicodedata.category(c).startswith("C") for c in text)


def _shown(path):
    return ascii(path) if _unprintable(path) else path


def refusal(verb, foreign):
    lead = "agents-config %s: refused, nothing printed — " % verb
    if foreign.source is None:
        return lead + "git could not say whether %s %s: %s." % (
            _shown(foreign.path), foreign.unknown, foreign.reason)
    source = foreign.source
    via = "" if source.path == foreign.path else " resolves through %s, which" % _shown(source.path)
    return lead + "%s%s is %s, so it does not steer a secret, a host or an identity here. %s" % (
        _shown(foreign.path), via, foreign.reason, COMMITTERS_DECIDE)


def refuse(verb, foreign):
    print(refusal(verb, foreign), file=sys.stderr)
    sys.exit(FOREIGN_EXIT)


def resolve(opts):
    tool = opts["key"]
    lines = ["explicit=%s" % (opts["explicit"] or "<none>")]
    foreign = None
    try:
        level = project(opts["root"] or os.getcwd(), opts["floor_only"])
    except Foreign as f:
        level, foreign = None, f
    if foreign:
        lines.append("project=%s foreign" % foreign.path)
    elif opts["floor_only"]:
        lines.append("project=<none> floor-only")
    elif level.dir is None:
        lines.append("project=<none> no-project")
    else:
        found = level.configs.get(tool)
        if isinstance(found, Foreign):
            foreign = found
        state = "foreign" if foreign else "present" if found else "absent"
        lines.append("project=%s %s" % (os.path.join(level.dir, tool + ".md"), state))
    if foreign:
        refuse("resolve", foreign)
    floor = os.path.join(FLOOR_DIR, tool + ".md")
    lines.append("floor=%s %s" % (floor, "present" if os.path.isfile(floor) else "absent"))
    lines.append("tool=%s" % tool)
    print("\n".join(lines))
    return 0


def role(opts):
    wanted = opts["key"]
    try:
        level = project(opts["root"] or os.getcwd(), opts["floor_only"])
    except Foreign as f:
        refuse("role", f)
    proj = [c for c in level.configs.values() if declares(c.path, wanted)]
    for c in proj:
        if isinstance(c, Foreign):
            refuse("role", c)
    lines = ["project=" + c.path for c in proj]
    lines += ["floor=" + f for f in (os.path.join(FLOOR_DIR, t + ".md") for t in floor_tools()) if declares(f, wanted)]
    if not lines:
        print("role=%s NONE" % wanted, file=sys.stderr)
        return 1
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import agents_config
    sys.exit(agents_config.main(sys.argv[1:]))
