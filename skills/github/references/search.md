# Search

- Full text, every state → `gh search issues --repo <owner>/<name> "<phrasing>" --limit 10 --json number,title,state,url`; no `--state` returns open and closed alike.
- Search is lexical; no semantic query exists.
- `--match title|body|comments` restricts the field · none passed searches all.
- Recent arrivals → the same call with `--created ">=<ISO date of one hour ago>"`.
- The tree → a parent's children and a ticket's blockers per `references/issue-model.md § Issue relationships`.
