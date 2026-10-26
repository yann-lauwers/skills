---
name: proton
description: "Specifies, rotates, renames and reads developer-tooling credentials in Proton Pass, the `role: secrets` store, and keeps the injector daemon's vault session alive. Use on 'vault locked', 'add a secret to the vault', 'rotate a secret', 'list vault items', 'the daemon lost its Proton session', 'renew the agent token', 'proton pass'; also before a `<NAME>__<FIELD>` read or `pass-cli` runs, and when `keyless run` injects nothing. Not for app-runtime secrets — the tool holding `role: app-secrets`."
user-invocable: false
---

# Proton

One shared vault holds every developer-tooling credential; item titles are global, so nothing is per-project.

## Project config

- `~/.claude/skills/agents-config/scripts/agents-config get proton vault` → the vault, from `~/.claude/skills/agents-config/integrations/proton.md`. Floor only: no repo gets its own.
- Config absent → the store is not wired on this machine: ask which provider holds the credentials, never guess a command.
- keylessd's config, its path the `--config` default `keylessd check --help` prints → the store's `session_dir`, `key_provider`, `binary`, `token_expires` and `session.auto_login` · `~/.claude/skills/agents-config/scripts/agents-config get --role injector source_checkout` → the daemon's source.

## Reading

- `keyless run -s VAR=<NAME> -- <cmd>` → the item's password · `<NAME>__<FIELD>` → a named field.
- Nothing to declare: the daemon mints `<NAME>` from the vault — the title uppercased, every non-alphanumeric as `_`, a leading digit prefixed with `_`.
- The daemon lists the vault and reads the match by share and item id under its vault-scoped agent session → never read through raw `pass-cli item view` or `pass-cli run`: they fall back to the full-account login and skip the trash filter.
- Provenance: 2026-09-02, `keyless run -s K=NEXUS_LINEAR -- sh -c 'echo "${#K} chars"'` printed a length and no value; an unknown name warned `DEGRADED` on stderr and exited 0.
- Confirm an item exists → read its name once, then `keyless ls`, never `pass-cli item list`: it reads under a session nothing maintains, and `--output json` prints every item's secret fields.
- A job running as root is refused: `peer.allow_uids` in keylessd's config excludes 0, with no root exemption → `sudo -u '#501' keyless run …`, or add root to that list deliberately.

## Conventions

- Item title `<entity>-<tool>`, lowercase-hyphenated; `<entity>` owns the account — a project, a business or a person.
- Never write to the vault: hand the user an item spec, then prove the name resolves.
- Which item serves which service → `keyless ls` and the vault; canon keeps no list of it.
- Every consumer reads through `keyless run`, unattended jobs included; no job gets a store of its own.
- Never confirm a session with a bare `pass-cli info` — `references/session-keeper.md` § Traps.

## Routing

| Task | Read |
| --- | --- |
| A credential that has to exist or change — new, rotated, retitled, purged | `references/adding-a-secret.md` |
| A read that injected nothing or the wrong value | `references/troubleshooting.md` |
| Wiring a machine, a session that keeps dying, logging the daemon in, rotating the agent token | `references/session-keeper.md` |
| Moving the vault to another provider | `references/moving-provider.md` |
