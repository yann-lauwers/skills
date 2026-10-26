"""Whether a shell command only reads, walks a tree, or follows links — read off its words, never run."""
import re
import shlex

import hook_shell as hs


# Verbs that only ever read. The widened paths grant on this closed set alone
# (law 3 — the allowlist goes on the closed side): the set of readers is small
# and known, the set of writers is not, so a verb nobody enumerated fails toward
# asking rather than toward a grant.
READ_VERBS = {
    "grep", "egrep", "fgrep", "rg", "cat", "head", "tail", "sed", "wc", "ls",
    "find", "file", "stat", "diff", "cmp", "sort", "uniq", "cut", "tr", "jq",
    "nl", "basename", "dirname", "readlink", "realpath", "echo", "printf",
    "true", "test", "which", "command", "column", "rev", "od", "xxd", "strings",
}

# Two readers that become writers under a flag. Rejected on sight rather than
# parsed: the spellings are many (`-i`, `-i''`, `-i.bak`, `-ni`) and a missed one
# grants a write.
_HARMLESS_REDIRECT = re.compile(
    r"(?<!\S)(?:[0-9&]?>>?\s*/dev/null|[0-9]?>&(?:[0-9]+|-))(?=\s|$|[;&|)])")
_SUBSTITUTION = re.compile(r"<\(|>\(|\$\(|`")
_SED_PRINT_SCRIPT = re.compile(r"^(?:\$|\d+(?:,(?:\d+|\$))?|/[^/]*/(?:,/[^/]*/)?)?p$")
_FIND_ACTIONS = {"-delete", "-exec", "-execdir", "-ok", "-okdir", "-fprint", "-fprint0", "-fprintf", "-fls",
                 "-fprint", "-fprintf", "-fls"}


def _segment_reads_only(segment):
    verb = hs.command_word(segment)
    if verb is None:
        return False                      # an empty parse is "I don't know"
    if verb == "cd":
        return True                       # movement, not a read or a write
    if verb not in READ_VERBS:
        return False
    tokens = segment.split()
    operands = [t for t in tokens[1:] if not t.startswith("-")]
    if verb == "find" and any(t in _FIND_ACTIONS for t in tokens):
        return False
    if verb == "sort" and any(t == "-o" or t.startswith(("-o", "--output", "--compress")) for t in tokens):
        return False
    if verb == "file" and any(t in ("-C", "--compile") or t.startswith("-m") for t in tokens):
        return False
    if verb in ("uniq", "xxd") and len(operands) > 1:
        return False
    if verb == "rg" and any(t.startswith("--pre") for t in tokens):
        return False
    return True


def _sed_prints_only(statement):
    try:
        words = shlex.split(statement)
    except ValueError:
        return False
    scripts, flags = [], set()
    for w in words[1:]:
        if w.startswith("-"):
            flags.add(w)
        elif not scripts:
            scripts.append(w)
    return flags <= {"-n", "-E", "-r"} and "-n" in flags and len(scripts) == 1 \
        and bool(_SED_PRINT_SCRIPT.match(scripts[0]))


def _segments(command):
    for _, statement in hs.statements(command):
        for segment in hs.act_view(statement).split("|"):
            if segment.strip():
                yield segment


def _pipeline_members(command):
    for _, statement in hs.statements(command):
        start = 0
        for pipe in [i for i, c in enumerate(hs.act_view(statement)) if c == "|"] + [len(statement)]:
            if statement[start:pipe].strip():
                yield statement[start:pipe]
            start = pipe + 1


def reads_only(command):
    """Every command in every statement, pipeline members included, is a reader.

    A statement is not split on `|` upstream — `file_operands` stops at the pipe
    instead — so a pipeline's later members are invisible to the operand walk.
    They are not invisible to this one: `grep x . | tee out` writes, and reading
    only its first verb would grant it.
    """
    try:
        if _SUBSTITUTION.search(command) or ">" in _HARMLESS_REDIRECT.sub("", command):
            return False
        if any(hs.command_word(member) == "sed" and not _sed_prints_only(member)
               for member in _pipeline_members(command)):
            return False
        return all(_segment_reads_only(segment) for segment in _segments(command))
    except Exception:
        return False


# Which readers walk a tree. Complete over READ_VERBS, which is what makes the
# enumeration honest: a directory operand is only a whole-tree read when the verb
# descends into it, and `ls lib/` reads the directory's own entries — a path the
# host's deny patterns already match directly.
_RECURSE_ALWAYS = {"find", "rg"}
_RECURSE_FLAGGED = {"grep": ("-r", "-R", "--recursive", "--dereference-recursive"),
                    "egrep": ("-r", "-R", "--recursive"),
                    "fgrep": ("-r", "-R", "--recursive"),
                    "ls": ("-R", "--recursive"),
                    "diff": ("-r", "--recursive")}
_FOLLOW_LINKS_FLAGGED = {"grep": ("-R", "--dereference-recursive"),
                         "egrep": ("-R", "--dereference-recursive"),
                         "fgrep": ("-R", "--dereference-recursive"),
                         "rg": ("-L", "--follow"),
                         "ls": ("-L", "--dereference"),
                         "diff": ("-r", "--recursive")}
_FIND_FOLLOWS_LINKS = {"-L", "-follow"}


def _carries_flag(segment, flags):
    for token in segment.split():
        if not token.startswith("-"):
            continue
        if token in flags:
            return True
        # A bundled short flag: `-rn` carries `-r`. Long options are excluded so
        # `--regexp=r` is not read as recursion.
        if not token.startswith("--") and any(
                f[1:] in token[1:] for f in flags if len(f) == 2):
            return True
    return False


def _segment_walks_tree(segment):
    verb = hs.command_word(segment)
    if verb is None:
        return True                       # an empty parse is "I don't know"
    if verb == "cd":
        return False                      # movement, and its operand is the root
    if verb in _RECURSE_ALWAYS:
        return True
    flags = _RECURSE_FLAGGED.get(verb)
    if flags is None:
        return verb not in READ_VERBS     # closed set: everything else stays put
    return _carries_flag(segment, flags)


def walks_tree(command):
    """Does any command here descend into a directory operand?

    True is the conservative answer — it routes a directory operand through the
    reachability test, which grants less. So an unrecognised verb walks.
    """
    try:
        return any(_segment_walks_tree(segment) for segment in _segments(command))
    except Exception:
        return True


def _segment_follows_links(segment):
    verb = hs.command_word(segment)
    if verb == "find":
        return any(token in _FIND_FOLLOWS_LINKS for token in segment.split())
    flags = _FOLLOW_LINKS_FLAGGED.get(verb)
    return flags is not None and _carries_flag(segment, flags)


def follows_links(command):
    try:
        return any(_segment_follows_links(segment) for segment in _segments(command))
    except Exception:
        return True
