---
name: keyless
description: "Runs a command with a named credential injected into its environment through `keyless run`, without the value reaching the transcript. Use when a command needs an API key, token, DB URL or secret; a `.env` or credential read is refused; auth fails on a store value; on 'keyless', 'keyless ls', 'the token isn't found', a `DEGRADED` banner or a `KL-FILE` refusal. Not for adding, rotating or listing a secret — the secrets store's skill; not for app-runtime secrets — the tool holding `role: app-secrets`."
---

# keyless

A named credential reaches one child's environment and nothing else; no verb or flag prints a value.

```
keyless run -s DATABASE_URL -- psql
keyless run -s VAR=<NAME> -- <cmd>
keyless ls                                 the names you can use
```

- `keyless` not on `PATH` → stop and say so.
- Every caller writes `keyless run` and the name; no wrapper script stands in front of it.

## An unresolved name still runs

- `keyless run` never refuses: an unresolved name warns `DEGRADED` on stderr and the child runs without it, at its own exit code → read stderr; exit 0 proves nothing.
- `DEGRADED` naming a store that failed to answer → the tool `~/.claude/skills/agents-config/scripts/agents-config role secrets` resolves.
- No such name → check the app-runtime store (`role: app-secrets`), where a wrong environment or path answers zero secrets with no error, before calling it missing.

## Quoting

- The variable exists only in the child → single-quote a `sh -c` body: `keyless run -s TOKEN -- sh -c 'curl -H "Authorization: Bearer $TOKEN" "$URL"'`; double quotes expand it in the calling shell, where it is empty.
- A header on curl ≥ 8.3 → `keyless run -s K=<NAME> -- curl --variable %K --expand-header '<Header>: {{K}}' <url>`, keeping the value out of `argv`.
- A script reading a secret keeps every value away from its prints, and its variable names say which values those are.
- Inspect a credential store only through a script printing structure — whether it parses, entry names, the failing line.
- A live process holding injected values is a credential store: read one named variable, never list its environment (`ps eww`).
- Before a write near a credential store → `keyless doctor`; hook pack absent or off → say the write is unguarded.

## A `KL-FILE` refusal naming a path the command never mentioned

- The guard resolves a relative operand against the Bash tool's persisted cwd: after a `cd` into a protected directory, `cat /etc/hosts` is judged as `<cwd>/cat`.
- `ls` and `echo` still work while every named binary is refused → run `pwd`, then `cd` out as its own call: `cd x && cat f` is judged from the old cwd.
- Never `allowed`, `KEYLESS_HOOKS_DISABLE` or a subagent to get past it.
- This machine's extra protected paths → `_add` in the hook pack's config.

## Files

- Client config `~/.config/keyless/config.json` (`$KEYLESS_CONFIG`) · daemon config `/usr/local/etc/keyless/keylessd.json` · hook pack config `~/.config/keyless/hooks.json` (`$KEYLESS_HOOKS_CONFIG`) · hook decisions `~/.local/state/keyless/hook-decisions.jsonl`.

## Project config

- `~/.claude/skills/agents-config/scripts/agents-config get keyless source_checkout` → the source, for how the daemon behaves. Floor only.
