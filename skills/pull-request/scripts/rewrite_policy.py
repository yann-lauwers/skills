"""Whether a branch may be rewritten, and which pull requests merged into it, read from the forge."""
import fnmatch
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pr_policy import ALLOW, REFUSE, UNKNOWN, CONFIG_REFUSED, GIT_TIMEOUT, Verdict, _git, project_config, project_config_refusal


# ── rewriting an integration base ────────────────────────────────────────────

# The answer `merged_into` and `forge_repo` give when the remote is not on a forge
# this module can read: no opinion, and no call is made. Compared by identity.
NO_FORGE = type("NoForge", (), {"__repr__": lambda self: "NO_FORGE",
                                "__bool__": lambda self: False})()
GH_TIMEOUT = 10
SSH_TIMEOUT = 5
GITHUB_HOSTS = frozenset(("github.com", "ssh.github.com"))
MERGED_INTO_QUERY = ("query($o:String!,$n:String!,$b:String!){repository(owner:$o,name:$n)"
                     "{pullRequests(baseRefName:$b,states:MERGED,first:1){totalCount}}}")

# A branch name this verb will judge: one git could have created. `HEAD`, `@`, a full
# ref, a revision expression (`~`, `^`, `:`, `@{`), whitespace or an empty string
# name a commit or a ref of another kind, never a branch a rewrite targets.
_NOT_A_BRANCH = re.compile(r"[~^:\s]|@\{|^@$|^HEAD$|^refs/|^$|^-")


def _run(cmd, timeout, env=None, cwd=None):
    """(exit code, stdout) of one bounded subprocess; (None, "") when it could not run
    or did not answer in time. Its whole process group is killed on the timeout, so a
    stub or a helper that spawned a child cannot hold the pipe open past the bound."""
    try:
        proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, start_new_session=True)
    except Exception:
        return None, ""
    try:
        out, _err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, 9)
        except Exception:
            pass
        try:
            proc.communicate(timeout=5)
        except Exception:
            pass
        return None, ""
    return proc.returncode, out or ""


def _base_root(path):
    if not path or not os.path.isdir(path):
        return None
    common = _git(path, "rev-parse", "--path-format=absolute", "--git-common-dir")
    return os.path.dirname(os.path.realpath(common)) if common else None


def _declared(path):
    """Branch globs the repo at `path` declares as integration bases, or None.

    Private: the one parser of the `integration_bases` key. Read from the BASE
    checkout's `docs/agents/integrations/git.md` — the common git dir's parent — so
    a linked worktree answers from the file its base holds. Inline (`[a/*, b]`) or a
    block list; a missing file, missing key or empty list is None.
    """
    base = _base_root(path)
    if not base:
        return None
    cfg = project_config(base)
    try:
        with open(cfg) as fh:
            text = fh.read()
    except Exception:
        return None
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return None
    lines = m.group(1).splitlines()
    for i, line in enumerate(lines):
        found = re.match(r"^\s*integration_bases:\s*(.*)$", line)
        if not found:
            continue
        rest = found.group(1).strip()
        if rest.startswith("["):
            items = [x.strip().strip("'\"") for x in rest.strip("[]").split(",")]
            return [x for x in items if x] or None
        items = []
        for nxt in lines[i + 1:]:
            b = re.match(r"^\s*-\s*(.+?)\s*$", nxt)
            if not b:
                break
            items.append(b.group(1).strip("'\""))
        return items or None
    return None


def declared_bases(path):
    return _declared(path) or []


def push_remote(path, branch):
    """The remote a bare `git push` of `branch` goes to, per `git help config`:
    `branch.<b>.pushRemote`, then `remote.pushDefault`, then `branch.<b>.remote`,
    then `origin`."""
    for key in ("branch.%s.pushRemote" % branch, "remote.pushDefault",
                "branch.%s.remote" % branch):
        value = _git(path, "config", "--get", key) if path and branch else None
        if value:
            return value
    return "origin"


def _url_parts(url):
    """(host, path) of a remote URL — `scheme://`, or scp-like `[user@]host:path` —
    or None for a local path or anything else."""
    m = re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://(?:[^@/]*@)?([^/:]+)(?::\d+)?/(.*)$", url)
    if m:
        return m.group(1).lower(), m.group(2)
    if "://" in url or url.startswith(("/", ".", "~")) or url.startswith("file:"):
        return None
    m = re.match(r"^(?:[^@/]*@)?([^:/]+):(.*)$", url)
    if m:
        return m.group(1).lower(), m.group(2)
    return None


def _ssh_hostname(alias):
    """The host an ssh alias reaches, from `ssh -G`'s `hostname` line; None unread."""
    code, out = _run(["ssh", "-G", alias], SSH_TIMEOUT)
    if code != 0:
        return None
    for line in out.splitlines():
        key, _, value = line.partition(" ")
        if key.strip().lower() == "hostname" and value.strip():
            return value.strip().lower()
    return None


