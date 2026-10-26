#!/usr/bin/env python3

import os
import re
import shlex
import sys

_LIB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LIB_DIR not in sys.path:
    sys.path.insert(0, _LIB_DIR)

import hook_shell

PLACEHOLDER_BASENAME = "<unresolved>"

LAST_OPERAND_VERBS = frozenset(("cp", "install", "rsync", "ln"))
_TARGET_DIR_VERBS = frozenset(("cp", "install", "ln"))

ALL_OPERANDS_VERBS = frozenset(("mv", "rm", "touch", "tee", "truncate", "shred", "unlink", "gzip", "gunzip", "zip", "split"))

IN_PLACE_VERBS = {"sed": ("-i", "--in-place"), "perl": ("-i", "--in-place")}

_SCRIPT_FLAGS = {
    "sed": ("ef", ("--expression", "--file")),
    "perl": ("eE", ()),
}

_WRAP_VERBS = frozenset(("sh", "bash", "zsh", "dash", "ksh", "eval"))

_KEY_VALUE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*=")


MAX_STATEMENTS = 40
_MAX_UNWRAP_DEPTH = 2

_PY_INTERPRETERS = re.compile(r"^python(?:\d+(?:\.\d+)?)?$")
_NODE_INTERPRETERS = frozenset(("node", "nodejs", "bun", "deno"))
_LIT = r"""(?P<q>['"])(?P<p>[^'"\n]+)(?P=q)"""
_PY_WRITES = (
    re.compile(r"\bopen\(\s*" + _LIT + r"\s*,\s*(?:mode\s*=\s*)?['\"](?P<m>[^'\"]*)['\"]"),
    re.compile(r"\bPath\(\s*" + _LIT + r"\s*\)\s*\.\s*(?:write_text|write_bytes|touch)\s*\("),
    re.compile(r"\bPath\(\s*" + _LIT + r"\s*\)\s*\.\s*open\(\s*(?:mode\s*=\s*)?['\"](?P<m>[^'\"]*)['\"]"),
)
_PY_DEST = re.compile(
    r"\b(?:os\.replace|os\.rename|shutil\.copy2?|shutil\.copyfile|shutil\.move)\(\s*"
    r"(?:['\"][^'\"\n]*['\"]|[A-Za-z_][\w.]*)\s*,\s*" + _LIT)
_NODE_WRITES = re.compile(
    r"\b(?:writeFileSync|appendFileSync|writeFile|appendFile|createWriteStream)\(\s*"
    r"(?P<q>['\"`])(?P<p>[^'\"`\n]+)(?P=q)")


def _expand_home(token):
    home = os.path.expanduser("~")
    if token == "~" or token.startswith("~/"):
        return home + token[1:]
    if token.startswith("${HOME}"):
        return home + token[len("${HOME}"):]
    if token == "$HOME":
        return home
    if token.startswith("$HOME/"):
        return home + token[len("$HOME"):]
    return token


def _is_remote_spec(token):
    if token.startswith(("/", "~", ".", "$")):
        return False
    head = token.split("/", 1)[0]
    return ":" in head


def _resolve_dir(head, cwd):
    if head == "":
        return os.path.normpath(cwd) if cwd else None
    head = _expand_home(head)
    if "$" in head or "`" in head:
        return None
    if os.path.isabs(head):
        return os.path.normpath(head)
    if cwd is None:
        return None
    return os.path.normpath(os.path.join(cwd, head))


def _resolve(token, cwd):
    if not token:
        return None
    token = _expand_home(token)
    if "$" not in token and "`" not in token:
        if os.path.isabs(token):
            return os.path.normpath(token)
        if cwd is None:
            return None
        return os.path.normpath(os.path.join(cwd, token))

    head, tail = os.path.split(token)
    if ("$" in tail or "`" in tail) and head and "$" not in head and "`" not in head:
        resolved_dir = _resolve_dir(head, cwd)
        if resolved_dir is not None:
            return os.path.join(resolved_dir, PLACEHOLDER_BASENAME)
    return None


