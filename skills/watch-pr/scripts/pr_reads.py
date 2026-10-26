"""Every read the pull-request watcher makes: GitHub through `gh api`, git through the
local checkout. Reads are uncached; `Reader.read` answers the facts `pr_classify.classify`
takes. `gh` owns auth: no token is read, printed or passed.
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path

from pr_classify import now_utc, parse_iso

GH_TIMEOUT = 60.0

_POLICY_PATHS = [
    Path(__file__).resolve().parents[2] / "pull-request" / "scripts" / "rewrite_policy.py",
    Path.home() / ".claude" / "skills" / "pull-request" / "scripts" / "rewrite_policy.py",
]
_policy_module = None
_policy_loaded = False


class GhError(Exception):
    """A gh invocation that produced no usable answer: transport, a gateway page, a bad body."""


class GhMissing(Exception):
    pass


class Auth(Exception):
    pass


class RateLimited(Exception):
    def __init__(self, retry_after: float):
        super().__init__(f"rate limited, retry after {retry_after:.0f}s")
        self.retry_after = retry_after


class NotFound(Exception):
    pass


def pr_policy():
    """The rewrite rule's module, loaded once per process, or None. Absent or unloadable,
    every conflict routes to the merge, which is wrong only in being more careful."""
    global _policy_module, _policy_loaded
    if _policy_loaded:
        return _policy_module
    _policy_loaded = True
    for path in _POLICY_PATHS:
        if not path.exists():
            continue
        try:
            spec = importlib.util.spec_from_file_location("rewrite_policy", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except BaseException:
            continue
        if all(hasattr(module, n) for n in ("may_rewrite", "merged_into", "forge_repo")):
            _policy_module = module
            break
    return _policy_module


def _gh(cmd: list[str], what: str) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=GH_TIMEOUT)
    except FileNotFoundError:
        raise GhMissing("gh is not installed or not on PATH")
    except subprocess.TimeoutExpired:
        raise GhError(f"{what} exceeded {GH_TIMEOUT:.0f}s")


def gh_api(path: str):
    """GET through `gh api -i`. Returns the decoded body.

    `gh` exits 1 on a bodyless status, so the status line is parsed from stdout and the exit
    code is read only when no status line exists (a transport-level failure).
    """
    proc = _gh(["gh", "api", "-i", "-H", "Accept: application/vnd.github+json", path], f"gh api {path}")
    head, _, body = proc.stdout.partition("\n\n")
    if "\r\n\r\n" in proc.stdout:
        head, _, body = proc.stdout.partition("\r\n\r\n")
    m = re.match(r"HTTP/[\d.]+ (\d{3})", head)
    if not m:
        err = (proc.stderr or proc.stdout).strip()
        if "gh auth login" in err:
            raise Auth(err[:300])
        raise GhError(err[:300] or f"exit {proc.returncode}")
    status = int(m.group(1))
    headers = {}
    for line in head.splitlines()[1:]:
        k, _, v = line.partition(":")
        headers[k.strip().lower()] = v.strip()
    if status == 401:
        raise Auth(f"HTTP 401 on {path}")
    if status in (403, 429):
        ra = headers.get("retry-after")
        reset = headers.get("x-ratelimit-reset")
        if ra:
            wait = float(ra)
        elif headers.get("x-ratelimit-remaining") == "0" and reset:
            wait = max(60.0, float(reset) - time.time())
        else:
            wait = 60.0
        raise RateLimited(wait)
    if status == 404:
        raise NotFound(path)
    try:
        data = json.loads(body) if body.strip() else None
    except ValueError:
        raise GhError(f"HTTP {status} on {path} with a body that is not JSON: {body.strip()[:120]}")
    if status >= 400:
        raise GhError(f"HTTP {status} on {path}: {json.dumps(data)[:200]}")
    return data


def gh_graphql(query: str, **vars) -> dict:
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for k, v in vars.items():
        cmd += (["-F", f"{k}={v}"] if isinstance(v, int) else ["-f", f"{k}={v}"])
    proc = _gh(cmd, "gh api graphql")
    if proc.returncode != 0 and not proc.stdout.strip():
        err = proc.stderr.strip()
        if "HTTP 401" in err or "gh auth login" in err:
            raise Auth(err[:300])
        if "rate limit" in err.lower():
            raise RateLimited(60.0)
        raise GhError(err[:300])
    try:
        data = json.loads(proc.stdout)
    except ValueError:
        raise GhError(f"graphql answered a body that is not JSON: "
                      f"{(proc.stdout.strip() or proc.stderr.strip())[:120]}")
    if data.get("errors") and not data.get("data"):
        msg = json.dumps(data["errors"])[:300]
        if "NOT_FOUND" in msg:
            raise NotFound("graphql")
        raise GhError(msg)
    return data.get("data") or {}


def find_repo_checkout(owner: str, repo: str) -> str | None:
    """Any checkout of this repo on disk: the cwd's repo, else ~/Code/<repo>, matched exactly
    through `rewrite_policy.forge_repo`: a substring test on the remote URL accepts
    `acme/widgets-legacy` for `acme/widgets`."""
    policy = pr_policy()
    for root in (Path.cwd(), Path.home() / "Code" / repo):
        top = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True)
        if top.returncode != 0:
            continue
        path = top.stdout.strip()
        if policy is not None and policy.forge_repo(path, "origin") == (owner, repo):
            return path
    return None


THREADS_QUERY = """
query($owner: String!, $repo: String!, $pr: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      reviews(last: 50) { nodes { author { login } commit { oid } } }
      comments(last: 50) { nodes { author { login } } }
      reviewThreads(first: 100) {
        nodes { isResolved comments(first: 1) { nodes { author { login } } } }
      }
    }
  }
}
"""


class Scm:
    """The git half of the read: facts about two commits rather than about the forge.

    Every command addresses immutable shas and writes nothing: `merge-tree --write-tree`
    merges into the object store, never into a working tree.
    """

    def __init__(self, owner: str, repo: str):
        self.path = find_repo_checkout(owner, repo)
        self._cache: dict[tuple[str, str], dict] = {}

    def _git(self, *args: str, timeout: float = 120.0):
        return subprocess.run(["git", "-C", self.path, *args],
                              capture_output=True, text=True, timeout=timeout)

    def _have(self, sha: str) -> bool:
        return self._git("cat-file", "-e", f"{sha}^{{commit}}", timeout=30.0).returncode == 0

    def facts(self, head_sha: str, head_ref: str, base_ref: str, base_tip: str) -> dict | None:
        """What the base carries that the head lacks, and whether it merges cleanly.

        `None` when no checkout answers for this repo, or when a git command fails: the
        caller reads that as no opinion and falls back to the forge's own fields.
        """
        if not (self.path and head_sha and base_tip):
            return None
        hit = self._cache.get((head_sha, base_tip))
        if hit is not None:
            return hit
        try:
            if not (self._have(head_sha) and self._have(base_tip)):
                self._git("fetch", "--quiet", "origin", base_ref, head_ref, timeout=300.0)
            if not (self._have(head_sha) and self._have(base_tip)):
                return None
            rl = self._git("rev-list", "--count", f"{head_sha}..{base_tip}")
            if rl.returncode != 0:
                return None
            behind = int(rl.stdout.strip() or 0)
            changed = 0
            mb = self._git("merge-base", head_sha, base_tip)
            if mb.returncode == 0 and mb.stdout.strip():
                names = self._git("diff", "--name-only", mb.stdout.strip(), base_tip)
                if names.returncode == 0:
                    changed = len([ln for ln in names.stdout.splitlines() if ln.strip()])
            mt = self._git("merge-tree", "--write-tree", head_sha, base_tip, timeout=300.0)
            conflicted = {0: False, 1: True}.get(mt.returncode)
        except (OSError, ValueError, subprocess.SubprocessError):
            return None
        facts = {"source": "git", "base_tip_sha": base_tip, "behind_by": behind,
                 "base_changed_files": changed, "conflicted": conflicted}
        self._cache[(head_sha, base_tip)] = facts
        return facts


class Reader:
    """One uncached reading of one pull request per `read()`. Holds only what is immutable
    or monotonic: commit times, the ready event, a positive `merged_into`, git facts by sha."""

    def __init__(self, owner: str, repo: str, pr: int, fresh_window: int, bot_pending_timeout: int):
        self.owner, self.repo, self.pr = owner, repo, pr
        self.fresh_window, self.bot_pending_timeout = fresh_window, bot_pending_timeout
        self.scm = Scm(owner, repo)
        self.head_committed: dict[str, datetime | None] = {}
        self.ready_at: datetime | None | str = "unread"
        self.merged_into: bool | str = "unread"
        self.pull: dict | None = None

    @property
    def base_path(self) -> str:
        return f"repos/{self.owner}/{self.repo}"

    def read_pull(self) -> dict:
        data = gh_api(f"{self.base_path}/pulls/{self.pr}")
        if not data:
            raise GhError("empty pull payload")
        self.pull = data
        return data

    def settled_pull(self, tries: int = 5, pause: float = 3.0) -> dict:
        """GitHub computes mergeability lazily: `mergeable: null` means re-request."""
        pull = self.read_pull()
        for _ in range(tries):
            if pull.get("mergeable") is not None or pull.get("merged"):
                break
            time.sleep(pause)
            pull = self.read_pull()
        return pull

    def read_base_tip(self, base_ref: str) -> str | None:
        data = gh_api(f"{self.base_path}/git/ref/heads/{base_ref}")
        return ((data or {}).get("object") or {}).get("sha")

    def read_checks(self, sha: str) -> list[dict]:
        """Check runs for HEAD, paging past 100."""
        data = gh_api(f"{self.base_path}/commits/{sha}/check-runs?per_page=100")
        runs = list((data or {}).get("check_runs") or [])
        total = int((data or {}).get("total_count") or 0)
        page = 2
        while len(runs) < total and page <= 5:
            more = gh_api(f"{self.base_path}/commits/{sha}/check-runs?per_page=100&page={page}")
            runs += list((more or {}).get("check_runs") or [])
            page += 1
        return runs

    def head_committed_at(self, sha: str) -> datetime | None:
        if sha not in self.head_committed:
            data = gh_api(f"{self.base_path}/commits/{sha}")
            self.head_committed[sha] = parse_iso(
                (((data or {}).get("commit") or {}).get("committer") or {}).get("date"))
        return self.head_committed[sha]

    def ready_at_utc(self) -> datetime | None:
        """When the PR last became ready for review, or None. Read once: the timeline is
        append-only for this event. An unreadable timeline is no opinion, not "never ready"."""
        if self.ready_at != "unread":
            return self.ready_at
        self.ready_at = None
        try:
            events = gh_api(f"{self.base_path}/issues/{self.pr}/timeline?per_page=100")
            for ev in reversed(list(events or [])):
                if isinstance(ev, dict) and ev.get("event") == "ready_for_review":
                    self.ready_at = parse_iso(ev.get("created_at"))
                    break
        except (GhError, NotFound, RateLimited):
            self.ready_at = None
        return self.ready_at

    def read_threads(self) -> dict:
        d = gh_graphql(THREADS_QUERY, owner=self.owner, repo=self.repo, pr=self.pr)
        pr = ((d.get("repository") or {}).get("pullRequest")) or {}
        return {
            "reviews": (pr.get("reviews") or {}).get("nodes") or [],
            "comments": (pr.get("comments") or {}).get("nodes") or [],
            "threads": (pr.get("reviewThreads") or {}).get("nodes") or [],
        }

    def read_merged_into(self, head_ref: str) -> bool | str:
        """True once any pull request has merged INTO this head: a branch other work lands
        on is absorbed from its base by merge, a feature branch is rebased. Re-read while the
        answer is still no, because a branch becomes one the day its first child lands; a
        positive is kept, a negative never is."""
        if self.merged_into is True:
            return True
        policy = pr_policy()
        seen = None if policy is None else policy.merged_into(None, head_ref, forge=(self.owner, self.repo))
        if policy is not None and seen is policy.NO_FORGE:
            seen = None
        self.merged_into = "unknown" if seen is None else bool(seen)
        return self.merged_into

    def read(self) -> dict:
        pull = self.settled_pull()
        scm = None
        integration = "unknown"
        check_runs: list[dict] = []
        threads = {"reviews": [], "comments": [], "threads": []}
        head_age = reviewable_age = None
        if not pull.get("merged") and pull.get("state") == "open":
            head = pull["head"]["sha"]
            base_ref, head_ref = pull["base"]["ref"], pull["head"]["ref"]
            check_runs = self.read_checks(head)
            threads = self.read_threads()
            committed = self.head_committed_at(head)
            head_age = None if committed is None else (now_utc() - committed).total_seconds()
            started = max([m for m in (committed, self.ready_at_utc()) if m is not None], default=None)
            reviewable_age = None if started is None else (now_utc() - started).total_seconds()
            integration = self.read_merged_into(head_ref)
            base_tip = self.read_base_tip(base_ref)
            scm = self.scm.facts(head, head_ref, base_ref, base_tip or "")
        return {"pull": pull, "check_runs": check_runs, "threads": threads,
                "head_age": head_age, "reviewable_age": reviewable_age,
                "scm": scm, "integration_base": integration,
                "fresh_window": self.fresh_window, "bot_pending_timeout": self.bot_pending_timeout}
