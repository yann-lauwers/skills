# Search

Whether a ticket already covers a subject, in any state.

- Full text, every state → `grep -rin '<phrasing>' .scratch/`, once per phrasing, over every ticket file, closed ones included.
- No semantic search.
- Recent arrivals → `find .scratch -name '*.md' -mmin -60`.