def _tokens(segment):
    view_tokens = hook_shell.act_view(segment).split()
    raw_tokens = segment.split()
    if len(view_tokens) != len(raw_tokens):
        raw_tokens = view_tokens
    return view_tokens, raw_tokens


def _short_value(segment, letter, long_name=None):
    short = "-" + letter
    view_tokens, raw_tokens = _tokens(segment)
    for i, (vt, rt) in enumerate(zip(view_tokens, raw_tokens)):
        vt = vt.lstrip("({")
        if long_name and vt == "--" + long_name:
            return raw_tokens[i + 1].strip("'\"") if i + 1 < len(raw_tokens) else None
        if long_name and vt.startswith("--" + long_name + "="):
            return rt.split("=", 1)[1].strip("'\"") if "=" in rt else None
        if vt == short:
            return raw_tokens[i + 1].strip("'\"") if i + 1 < len(raw_tokens) else None
        if vt.startswith(short) and len(vt) > len(short) and not vt.startswith("--"):
            return rt[len(short):].strip("'\"")
    return None


def _bundled_cluster_value(segment, letter):
    view_tokens, raw_tokens = _tokens(segment)
    for i, (vt, rt) in enumerate(zip(view_tokens, raw_tokens)):
        vt = vt.lstrip("({")
        if vt.startswith("-") and not vt.startswith("--") and len(vt) > 2 and vt[-1] == letter:
            return raw_tokens[i + 1].strip("'\"") if i + 1 < len(raw_tokens) else None
    return None


def _input_redirect_targets(segment):
    view_tokens, raw_tokens = _tokens(segment)
    out, skip = set(), False
    for vt, rt in zip(view_tokens, raw_tokens):
        if skip:
            out.add(rt.strip("'\""))
            skip = False
            continue
        if vt in ("<", "0<"):
            skip = True
    return out


def _truncate_operands(segment):
    tokens = [t for t in hook_shell.file_operands(segment) if not _KEY_VALUE_RE.match(t)]
    value = _short_value(segment, "s", "size")
    return [t for t in tokens if t != value] if value is not None else tokens


def _is_backup_suffix(word):
    return word == "" or (len(word) > 1 and word.startswith(".")
                          and not word.startswith("./") and "/" not in word)


def _in_place_non_files(segment, verb):
    short_valued, long_valued = _SCRIPT_FLAGS[verb]
    try:
        words = shlex.split(segment, posix=True)
    except ValueError:
        words = segment.split()
    start = next((i for i, w in enumerate(words)
                  if w.lstrip("({").rsplit("/", 1)[-1] == verb), None)
    if start is None:
        return []
    non_files, positional, script_given = [], [], False
    j = start + 1
    while j < len(words):
        w = words[j]
        if w == "--":
            positional.extend(words[j + 1:])
            break
        if w.startswith("--"):
            name, eq, value = w.partition("=")
            if name in long_valued:
                script_given = True
                if not eq and j + 1 < len(words):
                    j += 1
                    value = words[j]
                non_files.append(value)
            j += 1
            continue
        if w.startswith("-") and len(w) > 1:
            letters = w[1:]
            for k, ch in enumerate(letters):
                rest = letters[k + 1:]
                if ch in short_valued:
                    script_given = True
                    if not rest and j + 1 < len(words):
                        j += 1
                        rest = words[j]
                    non_files.append(rest)
                    break
                if ch == "i":
                    if (not rest and verb == "sed" and j + 1 < len(words)
                            and _is_backup_suffix(words[j + 1])):
                        j += 1
                        non_files.append(words[j])
                    break
            j += 1
            continue
        positional.append(w)
        j += 1
    if not script_given and positional:
        non_files.append(positional[0])
    return non_files


def _same_word(a, b):
    return a == b or a.replace("\\", "") == b.replace("\\", "")


def _in_place_files(segment, verb):
    pending = [w for w in _in_place_non_files(segment, verb) if w]
    out = []
    for token in hook_shell.file_operands(segment):
        hit = next((i for i, w in enumerate(pending) if _same_word(w, token)), None)
        if hit is None:
            out.append(token)
        else:
            pending.pop(hit)
    return out


