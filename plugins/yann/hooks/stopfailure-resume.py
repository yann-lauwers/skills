#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import hook_decisions
import hook_run

CHECK_ID = "stopfailure-resume"
EVENT = "StopFailure"
RESUME_LINE = "continue (auto-resume after API error)"
SETTLE_SECONDS = float(os.environ.get("STOPFAILURE_RESUME_SETTLE_SECONDS") or 5)
TRANSCRIPT_TAIL_BYTES = 8 * 1024 * 1024
RESUME_SPENT = "Failed again right after an auto-resume (%s). Type continue to resume."
NOT_RESUMED = "The turn ended on an API error (%s) and could not auto-resume. Type continue to resume."
NOTIFY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nx-notify.sh")


def text_of(value):
    return value if isinstance(value, str) else ""


def transcript_entries(path):
    try:
        with open(path, "rb") as fh:
            fh.seek(max(0, os.path.getsize(path) - TRANSCRIPT_TAIL_BYTES))
            raw = fh.read().decode("utf-8", "replace")
    except OSError:
        return None
    entries = []
    for line in raw.splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if isinstance(entry, dict) and not entry.get("isSidechain"):
            entries.append(entry)
    return entries


def prompt_text(entry):
    if entry.get("type") != "user" or entry.get("isMeta"):
        return None
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return None
    parts = [part for part in content if isinstance(part, dict)]
    if any(part.get("type") == "tool_result" for part in parts):
        return None
    texts = [text_of(part.get("text")) for part in parts if part.get("type") == "text"]
    return "\n".join(texts) if texts else None


def is_model_output(entry):
    if entry.get("type") != "assistant" or entry.get("isApiErrorMessage"):
        return False
    message = entry.get("message") or {}
    return message.get("model") != "<synthetic>" and bool(message.get("content"))


def resume_already_spent(entries):
    for entry in reversed(entries):
        if is_model_output(entry):
            return False
        prompt = prompt_text(entry)
        if prompt is not None:
            return prompt.strip() == RESUME_LINE
    return False


def notify(folder, template, error):
    subprocess.run(
        ["bash", NOTIFY, "Claude Code stopped in %s" % (folder or "a session"), template % error],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        timeout=15, check=False)


def type_resume(workspace, surface):
    result = subprocess.run(
        ["cmux", "paste", "--workspace", workspace, "--surface", surface, "--submit", RESUME_LINE],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        timeout=15, check=False)
    return result.returncode == 0


def settle_and_act(session, transcript, error, folder, workspace, surface):
    time.sleep(SETTLE_SECONDS)
    detail = "error=%s" % error
    entries = transcript_entries(transcript) if transcript else None
    if entries is None:
        notify(folder, NOT_RESUMED, error)
        hook_decisions.log(CHECK_ID, "abstain", detail + " class=transcript-unreadable",
                           session=session, event=EVENT)
    elif resume_already_spent(entries):
        notify(folder, RESUME_SPENT, error)
        hook_decisions.log(CHECK_ID, "warn", detail + " reason=resume-spent",
                           session=session, event=EVENT)
    elif not (workspace and surface):
        notify(folder, NOT_RESUMED, error)
        hook_decisions.log(CHECK_ID, "abstain", detail + " class=no-cmux-seat",
                           session=session, event=EVENT)
    elif type_resume(workspace, surface):
        hook_decisions.log(CHECK_ID, "injected", detail, session=session, event=EVENT)
    else:
        notify(folder, NOT_RESUMED, error)
        hook_decisions.log(CHECK_ID, "warn", detail + " reason=paste-refused",
                           session=session, event=EVENT)


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    args = [
        text_of(payload.get("session_id")),
        text_of(payload.get("transcript_path")),
        text_of(payload.get("error")) or "unknown",
        os.path.basename(text_of(payload.get("cwd")).rstrip("/")),
        os.environ.get("CMUX_WORKSPACE_ID") or "",
        os.environ.get("CMUX_SURFACE_ID") or "",
    ]
    subprocess.Popen(
        [sys.executable, os.path.abspath(__file__), "--settle"] + args,
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True)


def settle():
    settle_and_act(*sys.argv[2:8])


if __name__ == "__main__":
    if sys.argv[1:2] == ["--settle"]:
        sys.exit(hook_run.run(CHECK_ID, settle, event=EVENT))
    sys.exit(hook_run.run(CHECK_ID, main, event=EVENT))
