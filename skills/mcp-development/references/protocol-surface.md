# The protocol surface a server implements

Normative wording is quoted from the 2026-07-28 revision (`https://modelcontextprotocol.io/specification/2026-07-28/...`, read 2026-09-22) unless a line says Legacy.

## Discovery and per-request metadata

- No handshake. Every request's `params._meta` carries `io.modelcontextprotocol/protocolVersion` (required), `io.modelcontextprotocol/clientCapabilities` (required; `{}` means none) and `io.modelcontextprotocol/clientInfo` (SHOULD). Missing required fields → `-32602`, HTTP 400.
- "Servers **MUST NOT** rely on prior requests over the same connection to establish context." State that spans calls is an explicit, server-minted handle passed as a tool argument.
- `server/discover` — "Servers **MUST** implement it." Returns `supportedVersions`, `capabilities`, optional `instructions`, cache fields; `serverInfo` in `_meta`.
- Unsupported version → `-32022` `UnsupportedProtocolVersion` with `data.supported[]` and `data.requested`; the client retries with one it shares.
- A request needing a client capability the request did not declare → `-32021` `MissingRequiredClientCapability`.
- Put `io.modelcontextprotocol/serverInfo` in every result's `_meta` (SHOULD). Neither `clientInfo` nor `serverInfo` may drive security decisions.
- Server capabilities: `tools { listChanged? }`, `resources { subscribe?, listChanged? }`, `prompts { listChanged? }`, `completions`, `extensions`, and deprecated `logging`.

## Tools

- `tools/list` is paginated and cacheable. "**MUST NOT** vary per-connection or as a side effect of other requests on the connection"; "**MAY** vary by the authorization presented"; "**SHOULD** return tools in a deterministic order".
- `Tool` = `name`, `title?`, `description?`, `icons?`, `inputSchema`, `outputSchema?`, `annotations?`, `_meta?`. `name` is the programmatic id; `title` is for people.
- Name: 1–128 characters, case-sensitive, only `A-Z a-z 0-9 _ - .`, unique within the server (SHOULD-level). Clients add their own prefix (`mcp__<server>__<tool>` in Claude Code), so leave room: `references/clients.md` § What a server can rely on.
- `inputSchema` — `type: "object"` at the root, any JSON Schema 2020-12 keyword beyond that; a tool with no arguments sends `{ "type": "object", "additionalProperties": false }`.
- `outputSchema` — any 2020-12 schema, arrays allowed at the root. "Servers **MUST** provide structured results that conform to this schema." Return `structuredContent` (any JSON value) and, for older clients, the same JSON serialised in a `text` block (SHOULD).
- Content blocks: `text`, `image`, `audio` (base64 + `mimeType`), `resource_link`, embedded `resource`; each may carry `annotations { audience, priority, lastModified }`.
- `tools/call` params: `name`, `arguments`, and on an MRTR retry `inputResponses` and `requestState`. Result: `CallToolResult` or `InputRequiredResult`.
- Annotations are hints. Verbatim: "all properties in `ToolAnnotations` are **hints** … Clients should never make tool use decisions based on `ToolAnnotations` received from untrusted servers."

  | Field | Meaning | Default |
  | --- | --- | --- |
  | `readOnlyHint` | does not modify its environment | `false` |
  | `destructiveHint` | may perform destructive updates (meaningful only when not read-only) | **`true`** |
  | `idempotentHint` | repeating with the same arguments has no further effect | `false` |
  | `openWorldHint` | reaches an open world of external entities | **`true`** |

  An unannotated tool is, by default, a destructive open-world writer. Annotations earn a tool lighter treatment; they never make one quietly dangerous.
- Stateful tools: a creation tool returns an opaque handle, later calls take it as an argument, authorization is checked on every call, the description states the handle's lifetime, and an expired handle is a tool execution error.

## Resources and prompts

- Resources are application-controlled context: `resources/list`, `resources/read`, `resources/templates/list` (RFC 6570). Not found → `-32602` (clients also accept legacy `-32002`); never an empty `contents`. Sanitise file paths against traversal.
- Prompts are user-controlled templates: `prompts/list`, `prompts/get`. Claude Code surfaces them as slash commands.

## Utilities

- Pagination — opaque `cursor`; page size is the server's; absent `nextCursor` means the end; an empty-string cursor is valid and is not the end; bad cursor → `-32602`.
- Progress — the request's `_meta.progressToken`; `notifications/progress { progressToken, progress, total?, message? }`, `progress` strictly increasing, stopping at completion.
- Cancellation — `notifications/cancelled { requestId }` on stdio; on Streamable HTTP closing the response stream is the signal and "the server **MUST** treat a client disconnect as cancellation". A cancelled handler stops and sends no result.
- Subscriptions — the client opens `subscriptions/listen` naming what it wants (`toolsListChanged`, `promptsListChanged`, `resourcesListChanged`, `resourceSubscriptions`); the server's first message is `notifications/subscriptions/acknowledged`; the server "**MUST NOT** send notification types the client has not explicitly requested". `listChanged` in the capability still gates `notifications/tools/list_changed`.
- Caching — results of `server/discover`, the `*/list` methods and `resources/read` carry `ttlMs` (0 = stale now) and `cacheScope` (`public` | `private`, never shared across authorization contexts). A list-changed notification invalidates the cache.
- Logging — deprecated; write to stderr (stdio) or OpenTelemetry. `ping` is gone.

## Asking the client for something

- Servers never send requests. A handler that needs input returns `InputRequiredResult { resultType: "input_required", inputRequests?, requestState? }`; the client retries the original call with a new id, `inputResponses` under the same keys, and `requestState` echoed byte for byte. Allowed on `tools/call`, `prompts/get`, `resources/read`.
- "The server **MUST** treat `requestState` as an attacker-controlled input" — sign or encrypt it and bind it to the principal and a TTL.
- Elicitation (not deprecated): form mode takes a flat object of primitives and "**MUST NOT**" ask for passwords, API keys, tokens or payment details; URL mode sends the person to a page (third-party OAuth, payment) and is flagged as liable to change.
- Sampling and roots are deprecated: call a model provider directly; take paths as tool arguments or config.

## Errors

- A tool's own failure — including invalid arguments, not-found, not-permitted, an upstream outage — is a `CallToolResult` with `isError: true`. Verbatim: "Any errors that originate from the tool SHOULD be reported inside the result object … Otherwise, the LLM would not be able to see that an error occurred and self-correct."
- A protocol error is for failing to find the tool, a malformed request, or the server itself: `-32601` method not found, `-32602` invalid params (including "Unknown tool: …"), `-32603` internal.
- MCP's own codes: `-32020` header mismatch, `-32021` missing client capability, `-32022` unsupported version. Application codes go outside `-32768..-32000`.

## Legacy lifecycle, for dual-era servers

2025-11-25 and earlier: the client sends `initialize { protocolVersion, capabilities, clientInfo }`; the server answers with the same version if it supports it, else another it supports; the client sends `notifications/initialized`; only then do other requests flow. Capabilities hold for the connection. A modern client probes with `server/discover` and falls back on a non-modern error; a modern-only server names its supported versions in whatever error it returns to `initialize`.
