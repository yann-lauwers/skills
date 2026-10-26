# Pagination

## Offset-based

```
GET /api/v1/users?page=2&per_page=20

# Implementation
SELECT * FROM users
ORDER BY created_at DESC
LIMIT 20 OFFSET 20;
```

- Offset → jumps to page N; scans every skipped row, and a concurrent insert shifts later pages, serving a row twice or skipping it.

## Cursor-based

```
GET /api/v1/users?cursor=eyJpZCI6MTIzfQ&limit=20

# Implementation
SELECT * FROM users
WHERE id > :cursor_id
ORDER BY id ASC
LIMIT 21;  -- fetch one extra to determine has_next
```

```json
{
  "data": [ ... ],
  "meta": {
    "has_next": true,
    "next_cursor": "eyJpZCI6MTQzfQ"
  }
}
```

- Cursor → constant cost at any position, stable under concurrent inserts; no jump to an arbitrary page.
- The cursor is opaque — the client never parses it, so its encoding changes without a version bump.

## Which one

| Use Case | Pagination Type |
|----------|----------------|
| Admin dashboards, small datasets (<10K) | Offset |
| Infinite scroll, feeds, large datasets | Cursor |
| Public APIs | Cursor (default) with offset (optional) |
| Search results | Offset (users expect page numbers) |

- Every list endpoint paginates from its first version.
