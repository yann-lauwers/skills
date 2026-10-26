import json

try:
    import hook_decisions
except Exception:
    hook_decisions = None

CHECK_ID = "tool-config-commit"
CHECK_ID_POINTER = "tool-config-pointer"


def log(check, session, verdict, detail):
    try:
        if hook_decisions:
            hook_decisions.log(check, verdict, str(detail)[:200], session=session)
    except Exception:
        pass


def acting(check):
    try:
        import hook_mode
        return bool(hook_mode.acting(check))
    except Exception:
        return True


def emit(decision, reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": decision,
                                             "permissionDecisionReason": reason}}))