def forge_repo(path, remote):
    """(owner, name) of the github.com repository `remote` reaches from `path`, NO_FORGE
    when it reaches no repository this module can read, None when that could not be
    established.

    `remote` is a remote name — read through `git remote get-url --push`, so `pushurl`
    and `insteadOf` rewrites apply — or a URL taken as it is. The host is github.com or
    ssh.github.com, case-insensitive, in `https://`, `ssh://` or scp-like form with or
    without `.git`; an scp-like or `ssh://` host that is neither is an ssh alias until
    `ssh -G` says what it reaches.
    """
    if not isinstance(remote, str) or not remote:
        return NO_FORGE
    url = None
    if path and os.path.isdir(path):
        code, out = _run(["git", "-C", path, "remote", "get-url", "--push", remote], GIT_TIMEOUT)
        if code is None:
            return None
        if code == 0 and out.strip():
            url = out.strip().splitlines()[0]
    if url is None:
        url = remote
    parts = _url_parts(url)
    if parts is None:
        return NO_FORGE
    host, rest = parts
    if host not in GITHUB_HOSTS:
        if "://" in url and not url.lower().startswith("ssh://"):
            return NO_FORGE
        resolved = _ssh_hostname(host)
        if resolved is None:
            return None
        if resolved not in GITHUB_HOSTS:
            return NO_FORGE
    segments = [s for s in rest.split("/") if s]
    if len(segments) < 2:
        return NO_FORGE
    owner, name = segments[0], segments[1]
    if name.endswith(".git"):
        name = name[:-4]
    if not owner or not name:
        return NO_FORGE
    return owner, name


def merged_into(path, branch, remote=None, forge=None):
    """Has any pull request merged INTO `branch` on the forge the rewrite targets?

    True / False from the forge's own count of merged pull requests whose base is the
    branch — exact whatever the merge method, and read by name so a stale checkout or
    an unheld remote ref changes nothing. NO_FORGE when the remote is not on github.com
    (no call is made); None when the read failed: `gh` missing, unauthenticated, a
    non-zero exit, a timeout at GH_TIMEOUT, or an answer with no integer `totalCount`.

    `forge` names the repository as (owner, name) and is used as-is; otherwise it is
    `forge_repo(path, remote or push_remote(path, branch))`. Fields go through `-f`,
    never `-F`: a branch named `1234` has to reach the query as a string.
    """
    if forge is None:
        forge = forge_repo(path, remote or push_remote(path, branch))
    if forge is NO_FORGE:
        return NO_FORGE
    if not (isinstance(forge, tuple) and len(forge) == 2):
        return None
    owner, name = forge
    cmd = ["gh", "api", "graphql", "-f", "query=" + MERGED_INTO_QUERY,
           "-f", "o=%s" % owner, "-f", "n=%s" % name, "-f", "b=%s" % branch]
    code, out = _run(cmd, GH_TIMEOUT, env=dict(os.environ, GH_PAGER="cat"))
    if code != 0:
        return None
    try:
        count = json.loads(out)["data"]["repository"]["pullRequests"]["totalCount"]
    except Exception:
        return None
    if isinstance(count, bool) or not isinstance(count, int):
        return None
    return count > 0


def may_rewrite(path, branch, *, remote=None, forge=None, observe=None):
    """Decision verb: may `branch` in the checkout at `path` be rebased or force-pushed?

    In order:
      1. `path` is not a directory inside a git work tree  -> unknown  `no checkout`
      2. `branch` is not a plain branch name               -> unknown  `branch unread`
      3. the base checkout's git.md is refused by the gate -> unknown  `config refused`
      4. a declared `integration_bases` glob matches       -> refuse   `declared: <glob>`
         (no I/O past the config read)
      5. `merged_into(path, branch, remote, forge)`:
           NO_FORGE                                        -> allow    `no-forge`
           True                                            -> refuse   `merged-into`
           False                                           -> allow    `clear`
           None, or a raise                                -> unknown  `forge unread`

    Every allow's reason is exactly `clear` or `no-forge`. `observe(path, branch,
    remote, forge)` exists for tests and stands in for `merged_into`; None means the
    real read. Never raises.
    """
    try:
        if not isinstance(path, str) or not path or not os.path.isdir(path):
            return Verdict(UNKNOWN, "no checkout")
        if _git(path, "rev-parse", "--is-inside-work-tree") != "true":
            return Verdict(UNKNOWN, "no checkout")
        if not isinstance(branch, str) or _NOT_A_BRANCH.search(branch):
            return Verdict(UNKNOWN, "branch unread")
        if project_config_refusal(_base_root(path)):
            return Verdict(UNKNOWN, CONFIG_REFUSED)
        for glob in _declared(path) or ():
            if fnmatch.fnmatchcase(branch, glob):
                return Verdict(REFUSE, "declared: %s" % glob)
        reader = merged_into if observe is None else observe
        try:
            seen = reader(path, branch, remote, forge)
        except Exception:
            seen = None
        if seen is NO_FORGE:
            return Verdict(ALLOW, "no-forge")
        if seen is None:
            return Verdict(UNKNOWN, "forge unread")
        if seen:
            return Verdict(REFUSE, "merged-into")
        return Verdict(ALLOW, "clear")
    except Exception as exc:
        return Verdict(UNKNOWN, "rule raised: %s" % type(exc).__name__)


# ── CLI ──────────────────────────────────────────────────────────────────────
