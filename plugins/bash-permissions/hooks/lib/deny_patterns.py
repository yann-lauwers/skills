"""Whether a Read() deny pattern can match a path, or anything under a directory."""
import os
import re

GLOB_CHARS = re.compile(r"[*?\[]")


def _under(path, root):
    """Is `path` at or beneath `root`? Both absolute and already normalised."""
    path, root = path.casefold(), root.casefold()
    return path == root or path.startswith(root.rstrip(os.sep) + os.sep)


def _anchor(path):
    hit = GLOB_CHARS.search(path)
    return os.path.dirname(path[:hit.start()]) if hit else path


def _forms(path):
    return tuple(dict.fromkeys((os.path.normpath(path), os.path.realpath(path))))


def _pattern_forms(pat):
    out = []
    for form in (pat, os.path.normpath(pat)):
        out.append(form)
        if form.startswith(os.sep):
            anchor = _anchor(form)
            out.append(os.path.realpath(anchor) + form[len(anchor):])
    return tuple(dict.fromkeys(out))


def _owners(source):
    here = os.path.dirname(source)
    return (here, os.path.dirname(here))


def _anchored(pattern, source, bases=()):
    if pattern.startswith("//"):
        return (pattern[1:],)
    if pattern == "~" or pattern.startswith("~/"):
        return (os.path.expanduser(pattern),)
    roots = dict.fromkeys(_owners(source) + tuple(bases) + (
        os.path.join(os.path.expanduser("~"), ".claude"), os.sep))
    if pattern.startswith("/"):
        return tuple(os.path.join(root, pattern[1:]) for root in roots)
    rel = pattern[2:] if pattern.startswith("./") else pattern
    tail = rel
    while tail.startswith("**/"):
        tail = tail[3:]
    return ("*/" + tail,) + tuple(os.path.join(root, rel) for root in roots)


def _covering(path):
    while True:
        yield path
        parent = os.path.dirname(path)
        if parent == path:
            return
        path = parent


def pattern_can_match_under(directory, pattern, source, bases=()):
    """Could ANY path beneath `directory` match this deny pattern?

    True is the safe answer and the default: the caller reads it as no opinion,
    and the host asks exactly as it does today. False is a positive claim that a
    recursive read of this tree cannot reach a denied file, and it is returned
    only for a pattern anchored to an absolute prefix lying outside the tree.

    Unanchored patterns — `**/x`, or a bare relative one — bind at any depth, so
    they are always True. With a deny list written entirely in `**/` form every
    directory operand is therefore undecidable, which is the honest answer: the
    tree would have to be walked to do better, and that was measured too slow.
    """
    directory = os.path.normpath(directory)
    for pat in _anchored(pattern, source, bases):
        if not os.path.isabs(pat):
            return True
        for form in _pattern_forms(pat):
            anchor = _anchor(form)
            if _under(anchor, directory) or _under(directory, anchor):
                return True
    return False
