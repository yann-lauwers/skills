# Sign-in mechanics

## The browser

- Cloudflare Turnstile guards claude.ai's login and blocks Playwright's bundled chromium, headed or headless → `chrome.mjs` launches the installed Chrome and attaches over CDP.
- Cloudflare challenges the `HeadlessChrome` user agent → run headless with the agent naming plain Chrome, taken from the installed app's version, as `chrome.mjs` sets it.
- A sign-in → relaunch the profile in a window; every attempt counts toward the limit · `CLAUDE_LOGIN_VISIBLE=1` → a window for any run.
- `--window-position` cannot hide a window: Chrome moves one placed off-screen back onto the display → the separate `profiles/<email>/` cookie store is what keeps a run out of the person's own browser, which is never touched.

## The magic link

- Apple Mail's plain-text body drops the button → `login.mjs` reads the raw message source and undoes quoted-printable.
- The mail can lag minutes → the poll runs 300 s.
- Read Mail newest-first by position, never with a `whose` filter → `whose` walks the whole mailbox and outlasts AppleScript's 120 s event limit on a large one; `magicLink` reads the newest 30 and keeps the newest match by date.
- Mail just relaunched → it answers slowly, tens of seconds per call, for a while.
- Mailboxes are shared by several accounts → a link is this sign-in's only when all three hold: one recipient equals the address exactly, never a substring · it was received at or after the second this sign-in asked · it points at `https://claude.ai/magic-link`.
- `acceptLink` in `login.mjs` is that check, pure and held by `tests/pure.test.mjs`, which plants a substring match and a 30-second tolerance and must go red on each → change one only with the other.
- A concurrent sign-in of the same address can hand over its link → `ensureSession` closes by asking `api/account` who is signed in and throws unless it is the address named.

## How the link resolves

- A sign-in started on claude.ai → the link completes it itself and that tab is the signed-in page.
- A sign-in started elsewhere (the CLI's OAuth page) → the link shows a 6-digit code to type back into the original page, which holds the PKCE state.
- `signIn` handles both and returns whichever page is signed in.
