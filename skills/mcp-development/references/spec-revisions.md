# Spec revisions, eras, and what "v2" means

Read from the spec repository (`modelcontextprotocol/modelcontextprotocol`, `main` at `24efd6e`, 2026-09-18) and the live site on 2026-09-22; the revision list moves, and § Confirm the current revision is the check that keeps this file current.

## Confirm the current revision

Fetch, never recall.

1. `https://modelcontextprotocol.io/specification/latest` — the page's schema link names the revision (`schema/<rev>/schema.ts`).
2. `LATEST_PROTOCOL_VERSION` in `https://raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/main/schema/<rev>/schema.ts`.
3. `https://modelcontextprotocol.io/specification/draft/changelog` — what is coming.

Done when the revision about to be cited matches both 1 and 2, read this session.

## The revisions

The protocol version is a date string. The only `2.0` in the protocol is JSON-RPC 2.0.

| Revision | What it changed that a server author feels |
| --- | --- |
| 2024-11-05 | first revision; HTTP+SSE transport |
| 2025-03-26 | Streamable HTTP replaces HTTP+SSE; OAuth 2.1; **tool annotations**; batching (later removed) |
| 2025-06-18 | `outputSchema` + `structuredContent`; elicitation; `resource_link`; servers are OAuth resource servers (RFC 9728, RFC 8707); `title` separate from `name`; `MCP-Protocol-Version` header |
| 2025-11-25 | tool-name guidance (1–128 chars, `[A-Za-z0-9_.-]`); icons; URL-mode elicitation; input-validation failures become `isError` results; JSON Schema 2020-12 default; experimental tasks; client ID metadata documents |
| **2026-07-28** | **breaking, "Modern" era.** No `initialize` handshake and no sessions — every request carries `_meta` protocol version and client capabilities; `server/discover` is mandatory; server-to-client requests replaced by Multi Round-Trip Requests (`InputRequiredResult`); `resultType` on every result; `subscriptions/listen` replaces the GET stream and `resources/subscribe`; `ttlMs`/`cacheScope` required on list and read results; `ping` and `logging/setLevel` removed; tasks moved to the `io.modelcontextprotocol/tasks` extension; roots, sampling and logging deprecated (12-month window); new error codes `-32020`/`-32021`/`-32022` |

Each revision's changelog is `https://modelcontextprotocol.io/specification/<rev>/changelog`.

## Eras

The spec's own vocabulary (`/specification/2026-07-28/basic/versioning`):

- Legacy — 2025-11-25 and earlier. Stateful: `initialize` → `notifications/initialized`, then requests; capabilities negotiated once per connection.
- Modern — 2026-07-28 and later. Stateless per request. A server "MUST NOT rely on prior requests over the same connection to establish context".
- Dual-era — a server or client that speaks both. A legacy client against a modern-only server fails; the compatibility matrix is on the versioning page.

Picking an era is a design decision, not a default: `cookbook/design-a-server.md` § Step 2: Pick the era.

## "MCP version 2"

No spec revision is called version 2. The phrase names the v2 SDK majors that shipped for the 2026-07-28 revision:

| SDK | v2 shape |
| --- | --- |
| TypeScript | `@modelcontextprotocol/server` / `@modelcontextprotocol/client` replace the monolithic `@modelcontextprotocol/sdk` (still 1.x, maintained); ESM-only, Standard Schema (Zod v4, Valibot, ArkType); codemod `npx @modelcontextprotocol/codemod@beta v1-to-v2 .` |
| Python | `mcp` 2.x; `FastMCP` renamed `MCPServer` |
| C# | 2.x |

Source: the MCP blog post "SDK betas for 2026-07-28" (repo `blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md`) and `npm view` / PyPI on 2026-09-22.

Asked → "v2" is the new SDK line, which implements protocol revision 2026-07-28; moving to it is a breaking change on your own schedule.

## Which SDK speaks which revision

Never its major version number — `references/sdks.md` says what each SDK actually speaks and where it keeps that answer.
