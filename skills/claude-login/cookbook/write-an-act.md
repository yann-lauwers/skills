# Writing an act

- An act is a script under `examples/`, never a skill; past `ensureSession`, claude.ai is plain Playwright → copy `examples/accept-invites.mjs`, the worked one.

```js
import { ensureSession } from '../session.mjs';
const s = await ensureSession(email);
try {
  const page = await s.browser.contexts()[0].newPage();
  await page.goto(url, { waitUntil: 'domcontentloaded' });
  const btn = await byText(page, /^accept( and open)?$/i);   // read the page by visible TEXT
  …
} finally { await s.close(); }
```

## What every act keeps

- Read the page by visible text, never by selector; nothing matches → throw, naming the buttons seen.
- An OAuth consent act → answer the organization picker through `login.mjs`'s `isOrgPicker` and `pickOrg` with the manifest's `org`, never with a regex of its own; the workspace is declared, never guessed.
- `cswap-relogin/browser.mjs` carries an older copy of that picker → `login.mjs`'s is the one kept current.
- One tab per unit of work, closed after; the session outlives it.
- `close()` in a `finally` → it stops Chrome, which flushes the cookies, and releases the lock; skipped → the account stays locked until the process dies.
- The act's effect is repeatable → its own ledger under `state/`, so a rerun is a no-op · the act mints a one-time credential → no ledger, a refused one is retried by running again.
- An act on a published Artifact → its content runs in a frame on `*.claudeusercontent.com`, and a design system's previews mount only as its view's own scroll container passes them → `examples/design-system-look.mjs` finds both.
- Iterating on an act → run it against a second account rather than retrying one.
