#!/usr/bin/env python3
"""The pull-request rules, answered as data: who merges on which base, and whether a
branch may be rewritten.

Every caller asks the same question the same way — a hook deciding a Bash call,
an engine deciding a rebase no tool call carries. Answering it once here is what keeps those callers from each reading
the config their own way and disagreeing on the day it matters.

TWO VERB FAMILIES, and the answer shape follows the family.

  decision  `merge_decision`, `may_rewrite` answer a `Verdict`:
            `allow`, `refuse` or `unknown`, plus a reason. `unknown` means the rule
            could not be applied; a caller performing or instructing the act that
            reaches the remote with a rewrite treats it as `refuse`.
  query     `merge_actor` answers the actor the config names — `agent`,
            `agent-after-approval`, `person` — or `unknown`, and decides nothing.
            A caller writing its own wording maps it: `agent` takes the ungated
            path, everything else takes the gated one.

`allow` is not only "the rule permits it". Each verb also answers `allow` where
its rule has NO OPINION, and the reason says which: `may_rewrite` answers `clear`
when the forge counts no pull request merged into the branch and `no-forge` when
the remote is not on a forge it can read — those two are its only allow reasons,
and a declaration that names no base is never one of them. A caller that needs to
tell those apart reads the reason.

A caller of a decision verb that cannot import this module has no rule to apply,
and refuses. That is the caller's half of the contract, stated here because
nothing in this file can enforce it.

WHERE EACH RULE READS FROM.

  who merges    `merge_actor_by_base` then `merge_actor`, from the checkout's own
                `docs/agents/integrations/git.md` and then the user floor
                `~/.claude/skills/agents-config/integrations/git.md`. Rules resolve per level: the
                project's map, the floor's map, and only then either scalar, project
                over floor. Exact base first, then the longest matching pattern — a
                pattern holding `*` matches as the merge hook's floor reads it (`.`
                literal, `*` any run, the rest a regular expression); any other
                pattern is an exact name. The map is read as an indented block; an inline `{a: b}`
                reads as no rules. The project file is read only after the config
                gate (`~/.claude/skills/agents-config/scripts/config_levels.py resolve git --root <checkout>`,
                asked once per checkout) accepts it: a file git tracks is foreign, and
                so is an untracked one whose bytes a commit on any ref held at its
                path, so untracking it changes nothing. A gate that is foreign,
                unrunnable or exits otherwise leaves the actor `unknown` — the floor
                does not answer in its place — with the gate's refusal on stderr.
  rewriting     the same gate on the BASE checkout's file (`unknown`, reason
                `config refused`), then the declaration (`_declared`, private — `integration_bases` in the
                frontmatter of the BASE checkout's `docs/agents/integrations/git.md`,
                the common git dir's parent, so a linked worktree answers from the
                file its base holds), then the forge's merged-PR count on the
                targeted remote: one GraphQL read through `gh`, bounded by
                `GH_TIMEOUT`, of the github.com repository the push remote (or the
                `remote` / `forge` a caller names) reaches. Another host is no
                opinion; a failed read is `unknown`.

Whether the actor is a session or the person at their own terminal is read the way
`prkit`'s `_pr_actor_kind` reads it: a `CLAUDE_CODE_SESSION_ID` in the environment
is a session. The merge rule constrains sessions, so the person's own call is
allowed. A hook passes `kind="session"` explicitly — its subject is always the
session, whatever its environment says.

CLI:

  pr_policy.py merge-actor  --repo <checkout> --base <branch>   -> the actor, or unknown
  pr_policy.py merge        --repo <checkout> --base <branch>   -> allow|refuse|unknown
  pr_policy.py may-rewrite  --repo <checkout> --branch <branch>
                            [--remote <name|url>] [--forge <owner>/<name>] -> allow|refuse|unknown

Each prints the answer on stdout's first line and its reason on the second. The
three verbs exit 0 whenever an answer was printed.
"""

import argparse
import collections
import os
import pwd
import re
import subprocess
import sys

