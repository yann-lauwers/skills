# Feedback & roadmap

- Resolve the board first: the product the request names as a key of the config's `boards`, else `default_board`.
- Search the board for the request's terms, then synonyms; report each near-match with title and vote count.
- A post is public and attributed to the user → show the final title and body and get an explicit go-ahead before publishing.
- A post saying the same thing exists → vote and comment on it instead of filing, and say so. An adjacent post → the new post cites it by title and states the difference.
- After publishing, read the post back through the unauthenticated search; report its URL and status.
- Roadmap or progress question → `x1.roadmap.getPage` on the board, or a search for the request and that post's status (an untriaged request carries none, which is information).
- Expiry signal fires → re-mint the session per SKILL.md § The API, retry once, then escalate.
