# Rate limiting

## Headers

```
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000

# When exceeded
HTTP/1.1 429 Too Many Requests
Retry-After: 60
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Try again in 60 seconds."
  }
}
```

- `X-RateLimit-*` — the de facto form, as GitHub sends it, `Reset` in UTC epoch seconds; the IETF's `RateLimit` and `RateLimit-Policy` fields are still a draft (draft-ietf-httpapi-ratelimit-headers-11, 2026-05-23).

## Tiers

| Tier | Limit | Window | Use Case |
|------|-------|--------|----------|
| Anonymous | 30/min | Per IP | Public endpoints |
| Authenticated | 100/min | Per user | Standard API access |
| Premium | 1000/min | Per API key | Paid API plans |
| Internal | 10000/min | Per service | Service-to-service |

- Every endpoint ships with a limit; a public surface starts from this table.

## Behavior

- Send the three `X-RateLimit-*` headers on every response, the 429 included.
- Every 429 carries `Retry-After`, though RFC 6585 §4 leaves it optional.
