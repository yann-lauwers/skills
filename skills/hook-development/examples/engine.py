#!/usr/bin/env python3
"""Minimal single-engine hook skeleton.

One engine per event, not many scripts. Two hooks on the same event run in PARALLEL and
cannot see each other's output, so they cannot coordinate a verdict — the fix is one
emitter that runs every check, short-circuits on the first deny, and merges the rest.

Wire it for PreToolUse (see examples/settings-snippet.json), then add rows to CHECKS.

Everything project-specific lives in CONFIG and CHECKS. The rest is mechanism.

Run standalone to self-test:
    echo '{"hook_event_name":"PreToolUse","session_id":"s1","tool_name":"Bash",
           "tool_input":{"command":"rm -rf /"}}' | python3 engine.py
"""
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- config
CONFIG = {
    # Where per-session state lives. Resolved PER CALL, never at import, so a test that
    # redirects HOME after import lands in its sandbox instead of the real store.
    "state_root": lambda: os.path.join(
        os.environ.get("HOOK_STATE_ROOT") or os.path.expanduser("~/.hook-state")),
    # Observe markers live next to this file and are per-INSTALLATION state.
    # Add `.*-observe` to .gitignore and `git rm --cached` any that are already tracked.
    "marker_dir": HERE,
}


# ---------------------------------------------------------------- payload coercion
def s(v, default=""):
    """A payload field that MUST be a string. Non-str -> default, never a crash."""
    return v if isinstance(v, str) else default


def d(v):
    """A payload field that MUST be a mapping. Non-dict -> {}."""
    return v if isinstance(v, dict) else {}


# ---------------------------------------------------------------- shell views
_QUOTE_STATE = {"'": "'", '"': '"'}


def strip_quoted_spans(cmd):
    """Blank quoted spans, honouring backslash escapes.

    A naive `'[^']*'|"[^"]*"` regex is NOT shell-aware: it mishandles '\\'' concatenation
    and \\" escaping, so an escaped quote ends the span early and leaks the rest of a
    string into the view. Five copies of that regex produced measurable defects across two
    audits, so this exists once and everything calls it.
    """
    out, quote, i = [], None, 0
    while i < len(cmd):
        ch = cmd[i]
        if quote:
            if ch == "\\" and quote == '"' and i + 1 < len(cmd):
                out.append("  ")
                i += 2
                continue
            if ch == quote:
                quote = None
                out.append(" ")
            else:
                out.append(" " if ch != "\n" else "\n")
        elif ch in _QUOTE_STATE:
            quote = ch
            out.append(" ")
        else:
            out.append(ch)
        i += 1
    return "".join(out)


# A here-document operator. `(?<!<)` and `(?!<)` keep `<<<`, a here-string, out: it opens
# no body, and without the guards the regex matches from the second `<` and swallows the
# lines after it.
_HEREDOC_OP_RE = re.compile(
    r"(?<!<)<<(-?)(?!<)\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2")


# Every blanking here replaces a character with a space and keeps every newline, so the
# view is the same LENGTH as the raw command. That is not cosmetic: offsets from a match on
# one view are compared against command positions computed on another, and a substitution
# that changes length silently invalidates every such comparison.


def strip_heredocs(cmd):
    """Blank heredoc BODIES, length-preservingly — reading the way a shell reads.

    Line by line, because both halves of a here-document are a per-line question and a
    single regex over the whole command answers neither:

    THE OPERATOR. `echo '<<EOF'` is a string holding two angle brackets, not a redirection.
    A pattern that scans the whole command makes it one and blanks every line up to the
    next line reading `EOF` — so the command on the next line is read as nothing at all,
    which is a guard failing OPEN. Measured 2026-09-15 on one estate's own reader: a
    `git push --force` behind that line reached the act reader as `echo` and a bare `EOF`.
    So the operators are found on the raw line and dropped where the `<<` sits inside a
    quoted span, which is also why the tag survives: quoting the TAG (`<<'EOF'`) is
    ordinary, and masking the line before reading it loses the tag instead.

    THE TERMINATOR. A shell ends the body at a line that IS the tag. `  EOF` and `EOF-x`
    are body lines, and only `<<-` accepts leading TABS. Ending the body early leaves body
    text scanned as commands; a body with no terminator at all runs to the end of input,
    which is what the shell does with it.

    ORDER MATTERS: run this BEFORE stripping quotes. Quote-stripping first destroys the
    tag, the body is never recognised, and every trigger then scans documentation as if it
    were a command. Ask what a normalisation DESTROYS before choosing its order.
    """
    if not cmd or "<<" not in cmd:
        return cmd or ""
    out, lines, pos, starts = list(cmd), cmd.split("\n"), 0, []
    for line in lines:
        starts.append(pos)
        pos += len(line) + 1
    quote, pending, i = None, [], 0
    while i < len(lines):
        line, base = lines[i], starts[i]
        if pending:
            tag, dash = pending[0]
            if (line.lstrip("\t") if dash else line) == tag:
                pending.pop(0)
            else:
                for j in range(base, base + len(line)):
                    out[j] = " "
            i += 1
            continue
        masked, quote = _mask_quotes(line, quote)
        for m in _HEREDOC_OP_RE.finditer(line):
            if masked[m.start()] == line[m.start()]:
                pending.append((m.group(3), bool(m.group(1))))
        i += 1
    return "".join(out)


