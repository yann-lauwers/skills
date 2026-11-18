# ledger.md

The harness's account of the slice, rewritten whole by each run and read first by the next.

```markdown
# <slice> — ledger

- Last run: <YYYY-MM-DD>_<n> at <hash> → <verdict>
- Open: <each FAIL, defect, ask and blocker, one line each>

| C | last verdict | at | driver |
| --- | --- | --- | --- |

## Tools
<per tool in the harness: its file — what it reaches; how to call it>

## Gotchas
<what a scenario needs that no tool or file confesses>
```

- `C` and `last verdict` are the newest `run.md`'s; `at` is the commit that verdict was taken on; `driver` is the harness path that proved it, `—` naming why there is none.
- A tool or driver no row names any more → deleted from the harness.
