#!/usr/bin/env python3
import argparse
import fnmatch
import json
import os
import pwd
import shutil
import subprocess
import sys

HOME = pwd.getpwuid(os.getuid()).pw_dir
sys.path.insert(0, os.path.join(HOME, ".claude", "skills", "pull-request", "scripts"))
import rewrite_policy  # noqa: E402

ALLOW, REFUSE, UNKNOWN = "allow", "refuse", "unknown"
ABSENT, FOUNDED, LIVE, SPENT = "absent", "founded", "live", "spent"
TIMEOUT = 20
FOUND_MESSAGE = "chore: found {branch}\n\nIntegration base for one wave of child pull requests; carries no implementation of its own."


class Unread(Exception):
    pass


def run(cmd):
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT,
                             env=dict(os.environ, GH_PAGER="cat"))
    except Exception as exc:
        raise Unread("%s did not run: %s" % (cmd[0], exc))
    return out.returncode, out.stdout, out.stderr.strip()


def gh(*args):
    code, out, err = run(["gh", *args])
    if code:
        raise Unread("gh %s failed: %s" % (" ".join(args[:3]), err[:200]))
    return out


def base_checkout(path):
    code, out, _ = run(["git", "-C", path, "rev-parse", "--path-format=absolute", "--git-common-dir"])
    if code or not out.strip():
        raise Unread("not a git checkout: %s" % path)
    return os.path.dirname(os.path.realpath(out.strip()))


def git_config(root):
    tool = shutil.which("agents-config") or os.path.join(HOME, ".claude", "skills", "agents-config", "scripts", "agents-config")
    code, out, err = run([tool, "get", "git", "--root", root])
    if code:
        raise Unread("git config unread: %s" % err[:200])
    try:
        return json.loads(out).get("defaults") or {}
    except ValueError:
        raise Unread("git config is not JSON")


class Repo:
    def __init__(self, path):
        self.root = base_checkout(path)
        cfg = git_config(self.root)
        self.globs = rewrite_policy.declared_bases(self.root)
        forge = rewrite_policy.forge_repo(self.root, "origin")
        if not isinstance(forge, tuple):
            raise Unread("origin reaches no github.com repository")
        self.forge = forge
        self.slug = "%s/%s" % forge
        base = cfg.get("base_branch")
        if not base or base == "auto":
            base = gh("repo", "view", self.slug, "--json", "defaultBranchRef",
                      "-q", ".defaultBranchRef.name").strip()
            if not base:
                raise Unread("base_branch unresolved")
        self.base = base

    def declared(self, branch):
        return next((g for g in self.globs if fnmatch.fnmatchcase(branch, g)), None)

    def sha(self, branch):
        code, out, err = run(["gh", "api", "repos/%s/git/ref/heads/%s" % (self.slug, branch)])
        if code:
            if "404" in err or "Not Found" in err:
                return None
            raise Unread("ref read failed: %s" % err[:200])
        return json.loads(out)["object"]["sha"]

    def prs(self, *filters):
        out = gh("pr", "list", "--repo", self.slug, *filters, "--limit", "100",
                 "--json", "number,isDraft,state,headRefName,baseRefName")
        return json.loads(out or "[]")


def status(repo, branch):
    facts = {"branch": branch, "base": repo.base}
    if repo.sha(branch) is None:
        return ABSENT, "no branch %s on %s" % (branch, repo.slug), facts
    promotion = repo.prs("--head", branch, "--state", "all")
    open_promotion = [p for p in promotion if p["state"] == "OPEN"]
    children = repo.prs("--base", branch, "--state", "open")
    facts["children_open"] = ",".join("#%d" % p["number"] for p in children) or "none"
    if open_promotion:
        pr = open_promotion[0]
        facts["promotion"] = "#%d" % pr["number"]
        facts["draft"] = "yes" if pr["isDraft"] else "no"
        return LIVE, "promotion pull request #%d is open" % pr["number"], facts
    if promotion:
        return SPENT, "its promotion pull request is %s" % promotion[0]["state"].lower(), facts
    return FOUNDED, "the branch exists and no promotion pull request was ever opened", facts


