# Permissions

| Tier | What it opens |
| --- | --- |
| Automation → Mail | every script in this skill: accounts, list, read, draft, trash, search, refresh |
| Accessibility | raising the compose window and sending it ⌘V, which is how `mail-draft.sh` places a body |
| Full Disk Access | `~/Library/Mail/`, which is the SQLite index and the message files `mail-search.sh` reads |

- A script's error naming `assistive access` → Accessibility · `Operation not permitted` on `~/Library/Mail/` → Full Disk Access · an error naming neither → not a permission; report it as printed.
- `mail-search.sh` stopped on Full Disk Access → answer from `mail-list.sh` plus `mail-read.sh` over the candidate range, and name the tier.

## Done when

A tier matched above → it is named in the reply as Yann's to grant, with the script that needs it;
no script is edited around a missing permission.
