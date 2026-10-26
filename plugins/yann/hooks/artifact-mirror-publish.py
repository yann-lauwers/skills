#!/usr/bin/env python3
"""PostToolUse — a page published to the hosted artifact store is copied into the local one.

FAILURE IT PREVENTS. A page is published to claude.ai, the session ends, the scratchpad it
was written in is cleaned, and the account that owns the page is not the account signed in
next week. The page is then gone locally and unreachable remotely at the same time.
Measured 2026-09-08 across every recorded session on this machine: 188 artifacts split
across three accounts, 161 of 168 source files written under /private/tmp, 25 still on disk.

WHY THIS CAPTURES AND DOES NOT BLOCK. An earlier version of this design switched the
Artifact tool off. That bought the local copy by removing the ability to share a page with
anyone who is not sitting at this machine, which is a capability the tool exists for. The
model is ArchiveBox's: the normal path is never interrupted, and a copy is kept as a side
effect. Publishing stays exactly as it was; this runs afterwards and takes a copy.

WHY PostToolUse AND NOT PreToolUse. The remote's identity — its url, its slug, its version —
exists only after the publish has happened, and those are the fields that cannot be
recovered later. A PreToolUse copy would have the bytes and none of the addressing.

IT REWRITES NOTHING, AND IT ASKS FOR BOTH LINKS. `updatedToolOutput` would let this replace
the URL the model reports, and it deliberately does not: the hosted URL is the one the user
asked for when they published, and a hook that quietly swaps it makes the tool lie about
where the page is. The local address is ADDED, in `additionalContext`, beside it.

The first revision said to mention the local copy "only if the user asks where it lives",
and the copy then existed with no way to reach it: the reply carried the hosted URL, the
served address appeared nowhere, and the store was invisible from the conversation that
filled it. A capture the reader cannot open is a backup, not a second route.

TWO CHANNELS, BECAUSE ONE OF THEM IS A REQUEST AND THE OTHER IS NOT.
`additionalContext` reaches the MODEL, so anything sent there is a nudge the reply may or
may not carry, and the second revision wrote it as an imperative — "REPORT BOTH ADDRESSES"
— which is the exact shape messages.md § The rules behind those verdicts warns against: text a
hook hands the model is written as facts, never an order to the model, "which can trip the
host's prompt-injection defences and surface the text to the user instead of using it as context".
So the context is now a statement of where the copy is, and nothing is asked of the model.

`systemMessage` reaches the USER directly — messages.md: *"displays to the human. One-way:
a hook can show a question but cannot collect an answer."* The served URL goes there, so it
lands on Yann's screen whether the reply mentions it or not. That is what makes the local
address a guarantee rather than a hope. It is discarded at `SubagentStop` and `PostCompact`;
this fires on `PostToolUse`, which carries it.

IT OPENS THE LOCAL COPY WHERE CLAUDE CODE OPENS THE HOSTED ONE. Claude Code opens the
hosted URL in the browser on a first publish, so the `systemMessage` alone left the local
copy as a line of terminal text beside a tab that had already opened. The served URL goes to
bare `open`, which hands it to the person's default browser. The gate mirrors the host's own:
the result's `updated` flag is `False` (a first publish — a redeploy opens nothing, and a
missing or non-boolean flag is no opinion), the call is not from a subagent, the entrypoint
is the interactive CLI, the session is not remote, and `CLAUDE_CODE_ARTIFACT_AUTO_OPEN` is
not switched off. An `open` that fails costs the tab, never the copy or the message.

CONTRACT (verified against hook-development/references/events-and-contracts.md).
  exit 0 + no stdout                             -> silent
  exit 0 + hookSpecificOutput.additionalContext  -> the local path reaches the model
  any other exit                                 -> non-blocking error; the publish stands

A crash here loses a copy, never a publish. Every payload field is coerced at the entry
point and there is no blanket except.
"""

import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
try:
    import hook_decisions
except Exception:
    hook_decisions = None
try:
    import hook_mode
except Exception:
    hook_mode = None

CHECK_ID = "artifact-mirror-publish"
ARTIFACT_BIN = os.path.expanduser("~/.local/share/claude-artifacts/bin/artifact")
# The store's fixed serving port, declared in `bin/artifact` as PORT.
STORE_PORT = 4310
SLUG_RE = re.compile(r"^[0-9a-f-]{8,64}$")
CAPTURE_INCOMPLETE = 6
MISSING_RE = re.compile(r"^missing (.+): (.+)$")


def acting():
    if hook_mode is None:
        return False
    try:
        return bool(hook_mode.acting(CHECK_ID))
    except Exception:
        return False


def log(verdict, detail, session):
    if hook_decisions is None:
        return
    try:
        hook_decisions.log(check=CHECK_ID, verdict=verdict, detail=detail, session=session,
                           event="PostToolUse", mode="enforce" if acting() else "observe")
    except Exception:
        pass


AUTO_OPEN_OFF = {"0", "false", "off", "no"}


def opens_here(payload, resp):
    """True where Claude Code itself auto-opens the hosted page on this publish."""
    if resp.get("updated") is not False:
        return False
    if payload.get("agent_id"):
        return False
    if os.environ.get("CLAUDE_CODE_ENTRYPOINT") != "cli":
        return False
    if os.environ.get("CLAUDE_CODE_REMOTE", "").strip().lower() == "true":
        return False
    return os.environ.get("CLAUDE_CODE_ARTIFACT_AUTO_OPEN", "").strip().lower() not in AUTO_OPEN_OFF


