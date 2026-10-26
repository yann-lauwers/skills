#!/usr/bin/env python3

import os
import re
import shlex

_SEP_RE = re.compile(r"(?:\|\||&&|;|(?<![<>])&(?![&>])|\n)")

_INNER_POS_RE = re.compile(r"(?:^|[\s;&|])(?:[({]|(?:do|then|else|elif|in)\b)")

_WRAPPERS = frozenset((
    "sudo", "env", "xargs", "nohup", "time", "command", "builtin", "exec",
    "stdbuf", "timeout", "nice", "ionice", "setsid", "doas",
))

_ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")

_LEADING_GROUP = "({"
_TRAILING_GROUP = ")};"

_REDIRECT_RE = re.compile(r"(?<![0-9<>])>{1,2}(?!&)|(?<![0-9<>])>&|\|")

_REDIRECT_OP_RE = re.compile(r"[0-9]?>{1,2}\|?(?!&)")
_REDIRECT_WORD_END = frozenset(";&|<>()")


def strip_quoted_spans(cmd):
    return _mask_quotes(cmd or "", None)[0]


_HEREDOC_OP_RE = re.compile(
    r"(?<!<)<<(-?)(?!<)\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2")


def strip_heredocs(cmd):
    if not cmd or "<<" not in cmd:
        return cmd or ""
    out = list(cmd)
    lines = cmd.split("\n")
    starts, pos = [], 0
    for line in lines:
        starts.append(pos)
        pos += len(line) + 1

    quote = None
    pending = []
    i = 0
    while i < len(lines):
        line, base = lines[i], starts[i]
        if pending:
            tag, dash = pending[0]
            candidate = line.lstrip("\t") if dash else line
            if candidate == tag:
                pending.pop(0)
            else:
                for j in range(base, base + len(line)):
                    out[j] = " "
            i += 1
            continue

        masked, quote = _mask_quotes(line, quote)
        for m in _HEREDOC_OP_RE.finditer(line):
            if masked[m.start()] != line[m.start()]:
                continue
            pending.append((m.group(3), bool(m.group(1))))
        i += 1

    return "".join(out)


def _mask_quotes(line, quote):
    out = list(line)
    i = 0
    while i < len(line):
        ch = line[i]
        if quote is None:
            if ch in ("'", '"'):
                quote = ch
        elif ch == quote:
            quote = None
        elif quote == '"' and ch == "\\" and i + 1 < len(line):
            out[i] = out[i + 1] = " "
            i += 2
            continue
        if quote is not None or ch in ("'", '"'):
            out[i] = " "
        i += 1
    return "".join(out), quote


def act_view(cmd):
    return strip_quoted_spans(strip_heredocs(cmd or ""))


def statements(cmd):
    if not cmd:
        return []
    view = act_view(cmd)
    spans, last = [], 0
    for m in _SEP_RE.finditer(view):
        spans.append((last, cmd[last:m.start()], view[last:m.start()]))
        last = m.end()
    spans.append((last, cmd[last:], view[last:]))
    return [(off, text) for off, text, vtext in spans if vtext.strip()]


def _cd_target(statement, cwd):
    tokens = [t for t in act_view(statement).split() if t.strip(_LEADING_GROUP)]
    if tokens and "-" in tokens[1:]:
        return None
    args = operands(statement)
    if not args:
        return os.path.expanduser("~")
    target = args[0]
    if "$" in target or "`" in target:
        return None
    if target.startswith("~"):
        return os.path.normpath(os.path.expanduser(target))
    if os.path.isabs(target):
        return os.path.normpath(target)
    if cwd is None:
        return None
    return os.path.normpath(os.path.join(cwd, target))


def statements_with_cwd(cmd, cwd):
    return [(statement, at) for _off, statement, at in _spans_with_cwd(cmd, cwd)]


def _spans_with_cwd(cmd, cwd):
    out = []
    for off, statement in statements(cmd):
        out.append((off, statement, cwd))
        if command_word(statement) == "cd":
            cwd = _cd_target(statement, cwd)
    return out


def fed_texts_with_cwd(cmd, cwd):
    spans = _spans_with_cwd(cmd, cwd)
    out = []
    for at, verb, text in _fed_texts_at(cmd):
        where = cwd
        for off, _statement, span_cwd in spans:
            if off > at:
                break
            where = span_cwd
        out.append((verb, text, where))
    return out


def pipe_segments(statement):
    if not statement:
        return []
    view = act_view(statement)
    out, last = [], 0
    for m in re.finditer(r"(?<!>)\|(?!\|)", view):
        out.append(statement[last:m.start()])
        last = m.end()
    out.append(statement[last:])
    return [s for s in out if s.strip()]


