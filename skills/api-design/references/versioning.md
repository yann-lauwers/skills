# Versioning and deprecation

## URL path versioning — the default

```
/api/v1/users
/api/v2/users
```

- Path → explicit, routable, cacheable per version; every consumer edits a string to move.

## Header versioning

```
GET /api/users
Accept: application/vnd.myapp.v2+json
```

- Header → clean URLs; harder to test by hand, and a caller omitting the header gets the default version.

## Strategy

- Start at `/api/v1/`; cut a new version only for a breaking change.
- At most 2 active versions: current and previous.
- Deprecating a version:
  1. Announce it — 6 months' notice for a public API — with a `Deprecation` header (RFC 9745) on its responses.
  2. Add the `Sunset` header (RFC 8594), never earlier than the `Deprecation` date: `Sunset: Fri, 01 Jan 2027 00:00:00 GMT`.
  3. After the sunset date → `410 Gone`.
- Non-breaking, no new version: a field added to a response · a new optional query parameter · a new endpoint.
- Breaking, a new version: a field removed or renamed · a field's type changed · the URL structure changed · the authentication method changed.
- A field added to a response is non-breaking only where consumers ignore unknown fields → state that tolerant-reader expectation in the API's own docs before the first additive change ships.
