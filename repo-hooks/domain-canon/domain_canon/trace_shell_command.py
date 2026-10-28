import os
import shlex

import hook_shell
import shell_writes

from domain_canon.expand_operands import (
    COMPOUND_KEYWORD_PREFIX, MAX_OPERANDS, MAX_STATEMENTS, bind_variables, bindings_certain,
    literal_directory, segment_operands,
)
from domain_canon.find_governing_canon import place

WHOLE_FILE_READERS = frozenset(("cat", "bat"))
SLICE_READERS = frozenset((
    "head", "tail", "sed", "grep", "rg", "awk", "less", "more", "wc",
    "diff", "cut", "sort", "uniq", "jq", "git", "ls", "find", "python3",
))
NAME_ONLY_VERBS = frozenset((
    "[", "[[", "test", "for", "select", "case",
    "echo", "printf", "basename", "dirname", "realpath", "readlink",
    "ls", "stat", "file", "du", "wc", "cksum", "md5", "md5sum", "shasum",
    "sha1sum", "sha256sum",
    "touch", "mkdir", "rmdir", "rm", "unlink", "chmod", "chown", "trash",
    "cd", "pushd", "popd", "export", "local", "declare", "typeset", "readonly",
    "unset", "which", "type",
))
CONTENT_READERS = WHOLE_FILE_READERS | frozenset((
    "head", "tail", "sed", "grep", "egrep", "fgrep", "rg", "awk", "less", "more",
    "diff", "cut", "sort", "uniq", "jq", "nl", "od", "xxd", "hexdump", "strings",
    "tac", "column", "fold", "fmt", "pr", "paste", "view", "vim", "vi", "nano",
    "python", "python3", "node", "perl", "ruby", "sh", "bash", "zsh", "source", ".",
))
NAME_FEEDING_VERBS = frozenset(("xargs", "parallel"))
TREE_SEARCH_NAME_ONLY_LETTERS = {
    "grep": "lLcq", "egrep": "lLcq", "fgrep": "lLcq", "rg": "lcq", "ag": "lLc", "ack": "lLc",
}
TREE_SEARCH_NAME_ONLY_FLAGS = frozenset((
    "--files", "--files-with-matches", "--files-without-match", "--files-without-matches",
    "--count", "--count-matches", "--quiet",
))
GREP_RECURSIVE_FLAGS = frozenset(("--recursive", "--dereference-recursive"))
TREE_SEARCH_VALUED_LETTERS = {
    "grep": "efmABCDd", "egrep": "efmABCDd", "fgrep": "efmABCDd",
    "rg": "efgtTmABCEjMr", "ag": "GgmABC", "ack": "gmABC",
}
TREE_SEARCH_VALUED_FLAGS = frozenset((
    "--regexp", "--file", "--glob", "--iglob", "--type", "--type-not", "--max-count",
    "--after-context", "--before-context", "--context", "--encoding", "--threads",
    "--max-columns", "--replace", "--directories", "--devices", "--include", "--exclude",
    "--exclude-dir", "--ignore-dir", "--label", "--color", "--colour",
))
GIT_CONTENT_SUBCOMMANDS = frozenset((
    "show", "diff", "blame", "annotate", "grep", "cat-file", "format-patch",
    "difftool", "range-diff", "merge-file",
))
GIT_WORKTREE_OVERWRITE_SUBCOMMANDS = frozenset(("checkout", "restore"))
GIT_HISTORY_SUBCOMMANDS = frozenset(("log", "whatchanged"))
GIT_PATCH_FLAGS = ("-p", "-u", "--patch", "--patch-with-stat", "--patch-with-raw", "--cc", "-c",
                   "--remerge-diff")
GIT_PATCH_FLAG_PREFIXES = ("-L", "-U", "--unified")
GIT_GLOBALS_TAKING_VALUE = frozenset(("-C", "-c", "--git-dir", "--work-tree", "--namespace",
                                      "--exec-path", "--config-env", "--super-prefix"))


def git_opens_and_base(segment, at):
    try:
        argv = shlex.split(segment, posix=True)
    except ValueError:
        argv = segment.split()
    try:
        i = next(k for k, w in enumerate(argv) if w.rsplit("/", 1)[-1] == "git") + 1
    except StopIteration:
        return True, at
    base = at
    while i < len(argv):
        word = argv[i]
        if word in GIT_GLOBALS_TAKING_VALUE:
            if word == "-C" and i + 1 < len(argv):
                target = os.path.expanduser(argv[i + 1])
                if "$" in target or "`" in target or (base is None and not os.path.isabs(target)):
                    base = None
                else:
                    base = os.path.normpath(os.path.join(base or "", target))
            i += 2
            continue
        if word.startswith("-"):
            i += 1
            continue
        break
    sub = argv[i] if i < len(argv) else ""
    rest = argv[i + 1:]
    if sub in GIT_CONTENT_SUBCOMMANDS or sub in GIT_WORKTREE_OVERWRITE_SUBCOMMANDS:
        return True, base
    if sub in GIT_HISTORY_SUBCOMMANDS:
        return any(w in GIT_PATCH_FLAGS or w.startswith(GIT_PATCH_FLAG_PREFIXES) for w in rest), base
    return False, base


