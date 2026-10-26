# When the run stops

- Each stop names what is missing → supply it, then re-run.
- A stop about the browser — a sign-in, a mailbox, a cooldown, a held profile → /claude-login 's own list of stops.
- "login landed on '<other>', not <account>", with cswap's log showing `Switched from account <target>` at the same second → the login landed and the verify read another profile: stop re-running, sign in by hand (`claude auth login`, then `cswap add`) and file it against the tool.
- "cswap add failed" → the global credential was restored and nothing was captured; read cswap's own error, the slot list is unchanged.
- "the browser half did not reach Authorize" → the lines above it name the page it stopped on; an org picker with no `--org` is the common one.
- An hCaptcha puzzle → no stop: the consent pass runs in a visible Chrome window, `browser.mjs` DMs Yann through `credential-watch notify`, waits up to 120 min for the puzzle to clear, then drives on in the same page · a page with no Authorize button → the same DM, and Yann finishes it up to Authorize there · either unfinished → `oauth.py` exits 3, the global account restored, nothing captured.
