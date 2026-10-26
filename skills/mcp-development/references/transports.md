# Transports

Quotes are from the 2026-07-28 revision's transport pages (`https://modelcontextprotocol.io/specification/2026-07-28/basic/transports`, `…/stdio`, `…/streamable-http`), read 2026-09-22.

## What a transport is

- "A transport is a **binding**: it defines how messages are framed and delivered, how request metadata is carried, and how cancellation and termination are signaled. It does not define what the messages mean."
- Messages are JSON-RPC, in Unicode text. Servers never send requests; clients never send responses.
- Two transports are official — stdio for local, Streamable HTTP for remote — and the maintainers have said they will stay the only two (MCP blog, 2025-12-19, "transport future"). Anything else is a custom transport.

## stdio

- The client launches the server as a subprocess, writes to its stdin, reads its stdout.
- One JSON-RPC message per line; a message "**MUST NOT** contain embedded newlines".
- "The server **MUST NOT** write anything to its `stdout` that is not a valid MCP message." Logs go to stderr, which the client may show, forward or drop and "**SHOULD NOT** assume … indicates error conditions".
- No header layer: version and capabilities ride in each request's `_meta`.
- Cancellation: the client "**MUST** send a `notifications/cancelled`"; the server sends nothing further for that request.
- Shutdown: the client closes stdin, waits, then SIGTERM, then SIGKILL. "Servers **SHOULD** exit promptly when their standard input is closed or reads return end-of-file."
- Crash: the client restarts the server; in-flight requests are lost and retried.
- Auth: none in-protocol. "Implementations using an STDIO transport **SHOULD NOT** follow [the authorization] specification, and instead retrieve credentials from the environment."
- A stdio server is a child of its client: anything that must outlive one client, or already runs when the client arrives — a desktop app, a daemon, a shared cache — cannot be the stdio server itself.

## Streamable HTTP

- One endpoint path, POST only in 2026-07-28. Each client message is its own POST; `Accept` lists `application/json` and `text/event-stream`; a notification gets `202`.
- A response is either one JSON body or an SSE stream scoped to that request; "The final JSON-RPC _response_ **SHOULD** terminate the stream." Closing the stream is cancellation.
- Headers on every POST: `MCP-Protocol-Version` (must equal `_meta` protocol version, else `400` + `-32020`), `Mcp-Method`, and `Mcp-Name` on `tools/call` / `resources/read` / `prompts/get`. A tool parameter marked `x-mcp-header` is mirrored into `Mcp-Param-{Name}`; header and body disagreeing is `400` + `-32020`.
- No sessions, no `Mcp-Session-Id`, no GET stream, no `Last-Event-ID` resumability. A modern-only server answers legacy GET/DELETE with `405` and ignores those headers.
- Security, verbatim:
  > 1. Servers **MUST** validate the `Origin` header on all incoming connections to prevent DNS
  >    rebinding attacks. If the `Origin` header is present and invalid, servers **MUST** respond
  >    with HTTP 403 Forbidden.
  > 2. When running locally, servers **SHOULD** bind only to localhost (127.0.0.1) rather than all
  >    network interfaces (0.0.0.0).
  > 3. Servers **SHOULD** implement proper authentication for all connections.
- The deprecated 2024-11-05 HTTP+SSE transport: new implementations "**SHOULD NOT** adopt it".
- DNS rebinding — a web page the person visits resolves its own hostname to `127.0.0.1` and its JavaScript then talks to your local port as a same-origin peer. The `Origin` check is what refuses it; binding to loopback does not.

## Custom transports — a Unix-domain socket

- "Implementers who choose to support custom transports **MUST** preserve the JSON-RPC message format, the message patterns, and the per-request metadata model."
- "Custom transports that run over a reliable bidirectional byte stream (e.g., Unix domain sockets or TCP) **SHOULD** reuse the stdio framing rather than defining a new one" — newline-delimited JSON-RPC, one message per line. Only the subprocess parts (launch, stderr, shutdown by closing stdin, restart) need socket equivalents: connect, the app's own log, shutdown by closing the connection, reconnect.
- "Custom transports **SHOULD** document their connection establishment, message framing, and cancellation patterns."
- The security best-practices page recommends it for local servers that would otherwise use HTTP: "Use unix domain sockets or other Interprocess Communication (IPC) mechanisms with restricted access".
- The spec says nothing about the socket's permissions, peer credentials or path. Those are the server's own: `references/security.md` § A local socket.

## The stdio bridge

A small CLI the client launches over stdio (`yourapp mcp`) copies stdin lines to the socket and socket lines to stdout, since clients speak stdio or HTTP, never the server's socket.

- Modern requests (2026-07-28) carry their own `_meta`, so the bridge holds no protocol state and may open one connection per request.
- Legacy requests need one connection held for the whole `initialize`-then-requests exchange: the capabilities negotiated on it are the session. A server that ends the connection after each reply breaks a Legacy client at its second request.
- Cancellation: a stdio client cancels with `notifications/cancelled { requestId }`. With a connection per request, the bridge maps it to closing that request's connection, and the server treats a closed connection as cancellation of the request on it — the same rule Streamable HTTP uses. With one held connection, the bridge forwards the notification.
- Nothing listening: the bridge exits non-zero with one line on stderr naming the socket path.

## Choosing

| | stdio | Streamable HTTP | Unix socket + stdio bridge |
| --- | --- | --- | --- |
| Who starts the server | the client, per connection | the operator | the app, once |
| Caller identity | the parent process | a bearer token | the peer's uid, from the kernel |
| Reachable by a browser | no | yes — `Origin` check MUST | no |
| Auth in-protocol | none; env credentials | OAuth 2.1 resource server | none; filesystem permissions and peer credentials |
| Fits | a tool the client owns and can respawn | a remote or multi-user service | a long-lived local app or daemon |
