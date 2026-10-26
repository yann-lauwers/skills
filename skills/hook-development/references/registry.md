# The check registry

- The registry answers what an id means and whether it enforces; it is a maintained contract, never documentation.

## The contract

Put this line at the top of the file:

> **A check that is not listed here is a defect: add the row in the same commit that adds the check.**

And its mirror:

> **A check that is removed is retired in the same commit: the row goes, the `Retired id` clause arrives, and every surface that named it is cleared.**

## Row schema

| Column | Why |
|---|---|
| `id` | the stable literal written to the decision log |
| `component` | which script emits it |
| `event` | which lifecycle point |
| `fires when` | one sentence, in behavioural terms — what condition, on what observable |
| `class` | **DENY** blocks · **PERMIT** answers the permission question (allow / ask) · **ACT** changes state rather than voting · **WARN** advises · **ANNOT** records only |
| `rollout` | `ENFORCING`, `OBSERVE` while it records without acting, or `RECORDING` where the event has no enforce axis — the cell's first backticked token |

- A WARN or ANNOT check kept for its rows alone → its `fires when` cell ends `read by <script · reminder · skill>`.
- Every handler that answers `allow` or `ask` takes a PERMIT row: a branch that grants is a decision as much as a branch that blocks.
- Group the file by class, blocking tier first, and head the blocking tier with its entry requirement — *"every one of these has been driven red on a known-bad input"*.
- Record, once, how to read a decision row: the field order, and the vocabulary of verdict values in use.

## Minting an id

- One stable literal per check; never derive an id from message text.
- Pass the id from the call site, the only place that knows which check spoke.
- Never reuse a retired id: historical rows in the log carry it, and reuse merges two populations.
- Never let one id name two different checks; avoid an id that is a strict prefix of another.
- Never write a merged id like `A,B` for a combined decision; emit two rows.

## Retiring a check

- A check lives on these surfaces; retire it from every one, in the same change:

| Surface | Left behind, it does this |
|---|---|
| the source file | deleted outside git, a check takes its reasoning with it, and the next author rebuilds it |
| the wiring, at **every** level — each `settings.json` | the host launches a command that no longer exists — exit 127 on every matching call, and no line of any script runs to record it |
| the rollout table — the shipped default **and** any dated review entry | a review entry outliving its check arms a ping on a date nobody can act on; a default deleted while the check still exists silently drops it to the fallback, which is `enforce` |
| a repo's hook suite, where it keeps one | a suite that imports a missing module goes red for a reason unrelated to anything anyone changed |
| the registry row | the id keeps reconciling as live-but-silent, so a check that is gone reads as a check that never fires |

- A source in git is deleted, its history staying in git; a source outside git is archived — to `~/.agents/archive/hooks/` for a user-level check, the repo's own `.agents/archive/hooks/` for a project one.
- The row is replaced by a retirement clause in the same change — `**Retired id — \`<id>\`.**` followed by what the check did, why it lost, and where the capability went if it went anywhere. The reconciler reads the clause to classify the id's past rows as historical; a retirement without one turns every past row into a drift report.
- Name the successor — another check, a sweep over the corpus, a rule the session already loads — or record that there is none.
- The retirement is finished when the tooling says so: `hook-decisions --drift` reports the id under historical rather than unregistered, and `hook-decisions --modes` no longer lists it at all.

## What keeps it true

1. The row lands in the same change as the check — never a follow-up or a batch pass.
2. Every deciding handler holds a row, "deciding" read off the decision path, never the filename: before listing a handler as verdict-free, open it and follow the branch that exits or emits.
3. The reconciliation runs and someone reads it, in three directions — in code not in the registry, in the registry not in code, in the log not in the registry. Done when a run ends with the list at zero or with each survivor carrying a recorded reason.
4. A row's `detail` carries the *name* of the pattern or rule that matched, never the payload that matched it: the payload is the likeliest credential, and the count per name is a coverage report — a rule with zero rows is dead or wrong.

