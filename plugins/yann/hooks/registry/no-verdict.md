# Handlers that render no verdict

They write state, sync, notify or record, so they hold no row; every handler in `~/.claude/settings.json` is a row in a tier part or a name here.

`record-loaded-context.py`

- `record-loaded-context.py` writes `read-log/<session>` and the cumulative `skill-invocations.jsonl`, both for Skill-tool invocations only — a `/<skill>` the user types reaches neither — and stamps `canon:<sha>` and `always-loaded-bytes:<n>` on `InstructionsLoaded`.
- Wired to nothing: `nx-notify.sh`, `run-if-due.sh`.
