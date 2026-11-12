# The daemon's store

- `keylessd check` as the login user reports `identity PROBLEM … Permission denied` and `store proton PROBLEM` on a healthy machine: it cannot read the daemon's credential file → is the session alive: `~/.local/bin/keyless-resume-check` (`FRESH` = the store answered) · what the renewal loop did: `/usr/local/var/log/keyless/keylessd.err`.
- The daemon renews its own session; reads still degrading after its next probe (five minutes), or the log repeating a failure → stop and hand the user `keyless-bootstrap-daemon`, which asks for sudo itself and for a token only when the stored one is unsound; one monitor on the repair, never a retry loop.
- A renewed vault token → the user sets `stores.proton.token_expires` in `/usr/local/etc/keyless/keylessd.json` to the new expiry, the expiry warning's only input, then runs `keyless-bootstrap-daemon --rotate`: one paste, it writes the credential file and restarts the daemon.
