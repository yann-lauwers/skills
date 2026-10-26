# Auditing an existing layer

The entry procedure for improving a hook layer that already exists: the inventory pass that holds before any coverage claim of the loop in `hardening-cycle.md`, which it feeds.

- Start at the registry, never at a signal: build the inventory before believing any claim about coverage — `registry.md`.

## The order

1. Enumerate every check id from source by AST, never by grep — `registry.md` § The inventory must be an AST walk, not a grep; `scripts/check_inventory.py`. Done when the inventory reconciles against the registry or each survivor is listed.
2. Measure the false-positive rate — `test-agents.md` T-A5 carries the two-corpus contract and the labelling rule. Done when both corpora are scored.
3. Read the decision log. A blocking check with no rows is unmeasured, never quiet — the log alone cannot tell the two apart. Done when every blocking check has rows or is recorded as unmeasured.
4. Prove each blocking check with no host row live — `testing.md` § The proof and § Break on purpose. Done when each one's row moved under a deliberate break, or the check is recorded as dead.
