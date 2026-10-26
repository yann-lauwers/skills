# Handlers this layer runs beside but does not own

## Keyless pack — installed by `keyless setup`, enforced from its own checkout

- One engine, `python3 ~/Code/keyless/hooks/keyless_hook.py`, wired on `PreToolUse` and `PostToolUse` with no matcher; its predicates, tests, rollout and messages belong to that repo (`hooks/README.md`).
- It is invisible to every reader of this registry: its rows go to `~/.local/state/keyless/hook-decisions.jsonl`, its uppercase ids never parse as ids, and it sources neither `lib/hook_run.py` nor `lib/log-decision.sh`; a zero here means uninstrumented, and `keyless doctor` is its reader.
- Its mode is its own: `KEYLESS_HOOKS_OBSERVE=1` in the settings `env` records only, `KEYLESS_HOOKS_DISABLE=1` or `keyless disable` turns it off; `HOOK_MODE_*` reaches none of it.
- It never emits `allow`; a rewrite travels as `updatedInput` with no `permissionDecision`.
- It is the only secrets guard on this machine; the path list and vault-CLI table are its own (`keyless_hooks/secretpaths.py`, `KL-VAULT`).
- `keyless setup` also added `permissions.allow` entries for `keyless ls|items|fields|doctor|--version` and `Read(**/…)` deny entries; `keyless run` is absent from the allow list on purpose, since a prefix rule would approve whatever follows `--`. `keyless uninstall` removes exactly these from `~/.local/state/keyless/setup-receipt.json`.

| id | event | fires when | class |
| --- | --- | --- | --- |
| `KL-FILE` | PreToolUse (Read, Bash, Grep) | a credential file — `.env`, `~/.aws/credentials`, `~/.ssh/id_*`, `.npmrc`, `.claude.json` — is about to be read | ACT (names-only view) on Read · DENY on Bash and Grep |
| `KL-VAULT` | PreToolUse (Bash) | a vault CLI verb that prints plaintext, across 16 stores | DENY |
| `KL-ENV` | PreToolUse (Bash) | an environment dump, bare or inside an interpreter | ACT (masking `sed`) when bare · DENY when captured |
| `KL-ENVVAR` | PreToolUse (Bash) | a credential-named variable is echoed | WARN |
| `KL-ASSIGN` | PreToolUse (Bash) | a credential literal typed into a shell assignment | DENY, never rewritten |
| `KL-HEREDOC` | PreToolUse (Bash) | a credential literal written into a file through a here-document | DENY · WARN when no file is named |
| `KL-WRITE` | PreToolUse (Write, Edit, MultiEdit, NotebookEdit) | a credential literal in the text being written | ACT (`${NAME}`) where the reader expands it or the file is prose · DENY on a vendor shape elsewhere · WARN otherwise |
| `KL-SEEN` | PostToolUse (all) | a credential-shaped value in tool output | WARN |

## Plugins — wired by the harness

- The enabled set is `enabledPlugins` in `~/.claude/settings.json`; `claude plugin list --json` gives each plugin's `installPath`, and its handlers are in `<installPath>/hooks/hooks.json`.
- A plugin's handlers appear in no `settings.json` entry and write no decision row, so nothing here records what they decided; review what a plugin ships before enabling it.

## Orca — not wired

- Orca's entries were dropped from `~/.claude/settings.json`; an Orca install that writes them again shows as a `git diff` in `~/Code/machine-setup/home/`, and is reverted there.
