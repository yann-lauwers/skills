---
name: x
description: "Reads a public post on X from its URL or id, with no account. Started only by /x ."
disable-model-invocation: true
---

# X

## Reading on an account

- A repo reading X on its own account → a persisted session from a `agents:browser-pilot` `MODE: DISCOVERY` dispatch, never a key on this route; where that session lives → as the project's instructions state it.

## Routing

| Intent | Read |
| --- | --- |
| read a post or a tweet | § Reading a post |
| an `article` key · exit `3` on a protected account · what the official API costs | `references/where-the-free-route-stops.md` |

## The route

- An `x.com/<handle>/status/<id>` page fetched as a web page answers 200 with a JavaScript shell and no post text → that route failed, never the service; never reach for a login, a token or the paid API on it.
- The `token` `scripts/read-post.py` sends to its endpoint is derived, never a credential: the endpoint needs it non-empty and does not check its value.

## Reading a post

- Run `${CLAUDE_SKILL_DIR}/scripts/read-post.py '<url-or-id>'`, the argument quoted: a share-button URL carries `?s=…`, which zsh refuses unquoted.
- An `article` key → the post is long-form: `text` is only a `t.co` link and the substance is `article.title` and `article.preview_text`; never report the `t.co` link as what the post says.
- Report what the post says, naming the author and the date; add the engagement counts when the point rests on reach.
- A post worth keeping → capture its title, author, thesis, and engagement when reach is the point; never only its URL and a status line.

## Exit codes

- Every non-zero exit prints its cause on stderr.
- `3` on a protected account → `references/where-the-free-route-stops.md`.
- `4` → the post is gone; terminal.
- `5` → retry once.
- `5` naming an empty object → confirm on the control id `2070846650780664143` first (recorded 2026-08-24, bare id, full JSON); failing there too → the token derivation in `scripts/read-post.py` needs revisiting.
