---
name: garden-domain-docs
description: "Walks a repo's ADRs and glossaries against today's code and applies only what the user picks. Started only by /garden-domain-docs , narrowed by `adr` or `glossary`, then a folder, a file or a note."
argument-hint: "[adr|glossary] [folder or file] [context]"
disable-model-invocation: true
---

# Garden Domain Docs

/domain-modeling owns the rules: its three-part ADR bar, its ADR and glossary formats, its file structure. Read it for those; every verdict cites one. Its write-inline habit does not apply here: nothing changes before the user picks.

## 1. Scope

- First word `adr` or `glossary` → walk that kind only; neither → both. A kind the repo lacks is skipped silently.
- The rest of the message — a folder, a file, a note — narrows the walk and says what to look for.
- Find every `GLOSSARY.md` and `docs/adr/*.md` in this repo, under the folder passed when there is one, so the ones the map misses surface.

## 2. Classify

Read each ADR whole and test its claims against the code it names, as it stands today. Each takes one verdict, tested in this order:

- Retire, subject gone — what it decided about no longer exists in the code, or the decision changes nothing there today. Delete it; nothing to carry.
- Retire, fails the bar — name the criterion. What a reader still needs moves to the code that carries it; a rule a check could enforce becomes the check.
- Supersede — a later decision replaced it and the road between them is worth knowing; mark it per the ADR format, its text left as written.
- Merge — two ADRs hold one decision; the survivor carries both, the other's lessons in its _Considered Options_.
- Move — it sits outside the folder the file structure gives it; name that folder.
- Update — the decision holds, a clause doesn't; each stale clause gets its replacement, checked at `path:line`.
- Keep — it passes the bar and every clause holds.

Each glossary term takes one: keep · update · cut — it fails the glossary rules, or nothing in the code or the ADRs uses it · move — to its context's glossary.

Multi-context → each map entry takes one: keep · update · cut — the context is gone · add — a glossary in the repo the map misses.

## 3. Present

- One table per folder — number · ADR or term · verdict · one-line reason · change.
- Numbers run once across every table and never restart, so a number names one change.
- Calls only the user can make → one round of questions per /grilling ; then wait.

## 4. Apply what the user picked

Done when every path an ADR names exists, every ADR number cited in the repo names the ADR it meant, and the map lists exactly the glossaries in the repo.
