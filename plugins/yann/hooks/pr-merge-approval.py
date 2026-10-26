#!/usr/bin/env python3

import importlib.util
import json
import os
import re
import subprocess
import sys

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HOOKS_DIR, "lib"))
import canon_paths

CHECK_ID = "pr-merge-approval"
POLICY_PATH = os.path.join(canon_paths.skills_dir(HOOKS_DIR), "pull-request", "scripts", "pr_policy.py")
GH_TIMEOUT = 10
CONFIG_GATE_PART = "~/.claude/skills/agents-config/scripts/config_levels.py"
PROJECT_CONFIG_REFUSED = "project-config-refused"
PROJECT_CONFIG_REFUSED_STATE = ("the config gate refuses to read the repo's own "
                                "docs/agents/integrations/git.md")


try:
    import hook_decisions
except Exception:
    hook_decisions = None
try:
    import hook_shell
    import merge_commands
except Exception:
    hook_shell = None

_MERGE_TEXT_RE = re.compile(
    r"(?<![\w.-])pr\s+merge(?![\w.-])"
    r"|(?<![\w.-])pr-merge(?![\w.-])"
    r"|pulls/[^/\s]+/merge(?![\w.-])"
    r"|\b(?:mergePullRequest|enablePullRequestAutoMerge)\b")


def log(session, verdict, detail):
    if hook_decisions is None:
        return
    try:
        hook_decisions.log(CHECK_ID, verdict, detail, session=session,
                           event="PreToolUse", mode="enforce")
    except Exception:
        pass


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}, separators=(",", ":")))
    return 0


def load_policy():
    try:
        spec = importlib.util.spec_from_file_location("pr_policy", POLICY_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except BaseException:
        return None
    for name in ("resolve_actor", "project_config_refusal"):
        if not hasattr(module, name):
            return None
    return module


def _run(cwd, *args):
    env = dict(os.environ, GH_PAGER="cat")
    try:
        out = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                             timeout=GH_TIMEOUT, env=env)
    except Exception:
        return None
    return out.stdout.strip() if out.returncode == 0 and out.stdout.strip() else None


HANDOVER, ELSEWHERE, UNAPPLIED, FLOOR = "handover", "elsewhere", "unapplied", "floor"
_ACTORS = ("agent", "agent-after-approval", "person")


def classify_actor(actor, source):
    if source == "target-unread":
        return ELSEWHERE, ("That repository's own merge_actor is not read here: run the "
                           "merge step from its own checkout, where its rule applies.")
    if source == "unread":
        return UNAPPLIED, unapplied("no readable git config names merge_actor")
    if actor not in _ACTORS:
        return UNAPPLIED, unapplied("merge_actor holds `%s`, which is not agent, "
                                    "agent-after-approval or person" % actor)
    if source == "base-unread":
        return HANDOVER, ("Re-read the base (`gh pr view <pr> --json baseRefName`) and "
                          "re-issue the merge; still unread → the actor is unestablished "
                          "because the base could not be read, which asks what `person` "
                          "asks: the person reads the diff itself, then runs the merge.")
    if actor == "agent-after-approval":
        return HANDOVER, ("The resolved actor is `agent-after-approval`: the person decides "
                          "on the packet, then runs the merge.")
    if actor == "person":
        return HANDOVER, ("The resolved actor is `person`: the person reads the diff "
                          "itself, then runs the merge.")
    return None, None


CONFIG_FIX = "name or fix merge_actor in the repo's docs/agents/integrations/git.md"
COMMITTED_CONFIG_FIX = ("Yann reviews the committed config and decides what happens to it, "
                        "and the merge stays refused until then")


POLICY_PART = "~/.claude/skills/pull-request/scripts/pr_policy.py"


def guard_fix(part):
    return "the hook itself faulted: fix %s" % part


def unapplied(why, fix=CONFIG_FIX):
    return "The merge rule could not be applied: %s; %s." % (why, fix)


