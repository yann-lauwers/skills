---
name: infisical
description: "Runs a script, test, server or browser run that needs app-runtime secrets through the project's own injector, and finds why a secret read came back empty or refused. Use when a value is missing from `.env`, a run needs an API key or database URL, or on 'infisical', 'app secrets', 'secret not found', 'no valid login session', `401 Invalid credentials`, 'Project ID is required'. Not for an agent's own tooling credential or a refused `.env` read — the tool holding `role: secrets` and the credential injector."
user-invocable: false
---

# Infisical

- Every key's value comes from the project config — never from this file, never a guess.
- A read came back empty, a bare `401`, "Project ID is required", or a run hangs with no output → `references/silent-failures.md`.

## Project config

- `~/.claude/skills/agents-config/integrations/infisical.md` (floor) and `<repo>/docs/agents/integrations/infisical.md` (project) — read them merged first → `~/.claude/skills/agents-config/scripts/agents-config get infisical <key> --root "$CLAUDE_PROJECT_DIR"`, then run the command `injector` names.
- The config's body names values tiered below the store — a per-developer env file that wins over what is injected → read it.
- No project config → `~/.claude/skills/agents-config/scripts/agents-config role app-secrets`; still nothing → ask the user how the project supplies runtime values, never a vendor CLI directly.

| Key | What it answers |
| --- | --- |
| `injector` | the repo's own command that wraps a child with the store's values — `<path>` and `<command>` placeholders |
| `domain` | the store's host; unset → `references/silent-failures.md` § The four settings that fail silently |
| `environment` | the environment the values are read from |
| `path` | the folder the values sit in |
| `recursive` | whether the path's subfolders are read too |
| `project_id` or `project_id_source` | the project id, or the file and field that carry it |
| `token_file` | the user token the injector reads, where the repo uses one |
| `identity_reads_secrets` | whether the vault item's machine identity may read values at all |
| `secret` | the vault item holding a machine identity, or `null` |

## Running a command

- Wrap the command in the injector → values reach the child's environment, never stdout, the transcript or the argument list.
- Never fetch a value and hold it.
- Confirm a secret resolved → its character count or a fixed `present` / `absent`, never the value or a prefix of it.
- The injector reporting no login session → hand the user the fix it names; never run an interactive login · a vendor CLI run directly reporting no session → rerun through `injector`.
