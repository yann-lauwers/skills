# Who builds MCP servers best, and what to copy

Each entry was read from the company's own writing or source on 2026-09-22 (commit named where source was read); these projects move weekly.

## The five, and the one thing each does best

| # | Who | Copy this | Where |
| --- | --- | --- | --- |
| 1 | **Cloudflare** (`cloudflare/mcp` @ 76b19f1) | **Server-side code mode**: 2,594 API endpoints behind `search` + `execute`, each taking a code string run in a V8 isolate with outbound fetch off — 1.17M tokens of schemas down to ~1.1k. Read-only is the default OAuth consent template. Every annotation carries a written justification. Already serves 2026-07-28, with a test asserting `server/discover` and no session id. Truncates at 6k tokens with "Use more specific queries". Maintains `workers-oauth-provider` (pre-registration → CIMD → DCR, RFC 9728/8414/9207, tokens stored by hash). | blog.cloudflare.com/code-mode-mcp |
| 2 | **GitHub** (`github/github-mcp-server` @ 85598ba) | **Measured tool selection**: offline evals scored as classification (precision, recall, F1) with confusion matrices to find tools the model mixes up, then consolidation to `<resource>_read` / `<resource>_write` with published savings (projects: 6 tools → 3, ~23k tokens). Read-only mode filters on `readOnlyHint` and an AST lint fails the build when a tool omits it. Tools the token cannot use are hidden. 127 schema snapshots (`toolsnaps`). Renamed tools keep resolving through `DeprecatedToolAliases`. | github.blog "Measuring what matters" |
| 3 | **Sentry** (`getsentry/sentry-mcp` @ e61c188) | **A written tool budget**: target 20 visible tools, never over 25, enforced by a test; the long tail behind `search_sentry_tools` + `execute_sentry_tool`. Responses are "product UX for agents" with a fixed Markdown contract; errors classed by who can fix them; writes off by default; all three hints required; LLM tool-prediction evals against the real descriptions. | `docs/contributing/*.md` |
| 4 | **Microsoft** — Azure MCP (`microsoft/mcp` @ 9e95fd7) | **Lifecycle discipline**: a tool rename is a checklisted breaking change; `outputSchema` rolled out behind an operator flag (`--structured-output-mode`); four exposure modes from one routing tool to one tool per command; `--read-only`; elicitation before touching secrets; every unsafe switch named `Dangerously…`. | `docs/tool-rename-checklist.md` |
| 5 | **Stripe** (`stripe/ai` @ db0f0c3; hosted server closed) | **Human approval for money**: refunds and payouts return a URL a person opens; approval gives the agent a token to retry with; it expires in 24 h. Four generic tools split by HTTP verb (`stripe_api_read` = GET, `stripe_api_write` = the rest); permissions set per environment (live vs sandbox) at OAuth consent. | docs.stripe.com/mcp |

## Runners-up, one idea each

- Atlassian — deferred tools found by `discover`, run through `executeRead`, `executeWrite` or `executeDestructive`, so a meta-tool surface still carries its risk tier in the name.
- Block — "Design top-down from workflows, not bottom-up from API endpoints"; their Linear server went from 30+ tools to two GraphQL tools, read and mutation; "Keep tools to single risk levels".
- Shopify — a mandatory learn-first call and server-side validators that check the code the model wrote.
- Notion — a Markdown dialect for agents instead of JSON blocks.
- Docker's gateway — secret scanning on arguments and results of every call.
- AWS — `--allow-write` off by default across its servers, and a server retired in favour of an agent skill with a migration guide.
- Playwright — accessibility snapshots instead of pixels, and a human-readable twin for every element argument so approval prompts show words.

## What the leaders agree on

1. Few tools, shaped by workflow; the long tail behind a search/discover tool and an execute tool. Every leader that did this measured and published the token saving.
2. The read/write split is a permission boundary — in the tool name, a read-only endpoint, the consent screen, or a server flag that beats every other setting.
3. Hide what the caller cannot use (token scopes, customer capabilities, admin groups).
4. A person confirms high-risk writes — an approval URL, elicitation, or a client-forced prompt.
5. Bounded responses that say how to narrow, never a silent cut.
6. Errors as `isError` results naming the next step.
7. Evals of tool choice and arguments, run on every description change.
8. Annotations set deliberately, increasingly with a written reason per hint.
9. Remote Streamable HTTP with OAuth 2.1, SSE only as a deprecated fallback.
10. A registry `server.json` under a verified namespace, and skills or plugins shipped beside the server — the server is no longer the whole integration.

## Standards beyond the spec

- OWASP MCP Top 10 (2025, beta): token mismanagement, scope creep, tool poisoning, supply chain, command injection, intent-flow subversion, weak authN/authZ, missing audit, shadow servers, context over-sharing — `https://owasp.org/www-project-mcp-top-10/`.
- CoSAI (OASIS) MCP security taxonomy, 2026-01.
- OpenAI's app submission rules: all three hints with a justification each, verb names, no internal identifiers in responses.
