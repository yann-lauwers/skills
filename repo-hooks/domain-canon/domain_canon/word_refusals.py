import os
import shlex

from domain_canon.trace_shell_command import MAX_OPERANDS, MAX_STATEMENTS

WHAT_COUNTS = "Only a whole read counts: a file-read tool, or `cat` with no pipe or redirect."


def _listing(subject, missing):
    plural = "s" if len(missing) != 1 else ""
    return (f"{subject} sits under {len(missing)} canon file{plural} this session has not read:\n"
            + "".join(f"  {c}\n" for c in missing))


def _cat_lines(root, missing):
    paths = [shlex.quote(os.path.join(root, c)) for c in missing]
    return "".join("  cat " + " ".join(paths[i:i + MAX_OPERANDS]) + "\n"
                   for i in range(0, len(paths), MAX_OPERANDS))


def unread_canon(check_id, tool, root, rel, missing):
    one_call_each = " one call per line" if len(missing) > MAX_OPERANDS else ""
    return (f"[{check_id}] " + _listing(rel, missing)
            + f"Read them, then retry this {tool}{one_call_each}:\n"
            + _cat_lines(root, missing) + WHAT_COUNTS)


def over_parse_cap(check_id):
    return (f"[{check_id}] This command is past what the canon check reads "
            f"({MAX_STATEMENTS} statements, {MAX_OPERANDS} operands each). "
            f"Split it into shorter commands and retry.")


def reminder(check_id, subject, fresh):
    return (f"[{check_id}] " + _listing(subject, fresh)
            + "A change to it is refused until each is read. " + WHAT_COUNTS
            + " Until then, carry on without mentioning this.")
