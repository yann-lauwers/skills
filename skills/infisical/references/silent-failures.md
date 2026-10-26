# Silent failures

## The four settings that fail silently

Each differs from the CLI's own default → a wrong value reads as "the secret does not exist" → check the setting before the store.

| Setting | What a wrong value looks like |
| --- | --- |
| Domain | the CLI defaults to the US host and answers a bare `401 Invalid credentials`, indistinguishable from a bad credential |
| Environment | empty result set, no error |
| Path | a folder that does not hold the secret returns empty and no error; the miss surfaces later as a runtime failure · querying `/` reaches every folder |
| Project id | a machine-identity call fails with "Project ID is required" · `.infisical.json` `workspaceId` is honoured for user-token auth only |

## No login

- No session and no token on a TTY → the CLI opens an arrow-key login menu and waits forever, which looks like a hung server; off a TTY it exits 1.
- Every failure exits 1 — no login, unreachable, a server error, a bad token → tell them apart by the printed text, never the exit code.
- A server that accepts the connection and never answers → the CLI waits with no output; it sets no client timeout.

## An identity that reads nothing

- A machine identity can authenticate and resolve a project while returning zero secrets in every environment → project membership and secret-read permission are separate grants.
- Whether this project's identity carries the second → its config's `identity_reads_secrets` says; never infer it from a successful login.