def command_positions(cmd):
    if not cmd:
        return set()
    positions = {off for off, _ in statements(cmd)}
    view = act_view(cmd)
    for m in _INNER_POS_RE.finditer(view):
        positions.add(m.end())
    return positions


_WRAPPER_VALUED = {
    "sudo": frozenset(("-u", "-g", "-C", "-D", "-h", "-p", "-U", "-r", "-t", "--chdir")),
    "doas": frozenset(("-u", "-C")),
    "env": frozenset(("-u", "-C", "-S", "--unset", "--chdir", "--split-string")),
    "xargs": frozenset(("-n", "-I", "-i", "-L", "-l", "-P", "-d", "-E", "-e", "-s", "-a",
                        "--max-args", "--max-procs", "--delimiter", "--arg-file")),
    "nice": frozenset(("-n", "--adjustment")),
    "ionice": frozenset(("-c", "-n", "-p", "-t")),
    "timeout": frozenset(("-s", "-k", "--signal", "--kill-after")),
    "stdbuf": frozenset(("-i", "-o", "-e")),
    "exec": frozenset(("-a",)),
}

_KEYWORDS = frozenset(("if", "then", "else", "elif", "do", "while", "until", "!"))


def _verb_index(tokens, thorough=False):
    i, wrapper = 0, None
    while i < len(tokens):
        token = tokens[i].lstrip(_LEADING_GROUP).strip()
        if not token:
            i += 1
            continue
        if thorough and token in _KEYWORDS:
            i += 1
            continue
        if token.startswith("-"):
            if thorough and wrapper and token in _WRAPPER_VALUED.get(wrapper, ()):
                i += 1
            i += 1
            continue
        if _ASSIGN_RE.match(token):
            i += 1
            continue
        if thorough:
            token = token.rsplit("/", 1)[-1]
        if token in _WRAPPERS:
            wrapper = token
            i += 1
            if thorough and token == "timeout":
                while i < len(tokens) and tokens[i].startswith("-"):
                    i += 2 if tokens[i] in _WRAPPER_VALUED["timeout"] else 1
                i += 1
            continue
        if (thorough and token == "keyless" and i + 1 < len(tokens)
                and tokens[i + 1] == "run"):
            try:
                i = tokens.index("--", i + 2) + 1
            except ValueError:
                return None
            wrapper = None
            continue
        return i
    return None


def command_word(statement):
    if not statement:
        return None
    tokens = act_view(statement).split()
    i = _verb_index(tokens)
    if i is None:
        return None
    return tokens[i].lstrip(_LEADING_GROUP).strip().rsplit("/", 1)[-1].lstrip("\\")


def has_pipe_or_redirect(statement):
    return bool(_REDIRECT_RE.search(act_view(statement or "")))


def redirect_targets(statement):
    if not statement:
        return []
    view = act_view(statement)
    out = []
    for m in _REDIRECT_OP_RE.finditer(view):
        raw = _redirect_word(statement, m.end())
        if raw:
            out.append(raw)
    return out


def _redirect_word(statement, at):
    n = len(statement)
    i = at
    while i < n and statement[i] in " \t":
        i += 1
    word = []
    while i < n:
        ch = statement[i]
        if ch in "'\"":
            close = statement.find(ch, i + 1)
            if close < 0:
                return ""
            word.append(statement[i + 1:close])
            i = close + 1
            continue
        if ch.isspace() or ch in _REDIRECT_WORD_END:
            break
        word.append(ch)
        i += 1
    raw = "".join(word).lstrip(_LEADING_GROUP).rstrip(_TRAILING_GROUP)
    return raw


def has_flag(statement, *names):
    tokens = act_view(statement or "").split()
    wanted = set(names)
    for token in tokens:
        token = token.rstrip(_TRAILING_GROUP)
        if token in wanted:
            return True
        if (len(token) > 1 and token[0] == "-" and not token.startswith("--")
                and any(n.startswith("-") and len(n) == 2 and n[1] in token[1:]
                        for n in wanted)):
            return True
    return False


_SHELL_PUNCT_RE = re.compile(
    r"""^(?:[0-9]?[<>]{1,2}&?[0-9]*|\||&&?|;|<<-?['"]?[A-Za-z_][A-Za-z0-9_]*['"]?)$""")


def file_operands(statement):
    if not statement:
        return []
    drop = set(redirect_targets(statement))
    out = []
    for token in operands(statement):
        if token in ("|", "||", "&&", ";"):
            break
        if _SHELL_PUNCT_RE.match(token):
            continue
        if _REDIRECT_OP_RE.match(token):
            continue
        if token in drop:
            continue
        out.append(token)
    return out


_SHELLS = frozenset(("sh", "bash", "zsh", "dash", "ksh"))

