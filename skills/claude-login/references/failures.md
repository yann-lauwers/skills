# When it stops instead of finishing

- "signed in X min ago — claude.ai rate-limits repeated sign-ins" → the 15-minute cooldown, which counts attempts as well as successes; wait, or `--force` only when the last attempt is known to have failed before the link was sent.
- "Too many login attempts" → claude.ai's own limit; leave that account alone for a while.
- "Cloudflare challenged /api/account" → rerun with `CLAUDE_LOGIN_VISIBLE=1`.
- "is held by pid N" → wait, or kill the named pid when it is a leftover.
- "signs in with google/apple SSO" → not drivable; the person signs in by hand in a normal browser; the manifest's `"sso"` key is what makes it refuse fast.
- "no magic link for <email> within Ns" → the address's login mail is not in the mailbox the manifest names; fix that account's `mailbox_account` · `mailbox`.
- The invite or authorize page asks for a sign-in although the session is live → rerun; twice in a row → the session is stale: `forget`, then `ensure`.
- Any other stop → the message names its fix where it has one · an account not in the manifest → `SKILL.md`'s manifest line · none → `references/sign-in-mechanics.md`.