def open_in_browser(url):
    try:
        return subprocess.run(["open", url], capture_output=True, timeout=10).returncode == 0
    except Exception:
        return False


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict) or payload.get("tool_name") != "Artifact":
        return 0

    resp = payload.get("tool_response")
    if not isinstance(resp, dict):
        return 0

    # A publish is the only action that produces all three. Every read, list, comment and
    # database action is missing at least one, so no action list has to be maintained here.
    url = resp.get("url")
    path = resp.get("path")
    slug = resp.get("artifact_id")
    if not (isinstance(url, str) and isinstance(path, str) and isinstance(slug, str)):
        return 0
    if not SLUG_RE.match(slug) or not os.path.isfile(path):
        return 0

    session = payload.get("session_id")
    if not acting():
        log("would-capture", slug[:8], session)
        return 0

    cmd = [sys.executable, ARTIFACT_BIN, "capture", path,
           "--url", url, "--artifact-id", slug]
    for flag, key in (("--version", "version"), ("--title", "title")):
        value = resp.get(key)
        if isinstance(value, str) and value:
            cmd += [flag, value]

    tool_input = payload.get("tool_input")
    tool_input = tool_input if isinstance(tool_input, dict) else {}
    files_json = None
    if "files" in tool_input:
        cmd += ["--files-json", "-"]
        root = tool_input.get("root")
        cwd = payload.get("cwd")
        files_json = json.dumps({
            "files": tool_input.get("files"),
            "root": root if isinstance(root, str) else None,
            "cwd": cwd if isinstance(cwd, str) else os.getcwd(),
        })

    try:
        out = subprocess.run(cmd, input=files_json, capture_output=True, text=True, timeout=120)
    except Exception:
        log("capture-failed", slug[:8], session)
        return 0

    if out.returncode not in (0, CAPTURE_INCOMPLETE):
        log("capture-failed", f"{slug[:8]} rc={out.returncode}", session)
        # Said out loud rather than swallowed: a copy that silently did not happen is the
        # exact failure this hook exists to end.
        print(json.dumps({
            # A copy that did not happen has to reach the person, not only the model —
            # this is the one outcome nobody finds out about later.
            "systemMessage": f"No local copy was kept of {slug[:8]} — see the reply.",
            "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": (
                f"The local mirror of this artifact did not happen: "
                f"{(out.stderr or '').strip()[:400] or 'the capture command failed'}. "
                f"The hosted page is fine. To keep a local copy, run: "
                f"{ARTIFACT_BIN} capture {path} --url {url} --artifact-id {slug}"),
        }}))
        return 0

    where = (out.stdout or "").strip().splitlines()
    where = where[-1] if where else slug
    # `capture` names every OTHER hosted copy of this page on stderr: a hosted page is
    # visible only from the account that published it, and this machine rotates accounts,
    # so one page can hold several. Relayed to both channels, because a session that sees
    # only one copy reads the others as deleted and publishes yet another.
    others = []
    missing = []
    for line in (out.stderr or "").splitlines():
        if line.startswith("note: this page already has"):
            others = re.findall(r"(https://claude\.ai/\S+) \(([^)]+)\)", line)
        m = MISSING_RE.match(line)
        if m:
            missing.append((m.group(1), m.group(2)))
    if out.returncode == CAPTURE_INCOMPLETE and not missing:
        missing.append(("(unnamed)", "capture reported files missing without naming them"))
    served = f"http://127.0.0.1:{STORE_PORT}/{where}/"
    log("captured-incomplete" if missing else "captured", where, session)
    opened = False
    if opens_here(payload, resp):
        opened = open_in_browser(served)
        log("opened" if opened else "open-failed", where, session)
    keys = ", ".join(p for p, _ in missing)
    print(json.dumps({
        # Reaches the user directly, so the local address arrives whatever the reply says.
        "systemMessage": f"Local copy: {served}" + (" (opened)" if opened else "")
                         + (f" — missing {len(missing)} file(s): {keys}" if missing else "")
                         + (" · also hosted at " + ", ".join(f"{u} ({a})" for u, a in others)
                            if others else ""),
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            # Reaches the model. A statement of fact, never an instruction — an imperative
            # here reads as an injected command to the host's defences.
            "additionalContext": (
                (f"This artifact has {len(others) + 2} addresses: the hosted URL the tool "
                 f"returned, the other hosted "
                 f"cop{'y' if len(others) == 1 else 'ies'} "
                 + ", ".join(f"{u} (on the {a} account)" for u, a in others)
                 + ", and a local copy. Each hosted copy is visible only from the Claude "
                   "account that owns it, so one that reads 'not found' from a session on "
                   "another account is not deleted. "
                 if others else
                 "This artifact has two addresses. The hosted one is the URL the tool "
                 "returned. ")
                + f"The local one is {served} — a copy in the artifact store at "
                f"{where}, stamped with the account that owns the hosted page, holding the "
                f"page and every file this publish and earlier ones sent, so it opens from "
                f"every Claude account on this machine and outlives the scratchpad. "
                + (f"The local copy lacks {keys}: "
                   + "; ".join(f"{p} ({r})" for p, r in missing)
                   + ". Those parts 404 there while the hosted page renders whole; a publish "
                     "to the same url sending them completes it. " if missing else "")
                + ("It was opened in the default browser beside the hosted page. " if opened
                   else "") +
                f"It is served rather than opened from disk, because a page's diagram "
                f"library loads from a root-relative path and renders blank from a file. "
                f"Nothing answering on that port is a stopped server rather than a missing "
                f"page, and `launchctl kickstart -k gui/$(id -u)/com.yann.claude-artifacts` "
                f"restarts it. Every one of these addresses is useful to whoever reads the reply."),
        }}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