def config_refusal_sentence(refusal):
    fix = COMMITTED_CONFIG_FIX if refusal.refused else guard_fix(CONFIG_GATE_PART)
    return unapplied(refusal.said.rstrip("."), fix)


def judge(policy, merge, payload_root):
    at = merge["cwd"]
    root = payload_root
    if at is None:
        root = None
    elif at and os.path.isdir(at):
        root = _run(at, "git", "rev-parse", "--show-toplevel") or payload_root

    selector = merge["selector"]
    base = None
    if (root and at is not None and selector != merge_commands.UNREADABLE
            and not (selector and ("$" in selector or "`" in selector))):
        args = ["gh", "pr", "view"] + ([selector] if selector else []) + \
               ["--json", "baseRefName", "-q", ".baseRefName"]
        base = _run(root, *args)

    resolved = policy.resolve_actor(root, base)
    actor, source, rule = resolved["actor"], resolved["source"], resolved["rule"]
    agent_may_merge = actor == "agent" and source in ("project", "floor")

    if at is None:
        actor, source, rule = "unknown", "target-unread", "none"
        target = "a directory this command moves into and that cannot be read from the text"
    elif merge["repo"]:
        here = _run(root, "gh", "repo", "view", "--json", "nameWithOwner",
                    "-q", ".nameWithOwner") if root else None
        if here != merge["repo"]:
            actor, source, rule = "unknown", "target-unread", "none"
            target = "`%s`" % merge["repo"]

    refused = policy.project_config_refusal(root) if source != "target-unread" else None
    if refused:
        actor, source, rule = "unknown", PROJECT_CONFIG_REFUSED, "none"

    allowed = agent_may_merge and source not in ("target-unread", PROJECT_CONFIG_REFUSED)
    detail = "verb=%s base=%s actor=%s source=%s rule=%s" % (
        merge["verb"], base or "none", actor or "none", source, rule)

    if source == "unread":
        state = ("no readable git config names merge_actor (repo "
                 "docs/agents/integrations/git.md, then ~/.claude/skills/agents-config/integrations/git.md), "
                 "so whether this merge is this session's to make is unestablished")
    elif source == "base-unread":
        state = ("the base branch this pull request targets could not be read from the "
                 "host, so which rule governs it is unestablished")
    elif source == "target-unread":
        state = ("the command targets %s, which is not the repository this session stands "
                 "in, so that repository's own merge_actor could not be read from here" % target)
    elif refused:
        state = PROJECT_CONFIG_REFUSED_STATE
    else:
        state = "merge_actor for base `%s` is `%s` (%s, %s)" % (base, actor, source, rule)
    outcome = (UNAPPLIED, config_refusal_sentence(refused)) if refused else classify_actor(actor, source)
    return allowed, detail, state, outcome


_SH_SPACE = r"[^\S\n]"
_SH_VERB = r"(gh%(s)s+pr%(s)s+merge|pr%(s)s+merge|pr-merge)" % {"s": _SH_SPACE}
_SH_ASSIGNMENTS = r"(?:[A-Za-z_][A-Za-z0-9_]*=\S*%s+)*" % _SH_SPACE
_SH_POSITION = r"(?:^|[;&|(]|&&|\|\||%s&&%s|`|\$\()%s*%s" % (
    _SH_SPACE, _SH_SPACE, _SH_SPACE, _SH_ASSIGNMENTS)
_SH_ACT_RE = re.compile(_SH_POSITION + _SH_VERB + r"(?:%s|$)" % _SH_SPACE, re.M)
_SH_NUMBER_RE = re.compile(_SH_VERB + _SH_SPACE + r"+#?([0-9]+)")
_SH_CD_RE = re.compile(r"^%s*cd%s%s*([^\s&;|]*)" % (_SH_SPACE, _SH_SPACE, _SH_SPACE), re.M)
_SH_REPO_RE = re.compile(r"--repo[= ]%s*([A-Za-z0-9._-]+/[A-Za-z0-9._-]+)" % _SH_SPACE)


