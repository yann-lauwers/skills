---
name: garmin
description: >-
  Mints and re-mints a Garmin Connect login's tokens through the unofficial `garminconnect`
  library, and carries its traps. Use on "garmin token expired", "re-mint the garmin token",
  "garmin login", or a Garmin call failing on "Token is not active",
  `GarminConnectAuthenticationError` or a 429; also before a Garmin login runs or its item is read
  from the secrets store.
---

# Garmin

## Project config

- Config: the repo's `docs/agents/integrations/garmin.md` over the floor, read merged: `~/.claude/skills/agents-config/scripts/agents-config get garmin <key> --root "$CLAUDE_PROJECT_DIR"`; its body names whose login each item holds.
- Only a mint reads it.
- No `docs/agents/integrations/garmin.md` in the repo → ask the user; on their yes, write it per /managing-harness , `references/skills.md` § A tool's skill and its config, with the keys below, never guessing a value; then continue.
- `keyless ls` lacks the item, or `command -v keyless` finds nothing → the user types the login in their own shell.

| Key | What it answers |
| --- | --- |
| `secret` | the item holding one person's Garmin Connect login, fields `email` and `password` |
| `login_command` | the repo's command that logs in and stores the new tokens, `<slug>` the person the mint is for |
| `login_env` | the two env vars `login_command` reads, the email's first and the password's second |

- A person with no login item → hand the user its spec per the secrets store's skill, named as the config's body gives.

## Tokens

- Each stored copy of a token dies on its own after days unused → one copy staying green says nothing about another.
- `Token is not active` or a `GarminConnectAuthenticationError` → the token is dead: re-mint it, never refresh it.
- A token that reads fine locally can still be refused from the cloud → only a run on the copy the cloud holds proves it.
- A `garminconnect` call that starts failing → bump `garminconnect` before debugging the caller's code.

## Re-mint

- The user mints in their own terminal — never through the session, never behind `!`: the login can stop on an MFA prompt, and it prints the new token bundle to stdout.
- Repeat logins are 429'd account-wide.
- Two logins at once invalidate each other.
- Check the person and the item against each other before it runs: a mint carrying another person's login writes that account's data under the person it names and exits 0.
- Where the injector holds the item, the login runs as below, `<ITEM>` the item's name uppercased with every non-alphanumeric as `_`:

```sh
keyless run -s <login_env[0]>=<ITEM>__EMAIL -s <login_env[1]>=<ITEM> -- <login_command>
```
