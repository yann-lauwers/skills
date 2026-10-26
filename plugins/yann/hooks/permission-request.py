#!/usr/bin/env python3
"""PermissionRequest — the one handler on this event.

## cd-relative-read-allow — answer the question the host gave up on.

A `Read()` deny rule is a path pattern, so the host can only test it against a
full path. `cd /tmp/x && grep -n foo utils.js` never gives it one: the operand is
relative and the directory is decided by a `cd` the host reads but does not run.
Undecidable, so it asks — and the person clicking has no more resolved the path
than the host did. The prompt costs a click and confirms nothing.

`lib/hook_shell.statements_with_cwd` is the resolver the host is missing. It
tracks `cd` across a chain and hands back the directory each statement runs in,
or None the moment that stops being knowable. So this check resolves every file
operand and tests the resolved paths against the deny patterns actually
configured. All of them resolve and none matches -> `allow`, and the prompt the
host could not decide is decided on evidence instead of on a click.

Anything else is NO OPINION, and the host asks exactly as it does today: an
unresolvable cwd, an operand naming a path that matches a deny pattern, a glob
that expands to nothing, a deny pattern this cannot parse, a payload shape it
does not recognise.

Widened 2026-09-03, on two shapes the first cut left prompting. The id keeps
its name so its 291 existing rows still reconcile; the population it covers is
larger from that date.

* **A relative operand with no `cd`.** The original scoping read "a command
  without a `cd` drew its prompt from some other rule". That is false: a
  `Read()` deny rule is tested against a bare relative operand too, and
  `grep -rn foo .` in a worktree raises the prompt with no `cd` anywhere in it.
* **An operand that is a directory.** Here the host is not stuck on an
  unresolvable path — it resolved the operand and asks because a RECURSIVE read
  of that tree might reach a denied file. Testing the directory's own path
  against the pattern answers a different question and would grant on it, so a
  directory operand is decided by `pattern_can_match_under`: could any path
  beneath this tree match the pattern at all. An anchored absolute pattern
  lying outside the tree cannot, and that is the only case this returns False
  for. A `**/` pattern binds at any depth, so it stays undecidable and the host
  asks — anchoring the deny list to absolute paths is what makes a tree
  decidable, and that is a settings decision, not this file's.

Walking the tree to answer it directly was measured and rejected: 42,676 dirs /
263,553 files in one worktree, 3.6s for `os.walk` and 4.9-6.1s for `find` with
an early exit. A check on the permission critical path cannot spend that, and a
node cap large enough to be useful is a cap that repo already exceeds.

**Everything the widening added is granted only for a pure read** (`reads_only`,
a closed allowlist). Under `bypassPermissions` an allow is strictly stronger
than silence — it suppresses the host's prompt. The pre-widening shape keeps its
original terms so its measured behaviour does not move.

"""
import os
import sys

HOOKS = os.path.dirname(os.path.abspath(__file__))
sys.path[:] = [p for p in sys.path if os.path.realpath(p) != os.path.realpath(HOOKS)]

import fnmatch
import glob as globmod
import json
import re
import subprocess

sys.path.append(os.path.join(HOOKS, "lib"))

GIT_TIMEOUT = 2
MANAGED_DIR = ("/Library/Application Support/ClaudeCode" if sys.platform == "darwin"
               else "/etc/claude-code")
READ_RULE = re.compile(r"\s*Read\s*(?:\((.*)\))?\s*", re.S)
BASH_RULE = re.compile(r"\s*Bash\s*(?:\((.*)\))?\s*", re.S)
SHELL_QUOTING = re.compile(r"[\"'\\]")
BALANCED_BRACKETS = re.compile(r"(?:[^\[\]]|\[[^\[\]]*\])*", re.S)
try:
    import hook_shell as hs
    from command_shape import follows_links, reads_only, walks_tree
    from deny_patterns import GLOB_CHARS, _anchor, _anchored, _covering, _forms, _pattern_forms, pattern_can_match_under
    import hook_mode
    import hook_decisions
    from permission_files import NAME_RE as PROTECTED_NAME, writes_permission_file
except Exception as exc:
    print(json.dumps({"systemMessage": (
        "permission-request did not run: its libraries in %s failed to load (%s: %s), so no "
        "permission request is answered by it and every one goes to the prompt until they load."
        % (os.path.join(HOOKS, "lib"), type(exc).__name__, str(exc).splitlines()[0][:200] if str(exc) else ""))}))
    sys.exit(0)


