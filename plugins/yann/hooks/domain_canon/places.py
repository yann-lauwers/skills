import os
import shlex

import hook_shell
import shell_writes

from domain_canon.find_governing_canon import is_canon_file, place
from domain_canon.parse_event import BASH_TOOL, READ_TOOL, SEARCH_TOOLS, command_of, cwd_of, target_path, tool_of

READ_TOOLS = SEARCH_TOOLS | frozenset((READ_TOOL, "NotebookRead", "LS"))
WHOLE_FILE_READERS = frozenset(("cat", "bat"))
EXPANSION_CHARS = "$`*?["


def probe(directory):
    return os.path.join(directory, "_")


def places_of(payload):
    tool = tool_of(payload)
    cwd = cwd_of(payload)
    if tool in READ_TOOLS:
        return _placed([target_path(payload) or cwd])
    command = command_of(payload) if tool == BASH_TOOL else None
    if not command:
        return []
    named = []
    for statement, at in hook_shell.statements_with_cwd(command, cwd):
        here = at or cwd
        if _reads_canon_only(statement, here):
            continue
        named.append(here)
        for word in _words(statement):
            named.extend(_named_paths(word, here))
    return _placed(named)


def credited_reads(payload):
    tool = tool_of(payload)
    if tool == READ_TOOL:
        where = place(target_path(payload))
        return [where] if where else []
    command = command_of(payload) if tool == BASH_TOOL else None
    if not command:
        return []
    out = []
    for statement, at in hook_shell.statements_with_cwd(command, cwd_of(payload)):
        if (hook_shell.command_word(statement) not in WHOLE_FILE_READERS
                or hook_shell.has_pipe_or_redirect(statement)):
            continue
        for operand in hook_shell.operands(statement):
            path = _literal_file(operand, at)
            where = place(path) if path else None
            if where and where not in out:
                out.append(where)
    return out


def written_files(payload):
    command = command_of(payload) if tool_of(payload) == BASH_TOOL else None
    if not command:
        return []
    out = []
    for abs_path in shell_writes.write_targets(command, cwd_of(payload)):
        where = place(abs_path)
        if where and where not in out:
            out.append(where)
    return out


def _words(statement):
    try:
        return shlex.split(statement, posix=True)
    except ValueError:
        return statement.split()


def _named_paths(word, here):
    for candidate in {word, word.partition("=")[2]}:
        literal = candidate[:min((candidate.find(c) for c in EXPANSION_CHARS if c in candidate),
                                 default=len(candidate))]
        if not literal:
            continue
        literal = os.path.expanduser(literal)
        path = os.path.normpath(literal if os.path.isabs(literal) else os.path.join(here, literal))
        if os.path.exists(path):
            yield path
        elif os.path.isdir(os.path.dirname(path)):
            yield os.path.dirname(path)


def _literal_file(operand, at):
    if any(c in operand for c in EXPANSION_CHARS):
        return None
    path = os.path.expanduser(operand)
    if not os.path.isabs(path):
        if at is None:
            return None
        path = os.path.join(at, path)
    path = os.path.normpath(path)
    return path if os.path.isfile(path) else None


def _reads_canon_only(statement, here):
    if hook_shell.command_word(statement) not in WHOLE_FILE_READERS:
        return False
    files = [_literal_file(o, here) for o in hook_shell.operands(statement)]
    return bool(files) and all(f and _is_canon(f) for f in files)


def _is_canon(path):
    where = place(path)
    return bool(where) and is_canon_file(os.path.relpath(where[1], where[0]))


def _placed(paths):
    out, seen = [], set()
    for path in paths:
        if not path:
            continue
        if os.path.isfile(path):
            if _is_canon(path):
                continue
            path = os.path.dirname(path)
        where = place(probe(path))
        if not where or path in seen:
            continue
        seen.add(path)
        out.append((where[0], path))
    return out
