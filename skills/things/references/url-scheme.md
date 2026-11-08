# The URL scheme

- Checklist items · project headings · the `evening` slot · appending to notes or tags rather than replacing them → `open "things:///<command>?<params>"`; AppleScript has no vocabulary for these.
- `add` · `add-project` · `show` · `search` · `version` → no token.
- `update` · `update-project` · a `json` payload carrying an update → need an `auth-token` this setup does not hold; reach the same result with AppleScript, and where AppleScript has no vocabulary (a checklist item, the evening slot or a heading on an existing item) → tell the user it is out of reach.
- Percent-encode every value; `%0A` separates newline-delimited lists.
- Full parameter roster → https://culturedcode.com/things/support/articles/2803573/