def payload():
    try:
        return json.loads(sys.stdin.read() or "{}")
    except Exception:
        return {}


def settings_files():
    """Read rather than remembered: the check enforces the deny list that is
    actually configured, so a rule added tomorrow is covered without an edit here.
    """
    out = [os.path.join(os.path.expanduser("~"), ".claude", "settings.json"),
           os.path.join(os.path.expanduser("~"), ".claude", "settings.local.json")]
    config = os.environ.get("CLAUDE_CONFIG_DIR")
    if config:
        config = os.path.abspath(os.path.expanduser(config))
        out += [os.path.join(config, "settings.json"),
                os.path.join(config, "settings.local.json")]
    return out


def managed_files():
    out = [os.path.join(MANAGED_DIR, "managed-settings.json")]
    drop_ins = os.path.join(MANAGED_DIR, "managed-settings.d")
    if os.path.lexists(drop_ins):
        out += sorted(os.path.join(drop_ins, name) for name in os.listdir(drop_ins)
                      if name.endswith(".json") and not name.startswith("."))
    return out


def project_settings(cwd):
    out = []
    seen = set()
    d = os.path.abspath(cwd or "")
    while d and d not in seen and d != os.path.dirname(d):
        seen.add(d)
        for name in ("settings.json", "settings.local.json"):
            p = os.path.join(d, ".claude", name)
            if os.path.exists(p):
                out.append(p)
        d = os.path.dirname(d)
    return out


def git_roots(directory):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["LC_ALL"] = "C"
    run = subprocess.run(["git", "-C", directory, "rev-parse", "--path-format=absolute",
                          "--show-toplevel", "--git-common-dir"],
                         capture_output=True, text=True, timeout=GIT_TIMEOUT, env=env)
    if run.returncode and "not a git repository" in run.stderr:
        return ()
    if run.returncode:
        raise OSError(run.returncode, run.stderr.strip())
    toplevel, common = run.stdout.splitlines()[:2]
    return (toplevel, os.path.dirname(common))


def rule_context(cwd):
    try:
        starts = [os.path.abspath(cwd)]
        project = os.environ.get("CLAUDE_PROJECT_DIR")
        if project:
            starts.append(os.path.abspath(project))
        starts = list(dict.fromkeys(starts))
        roots = [root for start in starts for root in git_roots(start)]
        files = settings_files() + managed_files()
        for directory in starts + roots:
            files += project_settings(directory)
    except Exception:
        return None
    patterns, bash_asks, unparsed = read_rules(list(dict.fromkeys(files)))
    if unparsed or not patterns:
        return None
    return patterns, bash_asks, tuple(dict.fromkeys(starts + roots))


def parseable(pattern):
    if not pattern or pattern.startswith("!"):
        return False
    if pattern.startswith("~") and pattern != "~" and not pattern.startswith("~/"):
        return False
    return BALANCED_BRACKETS.fullmatch(pattern) is not None


def read_rules(files):
    pats, bash_asks, unparsed = [], [], False
    for path in files:
        try:
            with open(path, errors="replace") as fh:
                data = json.load(fh)
        except FileNotFoundError:
            continue
        except Exception:
            unparsed = True
            continue
        if not isinstance(data, dict):
            unparsed = True
            continue
        permissions = data.get("permissions") or {}
        for behavior in ("deny", "ask"):
            entries = ((permissions.get(behavior) or []) if isinstance(permissions, dict)
                       else None)
            if not isinstance(entries, list):
                unparsed = True
                continue
            for entry in entries:
                text = str(entry)
                if behavior == "ask" and re.match(r"\s*Bash\b", text):
                    m = BASH_RULE.fullmatch(text)
                    if m is None:
                        unparsed = True
                    else:
                        bash_asks.append((m.group(1) or "").strip())
                    continue
                if not re.match(r"\s*Read\b", text):
                    continue
                m = READ_RULE.fullmatch(text)
                pattern = (m.group(1) or "").strip() if m else ""
                if not parseable(pattern):
                    unparsed = True
                    continue
                pats.append((pattern, path))
    return pats, bash_asks, unparsed


def _shell_forms(command):
    folded = " ".join(command.casefold().split())
    return (folded, " ".join(SHELL_QUOTING.sub("", folded).split()))


