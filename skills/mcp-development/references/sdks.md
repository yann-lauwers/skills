# SDKs

Read 2026-09-22 from each repository, npm and PyPI.

- An SDK's own supported-versions constant decides what it speaks, never its major number.
- Tiers are the spec's own (`docs/community/sdk-tiers.mdx`): Tier 1 passes 100% of the conformance suite and ships new spec features before a revision is released; Tier 3 has "No minimum" and "No timeline commitment".

## The matrix

| SDK | Tier | Version read | Speaks 2026-07-28 | Schema comes from |
| --- | --- | --- | --- | --- |
| TypeScript `@modelcontextprotocol/server` | 1 | 2.0.0 (v1 `@modelcontextprotocol/sdk` 1.30.0, fixes only) | yes, both eras from one server | Standard Schema (Zod v4, Valibot, ArkType) → derived JSON Schema; args validated before the handler; `structuredContent` validated against `outputSchema` |
| Python `mcp` | 1 | 2.2.0 (`FastMCP` renamed `MCPServer`) | yes, both eras | type hints and Pydantic → input schema; return annotation → output schema |
| Go `go-sdk` | 1 | v1.8.0 | yes, when started stateless | Go structs |
| Rust `rmcp` | 1 | 3.4.0 | yes, and 2025-11-25 | `rmcp-macros` |
| C# | 1 | 2.2.0 | yes, at a stateless endpoint | attributes |
| Java, Ruby | 2 | 2.0.1, 1.6.0 | unverified | — |
| **Swift `swift-sdk`** | **3** | **0.12.1 (2026-05-07); no merge since** | **no — `Version.supported` stops at `2025-11-25`** | **hand-written `Value` tree; no derivation, no argument or output validation** |
| Kotlin, PHP | 3 | 0.15.0, 0.8.1 | PHP yes | — |

Standalone FastMCP (`PrefectHQ/fastmcp`, 4.x) is a separate, non-official project.

## Swift, in detail

- Package: `swift-tools-version:6.1` (the README's "Swift 6.0+" is wrong); macOS 13+, iOS 16+; Linux glibc/musl; no Windows. The library target builds with `StrictConcurrency`.
- `Server`, `Client` and every transport are actors; `Transport` is `protocol Transport: Actor { connect(); disconnect(); send(Data); receive() -> AsyncThrowingStream<Data, Error> }`.
- Tools are one `ListTools` handler returning every `Tool` and one `CallTool` handler switching on `params.name` — `server.withMethodHandler(CallTool.self) { params in … }`. There is no per-tool registry; a registry is the server's to build.
- `CallTool.Result(content:structuredContent:isError:)` and a generic `init<Output: Codable>(structuredContent:)`. Nothing checks it against `outputSchema`.
- Transports: `StdioTransport(input:output:)` over any `FileDescriptor`; `HTTPClientTransport` (server-pushed SSE compiled out on Linux); `StatefulHTTPServerTransport` / `StatelessHTTPServerTransport` that take an `HTTPRequest` and return an `HTTPResponse` — no listener included, and the stateful one implements the sessions and resumability 2026-07-28 removed; `InMemoryTransport.createConnectedPair()` for tests; `NetworkTransport(connection:)` over an `NWConnection` (Apple only).
- No Unix-socket transport. Two routes, neither documented by the SDK: `NetworkTransport` on an `NWListener` accepting `NWEndpoint.unix(path:)`, or `StdioTransport` on an accepted socket's fd.
- `NetworkTransport` sends heartbeats by default — the bytes `F0 9F 92 93` plus a timestamp, with no newline — which any non-Swift peer reads as a corrupt message. Pass `heartbeatConfig: .disabled`.
- Cancellation cancels the handler's `Task`; handlers must check `Task.isCancelled`. Progress: read `params._meta?.progressToken`, then `server.notify(ProgressNotification.message(…))`.
- Doc errors to ignore: the README's tool example has an invalid `inputSchema` (no `"type": "object"`, a string where a schema belongs); `InMemoryTransport`'s doc comment calls `server.connect`, the method is `start(transport:)`.
- Deriving a schema from a Swift type has no official route. Non-official, pre-1.0: `ajevans99/swift-json-schema` (`@Schemable` macro, Draft 2020-12, validates, Bowtie-tested) and `ajevans99/swift-mcp-toolkit` (typed `MCPTool` structs on the official SDK). `Cocoanetics/SwiftMCP` is a separate implementation with its own `@MCPTool` macros. Owning a small macro or a build-time generator over the server's own command types is the alternative; `cookbook/design-a-server.md` § Step 3: Pick the SDK weighs them.

## TypeScript, in detail

- `registerTool(name, { title, description, inputSchema, outputSchema, annotations, icons, _meta }, cb)`. The raw-shape form (`{ a: z.string() }` without `z.object`) is deprecated; `tool()` is gone. `fromJsonSchema()` wraps a hand-written schema.
- A thrown handler error and a schema-rejected argument both resolve as `isError: true` results.
- `registerTool` returns a handle with `.update()`, `.disable()`, `.enable()`, `.remove()`; each emits `notifications/tools/list_changed`.
- Serving: `StdioServerTransport` (`@modelcontextprotocol/server/stdio`), `createMcpHandler(factory)` for Streamable HTTP with a legacy fallback; `@modelcontextprotocol/express` / `node` / `hono` / `fastify` adapters. The server is a resource server only: `requireBearerAuth`, `mcpAuthMetadataRouter`, `requireScopes`.
- Migration: `npx @modelcontextprotocol/codemod@beta v1-to-v2 .`

## Python, in detail

- `mcp = MCPServer("name")`; `@mcp.tool(name=, title=, description=, annotations=, structured_output=)`.
- `Annotated[..., Field(...)]` adds descriptions and constraints; `Literal` makes an enum; a scalar return is wrapped as `{"result": …}`.
- MRTR inputs arrive through `Resolve(fn)` dependency injection.
