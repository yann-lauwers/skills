# Delete the ADRs

1. Prove nothing reads an ADR's content: `git grep -n -E 'docs/adr/[0-9]{4}' -- ':/' ':(top,exclude,glob)**/docs/adr/**'`. Done when every hit is handled per `cookbook/verify.md` § Citations.
2. `git rm` the round's ADRs, then the command regenerating the ADR index. Done when the index lists only the ADRs left.
3. An ADR left behind that cites a folded one → restate the cited decision in its own words. Done when no ADR on the tree names a folded one.
4. ADR tooling (`SKILL.md`) exits 0. A tool that fails on fewer ADRs is fixed with a self-test case per rule, each proven red by breaking the fix. Done when each exits 0.
5. Sweep pointers to one particular ADR: in numbers, the search in `cookbook/verify.md` § Citations; in prose, `git grep -n -i -E '(decision record|the record|the ADR|an ADR) (that|which)' -- ':/' ':(top,exclude,glob)**/docs/adr/**' ':(top,exclude).claude/hooks'`. Each hit pointing a reader at one ADR states the decision in words or names its carrier; a line about ADRs in general stays. Done when no hit points at a folded ADR.
6. A fact true only in this repo goes in its `docs/agents/domain.md`, in the section after Matt's seed. Done when no such fact sits elsewhere.
