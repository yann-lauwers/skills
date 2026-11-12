---
name: keyless
description: "Runs a command with a named credential injected through `keyless run`. Started only by /keyless ."
disable-model-invocation: true
---

# keyless

A named credential reaches one child's environment and nothing else; no verb or flag prints a value.

```
keyless run -s DATABASE_URL -- psql
keyless run -s VAR=<NAME> -- <cmd>
keyless ls                                 the names you can use
```

- `<NAME>` → a `keyless ls` name, or a vault item's title as written: `<title>` reads its password · `<title>__<field>` a named field.
- `keyless` not on `PATH` → stop and say so.
- Every caller writes `keyless run` and the name; no wrapper script stands in front of it.

## A name that did not arrive

- `DEGRADED` on stderr → a store stayed silent and the child ran without the variable, at its own exit code → read stderr; exit 0 proves nothing.
- `DEGRADED` naming `daemon` or `proton`, or a renewed vault token → `references/daemon.md`.
- `REFUSED` (exit 64, the child never started) → check the app-runtime secrets injector the project's instructions name, where a wrong environment or path answers zero secrets with no error, before calling it missing; an item absent from the vault → /proton .

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

## Source

- `~/Code/keyless` (github.com/nbstr/keyless) → how the daemon behaves.
