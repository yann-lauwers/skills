# The toolkit — scripts and examples

Every script is run, never paraphrased. Each declares its own dependencies and `--help`.

| Script | Purpose |
|---|---|
| `${CLAUDE_SKILL_DIR}/scripts/check_inventory.py` | AST enumeration of check ids; reconcile code against the registry; find dead checks |

| Example | Purpose |
|---|---|
| `examples/engine.py` | Minimal single-engine skeleton: the fold, two-view triggers, command-position anchoring, observe marker, decision log, per-check fail-open with a recorded trace. Copy it when starting a new engine |
| `examples/settings-snippet.json` | Wiring shape for `.claude/settings.json` |

Try it from the skill's directory; nothing here touches the project:

```bash
python3 scripts/check_inventory.py --src examples --sink log_decision --arg 2
```
