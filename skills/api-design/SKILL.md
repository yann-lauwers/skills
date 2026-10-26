---
name: api-design
description: "Settles an HTTP contract before a consumer exists — resource URLs, methods, status codes, error envelopes, pagination, filtering, versioning, rate-limit headers. Use on 'design this endpoint', 'cursor or offset', 'what status code for this', '401 or 403', 'how do we version the API', or a new route on a public or partner-facing surface. Not for the OpenAPI artifact or consumer drift — /contract-first ; not for Nest controllers — /nestjs-patterns ."
metadata:
  origin: ECC
  source: https://github.com/affaan-m/ECC/blob/main/skills/api-design/SKILL.md
---

# API Design

- A new or changed endpoint lands with its contract artifact updated in the same change.
- A route following a shape the codebase already ships → read the neighbouring handler; the choices below don't apply.
- Settle every choice below before the first consumer exists.
- An endpoint about to ship → check it against every reference below.

## Routing table

| Intent | Read |
| --- | --- |
| IF naming a path, deciding plurality, case, nesting, or whether an action may carry a verb | THEN `references/resource-urls.md` |
| IF picking a verb, choosing a status code, or an endpoint answers 200 for everything | THEN `references/methods-and-status.md` |
| IF shaping the success body, the error body, or deciding between a `data` envelope and a flat one | THEN `references/response-envelopes.md` |
| IF a list endpoint needs paging, or offset is being weighed against cursor | THEN `references/pagination.md` |
| IF adding filters, sorts, free-text search, or field selection to a collection | THEN `references/querying.md` |
| IF placing the credential, the ownership check, or the role check | THEN `references/auth.md` |
| IF adding limits, the `X-RateLimit-*` headers, or the 429 body | THEN `references/rate-limiting.md` |
| IF planning a version, deprecating one, or judging whether a change is breaking | THEN `references/versioning.md` |
| IF writing the handler — schema validation at the boundary, the 422 envelope, the 201 header | THEN `references/implementation.md` |
| IF the contract artifact itself is the subject — an OpenAPI spec, generated client types, provider/consumer drift | THEN /contract-first |
| IF the handler is a Nest controller — module layout, DTO validation, guards, the exception filter | THEN /nestjs-patterns |
| IF the request matches none of the above | THEN `references/methods-and-status.md`, say which row was closest |