_PIPE_START_RE = re.compile(r"(?<!>)\|(?!\|)")
_SEGMENT_END_RE = re.compile(r"[;|\n)`]|(?<![<>])&(?!>)")

_REDIRECTION_RE = re.compile(
    r"(?:(?<![^\s;&|(){}])[0-9]+)?(?:&>>?|<<<|<<-?|<>|>\||[<>]{1,2})(?!\()(&(?:[0-9]+-?|-))?")


def _word_end(raw, at):
    n, i = len(raw), at
    while i < n and raw[i] in " \t":
        i += 1
    while i < n:
        ch = raw[i]
        if ch in "'\"":
            close = raw.find(ch, i + 1)
            if close < 0:
                return n
            i = close + 1
            continue
        if ch.isspace() or ch in _REDIRECT_WORD_END:
            break
        i += 1
    return i


def _without_redirections(raw, view):
    out = list(raw)
    for m in _REDIRECTION_RE.finditer(view):
        start = m.start()
        end = m.end() if m.group(1) else _word_end(raw, m.end())
        for i in range(start, min(end, len(out))):
            out[i] = " "
    return "".join(out)
_HEREDOC_RE = re.compile(r"<<(?!<)-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
_HERESTRING_RE = re.compile(r"<<<\s*")

_INVOCATION_DEPTH = 3


def _argv(raw):
    import shlex
    try:
        return shlex.split(raw, comments=False, posix=True)
    except ValueError:
        return raw.split()


def _substitution_view(cmd):
    text = strip_heredocs(cmd)
    out, quote = list(text), None
    for i, ch in enumerate(text):
        if quote is None and ch == "'":
            quote = "'"
            out[i] = " "
        elif quote == "'":
            out[i] = " "
            if ch == "'":
                quote = None
        elif ch == '"':
            quote = None if quote == '"' else ('"' if quote is None else quote)
    return "".join(out)


def _substitutions(cmd):
    view = _substitution_view(cmd)
    bodies, i = [], 0
    while i < len(view):
        if view.startswith("$(", i) and not view.startswith("$((", i):
            depth, j = 1, i + 2
            while j < len(view) and depth:
                depth += {"(": 1, ")": -1}.get(view[j], 0)
                j += 1
            bodies.append(cmd[i + 2:j - 1 if depth == 0 else j])
            i += 2
            continue
        if view[i] == "`":
            j = view.find("`", i + 1)
            j = len(view) if j < 0 else j
            bodies.append(cmd[i + 1:j])
            i = j + 1
            continue
        i += 1
    return bodies


def _fed_start(view, start, at):
    outer, tick = [], False
    for i in range(start, at):
        ch = view[i]
        if ch in "({":
            outer.append(start)
            start = i + 1
        elif ch in ")}":
            start = outer.pop() if outer else start
        elif ch == "`":
            if tick:
                start = outer.pop() if outer else start
            else:
                outer.append(start)
                start = i + 1
            tick = not tick
        elif ch in ";|" or (ch == "&" and view[i - 1:i] not in ("<", ">")
                            and view[i + 1:i + 2] != ">"):
            start = i + 1
    return start


def _fed_verbs(cmd, view, at):
    start = _fed_start(view, cmd.rfind("\n", 0, at) + 1, at)
    text = cmd[start:at]
    out = []
    words = _argv(text)
    k = _verb_index(words, thorough=True)
    if k is not None:
        out.append(words[k].rstrip(_TRAILING_GROUP).rsplit("/", 1)[-1])
    if ")" in view[start:at] or "}" in view[start:at]:
        for _off, statement in statements(text):
            word = (command_word(statement) or "").rstrip(_TRAILING_GROUP)
            if word:
                out.append(word)
    out.extend(_launched_shell(words))
    return list(dict.fromkeys(w for w in out if w))


def _launched_shell(words):
    out = []
    for i, word in enumerate(words):
        base = word.rsplit("/", 1)[-1]
        if base in ("sudo", "doas", "su") and any(
                w in ("-s", "-i") or (w.startswith("-") and not w.startswith("--")
                                      and ("s" in w[1:] or "i" in w[1:]))
                for w in words[i + 1:]):
            out.append("sh")
        if base == "env":
            for j, flag in enumerate(words[i + 1:], i + 1):
                value = None
                if flag in ("-S", "--split-string") and j + 1 < len(words):
                    value = words[j + 1]
                elif flag.startswith("-S") and len(flag) > 2:
                    value = flag[2:]
                elif flag.startswith("--split-string="):
                    value = flag.split("=", 1)[1]
                if value:
                    inner = _argv(value)
                    k = _verb_index(inner, thorough=True)
                    if k is not None:
                        out.append(inner[k].rsplit("/", 1)[-1])
    return out


def _fed_heredocs_at(cmd):
    view = act_view(cmd)
    out = []
    for m in _HEREDOC_RE.finditer(cmd):
        if view[m.start()] != "<":
            continue
        body = re.compile(r"\n(.*?)(?=\n[ \t]*%s\b)" % re.escape(m.group(2)), re.S)
        found = body.search(cmd, m.end())
        if not found:
            continue
        for verb in _fed_verbs(cmd, view, m.start()):
            out.append((m.start(), verb, found.group(1)))
    return out


def _fed_heredocs(cmd):
    return [(verb, body) for _at, verb, body in _fed_heredocs_at(cmd)]


def _fed_texts_at(cmd):
    view = act_view(cmd)
    out = _fed_heredocs_at(cmd)
    for m in _HERESTRING_RE.finditer(cmd):
        if view[m.start()] != "<":
            continue
        rest = _argv(cmd[m.end():])
        if not rest:
            continue
        for verb in _fed_verbs(cmd, view, m.start()):
            out.append((m.start(), verb, rest[0]))
    return out


def _fed_texts(cmd):
    return [(verb, text) for _at, verb, text in _fed_texts_at(cmd)]


_BODY_RUNNERS = _SHELLS | frozenset(("source", ".", "fish", "tcsh", "csh"))
INLINE_RUNNERS = frozenset(("source", "."))


def shell_heredocs(cmd):
    return [(verb, body) for verb, body in _fed_heredocs(cmd) if verb in _BODY_RUNNERS]


_SHELL_VALUED = frozenset(("-o", "+o", "-O", "+O", "--rcfile", "--init-file"))


def _script_of(argv):
    k = 1
    while k < len(argv):
        word = argv[k]
        if word in _SHELL_VALUED:
            k += 2
            continue
        if word == "--" or not word.startswith(("-", "+")):
            return None
        if word.startswith("-") and not word.startswith("--") and "c" in word[1:]:
            return argv[k + 1] if k + 1 < len(argv) else None
        k += 1
    return None


def invocations_with_prefix(cmd, _depth=0):
    if not cmd or _depth > _INVOCATION_DEPTH:
        return []
    view = act_view(cmd)
    starts = set(command_positions(cmd))
    for m in _PIPE_START_RE.finditer(view):
        starts.add(m.end())
    out = []

    def add(pairs):
        for pair in pairs:
            if pair not in out:
                out.append(pair)

    for start in sorted(starts):
        end_m = _SEGMENT_END_RE.search(view, start)
        end = end_m.start() if end_m else len(cmd)
        if not view[start:end].strip():
            continue
        words = _argv(_without_redirections(cmd[start:end], view[start:end])
                      .lstrip().lstrip(_LEADING_GROUP))
        i = _verb_index(words, thorough=True)
        if i is None:
            continue
        prefix, argv = words[:i], words[i:]
        argv[0] = argv[0].rsplit("/", 1)[-1].lstrip("\\")
        add([(prefix, argv)])
        if argv[0] == "eval" and len(argv) > 1:
            add(invocations_with_prefix(" ".join(argv[1:]), _depth + 1))
        elif argv[0] in _SHELLS:
            script = _script_of(argv)
            if script:
                add(invocations_with_prefix(script, _depth + 1))
    for body in _substitutions(cmd):
        add(invocations_with_prefix(body, _depth + 1))
    for verb, text in _fed_texts(cmd):
        if verb in _SHELLS:
            add(invocations_with_prefix(text, _depth + 1))
    return out


def invocations(cmd):
    out = []
    for _prefix, argv in invocations_with_prefix(cmd):
        if argv not in out:
            out.append(argv)
    return out


def _shlex_operands(statement):
    try:
        tokens = shlex.split(statement, posix=True)
    except ValueError:
        tokens = statement.split()
    verb = _verb_index(tokens)
    if verb is None:
        return []
    out = []
    for token in tokens[verb + 1:]:
        stripped = token.lstrip(_LEADING_GROUP)
        if not stripped or stripped.startswith("-"):
            continue
        out.append(token.lstrip(_LEADING_GROUP).rstrip(_TRAILING_GROUP))
    return [t for t in out if t]


def operands(statement):
    if not statement:
        return []
    view_tokens = act_view(statement).split()
    raw_tokens = statement.split()
    if len(view_tokens) != len(raw_tokens):
        return _shlex_operands(statement)
    verb = _verb_index(view_tokens)
    if verb is None:
        return []
    out = []
    for view_token, raw_token in list(zip(view_tokens, raw_tokens))[verb + 1:]:
        stripped = view_token.lstrip(_LEADING_GROUP)
        if not stripped:
            continue
        if stripped.startswith("-"):
            continue
        out.append(raw_token.lstrip(_LEADING_GROUP).rstrip(_TRAILING_GROUP).strip("'\""))
    return [t for t in out if t]
