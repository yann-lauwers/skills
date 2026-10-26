# A read that failed

`keyless run` warns on stderr and runs the child with the variable unset; that `DEGRADED` line names which half failed — read it before anything else.

## Injected nothing

- `store <x> failed: … there is no session` → the session lapsed past the daemon's own renewal: § The renewal loop.
- `Error decrypting local session (aead::Error)`, `framing error: Resource temporarily unavailable`, or no answer within the timeout → terminal: read it once, stop, and hand the user `sudo keyless-bootstrap-daemon`; a retry returns the identical error.
- Waiting on that repair → arm one monitor on it, never a retry loop.
- The name unresolved, tail `no index yet` or `indexed <age>` → the miss queues a vault listing: a bare name answers on the second read; a `__<FIELD>` name says `the item behind that name serves: …` on the second and answers on the third.
- Unresolved past a fresh tail → the line names the cause: the title mints another name (`keyless ls` shows the minted form), the field is empty, or several items mint it.
- Confirm an item exists → read its name once, then `keyless ls`; `keyless items` and `keyless fields` use the client's own session, which nothing maintains, and answer `there is no session`.
- A read right after a daemon restart, upgrade, config change or reboot degrades once → read it twice before calling the store broken.

## Injected the wrong value

- A title matching two live items, or only a trashed one, is refused by name with every candidate id → hand over a retitle to `<entity>-<tool>-<environment>` or the purge of the trashed duplicate as an item spec (`references/adding-a-secret.md`), then prove the name resolves.
- Never recreate the item under the same title: the new one is active, the old stays trashed, and the collision survives.
- A retired value returned with no error → the read skipped the listing: a `pass://SHARE/ITEM/FIELD` reference or raw `pass-cli run`; use the minted name.

## The renewal loop

- `sudo launchctl print system/sh.keyless.keylessd` → the daemon; a healthy loop writes nothing to stderr.
- The startup line names no renewal → the loop is off or the installed build predates it: `stores.proton.session.auto_login` in keylessd's config says which, and `keyless-adopt-daemon-renewal` switches it on.
- `Proton session renewal failed` on stderr → the sentence after it is the vendor's; a refused token reads the same for expired, revoked and wrong, so check `stores.proton.token_expires` first.
- Silent and reads still failing → reads may answer from the 60-second cache while the session is dead, or the reverse; read the session as `references/session-keeper.md` § Traps gives it.
