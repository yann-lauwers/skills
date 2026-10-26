# Identities and session files

## Which identity

- Verify an identity's `profile` against `profile.info_cache` in the `Local State` file at the root of the browser's user-data directory, which maps each directory to the name the browser shows — never against directory order.
- An `interactive-only` identity → never load a session file for it; say so, never fall back to another identity.

## Three words the routes turn on

- Identity — an account axis: one row in the config, and the browser profile behind it.
- Live session — the browser the person is using; only a live-browser route reaches it, and it alone holds a session cookie.
- Derived session — a file read out of that profile's cookie store on disk: a snapshot, always behind the live one, and blind to anything the browser never flushed.
- Dispatched run — one with no person watching.

## Minting — the three forms

- `browser-login` writes session files into `~/.local/share/browser-sessions/`, one per identity or `<identity>-<environment>`; `browser-login --list` says which identities are minted.
- A session file is a login: never committed, printed or synced; a leaked one → rotate that login.
- A session file loads only into a browser of its own: `PW_SESSION=<identity> pw state-load <file>` in an isolated browser, `storageState` in a `yann:browser-pilot` script — never the session's default browser, which every subagent shares.
- "Reuse my session" → the first form.

| Form | What it does |
| --- | --- |
| `browser-login --from-dia <identity>` | derives a session from the live browser profile's cookie store, decrypting through Keychain — no sign-in, nothing typed |
| `browser-login --from-dia <identity> <host> …` | the same, keeping only cookies for those domains and their subdomains |
| `browser-login <identity>[-<environment>]` | opens a browser the person signs into by hand |

- **Name the hosts: scope a derive to the domains the task names, minted as `<identity>-<site>` so the full session is not overwritten; an unscoped one hands a run a login for every site the person is signed into, and a dispatched agent is right to refuse it.**
- Domains match as labels: `dkv.be` does not admit `mydkv.be`.
- A scoped file serves one site: a task reaching a second one re-mints rather than reusing what is on disk.

## What a derived session cannot carry

- A session cookie never reaches a derived session; the mint warns which hosts carry one.
- A site authenticating on a session cookie mints clean and fails as if the credential were bad → `pw --live`, `references/cdp.md`; re-minting never fixes it.
- `localStorage` is never carried either: it lives in LevelDB, outside the cookie store.
- A derived session failing to authenticate → read the cookies the page carries before naming which of the two is the cause.