def searches_tree(segment, verb):
    name_only = TREE_SEARCH_NAME_ONLY_LETTERS.get(verb)
    if name_only is None:
        return False
    try:
        tokens = shlex.split(segment, posix=True)
    except ValueError:
        tokens = segment.split()
    valued = TREE_SEARCH_VALUED_LETTERS[verb]
    start = next((k + 1 for k, w in enumerate(tokens) if w.rsplit("/", 1)[-1] == verb), len(tokens))
    letters, recursive, i = "", not verb.endswith("grep"), start
    while i < len(tokens):
        word = tokens[i]
        if word == "--":
            break
        if word.startswith("--"):
            name, eq, value = word.partition("=")
            if name in TREE_SEARCH_NAME_ONLY_FLAGS:
                return False
            if name in TREE_SEARCH_VALUED_FLAGS and not eq:
                i += 1
                value = tokens[i] if i < len(tokens) else ""
            recursive = recursive or name in GREP_RECURSIVE_FLAGS or (
                name == "--directories" and value == "recurse")
        elif word.startswith("-") and len(word) > 1:
            for k, c in enumerate(word[1:], 2):
                if c not in valued:
                    letters += c
                    continue
                value = word[k:]
                if not value:
                    i += 1
                    value = tokens[i] if i < len(tokens) else ""
                recursive = recursive or (c == "d" and verb.endswith("grep") and value == "recurse")
                break
        i += 1
    if any(c in name_only for c in letters):
        return False
    return recursive or "r" in letters or "R" in letters


def reached_files(command, cwd, unplaced=None):
    out, seen, known = [], set(), {}
    statements = hook_shell.statements_with_cwd(command, cwd)[:MAX_STATEMENTS]
    for (statement, at), certain in zip(statements, bindings_certain(command)):
        bind_variables(statement, at, known, certain)
        piped = hook_shell.has_pipe_or_redirect(statement)
        segments = [COMPOUND_KEYWORD_PREFIX.sub("", s)
                    for s in hook_shell.pipe_segments(statement) or [statement]]
        verbs = [hook_shell.command_word(s) for s in segments]
        names_feed_a_reader = any(
            v in NAME_FEEDING_VERBS
            or any(os.path.basename(w) in NAME_FEEDING_VERBS
                   for prefix, _ in hook_shell.invocations_with_prefix(s) for w in prefix)
            for s, v in zip(segments, verbs))
        for segment, verb in zip(segments, verbs):
            if verb is None:
                continue
            credits = verb in WHOLE_FILE_READERS and not piped
            base = at
            if verb == "git":
                opens, base = git_opens_and_base(segment, at)
            else:
                opens = names_feed_a_reader or verb not in NAME_ONLY_VERBS
            tree = searches_tree(segment, verb) and unplaced is not None
            operands = segment_operands(segment, verb, known, base)
            if tree and base is not None and not any(
                    os.path.exists(os.path.join(base, p)) for _o, ps in operands for p in ps or ()):
                unplaced.append((base, ".", verb))
            for operand, paths in operands:
                if paths is None:
                    if (unplaced is not None and opens and verb in CONTENT_READERS
                            and not any(c.isspace() for c in operand)):
                        unplaced.append((literal_directory(operand, base, cwd), operand, verb))
                    continue
                for path in paths:
                    if os.path.isabs(path):
                        abs_path = path
                    elif base is None:
                        continue
                    else:
                        abs_path = os.path.join(base, path)
                    abs_path = os.path.normpath(abs_path)
                    if tree and os.path.isdir(abs_path):
                        unplaced.append((abs_path, operand, verb))
                    if not os.path.isfile(abs_path):
                        continue
                    where = place(abs_path)
                    if not where or (where[1], credits, opens) in seen:
                        continue
                    seen.add((where[1], credits, opens))
                    out.append((where[0], where[1], credits, verb, opens))
    return out


def over_parse_cap(command, cwd):
    try:
        statements = hook_shell.statements_with_cwd(command, cwd)
        if len(statements) > MAX_STATEMENTS:
            return True
        return any(len(hook_shell.operands(st)) > MAX_OPERANDS for st, _ in statements)
    except Exception:
        return False


def written_files(command, cwd):
    out, seen = [], set()
    for abs_path in shell_writes.write_targets(command, cwd):
        where = place(abs_path)
        if not where or where[1] in seen:
            continue
        seen.add(where[1])
        out.append(where)
    return out


def whole_reads_naming_no_file(command, cwd, landed):
    missed = []
    try:
        for statement, at in hook_shell.statements_with_cwd(command, cwd)[:MAX_STATEMENTS]:
            if hook_shell.command_word(statement) not in WHOLE_FILE_READERS:
                continue
            for operand in hook_shell.file_operands(statement)[:MAX_OPERANDS]:
                expanded = os.path.expanduser(operand)
                if at is None and not os.path.isabs(expanded):
                    continue
                candidate = os.path.normpath(
                    expanded if os.path.isabs(expanded) else os.path.join(at, expanded))
                if candidate in landed or os.path.isfile(candidate):
                    continue
                missed.append(operand)
    except Exception:
        return []
    return missed
