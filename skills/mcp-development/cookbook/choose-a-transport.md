# Choose a transport

How clients reach the server, and the access control that comes with it; Step 1 decides most cases, `references/transports.md` carries the wire detail and `references/security.md` the controls.

## Step 1: Who starts the server

1. The client can launch the server as a child and throw it away afterwards — a CLI tool, a wrapper around an API → stdio is available.
2. The server already runs when the client arrives, or must outlive it — a desktop app, a daemon, a shared cache → stdio is structurally out as the server's own transport (`references/transports.md` § stdio); one GUI app cannot be spawned per connection.
3. Callers are remote, or many people share one instance → Streamable HTTP.

Done when one of the three is named, with the fact that decided it.

## Step 2: Pick the transport

1. Child process → stdio.
2. Long-lived local process → a Unix-domain socket the process owns, plus a stdio bridge; the socket reuses the stdio framing — newline-delimited JSON-RPC — as the spec asks of byte-stream custom transports.
3. Loopback HTTP for a local process → only where a socket is impossible: a client that speaks HTTP only and cannot launch a bridge.
4. Remote → Streamable HTTP, POST only under 2026-07-28, with authorization (`references/security.md` § HTTP: authorization). Never the deprecated HTTP+SSE transport.

Done when one transport is chosen and each rejected one has its reason in a line.

## Step 3: Apply its access control

1. stdio: credentials from the environment; nothing but protocol messages on stdout — every log line to stderr.
2. Unix socket: every control in the local-socket checklist — directory and socket permissions, the peer-uid check on every accept, the path-length check at bind, and unlinking a stale socket only after a failed connect. Details in `references/security.md` § A local socket.
3. The bridge: the connection and cancellation rules in `references/transports.md` § The stdio bridge — per-request connections under Modern, one held connection for a Legacy client, and a cancellation mapped to closing that request's connection.
4. HTTP: validate `Origin` and answer a bad one with 403; bind 127.0.0.1 when local; authorization as a resource server. On a request whose `_meta` names 2026-07-28, require `MCP-Protocol-Version` and `Mcp-Method` on every POST and `Mcp-Name` on `tools/call`, `resources/read` and `prompts/get` only, and reject a header that disagrees with the body (`400`, `-32020`). A dual-era server routes every other request — `initialize` and the calls after it — to its Legacy handler without those checks.

Done when every control in the chosen row is in the design, and each has a test named in `cookbook/test-a-server.md` § Step 3.

## Step 4: Write it down

1. Write the custom transport's connection establishment, message framing and cancellation patterns — a spec SHOULD (`references/transports.md` § Custom transports — a Unix-domain socket) — plus the socket path rule and what a client does when nothing is listening.
2. In a repo that keeps decision records → the transport choice is one, per `cookbook/design-a-server.md` § Step 7: Record the design.

Done when the three patterns are written where the next implementer reads them.
