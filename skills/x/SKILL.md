---
name: x
description: "Reads a public post on X from its URL or id, with no account."
disable-model-invocation: true
---

# X

- Run `${CLAUDE_SKILL_DIR}/scripts/read-post.py '<url-or-id>'`; a non-zero exit prints its cause on stderr.
- An `article` key → `text` is only a `t.co` link; the substance is `article.title` and `article.preview_text`, and the body past the preview is out of this route's reach.
- A `note_tweet` key → `text` is the first ~280 characters of a longer post; report it as cut short.
