# The URL scheme

- Checklist items · project headings · the `evening` slot · appending to notes or tags rather than replacing them → `open "things:///<command>?<params>"`; AppleScript has no vocabulary for these.
- `add` · `add-project` · `show` · `search` · `version` → no token.
- `update` · `update-project` · a `json` payload carrying an update → need `auth-token`, which the user enables at Things → Settings → General → Enable Things URLs → Manage, and which lives in the item the config's `secret` names.
- Token absent → reach the same result with AppleScript.
- Percent-encode every value; `%0A` separates newline-delimited lists.
- Full parameter roster → https://culturedcode.com/things/support/articles/2803573/
