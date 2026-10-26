# The item spec

The user creates or changes the item in the Proton Pass app from a spec written in the reply; a rotation or a retitle lists only the fields that change.

## The spec

One row per field, no value anywhere in it:

| Part | What it says |
| --- | --- |
| Vault | the config's `vault` |
| Item | a Login item titled `<entity>-<tool>` |
| Per field | username, password, or a custom field with a stable lowercase name, and where its value comes from — the app's generator with the length and character set the consumer needs, a vendor console page, an existing item, or a local file by path; a multi-line value such as a PEM key goes whole into a custom field or a note |
| Names | the minted name each field resolves under |

- A value with a format constraint says so in its row — hex only, a fixed length, no symbols inside a URL: the generator adds symbols by default.

## Once the user says it exists

1. Read the name twice, a few seconds apart: `keyless run -s V=<NAME> -- sh -c 'printf "%s\n" "${#V}"'`. Done when the second read prints no `DEGRADED` line — the first read of a new name degrades once while the daemon lists the vault; a `DEGRADED` line on the second → `references/troubleshooting.md` § Injected nothing.
2. Compare the length with the one the spec named, the vendor documents, or the user reads off the console. Done when they match; no length known → a non-empty length plus one authenticated call to the service.
