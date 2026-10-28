#!/usr/bin/env python3
import os
import sys

DETAIL_CAP = 200


def _record(check_id, exc, event):
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import hook_decisions
        hook_decisions.log(check_id, "error",
                           "why=%s" % repr(exc)[:DETAIL_CAP], event=event,
                           outcome="raised")
    except Exception:
        pass


def run(check_id, main, event=None):
    try:
        code = main()
    except Exception as exc:
        _record(check_id, exc, event)
        return 0
    return 0 if code is None else code
