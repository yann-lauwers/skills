# Issue model

- Each fact below says whether it is native here → `no`: it has no field, so the ticket body is the only place it can be recorded · `convention`: a line or a filename this layout defines carries it.

## Issue relationships

- Parent / sub-issue, native `no` → the child's position under `.scratch/<effort>/issues/`.
- Child order, native `convention` → the `NN` filename prefix, ascending.
- Blocking edge, native `no` → a `Blocked by: NN, NN` line near the top of the child file.
- Unblocked → every file its `Blocked by:` line lists is closed per § Issue state, a blocker closed as a duplicate or ruled out of scope included.
- Type / category, native `no` → the `Type:` line.

## Issue state

- Who filed it, native `no` → nothing records it; a pass needing the reporter's handle takes the tracker config's `maintainer`.
- No `maintainer` declared → an attended pass asks · an unattended pass stops and reports the tracker config as unwired.
- A pass taking the `maintainer` as the reporter → says so in its own report, the only record of the stand-in.
- Open / closed, native `convention` → the `Status:` line: closed when its value is in `settled_categories` or `settled_states`, open otherwise.
- Close as done, native `convention` → set `Status: resolved`, and record the answer under `## Answer` in the same file.
- Close as abandoned, native `convention` → set `Status: out-of-scope`.
- Close as duplicate, native `convention` → set `Status: duplicate`, with a `Duplicate of: NN` line beside it.
- Reopen, native `convention` → replace the resolution on the `Status:` line with a triage role.
- Assignee, native `no` → none: `Status: claimed` records that a session holds the ticket, not which one, so a claim cannot be attributed or safely reclaimed after its session dies.
- Body edit, native `convention` → replace the text between the convention lines and `## Answer`, `## Comments` or the end of the file, whichever comes first, the rest byte-identical · comment, native `convention` → append under `## Comments`, at the bottom of the file.
- Linked pull request, native `no` → none: a ticket file records no branch or pull request, so work in flight cannot be detected here.
