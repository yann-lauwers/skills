import fnmatch
import glob
import itertools
import os
import re
import shlex

import hook_shell

PROGRAM_FIRST_VERBS = frozenset(("grep", "egrep", "fgrep", "rg", "awk", "sed", "jq"))
PROGRAM_FLAGS = ("-e", "-f", "--regexp", "--file", "--expression")
PATTERN_FLAGS = ("--regexp", "--expression")
INLINE_CODE_LETTERS = {
    "python": "c", "python3": "c", "sh": "c", "bash": "c", "zsh": "c",
    "node": "ep", "perl": "eE", "ruby": "e",
}
INLINE_CODE_LONG_FLAGS = {"node": ("--eval", "--print")}
INLINE_CODE_BUNDLE_LETTERS = {
    "python": "bBdEhiIOqsSuvx", "python3": "bBdEhiIOqsSuvx",
    "sh": "abefhkmnptuvxBCHPilrs", "bash": "abefhkmnptuvxBCHPilrs", "zsh": "abefhkmnptuvxBCHPilrs",
    "node": "", "perl": "aclnpsTtuUwWX", "ruby": "acdlnpswvy",
}
SHELL_SCOPE_VERBS = frozenset(("eval", "source", "."))
STABLE_ENV = ("HOME", "USER", "TMPDIR")
MAX_STATEMENTS = 20
MAX_OPERANDS = 40
MAX_EXPANSIONS = 40
MAX_GLOB_ENTRIES = 2000
COMPOUND_KEYWORD_PREFIX = re.compile(r"^\s*(?:(?:do|then|else|elif|if|while|until|!)\s+)+")
_VAR_RE = re.compile(r"\$(?:\{([A-Za-z_][A-Za-z0-9_]*)\}|([A-Za-z_][A-Za-z0-9_]*))")
_ASSIGNMENT_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$", re.S)
_REDIRECT_WORD_RE = re.compile(r"^\d*[<>]")
_REDIRECT_OPERATOR_RE = re.compile(r"\d*[<>]+[|&]?")
_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_SHORT_FLAGS_RE = re.compile(r"-[A-Za-z]+")
_PATTERN_CLUSTER_RE = re.compile(r"-[A-Za-z]*e")
_NAMED_VARIABLE_RE = re.compile(r"^[({]*([A-Za-z_][A-Za-z0-9_]*)(?:\[|\+?=|[)};]*$)")
_SCOPE_RE = re.compile(r"\$\{|(?<![^\s;&|()])(?:if|fi|case|esac|do|done)(?![^\s;&|()])|[(){}]")
_SCOPE_CLOSERS = {"fi": "if", "esac": "case", "done": "do", ")": "(", "}": "{"}


def shell_words(text):
    words, value, expands, globs, tilde, quote, started = {}, [], False, False, False, None, False
    tilde_prefix = False
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
                _merge_word(words, "".join(value), (expands, globs, tilde))
            value, expands, globs, tilde, started, tilde_prefix = [], False, False, False, False, False
        else:
            if (not started and ch == "~") or (ch == "~" and value[-1:] == ["="]):
                tilde = tilde_prefix = True
            elif tilde_prefix and ch == "/":
                tilde_prefix = False
            elif tilde_prefix and ch in "'\"$`\\":
                tilde = tilde_prefix = False
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
        _merge_word(words, "".join(value), (expands, globs, tilde))
    return words


def _merge_word(words, value, flags):
    seen = words.get(value, (False, False, False))
    words[value] = tuple(a or b for a, b in zip(seen, flags))


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
    matches = bounded_glob(pattern)
    if matches is None or len(matches) > MAX_EXPANSIONS:
        return None
    return sorted(matches) or [path]


def bounded_glob(pattern):
    found, scanned = [os.sep], 0
    for part in (p for p in pattern.split(os.sep) if p):
        if not glob.has_magic(part):
            found = [os.path.join(d, part) for d in found if os.path.lexists(os.path.join(d, part))]
            continue
        deeper = []
        for directory in found:
            try:
                names = os.listdir(directory)
            except OSError:
                continue
            scanned += len(names)
            if scanned > MAX_GLOB_ENTRIES:
                return None
            deeper.extend(os.path.join(directory, n) for n in fnmatch.filter(names, part)
                          if part.startswith(".") or not n.startswith("."))
        found = deeper
    return found


def bindings_certain(command):
    view = hook_shell.act_view(command)
    spans = hook_shell.statements(command)
    out = []
    for k, (offset, text) in enumerate(spans):
        before = view[spans[k - 1][0] + len(spans[k - 1][1]):offset] if k else ""
        end = offset + len(text)
        after = view[end:spans[k + 1][0] if k + 1 < len(spans) else len(view)].lstrip()
        lead = len(text) - len(text.lstrip(" \t({"))
        out.append("&&" not in before and "||" not in before
                   and not (after.startswith("&") and not after.startswith("&&"))
                   and "|" not in hook_shell.act_view(text).replace("||", "")
                   and not COMPOUND_KEYWORD_PREFIX.match(text)
                   and not _inside_scope(view[:offset + lead]))
    return out