def _in_place(segment, verb):
    if hook_shell.has_flag(segment, *IN_PLACE_VERBS[verb]):
        return True
    return any(w.startswith("--in-place=") for w in hook_shell.act_view(segment).split())


def _tar_mode(segment):
    view_tokens, _raw = _tokens(segment)
    for idx, vt in enumerate(view_tokens[1:], start=1):
        vt = vt.lstrip("({")
        if not vt:
            continue
        if vt.startswith("--create"):
            return "c"
        if vt.startswith("--extract") or vt.startswith("--get"):
            return "x"
        if vt.startswith("-") and not vt.startswith("--"):
            letters = vt[1:]
            if "c" in letters:
                return "c"
            if "x" in letters:
                return "x"
            continue
        if idx == 1 and vt.isalpha():
            if "c" in vt:
                return "c"
            if "x" in vt:
                return "x"
        break
    return ""


def _tar_flag_value(segment, letter, long_name=None):
    view_tokens, raw_tokens = _tokens(segment)
    for idx, (vt, rt) in enumerate(zip(view_tokens, raw_tokens)):
        vt = vt.lstrip("({")
        if idx == 1 and vt and not vt.startswith("-") and vt.isalpha() and letter in vt:
            return raw_tokens[idx + 1].strip("'\"") if idx + 1 < len(raw_tokens) else None
    value = _bundled_cluster_value(segment, letter)
    if value is not None:
        return value
    return _short_value(segment, letter, long_name)


def _tar_targets(segment, cwd):
    mode = _tar_mode(segment)
    if mode == "c":
        value = _tar_flag_value(segment, "f", "file")
        if value is None:
            return []
        p = _resolve(value, cwd)
        return [p] if p else []
    if mode == "x":
        archive = _tar_flag_value(segment, "f", "file")
        directory = _tar_flag_value(segment, "C", "directory")
        if directory is not None:
            p = _resolve(directory, cwd)
            return [p] if p else []
        out = []
        for member in hook_shell.file_operands(segment):
            if member == archive:
                continue
            p = _resolve(member, cwd)
            if p:
                out.append(p)
        return out
    return []


def _unzip_targets(segment, cwd):
    value = _short_value(segment, "d")
    if value is None:
        return []
    p = _resolve(value, cwd)
    return [p] if p else []


def _patch_targets(segment, cwd):
    value = _short_value(segment, "o", "output")
    if value is not None:
        p = _resolve(value, cwd)
        return [p] if p else []
    excluded = _input_redirect_targets(segment)
    operands = [t for t in hook_shell.file_operands(segment) if t not in excluded]
    if not operands:
        return []
    p = _resolve(operands[0], cwd)
    return [p] if p else []


def _dd_targets(segment, cwd):
    for token in hook_shell.file_operands(segment):
        if token.startswith("of=") and len(token) > 3:
            p = _resolve(token[3:], cwd)
            return [p] if p else []
    return []


def _ln_single_operand_target(operand, cwd):
    base = os.path.basename(operand.rstrip("/"))
    if not base:
        return None
    return _resolve(base, cwd)


def _interpreter_lang(verb):
    verb = (verb or "").rsplit("/", 1)[-1]
    if _PY_INTERPRETERS.match(verb):
        return "py"
    if verb in _NODE_INTERPRETERS:
        return "node"
    return None


def _program_targets(program, lang, cwd):
    if not isinstance(program, str) or not program:
        return []
    found = []
    if lang == "py":
        for rx in _PY_WRITES:
            for m in rx.finditer(program):
                mode = m.groupdict().get("m")
                if mode is not None and not any(c in mode for c in "wax+"):
                    continue
                found.append(m.group("p"))
        for m in _PY_DEST.finditer(program):
            found.append(m.group("p"))
    elif lang == "node":
        for m in _NODE_WRITES.finditer(program):
            found.append(m.group("p"))
    out = []
    for token in found:
        p = _resolve(token, cwd)
        if p and p not in out:
            out.append(p)
    return out


