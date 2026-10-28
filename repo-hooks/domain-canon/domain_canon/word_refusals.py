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


def unplaced_read(check_id, tool, root, rel_dir, operand, missing):
    where = "this repository" if rel_dir == "." else f"{rel_dir}/"
    plural = "s" if len(missing) != 1 else ""
    one_call_each = " one call per line" if len(missing) > MAX_OPERANDS else ""
    return (f"[{check_id}] `{operand}` names a path this check cannot resolve — a variable "
            f"set outside this command, a substitution, or a `cd` into one — so it cannot rule "
            f"out governed code under {where}. {len(missing)} canon file{plural} governing "
            f"that path {'are' if len(missing) != 1 else 'is'} unread this session:\n"
            + "".join(f"  {c}\n" for c in missing)
            + f"Read them, then retry this {tool}{one_call_each}:\n" + _cat_lines(root, missing)
            + WHAT_COUNTS + " Spelling the path out literally, or assigning it inside the same "
            "command, lets the check place it instead.")


def over_parse_cap(check_id):
    return (f"[{check_id}] This command is past what the canon check reads "
            f"({MAX_STATEMENTS} statements, {MAX_OPERANDS} operands each). "
            f"Split it into shorter commands and retry.")


def reminder(check_id, subject, fresh):
    return (f"[{check_id}] " + _listing(subject, fresh)
            + "A change to it is refused until each is read. " + WHAT_COUNTS
            + " Until then, carry on without mentioning this.")
