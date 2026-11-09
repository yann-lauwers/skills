# run.md

Read by the opener relaying it and by the next run, which takes its `owner` rows.

```markdown
# <slice> — run <YYYY-MM-DD>_<n>

- Commit: <hash>
- Verdict: <BLOCKED|FAIL|PASS|INCOMPLETE> — <what decides it>

| C | criterion, verbatim | provenance | source | plan | expected | verdict | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |

## FAIL
<per FAIL: steps, expected, observed>

## Defects · Asks · Blockers
<each with who must act>
```

- `provenance` → `ticket` · `owner` · `self`; `plan` → `prove` · `skip` · `ask` · `review`; `verdict` → PASS · FAIL · NOT EXERCISED.
- A section with no entries is left out.