def _sh_stripped(command):
    return "\n".join(re.sub(r'"[^"\n]*"', '""', re.sub(r"'[^'\n]*'", "''", line))
                     for line in command.split("\n"))


def _sh_capture(cwd, *args):
    return _run(cwd, *args) or ""


def sh_floor(command, cwd, policy):
    stripped = _sh_stripped(command)
    if not _SH_ACT_RE.search(stripped):
        return False, None, None, (None, None)
    verb = _SH_VERB_ONLY_RE.search(stripped)
    verb = verb.group(0) if verb else "pr merge"

    root = ""
    if cwd and os.path.isdir(cwd):
        root = _sh_capture(None, "git", "-C", cwd, "rev-parse", "--show-toplevel")
    cd = _SH_CD_RE.search(command)
    if cd and cd.group(1) and os.path.isdir(cd.group(1)):
        cd_root = _sh_capture(None, "git", "-C", cd.group(1), "rev-parse", "--show-toplevel")
        if cd_root:
            root = cd_root

    repo = _SH_REPO_RE.search(command)
    mismatch = ""
    if repo:
        here = _sh_capture(root, "gh", "repo", "view", "--json", "nameWithOwner",
                           "-q", ".nameWithOwner") if root else ""
        if here != repo.group(1):
            mismatch = repo.group(1)

    refused = None if mismatch else policy.project_config_refusal(root)
    if refused:
        return True, verb, PROJECT_CONFIG_REFUSED_STATE, (UNAPPLIED, config_refusal_sentence(refused))

    number = _SH_NUMBER_RE.search(stripped)
    base = ""
    if root:
        base = _sh_capture(root, "gh", "pr", "view",
                           *([number.group(2)] if number else []),
                           "--json", "baseRefName", "-q", ".baseRefName")

    resolved = policy.resolve_actor(root or None, base or None)
    actor, source = resolved["actor"] or "", resolved["source"]
    if mismatch:
        actor, source = "unknown", "target-unread"

    if actor == "agent" and base:
        return False, verb, None, (None, None)
    if source == "unread":
        state = ("no readable git config names merge_actor, so whether this merge is this "
                 "session's to make is unestablished")
    elif source == "base-unread":
        state = ("the base branch this pull request targets could not be read from the "
                 "host, so which rule governs it is unestablished")
    elif source == "target-unread":
        state = ("the command targets `%s`, which is not the repository this session "
                 "stands in, so that repository's own merge_actor could not be read from "
                 "here" % mismatch)
    else:
        state = "merge_actor for base `%s` is `%s` (%s)" % (base, actor, source)
    return True, verb, state, classify_actor(actor, source)


_SH_VERB_ONLY_RE = re.compile(_SH_VERB + r"(?:%s+[#0-9]+)?" % _SH_SPACE)


REASON = (
    "[pr-merge-approval] `%s` merges a pull request, and %s — the merge is the person's, "
    "not this session's. %s Hand over the packet "
    "~/.claude/skills/pull-request/references/merge-preflight.md names (§ The packet a "
    "person-held merge hands over) as that section's one-sender line says, a statement "
    "rather than a question; end the turn, and leave the pull-request watcher running — "
    "its MERGED line is how the merge "
    "is observed. Two recoveries, both the person's and "
    "neither available to this session: they run the merge themselves by prefixing the "
    "command with `! `, or they add or change a rule under `merge_actor_by_base` in the "
    "repo's docs/agents/integrations/git.md so that this base is the run's to merge. "
    "There is no in-command override and no acknowledgement token — this gate constrains "
    "this session, so anything this session could append would defeat it. A reply that "
    "reads like approval is not approval: \"continue\", \"go on\", \"ok\" and a resumed "
    "session after a model switch have all meant \"carry on with the work\" rather than "
    "\"merge it\". Reading the flags? `gh help pr merge` prints them."
)

