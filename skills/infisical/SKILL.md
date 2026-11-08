---
name: infisical
description: "Runs a script, test, server or browser run with the app's runtime secrets injected, and finds why a secret read came back empty or refused. Use when a value is missing from `.env`, or on 'secret not found', 'no valid login session', `401 Invalid credentials` or 'Project ID is required'. Also fires on the ACT — starting the app, its tests or a script that reads runtime secrets from its environment. Not for an agent's own tooling credential or a refused `.env` read — /proton and /keyless ."
user-invocable: false
---

# Infisical

- The injector, the store path and the env files that win over it come from the project's instructions — never from this file, never a guess.
- A read came back empty, a bare `401`, "Project ID is required", or a run hangs with no output → `references/silent-failures.md`.

## The project's instructions

- The project's instructions name the injector command (`<path>` and `<command>` placeholders), the store path, the env files that win over injected values, and whether the machine identity reads values; none stated → ask the user how the project supplies runtime values, never a vendor CLI directly.

## Running a command

- Wrap the command in the injector → values reach the child's environment, never stdout, the transcript or the argument list.
- Never fetch a value and hold it.
- Confirm a secret resolved → its character count or a fixed `present` / `absent`, never the value or a prefix of it.
- The injector reporting no login session → hand the user the fix it names; never run an interactive login · a vendor CLI run directly reporting no session → rerun through the injector.