def _interpreter_targets(argv, cwd):
    if not argv:
        return []
    lang = _interpreter_lang(argv[0])
    if not lang:
        return []
    flags = ("-c",) if lang == "py" else ("-e", "--eval", "-p", "--print")
    for i, word in enumerate(argv[1:], start=1):
        if word in flags and i + 1 < len(argv):
            return _program_targets(argv[i + 1], lang, cwd)
        if lang == "py" and word.startswith("-") and not word.startswith("--") \
                and word.endswith("c") and len(word) > 2 and i + 1 < len(argv):
            return _program_targets(argv[i + 1], lang, cwd)
        if not word.startswith("-"):
            return []
    return []


def _scan(cmd, cwd, _depth=0):
    if not isinstance(cmd, str) or not cmd.strip() or hook_shell is None:
        return []

    out = []

    def add(path):
        if path and path not in out:
            out.append(path)

    try:
        pairs = hook_shell.statements_with_cwd(cmd, cwd)
    except Exception:
        return []

    for statement, scwd in pairs[:MAX_STATEMENTS]:
        for segment in (hook_shell.pipe_segments(statement) or [statement]):
            try:
                verb = (hook_shell.command_word(segment) or "").rsplit("/", 1)[-1]
            except Exception:
                continue

            for target in hook_shell.redirect_targets(segment):
                add(_resolve(target, scwd))

            if verb in IN_PLACE_VERBS:
                if _in_place(segment, verb):
                    for token in _in_place_files(segment, verb):
                        add(_resolve(token, scwd))
                continue

            if verb == "dd":
                for p in _dd_targets(segment, scwd):
                    add(p)
                continue

            if verb == "tar":
                for p in _tar_targets(segment, scwd):
                    add(p)
                continue

            if verb == "unzip":
                for p in _unzip_targets(segment, scwd):
                    add(p)
                continue

            if verb == "patch":
                for p in _patch_targets(segment, scwd):
                    add(p)
                continue

            if verb in LAST_OPERAND_VERBS:
                if verb in _TARGET_DIR_VERBS:
                    target_dir = _short_value(segment, "t", "target-directory")
                    if target_dir is not None:
                        add(_resolve(target_dir, scwd))
                        continue
                operands = hook_shell.file_operands(segment)
                if not operands:
                    continue
                if verb == "ln" and len(operands) == 1:
                    add(_ln_single_operand_target(operands[0], scwd))
                    continue
                if len(operands) < 2:
                    continue
                last = operands[-1]
                if verb == "rsync" and _is_remote_spec(last):
                    continue
                add(_resolve(last, scwd))
                continue

            if verb in ALL_OPERANDS_VERBS:
                tokens = [t for t in hook_shell.file_operands(segment)
                         if not _KEY_VALUE_RE.match(t)]
                if verb == "truncate":
                    tokens = _truncate_operands(segment)
                for token in tokens:
                    add(_resolve(token, scwd))

    for statement, scwd in pairs[:MAX_STATEMENTS]:
        try:
            argvs = hook_shell.invocations(statement)
        except Exception:
            argvs = []
        for argv in argvs:
            for p in _interpreter_targets(argv, scwd):
                add(p)
    try:
        fed = hook_shell.fed_texts_with_cwd(cmd, cwd)
    except Exception:
        fed = []
    for verb, text, fcwd in fed:
        lang = _interpreter_lang(verb)
        if lang:
            for p in _program_targets(text, lang, fcwd):
                add(p)

    if _depth < _MAX_UNWRAP_DEPTH:
        try:
            argvs = hook_shell.invocations(cmd)
        except Exception:
            argvs = []
        for argv in argvs:
            if not argv or argv[0] not in _WRAP_VERBS:
                continue
            script = next((w for w in argv[1:] if w and not w.startswith("-")), None)
            if not script or script == cmd:
                continue
            for p in _scan(script, cwd, _depth + 1):
                add(p)

    return out


def write_targets(cmd, cwd):
    return _scan(cmd, cwd)
