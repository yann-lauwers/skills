---
name: garmin
description: >-
  Mints and re-mints a Garmin Connect login's tokens. Use on "garmin token expired", "garmin login",
  or a Garmin call failing on "Token is not active", `GarminConnectAuthenticationError` or a 429;
  also before a Garmin login runs or its item is read from the secrets store.
---

# Garmin

Needs: `GARMIN_EMAIL` and `GARMIN_PASSWORD` — one person's Garmin Connect login, read only by the repo's login command; unset → the command prompts in the user's own shell.

## Whose login

- Which item holds whose login, and the command that logs one in → as the project's instructions state them; none stated → ask the user.
- A person with no login item → hand the user its spec per /proton , named as the project's instructions give.

## Tokens

- Each stored copy of a token dies on its own after days unused → one copy staying green says nothing about another.
- `Token is not active` or a `GarminConnectAuthenticationError` → the token is dead: re-mint it, never refresh it.
- A token that reads fine locally can still be refused from the cloud → only a run on the copy the cloud holds proves it.
- A `garminconnect` call that starts failing → bump `garminconnect` before debugging the caller's code.

## Re-mint

- The user mints in their own terminal — never through the session, never behind `!`: the login can stop on a password or MFA prompt, and everything a `!` command prints lands in the transcript.
- Repeat logins are 429'd account-wide.
- Two logins at once invalidate each other.
- Check the person and the item against each other before it runs: a mint carrying another person's login writes that account's data under the person it names and exits 0.
- The login runs as the project's instructions give it.
