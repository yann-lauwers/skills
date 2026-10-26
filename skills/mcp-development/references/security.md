# Security

Normative text is from the 2026-07-28 revision and the Security Best Practices page (`https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices`), read 2026-09-22.

## The premise

- Annotations are hints a client "should never make tool use decisions based on" when the server is untrusted. The maintainers' own post (MCP blog, 2026-03-16, "Tool Annotations as Risk Vocabulary"): "An untrusted server can lie. A server can claim `readOnlyHint: true` and delete your files anyway … They aren't enforcement."
- Risk is "a property of the session, not of any single server" — private data, untrusted content and an outbound channel in one session is the dangerous combination, and no single server's annotations see it.
- Enforcement lives in deterministic controls: the client's permission rules, the transport's access control, and the server's own authorization checks.

## Every server

- Tools page, verbatim: "Servers **MUST**: Validate all tool inputs; Implement proper access controls; Rate limit tool invocations; Sanitize tool outputs."
- A validation failure is an `isError` result the model can read and correct from, never a crash.
- Tool output is untrusted input to the next model turn. Content the server relays from elsewhere (a web page, a file, a ticket body) can carry instructions; label its provenance in the result and never let it widen what the server itself does.
- A read verb that returns a credential is a write in disguise: a token, a secret, or a transcript carrying either does not belong in a tool a client auto-approves.
- State handles (`references/protocol-surface.md` § Tools): "**MUST NOT** treat possession of a state handle as authentication"; random, expiring, and bound server-side to the verified principal.
- JSON Schema: never auto-dereference a network `$ref`; bound composition depth.
- Log to stderr or the server's own log; never credentials, PII, or internals that help an attacker.

## A local socket

The spec is silent here; these are the controls every local control surface surveyed uses.

- Directory `0700`, socket `0600`, both owned by the user; create the directory before `bind` and refuse to start if it exists with looser permissions or another owner.
- Check the peer's effective uid on every accepted connection (`getpeereid`, or `LOCAL_PEERCRED` / `SO_PEERCRED`) and refuse a foreign one — a second check on the claim the file mode makes.
- `sockaddr_un.sun_path` caps the path (104 bytes on macOS, 108 on Linux). Measure the longest real path, including an isolated test home, and fail loudly at bind rather than truncating.
- Unlink a stale socket only after `connect` to it fails; a live one means a second instance.
- State the honest floor: nothing at the transport stops another process running as the same user. What the design buys is that a caller can express a policy; the file mode does not enforce one.

## HTTP: authorization

Optional, and for HTTP only. When present:

- The server is an OAuth 2.1 resource server. It "**MUST** implement OAuth 2.0 Protected Resource Metadata (RFC9728)" with at least one `authorization_servers` entry, found through `resource_metadata` in the `WWW-Authenticate` of a 401 or at `/.well-known/oauth-protected-resource`.
- Clients send RFC 8707 `resource` on every authorization and token request; the server "**MUST** validate that access tokens were issued specifically for them as the intended audience". Invalid or expired → 401.
- No token passthrough: "The MCP server **MUST NOT** pass through the token it received from the MCP client." Calling an upstream API means being that API's OAuth client with its own token.
- Scopes: publish a minimal `scopes_supported`; challenge for more with `403` + `WWW-Authenticate: Bearer error="insufficient_scope", scope="…"`, all scopes the operation needs in one challenge. Never publish the whole catalog or a wildcard.
- Client registration order: pre-registered, then Client ID Metadata Documents, then Dynamic Client Registration (deprecated), then asking the person.
- stdio servers take credentials from the environment instead.
- Building an authorization server is out of scope; use an existing one (the SDKs ship resource-server helpers — `references/sdks.md`).

## The named attacks

| Attack | What happens | The mitigation that is yours |
| --- | --- | --- |
| DNS rebinding | a web page reaches your loopback HTTP port | validate `Origin` (403), bind 127.0.0.1, require auth — or use a socket |
| Confused deputy | a proxy with a static client id at a third-party AS lets a new client ride an old consent cookie | per-client consent registry checked before the upstream flow; exact redirect-URI match; single-use `state` set after consent |
| Token passthrough | the server forwards the client's token upstream | accept only tokens minted for you; mint your own upstream |
| State handle hijacking | a guessed or stolen handle is treated as identity | random, expiring handles bound to the verified principal |
| Local server compromise | a malicious startup command, or a local server reached by rebinding | stdio or a restricted socket; clients show the exact command before running it |
| SSRF | a client fetches attacker-supplied OAuth metadata URLs | clients: HTTPS only, block private ranges, validate each redirect hop |
| Scope inflation | a leaked broad token | minimal initial scopes, step-up challenges |

## What the spec does not cover

- Prompt injection and tool poisoning have no normative section. The client best-practices doc says "Tool results from one server are untrusted input to another … output truncation alone does not prevent exfiltration".
- A tool's own description is also model input: keep it factual, never instructive about other tools.
