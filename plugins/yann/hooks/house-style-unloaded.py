#!/usr/bin/env python3
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import artifact_page

try:
    import hook_decisions
except Exception:
    hook_decisions = None
try:
    import hook_mode
except Exception:
    hook_mode = None
try:
    import skill_held
except Exception:
    skill_held = None

CHECK_ID = "house-style-unloaded"
SKILL = "house-style"

STYLE_RE = re.compile(r"<style[^>]*>", re.I)
SHEET_RE = re.compile(r"<link[^>]+rel\s*=\s*[\"']?stylesheet", re.I)
DESIGN_CANVAS_RE = re.compile(
    r"--cds-[a-z0-9-]+\s*:|\bdc-(?:canvas|artboard)\b|\bappifact-doc\b", re.I)

EXEMPTIONS = (
    ("design-canvas",
     lambda path, text: path.lower().endswith(".dc.html") or bool(DESIGN_CANVAS_RE.search(text))),
    ("no-visual-system",
     lambda path, text: not (STYLE_RE.search(text) or SHEET_RE.search(text))),
)

MESSAGE = (
    "This page is headed for publishing — a standalone HTML page written outside any "
    "repository — and the house style has not been loaded in this session, so its "
    "palette, type scale and component values would be invented for this one page.\n\n"
    "Load it first, then write the page against it:\n\n"
    "    Skill(skill=\"house-style\")\n\n"
    "It carries the generated token block a page pastes whole — every variable name, "
    "`--background` through `--muted-foreground`, with its value in both themes — the "
    "type scale, the component classes and the chart palette.\n\n"
    "A design-canvas artboard and a page that declares no CSS never reach this message. "
    "A page that belongs to a project is written inside that project's repository, "
    "where this gate is silent. This refusal repeats until the skill is loaded."
)


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
                           event="PreToolUse", mode="enforce" if acting() else "observe")
    except Exception:
        pass


def exemption(path, text):
    for name, applies in EXEMPTIONS:
        try:
            if applies(path, text):
                return name
        except Exception:
            return "row-cannot-decide"
    return None


def verdict(payload):
    page = artifact_page.authored(payload)
    if page is None:
        return None
    path, text = page
    if exemption(path, text):
        return None
    if skill_held is None or skill_held.held(payload, SKILL) is not False:
        return None
    session = payload.get("session_id")
    session = session if isinstance(session, str) and session else "unknown"
    detail = os.path.basename(path)
    if not acting():
        log("would-deny", detail, session)
        return None
    log("deny", detail, session)
    return MESSAGE


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    reason = verdict(payload)
    if reason:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }}))


if __name__ == "__main__":
    main()
