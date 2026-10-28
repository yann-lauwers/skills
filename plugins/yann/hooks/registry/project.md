# PROJECT — enforced by a repo, recorded here so the shared log reconciles

Rows carry the id and where its source lives; predicate, rollout and tests belong to the repo.

| id | component | repo |
| --- | --- | --- |
| `backend-skill-unloaded` | `.claude/skills/architecting-backend/backend-skill-gate.mjs` | NexusGPT/nexus |
| `frontend-skill-unloaded` | `.claude/hooks/frontend-skill-gate.mjs` | NexusGPT/nexus |
| (none minted) | `.claude/skills/sentinel/sentinel-gate.mjs` | NexusGPT/nexus |
| `canon-read-first` | `.claude/hooks/domain-canon.py` | NexusGPT/nexus, NexusGPT/nutshell, yann-lauwers/athlete-os, yann-lauwers/lapepite, yann-lauwers/les-gites-du-haras, yann-lauwers/personal-ops |
| `canon-unplaced-read` | `.claude/hooks/domain-canon.py` | NexusGPT/nexus, NexusGPT/nutshell, yann-lauwers/athlete-os, yann-lauwers/lapepite, yann-lauwers/les-gites-du-haras, yann-lauwers/personal-ops |
| `canon-read-gate` | `.claude/hooks/domain-canon.py` | NexusGPT/nexus, NexusGPT/nutshell, yann-lauwers/athlete-os, yann-lauwers/lapepite, yann-lauwers/les-gites-du-haras, yann-lauwers/personal-ops |
| `canon-read-gate-shell` | `.claude/hooks/domain-canon.py` | NexusGPT/nexus, NexusGPT/nutshell, yann-lauwers/athlete-os, yann-lauwers/lapepite, yann-lauwers/les-gites-du-haras, yann-lauwers/personal-ops |
| `canon-read-reminder` | `.claude/hooks/domain-canon.py` | NexusGPT/nexus, NexusGPT/nutshell, yann-lauwers/athlete-os, yann-lauwers/lapepite, yann-lauwers/les-gites-du-haras, yann-lauwers/personal-ops |
| `canon-read-credit` | `.claude/hooks/domain-canon.py` | NexusGPT/nexus, NexusGPT/nutshell, yann-lauwers/athlete-os, yann-lauwers/lapepite, yann-lauwers/les-gites-du-haras, yann-lauwers/personal-ops |
| `canon-map-injection` | `.claude/hooks/domain-canon.py` | NexusGPT/nexus, NexusGPT/nutshell, yann-lauwers/athlete-os, yann-lauwers/lapepite, yann-lauwers/les-gites-du-haras, yann-lauwers/personal-ops |

- The domain canon checks write the shared log through each repo's own copy of `lib/hook_decisions.py`, and keep their reading ledger under `~/.claude/state/domain-canon/`, which `precompact-capture` reads.
- No other row writes the shared log, so a zero there means uninstrumented: the two skill gates log to `<git-dir>/backend-skill-gate.jsonl` and `<git-dir>/frontend-skill-gate.jsonl` through `.claude/hooks/skill-load-gate.mjs`, and the sentinel gate writes a marker, `<git-dir>/sentinel-pass`.
- The wiring names the launcher `with-node.sh`, which decides nothing; the gates it `exec`s decide.
