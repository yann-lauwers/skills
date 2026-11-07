import os
import re

ENFORCE = "enforce"
OBSERVE = "observe"


def env_name(check_id):
    return "HOOK_MODE_" + re.sub(r"[^A-Z0-9]", "_", str(check_id).upper())


def resolve(check_id, default=None):
    try:
        value = os.environ.get(env_name(check_id))
        if isinstance(value, str) and value.strip().lower() in (ENFORCE, OBSERVE):
            return value.strip().lower()
    except Exception:
        pass
    return default if default in (ENFORCE, OBSERVE) else ENFORCE


def acting(check_id, default=None):
    return resolve(check_id, default) == ENFORCE