def _inside_scope(view):
    depth = {}
    for m in _SCOPE_RE.finditer(view):
        token = m.group(0)
        if token == "${":
            depth["${"] = depth.get("${", 0) + 1
        elif token == "}" and depth.get("${"):
            depth["${"] -= 1
        elif token in _SCOPE_CLOSERS:
            opener = _SCOPE_CLOSERS[token]
            depth[opener] = max(0, depth.get(opener, 0) - 1)
        else:
            depth[token] = depth.get(token, 0) + 1
    return any(v for k, v in depth.items() if k != "${")


def forget_named(statement, known):
    for value in shell_words(statement):
        m = _NAMED_VARIABLE_RE.match(value)
        if m and m.group(1) in known:
            known[m.group(1)] = None


def bind_variables(statement, at, known, certain=True):
    statement = COMPOUND_KEYWORD_PREFIX.sub("", statement)
    words = [w for w in statement.split() if w]
    if not words:
        return
    if words[0] in SHELL_SCOPE_VERBS:
        for name in known:
            known[name] = None
        return
    if words[0] in ("read", "mapfile", "readarray"):
        for w in words[1:]:
            if not w.startswith("-"):
                known[w] = None
        return
    if words[0] == "for" and len(words) >= 3 and words[2] == "in":
        values = []
        for value, (expands, globs, tilde) in shell_words(" ".join(words[3:])).items():
            expanded = expand_word(value, known) if expands else [value]
            if expanded is not None and tilde:
                expanded = [os.path.expanduser(v) for v in expanded]
            if expanded is not None and globs:
                expanded = (None if at is None else
                            [m for v in expanded for m in (glob_operand(v, at) or [None])])
            if expanded is None or None in expanded or not certain:
                known[words[1]] = None
                return
            values.extend(expanded)
        known[words[1]] = values
        return
    if words[0] in ("export", "readonly") and all(_NAME_RE.fullmatch(w) for w in words[1:]):
        return
    if words[0] in ("export", "local", "declare", "typeset", "readonly"):
        statement = statement.split(None, 1)[1] if len(words) > 1 else ""
    parsed = shell_words(statement)
    assignments = [(_ASSIGNMENT_RE.match(v), info) for v, info in parsed.items()]
    if not certain or not assignments or not all(m for m, _info in assignments):
        forget_named(statement, known)
        for m, _info in assignments:
            if m:
                known[m.group(1)] = None
        return
    for m, (expands, _globs, tilde) in assignments:
        value = expand_word(m.group(2), known) if expands else [m.group(2)]
        if value is not None and tilde:
            value = [os.path.expanduser(v) for v in value]
        known[m.group(1)] = value if value is not None and len(value) == 1 else None


def inline_code(segment, verb):
    letters = INLINE_CODE_LETTERS.get(verb)
    if not letters:
        return None
    try:
        tokens = shlex.split(segment, posix=True)
    except ValueError:
        tokens = segment.split()
    longs = INLINE_CODE_LONG_FLAGS.get(verb, ())
    for word, following in zip(tokens, tokens[1:]):
        if word in longs or (_SHORT_FLAGS_RE.fullmatch(word) and word[-1] in letters
                             and all(c in INLINE_CODE_BUNDLE_LETTERS[verb] for c in word[1:-1])):
            return following
    return None


def pattern_values(segment):
    try:
        tokens = shlex.split(segment, posix=True)
    except ValueError:
        tokens = segment.split()
    return [following for word, following in zip(tokens, tokens[1:])
            if word in PATTERN_FLAGS or _PATTERN_CLUSTER_RE.fullmatch(word)]


def _without_word(raw, word):
    if word is None:
        return raw
    trimmed = word.lstrip("({").rstrip(")};").strip("'\"")
    for i, operand in enumerate(raw):
        if operand in (word, trimmed):
            return raw[:i] + raw[i + 1:]
    return raw


def segment_operands(segment, verb, known, base):
    raw = hook_shell.operands(segment)[:MAX_OPERANDS]
    if verb in PROGRAM_FIRST_VERBS:
        patterns = pattern_values(segment)
        if patterns:
            for pattern in patterns:
                raw = _without_word(raw, pattern)
        elif raw and not any(
                w in PROGRAM_FLAGS or w.startswith(("--regexp=", "--file=", "--expression="))
                for w in segment.split()):
            raw = raw[1:]
    else:
        raw = _without_word(raw, inline_code(segment, verb))
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