def bash_rule_reaches(command, content):
    literal = content[:-2] if content.endswith(":*") else content
    words = " ".join(literal.casefold().split())
    rule = re.compile(".*".join(re.escape(part) for part in words.split("*")), re.S)
    return any(rule.search(form) for form in _shell_forms(command))


def asked_by_a_hook_or_rule(data):
    return not isinstance(data.get("permission_suggestions"), list)


def matches_deny(abspath, pattern, source, bases=()):
    """Does one resolved absolute path match one deny pattern?

    Unparseable or unrecognised pattern shapes raise, and the caller reads that
    as no opinion. A pattern this cannot understand must never read as "does not
    match" — that is the direction that allows a denied path.
    """
    forms = [form.casefold() for pat in _anchored(pattern, source, bases)
             for form in _pattern_forms(pat)]
    return any(fnmatch.fnmatchcase(path.casefold(), form)
               for path in _covering(abspath) for form in forms)


def resolve_reads(command, cwd):
    """(paths, has_cd, ok, rel) — every file operand resolved to an absolute path.

    `ok` is False the moment any operand cannot be resolved. The caller must not
    read a short list as a clean one: an unresolvable operand and an absent one
    produce the same length, and only `ok` separates them.

    Every operand is treated as a candidate path, including ones that name no
    file — `file_operands` cannot tell `grep PATTERN file` apart. That direction
    is safe: a non-file operand resolves somewhere that does not exist, so it
    can only withhold an allow, never produce one.

    `rel` counts the operands that arrived relative and needed the cd chain to
    resolve. It is the review's handle on whether the resolver did any work:
    rel=0 means the allow rested on paths the host could already see, so a
    resolution bug could not have caused it.

    `empty` holds the directory each glob that expanded to nothing was pointed
    at. The operand reads no file, so it is decided by reachability rather than
    dropped: refusing to vouch for it was costing a prompt on a glob that could
    not have reached a credential in the first place.

    `dirs` is the subset of resolved paths that exist as directories. They are
    the operands a recursive read walks, and the caller decides them by
    reachability rather than by matching the directory's own path — a directory
    named `src` matches no credential pattern while the tree under it might.
    """
    paths, has_cd, ok, rel, dirs, empty = [], False, True, 0, set(), set()
    for statement, st_cwd in hs.statements_with_cwd(command, cwd):
        if hs.command_word(statement) == "cd":
            has_cd = True
            continue
        for token in hs.file_operands(statement):
            tok = os.path.expanduser(token)
            if os.path.isabs(tok):
                joined = tok
            elif st_cwd is None:
                ok = False                       # the cd went somewhere unknowable
                continue
            else:
                joined = os.path.join(st_cwd, tok)
                rel += 1
            if GLOB_CHARS.search(joined):
                hits = globmod.glob(joined)
                if not hits:
                    # A glob matching nothing reads nothing, so it cannot reach a
                    # denied file — UNLESS a denied path could appear where it is
                    # pointed. Its own directory is what decides that, on the same
                    # reachability test a tree operand takes, so `cat ~/.ssh/id_*`
                    # with no key present still asks and `grep x lib/*.js` in an
                    # empty dir does not.
                    empty.add(_forms(_anchor(joined)))
                    continue
                for h in hits:
                    paths.append(_forms(h))
                    if os.path.isdir(h):
                        dirs.add(_forms(h))
            else:
                paths.append(_forms(joined))
                if os.path.isdir(joined):
                    dirs.add(_forms(joined))
    return paths, has_cd, ok, rel, dirs, empty


