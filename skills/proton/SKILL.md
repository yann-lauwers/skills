---
name: proton
description: "Proton Pass vault conventions: the spec for an item the user creates or changes, and renewing the agent token."
disable-model-invocation: true
---

# Proton

- The vault → the one the host's instructions name; it holds every tooling credential, so an item's title is global.
- The agent's access is read-only by decision: the user makes every change in the Proton Pass app.
- `pass-cli` by hand → never: bare, it answers from the default session directory, the user's full-account login over every vault.

| Case | Read |
| --- | --- |
| A credential that has to exist or change | `references/item-spec.md` |
| The agent token expiring or renewed | `references/agent-token.md` |
