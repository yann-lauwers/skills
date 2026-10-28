import glob
import itertools
import os
import re

import hook_shell

PROGRAM_FIRST_VERBS = frozenset(("grep", "egrep", "fgrep", "rg", "awk", "sed", "jq"))
PROGRAM_FLAGS = ("-e", "-f", "--regexp", "--file", "--expression")
INLINE_PROGRAM_VERBS = frozenset(("python", "python3", "node", "perl", "ruby", "sh", "bash", "zsh"))
INLINE_PROGRAM_FLAGS = ("-c", "-e", "-E")
STABLE_ENV = ("HOME", "USER", "TMPDIR")
MAX_STATEMENTS = 20
MAX_OPERANDS = 40
MAX_EXPANSIONS = 40
COMPOUND_KEYWORD_PREFIX = re.compile(r"^\s*(?:(?:do|then|else|elif|if|while|until|!)\s+)+")
_VAR_RE = re.compile(r"\$(?:\{([A-Za-z_][A-Za-z0-9_]*)\}|([A-Za-z_][A-Za-z0-9_]*))")
_ASSIGNMENT_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$", re.S)
_REDIRECT_WORD_RE = re.compile(r"^\d*[<>]")
_REDIRECT_OPERATOR_RE = re.compile(r"\d*[<>]+[|&]?")


def shell_words(text):
    words, value, expands, globs, tilde, quote, started = {}, [], False, False, False, None, False
    i = 0
    while i < len(text):
        ch = text[i]
        if quote == "'":
            if ch == "'":
                quote = None
            else:
                value.append(ch)
        elif quote == '"':
            if ch == '"':
                quote = None
            elif ch == "\\" and i + 1 < len(text) and text[i + 1] in '$`"\\':
                i += 1
                value.append(text[i])
            else:
                expands = expands or ch in "$`"
                value.append(ch)
        elif ch.isspace():
            if started:
                words["".join(value)] = (expands, globs, tilde)
            value, expands, globs, tilde, started = [], False, False, False, False
        else:
            if not started and ch == "~":
                tilde = True
            started = True
            if ch in "'\"":
                quote = ch
            elif ch == "\\" and i + 1 < len(text):
                i += 1
                value.append(text[i])
            else:
                expands = expands or ch in "$`"
                globs = globs or ch in "*?["
                value.append(ch)
        if quote:
            started = True
        i += 1
    if started:
        words["".join(value)] = (expands, globs, tilde)
    return words


def expand_word(value, known):
    if "`" in value or "$(" in value:
        return None
    choices, pieces, last = [], [], 0
    for m in _VAR_RE.finditer(value):
        name = m.group(1) or m.group(2)
        if name in known:
            options = known[name]
        elif name in STABLE_ENV and os.environ.get(name):
            options = [os.environ[name]]
        else:
            options = None
        if options is None:
            return None
        pieces.append(value[last:m.start()])
        choices.append(options)
        last = m.end()
    pieces.append(value[last:])
    if "$" in "".join(pieces):
        return None
    out = []
    for combo in itertools.product(*choices):
        out.append("".join(p + c for p, c in zip(pieces, combo)) + pieces[-1])
        if len(out) > MAX_EXPANSIONS:
            return None
    return out


def glob_operand(path, base):
    pattern = path if os.path.isabs(path) else os.path.join(base, path)
    matches = sorted(glob.glob(pattern))
    if len(matches) > MAX_EXPANSIONS:
        return None
    return matches or [path]


def bind_variables(statement, at, known):
    statement = COMPOUND_KEYWORD_PREFIX.sub("", statement)
    words = [w for w in statement.split() if w]
    if not words:
        return
    if words[0] in ("read", "mapfile", "readarray"):
        for w in words[1:]:
            if not w.startswith("-"):
                known[w] = None
        return
    if words[0] == "for" and len(words) >= 3 and words[2] == "in":
        values = []
        for value, (expands, globs, _tilde) in shell_words(" ".join(words[3:])).items():
            expanded = expand_word(value, known) if expands else [value]
            if expanded is not None and globs:
                expanded = (None if at is None else
                            [m for v in expanded for m in (glob_operand(v, at) or [None])])
            if expanded is None or None in expanded:
                known[words[1]] = None
                return
            values.extend(expanded)
        known[words[1]] = values
        return
    if words[0] in ("export", "local", "declare", "typeset", "readonly"):
        statement = statement.split(None, 1)[1] if len(words) > 1 else ""
    parsed = shell_words(statement)
    assignments = [(_ASSIGNMENT_RE.match(v), info) for v, info in parsed.items()]
    if not assignments or not all(m for m, _info in assignments):
        return
    for m, (expands, _globs, _tilde) in assignments:
        value = expand_word(m.group(2), known) if expands else [m.group(2)]
        known[m.group(1)] = value if value is not None and len(value) == 1 else None


def segment_operands(segment, verb, known, base):
    raw = hook_shell.operands(segment)[:MAX_OPERANDS]
    if verb in PROGRAM_FIRST_VERBS and raw and not any(
            w in PROGRAM_FLAGS or w.startswith(("--regexp=", "--file=", "--expression="))
            for w in segment.split()):
        raw = raw[1:]
    elif verb in INLINE_PROGRAM_VERBS and raw and any(w in INLINE_PROGRAM_FLAGS for w in segment.split()):
        raw = raw[1:]
    live = shell_words(segment)
    out, target_next = [], False
    for operand in raw:
        if target_next or _REDIRECT_WORD_RE.match(operand):
            target_next = bool(_REDIRECT_OPERATOR_RE.fullmatch(operand)) and not target_next
            out.append((operand, [operand]))
            continue
        expands, globs, tilde = live.get(operand, ("$" in operand or "`" in operand, False, False))
        paths = expand_word(operand, known) if expands else [operand]
        if paths is not None and tilde:
            paths = [os.path.expanduser(p) for p in paths]
        if paths is not None and base is None and any(not os.path.isabs(p) for p in paths):
            paths = None
        if paths is not None and globs:
            matched = [glob_operand(p, base or "/") for p in paths]
            paths = None if None in matched else [m for ms in matched for m in ms]
        out.append((operand, paths))
    return out


def literal_directory(operand, base, cwd):
    cut = min((operand.find(c) for c in "$`*?[" if c in operand), default=len(operand))
    prefix = os.path.expanduser(operand[:cut]) if operand.startswith("~") else operand[:cut]
    directory = prefix[:prefix.rfind("/") + 1] if "/" in prefix else ""
    if os.path.isabs(directory):
        return os.path.normpath(directory)
    return os.path.normpath(os.path.join(base if base is not None else cwd, directory))