## The inventory must be an AST walk, not a grep

- Never inventory check ids by grep: a text search misses every check reporting through a variable.

Resolve each logging call's id argument back to the literals that can reach it:

```python
# For every call to the logging sink, resolve arg N:
#   - a string literal            → that id
#   - a NAME bound to a literal   → that id
#   - a NAME bound conditionally  → every literal that can reach it
#   - anything unresolved         → report as a DYNAMIC SINK, separately
```

- Report the dynamic sinks separately and loudly: their count is how much the inventory does not know.
- `scripts/check_inventory.py` implements this.

### The reconciliation's own readers are load-bearing, and they fail silently

- Every parser of the registry, the wiring or the call sites is evidence, and it fails by matching one spelling of a convention and returning a clean-looking subset.
- A parser over prose accepts every spelling the prose takes — `Retired id —` and `Retired ids —`, and the comma list after either.

1. One extractor per artifact kind, imported rather than reimplemented.
2. Run the parser against the shipped file, never only a sample: `parse(shipped_registry)` returning fewer than N live ids is a broken parser.
3. Break the parser on purpose by restoring the old pattern and run it against the shipped file; a count that does not move means the run never read that spelling.

### Three reconciliations, all mechanical

| Direction | Means |
|---|---|
| in code, **not** in the registry | undocumented check — the registry's own contract is broken |
| in the registry, **not** in code | a row pointing at a check that no longer exists — a map to nowhere |
| in code, **unreachable** from any entry point | a check that is not a check |

- Reachability belongs in the inventory.

### A convention-checker needs a denylist on the CLOSED side too — and its own break on purpose

- A meta-check asserting every check follows a convention is load-bearing evidence, and it fails by certifying the very file that violates the rule.

1. Invert the blacklist to an allowlist of accepted views: an unfamiliar subject fails toward being flagged.
2. Give a genuine exception an in-source annotation — `# raw-read: <reason>` on the line directly above it — never an allowlist entry.
3. Plant one real violation and confirm the meta-check reports it before believing its clean report; restore with plain `cp`.

## One engine, not many hooks

- Two hooks on the same event run in parallel and cannot see each other's output; where the host merges their output one can drop the other's → one emitter per event, never two coordinated scripts.

```python
denies, warns = [], []
for check in CHECKS:
    verdict = check(payload)
    if verdict is None:
        continue
    (denies if verdict.blocking else warns).append(verdict)
    log_decision(sid, event, verdict.id, verdict.decision, mode=verdict.mode)

if denies:
    emit_deny(denies[0])          # highest-priority deny short-circuits
elif warns:
    emit_context("  ".join("[%s] %s" % (w.id, w.text) for w in warns))
```

1. One verdict per event: a deny short-circuits; advisories merge into a single emission.
2. Every fire is logged before emission, the ones a deny pre-empts included; where each deny sits so it spends no one-shot flag → `robustness.md` § Ordering inside one engine.
3. The floor cost is paid once, not once per script.
4. One answer to "is this check enforcing?", never a dozen scripts' private conventions.

## Keeping project rules out of the mechanism

- Draw the boundary deliberately:

| Layer | Contains | Test |
|---|---|---|
| **Mechanism** | the evaluator loop, the emitter, the quoted-span scanner, command-position, coercion helpers, the state store, the mode resolver | would this work in another project with different config? |
| **Config** | paths, tool names, environment-variable names, directory markers, the check table itself | is this a noun this project happens to use? |
| **Rules** | trigger patterns, message text, prerequisite definitions | would this row say something different in another project? |

- Signs the boundary has leaked:
  - an identifier alphabet hardcoded in a generic helper — ship a shape, not a hand-maintained list;
  - an organisation name compiled into a regex inside the mechanism;
  - an adapter that resolves its target from its own install location, so it breaks in a second checkout;
  - a scope predicate hardcoding directory names where a marker-file walk would do.
- Scope by capability, not by location: "this repo declares X" is portable; "this path contains the string Y" is not.
