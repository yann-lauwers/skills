import re

import gh_calls
import hook_shell


UNREADABLE = "\x00unreadable"
_PR_URL_RE = re.compile(r"(?:https?://)?([^/\s]+)/([^/\s]+/[^/\s]+)/pull/(\d+)")
_API_MERGE_RE = re.compile(r"(?:^|/)pulls/([^/\s]+)/merge/?(?:\?.*)?$")
_API_REPO_RE = re.compile(r"(?:^|/)repos/([^/\s]+)/([^/\s]+)/pulls/")
_GRAPHQL_MERGE_RE = re.compile(r"\b(?:mergePullRequest|enablePullRequestAutoMerge)\b")
_GH_TARGET_ENV_RE = re.compile(r"\bGH_(?:REPO|HOST)=")
_MERGE_VALUED = frozenset(("-t", "--subject", "-b", "--body", "-F", "--body-file",
                           "-A", "--author-email", "--match-head-commit"))
_DIR_MOVERS = frozenset(("cd", "pushd", "popd"))
_CHDIR_FLAGS = {"env": ("--chdir", "C"), "sudo": ("--chdir", "D")}


def _selector(words):
    skip = False
    for word in words:
        if skip:
            skip = False
            continue
        if word.startswith("-"):
            skip = word in _MERGE_VALUED
            continue
        url = _PR_URL_RE.search(word)
        if url:
            host, repo, number = url.groups()
            return number, repo if host.lower() == "github.com" else "%s/%s" % (host, repo)
        return word.lstrip("#"), None
    return None, None


def _looks_up(prefix):
    in_command = False
    for word in prefix:
        if word.rsplit("/", 1)[-1] == "command":
            in_command = True
        elif not word.startswith("-"):
            in_command = False
        elif in_command and not word.startswith("--") and ("v" in word or "V" in word):
            return True
    return False


def merge_of(prefix, argv):
    if _looks_up(prefix):
        return None
    merge = None
    verb = argv[0]
    if verb == "gh":
        repo, rest = gh_calls.gh_args(argv)
        if rest[:2] == ["pr", "merge"]:
            selector, url_repo = _selector(rest[2:])
            merge = {"verb": "gh pr merge", "selector": selector, "repo": repo or url_repo}
        request = gh_calls.gh_api_request(rest)
        if request and request[0] != "GET":
            m = _API_MERGE_RE.search(request[1])
            if m:
                owner = _API_REPO_RE.search(request[1])
                api_repo = None
                if owner and not any(p.startswith(("{", ":")) for p in owner.groups()):
                    api_repo = "%s/%s" % owner.groups()
                merge = {"verb": "gh api %s pulls/merge" % request[0],
                         "selector": m.group(1), "repo": repo or api_repo}
            elif request[1] == "graphql" and any(_GRAPHQL_MERGE_RE.search(w) for w in rest):
                merge = {"verb": "gh api graphql merge", "selector": UNREADABLE, "repo": repo}
    elif verb == "pr" and argv[1:2] == ["merge"]:
        selector, url_repo = _selector(argv[2:])
        merge = {"verb": "pr merge", "selector": selector, "repo": url_repo}
    elif verb == "pr-merge":
        selector, url_repo = _selector(argv[1:])
        merge = {"verb": "pr-merge", "selector": selector, "repo": url_repo}
    if merge is None:
        return None
    if any(w.rsplit("/", 1)[-1] == "xargs" for w in prefix):
        merge["selector"] = UNREADABLE
    return merge


def _chdirs(prefix):
    wrapper = None
    for word in prefix:
        base = word.rsplit("/", 1)[-1]
        if base in _CHDIR_FLAGS:
            wrapper = base
            continue
        if wrapper is None or not word.startswith("-"):
            continue
        long_flag, short = _CHDIR_FLAGS[wrapper]
        if word == long_flag or word.startswith(long_flag + "="):
            return True
        if not word.startswith("--") and short in word[1:]:
            return True
    return False


def find_merges(command, cwd):
    pairs = hook_shell.statements_with_cwd(command, cwd)
    found, movers, top_level_cd = [], 0, 0
    for statement, at in pairs:
        if hook_shell.command_word(statement) == "cd":
            top_level_cd += 1
        for prefix, argv in hook_shell.invocations_with_prefix(statement):
            if argv[0] in _DIR_MOVERS:
                movers += 1 if argv[0] == "cd" else 1000
            if _chdirs(prefix):
                movers += 1000
            merge = merge_of(prefix, argv)
            if merge:
                merge["cwd"] = at
                found.append(merge)
    for verb, body in hook_shell.shell_heredocs(command):
        inner = hook_shell.invocations_with_prefix(body)
        moves = any(argv[0] in _DIR_MOVERS or _chdirs(prefix) for prefix, argv in inner)
        if moves and verb in hook_shell.INLINE_RUNNERS:
            movers += 1000
        for prefix, argv in inner:
            merge = merge_of(prefix, argv)
            if merge:
                merge["cwd"] = None if (moves or top_level_cd or movers) else cwd
                found.append(merge)
    grouped = "(" in hook_shell.act_view(command) and movers
    if movers > top_level_cd or grouped:
        for merge in found:
            merge["cwd"] = None
    if _GH_TARGET_ENV_RE.search(command):
        for merge in found:
            merge["repo"] = merge["repo"] or "the one GH_REPO or GH_HOST names"
    return found