ALLOW, REFUSE, UNKNOWN = "allow", "refuse", "unknown"
ACTORS = ("agent", "agent-after-approval", "person")
GIT_TIMEOUT = 5
CONFIG_GATE = os.path.join(pwd.getpwuid(os.getuid()).pw_dir, ".claude", "skills", "agents-config", "scripts", "config_levels.py")
CONFIG_GATE_TIMEOUT = 30
CONFIG_GATE_REFUSED = 4
CONFIG_REFUSED = "config refused"

Verdict = collections.namedtuple("Verdict", "answer reason")
ConfigRefusal = collections.namedtuple("ConfigRefusal", "said refused")


def _git(cwd, *args):
    try:
        out = subprocess.run(("git", "-C", cwd) + args, capture_output=True,
                             text=True, timeout=GIT_TIMEOUT)
    except Exception:
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def floor_config():
    return os.path.join(os.path.expanduser("~"), ".claude", "skills", "agents-config", "integrations", "git.md")


def project_config(root):
    return os.path.join(root, "docs", "agents", "integrations", "git.md") if root else None


_gate_answers = {}


def _ask_config_gate(root):
    try:
        proc = subprocess.run([sys.executable, CONFIG_GATE, "resolve", "git", "--root", root],
                              capture_output=True, text=True, errors="replace",
                              timeout=CONFIG_GATE_TIMEOUT, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as exc:
        return ConfigRefusal("the config gate did not answer (%s)" % type(exc).__name__, False)
    if proc.returncode == 0:
        return None
    said = next((ln.strip() for ln in proc.stderr.splitlines() if ln.strip()),
                "exit %d" % proc.returncode)
    if proc.returncode == CONFIG_GATE_REFUSED:
        return ConfigRefusal(said, True)
    return ConfigRefusal("the config gate exited %d: %s" % (proc.returncode, said), False)


def config_refusal_text(refusal):
    if refusal.refused:
        return refusal.said
    return "pr_policy: %s; the project git.md is not used" % refusal.said


def project_config_refusal(root):
    path = project_config(root)
    if not path or not os.path.exists(path):
        return None
    if root not in _gate_answers:
        _gate_answers[root] = _ask_config_gate(root)
    return _gate_answers[root]


def _lines(path):
    if not path:
        return None
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read().splitlines()
    except OSError:
        return None


def _clean(value):
    value = re.sub(r"\s*(#.*)?$", "", value.strip())
    return value.strip('"')


# ── who merges ───────────────────────────────────────────────────────────────

def _scalar_actor(path):
    """The first `merge_actor:` value in the file, or None."""
    for line in _lines(path) or ():
        m = re.match(r"^\s*merge_actor:\s*(.*)$", line)
        if m:
            return _clean(m.group(1)) or None
    return None


def _indent(line):
    stripped = line.lstrip(" ")
    return None if not stripped else len(line) - len(stripped)


def base_pattern_matches(pat, base):
    return pat == base or ("*" in pat and _floor_glob(pat, base))


def _floor_glob(pat, base):
    try:
        return re.search("^" + pat.replace(".", "\\.").replace("*", ".*") + "$", base) is not None
    except re.error:
        return False


def _by_base_actor(path, base):
    """The actor the file's `merge_actor_by_base` block names for `base`, or None.

    The block is the indented lines under the key, ending at the first blank line
    or the first line no deeper than the key. Exact name first; otherwise the
    longest pattern matching the whole base, so `cluster/x/*` beats `cluster/*`.
    """
    if not base:
        return None
    best_pat, best, depth = "", None, None
    for line in _lines(path) or ():
        if re.match(r"^\s*merge_actor_by_base:\s*$", line):
            depth = _indent(line)
            continue
        if depth is None:
            continue
        d = _indent(line)
        if d is None or d <= depth:
            depth = None
            continue
        body = _clean(line)
        if ":" not in body:
            continue
        pat, _sep, val = body.partition(":")
        pat, val = pat.strip().strip('"'), val.strip().strip('"')
        if pat == base:
            return val
        if "*" in pat and len(pat) > len(best_pat) and _floor_glob(pat, base):
            best_pat, best = pat, val
    return best


def resolve_actor(root, base):
    """{"actor", "source", "rule"} for a merge onto `base` from the checkout `root`.

    `source` is `project` / `floor` where a value was read, `unread` when no file
    names an actor or the project config is refused, and `base-unread` when a config
    answered but the base itself is unknown — an unread base is not a base no rule
    covers.
    """
    if project_config_refusal(root):
        return {"actor": None, "source": "unread", "rule": "none"}
    levels = [(project_config(root), "project")] if root else []
    levels.append((floor_config(), "floor"))
    actor = source = rule = None
    for path, level in levels:
        value = _by_base_actor(path, base)
        if value:
            actor, source, rule = value, level, "by-base"
            break
    if actor is None:
        for path, level in levels:
            value = _scalar_actor(path)
            if value:
                actor, source, rule = value, level, "default"
                break
    if actor is None:
        return {"actor": None, "source": "unread", "rule": "none"}
    if not base:
        return {"actor": actor, "source": "base-unread", "rule": "none"}
    return {"actor": actor, "source": source, "rule": rule}


def merge_actor(root, base):
    """Query verb: the actor name for this base, or `unknown`."""
    try:
        resolved = resolve_actor(root, base)
    except Exception:
        return UNKNOWN
    if resolved["source"] in ("unread", "base-unread"):
        return UNKNOWN
    return resolved["actor"] if resolved["actor"] in ACTORS else UNKNOWN


def actor_kind(environ=None):
    """`session` or `shell`, the way `prkit`'s `_pr_actor_kind` reads it."""
    environ = os.environ if environ is None else environ
    return "session" if environ.get("CLAUDE_CODE_SESSION_ID") else "shell"


def merge_decision(root, base, kind=None):
    """Decision verb: may this caller merge a pull request onto `base`?

    `allow` only when the resolved actor is `agent` and the base was read, or when
    the caller is the person at their own terminal. An unread config or base is
    `unknown`; every other actor is `refuse`.
    """
    kind = kind or actor_kind()
    if kind == "shell":
        return Verdict(ALLOW, "the person at their own terminal")
    try:
        resolved = resolve_actor(root, base)
    except Exception as exc:
        return Verdict(UNKNOWN, "config unreadable: %s" % type(exc).__name__)
    if resolved["source"] == "unread":
        return Verdict(UNKNOWN, "unread")
    if resolved["source"] == "base-unread":
        return Verdict(UNKNOWN, "base-unread")
    if resolved["actor"] == "agent":
        return Verdict(ALLOW, "agent (%s, %s)" % (resolved["source"], resolved["rule"]))
    return Verdict(REFUSE, "%s (%s, %s)" % (resolved["actor"], resolved["source"],
                                            resolved["rule"]))


def _toplevel(path):
    return _git(path, "rev-parse", "--show-toplevel") if os.path.isdir(path) else None


def _report_refusals():
    for refusal in filter(None, _gate_answers.values()):
        print(config_refusal_text(refusal), file=sys.stderr)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="pr_policy.py")
    sub = parser.add_subparsers(dest="verb", required=True)
    for name, extra in (("merge-actor", "--base"), ("merge", "--base"),
                        ("may-rewrite", "--branch")):
        p = sub.add_parser(name)
        p.add_argument("--repo", required=True)
        p.add_argument(extra, default="")
        if name == "may-rewrite":
            p.add_argument("--remote", default=None)
            p.add_argument("--forge", default=None, help="owner/name, used as-is")
    args = parser.parse_args(argv)
    root = _toplevel(args.repo)
    if args.verb == "merge-actor":
        print(merge_actor(root, args.base))
        _report_refusals()
        return 0
    if args.verb == "merge":
        v = merge_decision(root, args.base)
    else:
        forge = tuple(args.forge.split("/", 1)) if args.forge and "/" in args.forge else None
        import rewrite_policy
        v = rewrite_policy.may_rewrite(args.repo, args.branch, remote=args.remote, forge=forge)
    print(v.answer)
    print(v.reason)
    _report_refusals()
    return 0


if __name__ == "__main__":
    sys.exit(main())
