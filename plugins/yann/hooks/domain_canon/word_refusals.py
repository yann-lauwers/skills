import os
import shlex

PATHS_PER_CAT = 40
WHAT_COUNTS = "Only a whole read counts: a file-read tool, or `cat` with no pipe or redirect."


def _listing(subject, missing):
    plural = "s" if len(missing) != 1 else ""
    return (f"{subject} sits under {len(missing)} canon file{plural} this session has not read:\n"
            + "".join(f"  {c}\n" for c in missing))


def _cat_lines(root, missing):
    paths = [shlex.quote(os.path.join(root, c)) for c in missing]
    return "".join("  cat " + " ".join(paths[i:i + PATHS_PER_CAT]) + "\n"
                   for i in range(0, len(paths), PATHS_PER_CAT))


def unread_canon(check_id, tool, root, rel, missing):
    one_call_each = " one call per line" if len(missing) > PATHS_PER_CAT else ""
    return (f"[{check_id}] " + _listing(rel, missing)
            + f"Read them, then retry this {tool}{one_call_each}:\n"
            + _cat_lines(root, missing) + WHAT_COUNTS)


def reminder(check_id, subject, fresh):
    return (f"[{check_id}] " + _listing(subject, fresh)
            + "A change to it is refused until each is read. " + WHAT_COUNTS
            + " Until then, carry on without mentioning this.")