def verdict(data):
    """A truthy fingerprint string when the command may be allowed, else None for
    no opinion. Never `deny` — this check exists to answer a question the host
    could not, not to add a refusal of its own."""
    tool = data.get("tool_name") or ""
    if tool and tool != "Bash":
        return None
    tool_input = data.get("tool_input") or {}
    command = tool_input.get("command") or ""
    if not isinstance(command, str) or not command.strip():
        return None
    cwd = data.get("cwd") or tool_input.get("cwd") or os.getcwd()
    if asked_by_a_hook_or_rule(data):
        return None

    context = rule_context(cwd)
    if context is None:
        return None
    patterns, bash_asks, bases = context
    if any(bash_rule_reaches(command, rule) for rule in bash_asks):
        return None

    paths, has_cd, ok, rel, dirs, empty = resolve_reads(command, cwd)
    if not ok:
        return None
    if not (paths or empty):
        # No file operand at all — `grep -rn foo --include=*.ts -l`, `gh pr merge
        # --help`, a `python3 - <<PY` whose paths live inside the heredoc body. The
        # operand walk sees nothing, so the implicit read root is the working
        # directory, and it is decided by the same reachability test a tree operand
        # takes. A cwd no deny pattern can reach cannot hold a credential this
        # command could name relatively.
        #
        # A heredoc body is opaque to any operand walk, so this grants a command
        # whose absolute path to a denied file sits inside one. The host's own rule
        # cannot see into it either — that is why it asked — and refusing to vouch
        # was costing a prompt on every scripted edit inside a worktree.
        #
        # A command that is nothing but `cd` reads nothing at all, so there is no
        # implicit root to test and no verdict to give.
        try:
            acts = any(hs.command_word(st) != "cd"
                       for _, st in hs.statements(command))
        except Exception:
            return None
        if not (acts and cwd):
            return None
        empty = {_forms(cwd)}

    # A write aimed at the permission system is never granted here, whatever its
    # operands resolve to: an allow suppresses the host's own prompt for it.
    if writes_permission_file(command):
        return None

    # That test reads a WRITE VERB pointed at a path it can see. Measured on
    # 2026-09-09, three of the four routes to settings.json carry
    # neither: a `python3 - <<PY` body, a `python3 -c` one-liner, and `bash relax.sh`.
    # The one-liner was reaching `allow` here — an explicit grant that suppresses the
    # host's own prompt on a rewrite of the deny list.
    #
    # So a command that is not a pure reader and NAMES one of the four permission-
    # system files anywhere in its text gets no grant, wherever the name sits and
    # whatever the verb is. A reader keeps its grant, which is what holds the cost at
    # nothing: `grep -n deny ~/.claude/settings.json` still runs unprompted.
    #
    # This withholds a grant; it does not raise an ask. What a command does to those
    # files once it runs is decided after the fact, by comparing their bytes.
    if PROTECTED_NAME.search(command) and not reads_only(command):
        return None

    if follows_links(command):
        return None

    # A directory operand is only a whole-tree read when a verb descends into it.
    # `ls lib/` reads that directory's own entries, and the host's deny patterns
    # match those by path exactly as they match a file's — so it keeps the plain
    # test. `grep -rn foo .` does not, and its tree goes to reachability.
    trees = dirs if walks_tree(command) else set()

    # WHAT THE VERB IS DOES NOT DECIDE THIS. A reader allowlist here withheld grants
    # and protected nothing: measured over the census window it cost 18 prompts on
    # `gh pr merge --help`, `export GIT_DIR=…; git log …` and their shape. What makes a
    # call safe is that no operand of it resolves onto a denied path, which the walk
    # below decides.


    try:
        for forms in paths:
            for p in forms:
                for pat, src in patterns:
                    if forms in trees:
                        if pattern_can_match_under(p, pat, src, bases):
                            return None
                    elif matches_deny(p, pat, src, bases):
                        return None
        for forms in empty:
            for d in forms:
                for pat, src in patterns:
                    if pattern_can_match_under(d, pat, src, bases):
                        return None
    except Exception:
        return None
    # Counts, never paths. A row is a second copy of whatever it records, and a
    # resolved path is exactly the operand a credential would sit in. `n` and
    # `rel` say how much resolving stood behind the grant; the command itself is
    # recoverable from the session transcript by timestamp when a row needs one.
    return "allow n=%d rel=%d trees=%d empty=%d" % (len(paths), rel, len(trees), len(empty))


def main():
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except Exception:
        data = {}
    # Coerced at the entry point, not guarded at each read. Valid JSON on stdin
    # need not be an object, and `data.get` on a list raises.
    if not isinstance(data, dict):
        data = {}
    session = data.get("session_id") or "unknown"

    try:
        fingerprint = verdict(data)
    except Exception:
        fingerprint = None

    acting = fingerprint and hook_mode.acting("cd-relative-read-allow")

    if not fingerprint:
        sys.exit(0)
    hook_decisions.log("cd-relative-read-allow",
                       "allow" if acting else "would-allow",
                       "shape=cd-relative-read " + fingerprint, session,
                       event="PermissionRequest",
                       mode="enforce" if acting else "observe")
    if acting:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PermissionRequest",
            "decision": {"behavior": "allow"}}}))
    sys.exit(0)


if __name__ == "__main__":
    main()
