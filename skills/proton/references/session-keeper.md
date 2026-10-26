# The daemon's session

Reads run under a session keylessd owns, as the `_keyless` uid, in the `session_dir` keylessd's config names.

## The session

- A personal-access-token session lasts two hours, carries no lock and has no renewal verb: logging in again is the renewal.
- An emptied session directory heals itself — the token lives outside the session database, so the next command logs back in · a session expired at the cap stays populated and invalid, and only a fresh login replaces it.
- keylessd sets the token in every spawned command's environment → a failing read is never a missing token.
- `pass-cli personal-access-token list` answers under the account session and not under an agent's → it tells a web login from a token session.

## The loop

- A thread inside keylessd at the daemon's uid, switched on by `stores.proton.session.auto_login`, off by default.
- Two triggers, neither redundant: it replaces a session older than `login_after_minutes` (90), and every `probe_interval_seconds` (300) asks `pass-cli info` whether one still answers — the vendor drops sessions ahead of the cap without warning.
- Each renewal logs into a fresh `gen-<millis>-<pid>` directory under `session_dir`, proves it with `info`, then names it in `<session_dir>/current`; the generation reads are using is never opened, changed or deleted.
- On failure it backs off (1s→5m) and retries, re-reading the token from the credential file each attempt → a rotated token needs no restart.
- An unadopted machine runs the external keeper `system/sh.keyless.session-keeper` instead; never let it and the loop both own the session.

## Commands

| Command | When |
| --- | --- |
| `keyless-bootstrap-daemon` | wiring a machine, repairing a degraded or undecryptable store, `--rotate` after minting a token |
| `keyless-adopt-daemon-renewal` | moving the loop into keylessd, once per machine |
| `keyless-prove-renewal` | proving the loop repairs a session the vendor dropped early — destructive: drops the live session, and Proton reads degrade for the first minutes of its ~11 |

- The user runs `keyless-bootstrap-daemon` whenever it will ask for a token; a session never supplies one.
- Without `--rotate` it leaves a sound token alone and asks for nothing → the first command to reach for once reads start failing.
- It needs no `login` step: writing the credential file is the whole of wiring a machine and of rotating a token; its restart makes a rotated token take effect at once.
- `keyless-adopt-daemon-renewal` leaves `/usr/local/bin/keyless` alone: `peer.allow_images` pins the client by code hash, so replacing it without re-pinning refuses every request.
- Restart the daemon after a change to its config, never for a token change: the config is read once at startup, the credential file per lookup.

## Logging in

- `keylessd login` takes its token from a pipe, then the daemon's credential entry, then a prompt → `keylessd credential` then `login` costs one paste.
- `--prompt` forces the question; at a terminal `--replace` asks too, even with a token on disk.
- Without `--replace`, `keylessd login` refuses while the current generation answers and changes nothing; `--replace` makes a fresh generation current only once it proves itself.
- A token read from the credential file is never written back: that write can fail over a live session and report `logged_in_but_unwritten`.
- Judge a login by its exit code, never by re-reading the session.
- `src/daemon/login.rs`, `src/daemon/session.rs`, `src/store/proton_session.rs` and `src/store/proton.rs` in the daemon's source settle a question here faster than the error text.

## Traps

- A cache-independent reading of the daemon's session → `~/.local/bin/keyless-resume-check`, which reads one name twice and judges the audit rows.
- `vendor_says` in `keyless-bootstrap-daemon` and `as_daemon` in `keyless-prove-renewal` carry the working shape of `pass-cli info` as `_keyless`.
- `pass-cli info` as `_keyless` needs every `PROTON_PASS_*` variable inside the child, after `sudo -u _keyless`: sudo's `env_reset` strips them from the parent, and the check reads an empty default directory and answers "no session".
- Scope it at the current generation, `<session_dir>/<the name in current>`, never `session_dir` itself: the root holds no session, and the vendor creates `<root>/.session` on every verb.
- The client config's `session_dir` is a directory nothing maintains: it answers "no session" on a healthy machine.
- Under `key_provider: env` it needs `PROTON_PASS_ENCRYPTION_KEY` too, through the child's own environment (`execve`), never `env`'s argv, where `ps` shows it.
- `PROTON_PASS_KEY_PROVIDER` is never optional: a caller falling back to the vendor default `keyring` makes `pass-cli` force a logout — `Local encryption key not found but local data exists. Forcing logout for security.` — destroying the session for every caller.
- keylessd's config sets `env`, the daemon's default; `fs` is accepted, and `keyring` is a parse error that keeps the daemon from starting.
- `Error decrypting local session (aead::Error)` → no login repairs it, and it reads exactly like a wrong token; `keyless-bootstrap-daemon` empties the directory, safe because a token session keeps its token outside it and `keylessd login` is its only writer.
- Every `pass-cli` verb, reads included, against a directory with no identity creates `.session/pass-cli.db` and `.session/local.key` owned by whoever ran it → a hand-run `pass-cli` as anyone but `_keyless` leaves the daemon `Error creating local key file: Permission denied`, which points at the token; the loop names the `chown` and waits, and `keyless-bootstrap-daemon` gives the directory back.
- `stores.proton.binary` runs as `_keyless` holding the token while keylessd guards only its inbound edge → it and its whole path chain are root's; `keyless-bootstrap-daemon` installs a root copy under `/usr/local/libexec/` and backs the old config up to `.pre-harden`. Same test for anything a privileged job execs.

## The client config

- The injector's client config keeps `"secrets": {}` and `stores.proton.enabled: false`: keylessd's config is the only name list, and a client name list buries a real `DEGRADED` line under warnings.
- The person makes that edit: the guard pack refuses a session's write to that file.
- No local `proton` store: it would hand out more secrets once the daemon stops. The client's `keychain` store stays.

## The agent token

- It carries a mandatory expiry of at most one year, and issuing a new one kills the old at once; no loop removes this.
- `keylessd check` warns 30 days out; `keyless run` carries the warning on stderr from 14 days out.
- Its only home is the daemon's credential file — `0600`, the daemon's uid, a `0700` directory — never Proton, which it unlocks, and never a Keychain copy, by decision.
- Never `keyless put PROTON_AGENT_PAT`: it writes through the client's empty name list, and refuses while the daemon is on.

Rotation writes a credential, so the user runs it:

1. Hand the user both commands. Done when both exit 0.
   ```
   pass-cli agent renew <agent> --expiration <span>
   sudo keylessd credential --name AGENT_TOKEN --store proton   # reads stdin, echoes nothing
   ```
2. `stores.proton.token_expires` in keylessd's config → the new expiry, in the same change; it is the warning's only input. Done when the config reads the new date.
3. Prove a read, per `references/adding-a-secret.md` § Once the user says it exists. Done when the second read prints a length with no `DEGRADED` line.