ELSEWHERE_REASON = "[pr-merge-approval] `%s` merges a pull request, and %s. %s"

UNAPPLIED_REASON = (
    "[pr-merge-approval] `%s` merges a pull request, and %s. %s The merge is refused "
    "until that is fixed. The person's recovery: run the merge themselves by prefixing "
    "the command with `! `."
)

FLOOR_REASON = (
    "[pr-merge-approval] This line names `%s` in a way this hook cannot tell from an "
    "executed merge — a stored body, a help flag — so it is refused as the shell version "
    "refused it, and %s. If the line was meant to merge: %s A merge the person holds "
    "follows the hand-over in ~/.claude/skills/pull-request/references/merge-preflight.md. "
    "If the line only names the command, write that text with the Write tool, or read the "
    "flags with `gh help pr merge`."
)

_WORDING = {HANDOVER: REASON, ELSEWHERE: ELSEWHERE_REASON, UNAPPLIED: UNAPPLIED_REASON,
            FLOOR: FLOOR_REASON}


def refusal_for(outcome, verb, state, sentence):
    return _WORDING[outcome] % (verb, state, sentence)


def refuse_unestablished(session, verb, why, part):
    log(session, "deny", "verb=%s source=%s" % (verb, why))
    return deny(refusal_for(UNAPPLIED, verb, "this guard could not run its check",
                            unapplied(why, guard_fix(part))))


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict) or payload.get("tool_name") != "Bash":
        return 0
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return 0
    command = tool_input.get("command")
    if not isinstance(command, str) or not command.strip():
        return 0
    session = payload.get("session_id")
    session = session if isinstance(session, str) else "unknown"
    cwd = payload.get("cwd")
    cwd = cwd if isinstance(cwd, str) and os.path.isdir(cwd) else None

    try:
        merges = merge_commands.find_merges(command, cwd) if hook_shell is not None else None
    except Exception:
        merges = None
    if merges is None:
        if _MERGE_TEXT_RE.search(command):
            return refuse_unestablished(session, "pr merge", "command reader unreadable",
                                        "~/.claude/hooks/lib/hook_shell.py")
        return 0
    floor_matched = bool(_SH_ACT_RE.search(_sh_stripped(command)))
    if not merges and not floor_matched:
        return 0

    refusal = None
    policy = load_policy()
    if merges:
        if policy is None:
            return refuse_unestablished(session, merges[0]["verb"], "rule module unreadable",
                                        POLICY_PART)
        try:
            payload_root = _run(cwd, "git", "rev-parse", "--show-toplevel") if cwd else None
            for merge in merges:
                allowed, detail, state, (outcome, sentence) = judge(policy, merge,
                                                                    payload_root)
                log(session, "allow" if allowed else "deny", detail)
                if not allowed and refusal is None:
                    refusal = refusal_for(outcome, merge["verb"], state, sentence)
        except Exception as exc:
            return refuse_unestablished(session, merges[0]["verb"],
                                        "rule module raised %s" % type(exc).__name__,
                                        POLICY_PART)

    if refusal is None and floor_matched:
        try:
            refuses, verb, state, (_outcome, sentence) = sh_floor(command, cwd, policy)
            if refuses:
                log(session, "deny", "verb=%s floor=sh" % verb)
                refusal = refusal_for(FLOOR, verb, state, sentence)
        except Exception as exc:
            return refuse_unestablished(session, "pr merge",
                                        "shell-version floor raised %s" % type(exc).__name__,
                                        "sh_floor in ~/.claude/hooks/pr-merge-approval.py")
    if refusal:
        return deny(refusal)
    return 0


if __name__ == "__main__":
    try:
        from hook_run import run as _wrap
    except Exception:
        def _wrap(_check, fn, event=None):
            return fn() or 0
    sys.exit(_wrap(CHECK_ID, main, event="PreToolUse"))
