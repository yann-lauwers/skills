# Moving to another provider

Credentials come from this store through `keyless run`, whose names survive a swap, so no `keyless run` call changes; every file naming the store, `/proton` included, is in the rename census below.

## Rewrite

- Every `secrets.*.vault` in keylessd's config → the new provider's vault.
- keylessd's config → declare the new provider as a store in the same pass, or every injected name degrades.
- This skill → `references/session-keeper.md` is a redesign: the two-hour token session is Proton's.

## Rename only

- Every other file naming the vendor in passing: `grep -RIl -i proton ~/Code/skills/ ~/.agents/AGENTS.md ~/.local/bin/`, minus this skill.
- The hooks name the vendor → the census finds them; rename them.