def _mask_quotes(line, quote):
    """One line with its quoted spans blanked, plus the quote state it leaves.

    Carried across lines, so a string opened on one line and closed on the next masks
    both halves. Body lines are never asked: a body is not shell text, and an apostrophe
    inside one opens nothing.
    """
    out, i = list(line), 0
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


def command_view(cmd):
    """The view a trigger should match an ACT on: heredoc bodies and quoted spans blanked,
    offsets identical to the raw command."""
    return strip_quoted_spans(strip_heredocs(cmd))


_CMD_SEP_RE = re.compile(
    r"(?:^|[;&|(){}]\s*|\n\s*|\bdo\s+|\bthen\s+|\belse\s+|"
    r"(?:sudo|env|xargs|nohup|command|time)\s+(?:-\S+\s+)*(?:\w+=\S+\s+)*)")


def command_positions(cmd):
    """Offsets where a shell would begin reading a COMMAND.

    Quoted spans are excluded, so a command name inside a string is never a command
    position. Wrapper words that TAKE a command are absorbed, so the position lands on the
    real verb. This is the single shared answer to "act or mention?" — when the same
    question is re-invented per check, the checks that skip it produce most of the false
    positives.
    """
    if not cmd:
        return set()          # no command text, no command positions — NOT offset 0
    return {m.end() for m in _CMD_SEP_RE.finditer(command_view(cmd))}


def at_command_position(cmd, match):
    """True when `match` (matched on the RAW command) starts where a command starts."""
    return match is not None and match.start() in command_positions(cmd)


# ---------------------------------------------------------------- state + logging
def _session_dir(sid, create=True):
    root = CONFIG["state_root"]()
    path = os.path.join(root, "sessions", re.sub(r"[^\w.-]", "_", str(sid))[:120])
    if create:
        os.makedirs(path, exist_ok=True)
    return path


def _field(v):
    """One log field: never a separator, never a newline, never None.

    A positional log with no escaping does not merely corrupt a field when a value carries
    a newline — it FORGES A WHOLE ROW, one that parses perfectly and is attributed to a
    component that never ran.
    """
    return str(v).replace("\t", " ").replace("\n", " ").replace("\r", " ")


def log_decision(sid, event, check_id, verdict, mode="enforce", actor="", subject=""):
    """Append one decision row. Fail-open: telemetry never suppresses a verdict."""
    try:
        row = "\t".join(_field(x) for x in (
            int(time.time()), sid, event, actor, check_id, mode, verdict, subject[:120]))
        with open(os.path.join(_session_dir(sid), "decisions"), "a") as fh:
            fh.write(row + "\n")
    except Exception:
        try:
            with open(os.path.join(CONFIG["state_root"](), "health"), "a") as fh:
                fh.write("log-write-failure\n")
        except Exception:
            pass


def observing(check_id):
    """True when this check is in RECORD-ONLY mode.

    One shared primitive, one semantic: observe records `would-<verdict>` and does not act.
    Left to per-check convention this drifts into three incompatible meanings and no two
    rollouts stay comparable. Only checks that can BLOCK get a marker — an advisory has no
    enforcement to withhold.
    """
    slug = re.sub(r"[^a-z0-9-]", "-", check_id.lower())
    return os.path.isfile(os.path.join(CONFIG["marker_dir"], ".%s-observe" % slug))


# ---------------------------------------------------------------- verdicts
class Verdict(object):
    def __init__(self, check_id, text, blocking=False, subject=""):
        self.id = check_id
        self.text = text
        self.blocking = blocking
        self.subject = subject


# ---------------------------------------------------------------- checks
# Each check takes the coerced payload and returns a Verdict or None.
# None means NO OPINION — the correct default whenever parsing produced nothing.

_DESTRUCTIVE = re.compile(r"rm\s+(?:-\w+\s+)*-\w*[rR]\w*f|rm\s+(?:-\w+\s+)*-\w*f\w*[rR]")


