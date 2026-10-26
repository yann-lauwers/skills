import os
import re
from collections import namedtuple

from git_reads import git, lines

GIT_OPTIONS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--config-env"}
COMMIT_SHORT_OPTIONS_WITH_VALUE = set("mFCct")
COMMIT_LONG_OPTIONS_WITH_VALUE = {"--message", "--file", "--reuse-message", "--reedit-message", "--template",
                                  "--author", "--date", "--cleanup", "--fixup", "--squash", "--trailer"}
INTERACTIVE_ADD_FLAGS = ("-p", "--patch", "-i", "--interactive", "-e", "--edit")
CLEARS_WHOLE_INDEX_FLAGS = ("--hard", "--merge", "--keep")

GitCall = namedtuple("GitCall", "directory subcommand args")
CommitScope = namedtuple("CommitScope", "everything include paths dry_run")


def resolve_against(base, value):
    return value if os.path.isabs(value) else (os.path.join(base, value) if base else None)


def git_call(argv, cwd):
    where, i = cwd, 1
    while i < len(argv) and argv[i].startswith("-"):
        word = argv[i]
        if word in GIT_OPTIONS_WITH_VALUE:
            value = argv[i + 1] if i + 1 < len(argv) else ""
            if word == "-C":
                if "$" in value or "`" in value:
                    return None
                where = resolve_against(where, value)
            elif word == "--work-tree":
                where = resolve_against(where, value)
            i += 2
            continue
        if word.startswith("--work-tree="):
            where = resolve_against(where, word.split("=", 1)[1])
        i += 1
    if where is None or i >= len(argv):
        return None
    return GitCall(os.path.normpath(os.path.expanduser(where)), argv[i], argv[i + 1:])


def commit_scope(args):
    everything = include = dry_run = False
    paths, i = [], 0
    while i < len(args):
        word = args[i]
        if word == "--":
            paths += args[i + 1:]
            break
        if word in ("-a", "--all"):
            everything = True
        elif word in ("-i", "--include"):
            include = True
        elif word == "--dry-run":
            dry_run = True
        elif word == "--pathspec-from-file" or word.startswith("--pathspec-from-file="):
            everything = True
            i += 0 if "=" in word else 1
        elif word in COMMIT_LONG_OPTIONS_WITH_VALUE:
            i += 1
        elif word.startswith("--"):
            pass
        elif word.startswith("-") and len(word) > 1:
            for k, ch in enumerate(word[1:], 1):
                if ch == "a":
                    everything = True
                elif ch == "i":
                    include = True
                elif ch in COMMIT_SHORT_OPTIONS_WITH_VALUE:
                    if k == len(word) - 1:
                        i += 1
                    break
        else:
            paths.append(word)
        i += 1
    return CommitScope(everything, include, paths, dry_run)


def would_add(repo, args):
    if any(a in INTERACTIVE_ADD_FLAGS for a in args):
        return None
    out = git(repo, "add", "--dry-run", *args)
    if out is None:
        return None
    return [re.sub(r"^(add|remove) '(.*)'$", r"\2", l) for l in lines(out)]


def would_unstage(repo, sub, args):
    flags = [a for a in args if a.startswith("-") and a != "--"]
    paths = [a for a in args if not a.startswith("-") or a == "--"]
    paths = paths[paths.index("--") + 1:] if "--" in paths else paths
    if sub == "restore":
        if not any(f in ("--staged", "-S") or (f.startswith("-") and not f.startswith("--") and "S" in f) for f in flags):
            return []
    elif sub == "rm":
        if "--cached" not in flags:
            return None
        return lines(git(repo, "ls-files", "--full-name", "--", *paths)) if paths else []
    elif sub == "reset":
        if any(f in CLEARS_WHOLE_INDEX_FLAGS for f in flags):
            return None
        if not paths:
            return lines(git(repo, "diff", "--cached", "--name-only", "--no-renames"))
    else:
        return []
    if not paths:
        return []
    return lines(git(repo, "ls-files", "--full-name", "--", *paths))

