---
name: claude-login
description: "Gets a Chrome signed in to claude.ai as one of this machine's accounts, with nobody at the browser, and keeps the session on disk. Use on 'accept those artifact invitations', 'open that artifact as dev-2', 'log in as that account', 'is that account signed in', 'sign it out', 'too many login attempts', or `claude-login status|ensure|forget|ensureSession`. Also fires before driving claude.ai in a browser for an account other than the person's own, and on an edit under `~/.local/share/claude-login/`. Not for reviving a dead cswap credential — /relogin ."
---

# claude-login

- `~/.local/share/claude-login/` — the tool: `session.mjs`'s `ensureSession(email) → { page, browser, close }` is its one API, `cli.mjs` the `claude-login` command, `examples/` the acts, one script each.
- `profiles/<email>/` — the session itself, its cookies on disk · `state/signins.json` — when each account last attempted, signed in, or was rate-limited.
- `~/.config/claude-login/accounts.json` — the manifest, per account: `mailbox_account` · `mailbox` · `org` · `sso` · `verified`.
- An account runs only once the manifest lists it under `accounts` → `"<email>": {}` is enough; write `mailbox_account` · `mailbox` · `org` · `sso` only where they differ from `defaults`.

## Getting a session

```
claude-login status [<email>]           which accounts hold a session, last sign-in, cooldown
claude-login ensure <email> [--force]   sign in if needed; exit 0 means signed in as that address
claude-login forget <email>             delete the profile — the only destructive verb
```

- Live or dead session → the same `ensure`; only a dead one reads mail and signs in.
- An act signs in through its own `ensureSession`, in the same run that uses the session → never after a separate `ensure`; some accounts' sessions are revoked server-side within minutes.
- Who is signed in → `https://claude.ai/api/account`'s `email_address` field (probed 2026-09-18), 403 when nobody is; never the page's own wording.

## Route

| Ask | Read or run |
| --- | --- |
| accept the artifact invitations waiting in a mailbox | `examples/accept-invites.mjs` |
| approve a `/design-login` authorize URL as one account, so a seat can write to that account's design-system projects | `examples/design-authorize.mjs` |
| prove named cards are listed and drawn in a design-system pane, the bundle links every component, and the index still carries them after the load — one `CARD`, `BUNDLE`, `INDEX` and `RESULT` line each, exit 0 only when all hold; usage in its header | `examples/design-pane-check.mjs` |
| save a design-system project's card index as its pane holds it (`--save`), or diff it against a local one (`--against`) — the cards and components each side lacks, and each card filed under another group | `examples/design-index.mjs` |
| write a new act, or change one | `cookbook/write-an-act.md` |
| a run stopped with a message instead of finishing | `references/failures.md` |
| change `chrome.mjs` or `login.mjs`, or a sign-in misbehaves with no message naming why | `references/sign-in-mechanics.md` |
| no row matches | the header of each script under `examples/`; none fits → `cookbook/write-an-act.md` |

## Done when

- `claude-login ensure <email>` exits 0 printing `signed in as <email>` → that line is the proof; `status`'s `●` only says a sign-in once completed and the profile is still there.
- An act → its own last line says what it did, and its ledger, where it keeps one, records it.

## The profiles are live sessions

- `profiles/<email>/` holds real cookies for a real account → never print, `cat`, upload or copy one into a report.
