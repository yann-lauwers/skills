# Search

Whether a ticket already covers a subject, in any state.

- Every state → `glab issue list --all --search "<phrasing>" --per-page <n> -O json`, once per phrasing; without `--all` the listing is open-only; `--per-page` above the set's size, or its oldest members never appear.
- Tickets only → add `--issue-type issue`; a bare listing mixes in tasks.
- `--search` reads `--in`, default `title,description` → comments are never searched; a thread's text comes only from `glab issue view <n> --comments`.
- JSON → `issue list` takes `-O json` (its `-F` is `--output-format`: `details|ids|urls`) · `issue view`, `mr list`, `mr view`, `mr note list`, `label list` take `-F json` · on `glab api`, `-F` is `--field`; a verb not just read → the long flag.
- Search is lexical.
- Recent arrivals → the listing's `created_at` within the last hour.
- The tree → children and blockers per `references/issue-model.md § Issue relationships`.