def check_destructive_root(ctx):
    """DENY: a recursive force delete whose own target is a protected root.

    Demonstrates the two-view rule: the ACT is matched on the stripped view and anchored to
    a command position, so `echo "rm -rf /"` and a heredoc naming it are silent; the
    OPERAND is then read from the RAW text, because stripping deletes quoted paths.
    """
    cmd = ctx["command"]
    if not cmd:
        return None
    act = _DESTRUCTIVE.search(command_view(cmd))
    # A match is only an ACT if it starts where a shell would begin reading a command.
    if not at_command_position(cmd, act):
        return None
    # Read the OPERAND from the raw text: stripping deletes quoted paths.
    # Tokenise and DROP FLAGS explicitly. A regex that tries to skip flags inline
    # (`rm\s+(?:-\S+\s+)*(\S+)`) silently captures the LAST FLAG as the target whenever the
    # command has no operand at all — so `rm -rf` parses as "delete the file named -rf",
    # the empty-parse guard below is never reached, and a test asserting "no opinion" here
    # passes for entirely the wrong reason.
    targets = []
    for seg in re.split(r"[;|&\n]", strip_heredocs(cmd)):
        toks = seg.strip().split()
        # `rm` need not be the first token: `sudo rm …`, `do rm …`, `/bin/rm …` are all
        # real invocations. Find the verb, then read the operands after it.
        idx = next((i for i, t in enumerate(toks)
                    if t == "rm" or t.endswith("/rm")), None)
        if idx is None:
            continue
        targets.extend(t for t in toks[idx + 1:] if not t.startswith("-"))
    if not targets:
        # Empty parse means "I could not tell what this touches" — never "it is safe".
        return None
    protected = {"/", os.path.expanduser("~"), os.path.expanduser("~") + "/"}
    for t in targets:
        if t.strip("'\"") in protected:
            return Verdict(
                "PROT-ROOT",
                "Refusing a recursive delete whose target is a protected root (%s). "
                "Name the specific subdirectory instead, e.g. `rm -rf %s/build`. "
                "If this is deliberate, re-issue the SAME command with DELETE_ACK=1."
                % (t, os.path.expanduser("~")),
                blocking=True, subject=t)
    return None


def check_stderr_discarded(ctx):
    """NUDGE: stderr sent to /dev/null as the act, which hides failures."""
    cmd = ctx["command"]
    if not cmd:
        return None
    view = command_view(cmd)
    if re.search(r"2>\s*/dev/null|2>>\s*/dev/null|&>\s*/dev/null|2>&-", view):
        return Verdict(
            "ERR-DISCARD",
            "This command sends stderr to /dev/null, which swallows diagnostics and turns "
            "a failure into apparent success. Use `2>&1` and inspect the captured output. "
            "If you only want the exit code and the output genuinely does not matter, take "
            "no action and do not mention this.",
            blocking=False, subject=cmd[:60])
    return None


CHECKS = [check_destructive_root, check_stderr_discarded]


# ---------------------------------------------------------------- emitters
def emit_deny(event, verdict):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": event,
        "permissionDecision": "deny",
        "permissionDecisionReason": verdict.text}}))


def emit_context(event, text):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": event,
        "additionalContext": text}}))


# ---------------------------------------------------------------- main
def main():
    try:
        raw = sys.stdin.read()
    except Exception:
        sys.exit(0)
    try:
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.exit(0)          # unparseable payload: no opinion, never a crash
    data = d(data)

    event = s(data.get("hook_event_name")) or "PreToolUse"
    sid = s(data.get("session_id")) or "unknown"
    actor = s(data.get("agent_id"))
    ti = d(data.get("tool_input"))
    ctx = {
        "event": event,
        "session_id": sid,
        "tool": s(data.get("tool_name")),
        "command": s(ti.get("command")),
        "file_path": s(ti.get("file_path")),
        "cwd": s(data.get("cwd")) or os.getcwd(),
    }

    denies, warns = [], []
    for check in CHECKS:
        try:
            v = check(ctx)
        except Exception as exc:
            # Fail-open per check: one broken check never kills the engine. But RECORD it —
            # otherwise "this check did not fire" and "this check could not run" are the
            # same observation, which is the silent-failure surface every audit trips over.
            # A crash that leaves no row is a guard you will believe is working.
            log_decision(sid, event, getattr(check, "__name__", "check"),
                         "check-error", mode="error", actor=actor,
                         subject=type(exc).__name__)
            continue
        if v is None:
            continue
        obs = v.blocking and observing(v.id)
        verdict = ("deny" if v.blocking else "warn")
        log_decision(sid, event, v.id,
                     ("would-" + verdict) if obs else verdict,
                     mode=("observe" if obs else "enforce"),
                     actor=actor, subject=v.subject)
        if v.blocking and not obs:
            denies.append(v)
        else:
            warns.append(v)

    if denies:
        emit_deny(event, denies[0])
    elif warns:
        emit_context(event, "\n".join("[%s] %s" % (w.id, w.text) for w in warns))
    sys.exit(0)              # exit 0 on every path; a deny is expressed in JSON, not a code


if __name__ == "__main__":
    main()