def found(repo, branch):
    if not repo.globs:
        return REFUSE, "the repo declares no integration_bases, so it takes no cluster"
    if not repo.declared(branch):
        return REFUSE, "%s matches no declared glob (%s)" % (branch, ", ".join(repo.globs))
    state, reason, _ = status(repo, branch)
    if state == LIVE:
        return ALLOW, "live, join it: %s" % reason
    if state == FOUNDED:
        return ALLOW, "exists, open its draft promotion pull request into %s" % repo.base
    if state == SPENT:
        return REFUSE, "spent, retire it before founding the next wave: %s" % reason
    parent = repo.sha(repo.base)
    if parent is None:
        return UNKNOWN, "base branch %s is absent on %s" % (repo.base, repo.slug)
    tree = json.loads(gh("api", "repos/%s/git/commits/%s" % (repo.slug, parent)))["tree"]["sha"]
    commit = json.loads(gh("api", "-X", "POST", "repos/%s/git/commits" % repo.slug,
                           "-f", "message=" + FOUND_MESSAGE.format(branch=branch),
                           "-f", "tree=" + tree, "-f", "parents[]=" + parent))["sha"]
    gh("api", "-X", "POST", "repos/%s/git/refs" % repo.slug,
       "-f", "ref=refs/heads/" + branch, "-f", "sha=" + commit)
    return ALLOW, "created %s at %s on %s, open its draft promotion pull request into %s" % (
        branch, commit[:12], repo.base, repo.base)


def ship(repo, branch):
    state, reason, facts = status(repo, branch)
    if state != LIVE:
        return REFUSE, "not live (%s): %s" % (state, reason)
    if facts["children_open"] != "none":
        return REFUSE, "children still open: %s" % facts["children_open"]
    merged = rewrite_policy.merged_into(repo.root, branch, forge=repo.forge)
    if merged is None or merged is rewrite_policy.NO_FORGE:
        return UNKNOWN, "merged children unread"
    if not merged:
        return REFUSE, "no child has merged into %s yet" % branch
    if facts["draft"] == "no":
        return ALLOW, "promotion pull request %s is already ready; a child with no pull request yet is invisible here" % facts["promotion"]
    gh("pr", "ready", facts["promotion"].lstrip("#"), "--repo", repo.slug)
    return ALLOW, "readied promotion pull request %s into %s; a child with no pull request yet is invisible here" % (facts["promotion"], repo.base)


def clusters(repo):
    names = []
    for glob in repo.globs:
        prefix = glob.split("*", 1)[0].split("?", 1)[0].split("[", 1)[0]
        refs = json.loads(gh("api", "repos/%s/git/matching-refs/heads/%s" % (repo.slug, prefix)) or "[]")
        for ref in refs:
            name = ref["ref"][len("refs/heads/"):]
            if fnmatch.fnmatchcase(name, glob) and name not in names:
                names.append(name)
    return names


def main(argv=None):
    parser = argparse.ArgumentParser(prog="cluster.py")
    sub = parser.add_subparsers(dest="verb", required=True)
    for name, text in (
            ("status", "absent|founded|live|spent, then key=value facts"),
            ("found", "create the branch with one empty commit off base_branch; allow|refuse|unknown"),
            ("ship", "ready the draft promotion pull request once no child is open and one merged"),
            ("list", "every branch matching a declared glob, with its state")):
        p = sub.add_parser(name, help=text)
        p.add_argument("--repo", required=True)
        if name != "list":
            p.add_argument("--branch", required=True)
    args = parser.parse_args(argv)
    try:
        repo = Repo(args.repo)
        if args.verb == "status":
            state, reason, facts = status(repo, args.branch)
            print(state)
            print(reason)
            for key, value in facts.items():
                print("%s=%s" % (key, value))
            return 0
        if args.verb == "list":
            names = clusters(repo)
            print(ALLOW if repo.globs else REFUSE)
            print("%d cluster(s) on %s" % (len(names), repo.slug) if repo.globs
                  else "the repo declares no integration_bases")
            for name in names:
                print("%s %s" % (name, status(repo, name)[0]))
            return 0
        answer, reason = (found if args.verb == "found" else ship)(repo, args.branch)
    except Unread as exc:
        answer, reason = UNKNOWN, str(exc)
    print(answer)
    print(reason)
    return 0 if answer == ALLOW else 1


if __name__ == "__main__":
    sys.exit(main())
