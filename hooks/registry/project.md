# PROJECT — enforced by a repo, recorded here so the shared log reconciles

Rows carry the id and where its source lives; predicate, rollout and tests belong to the repo.

| id | component | repo |
| --- | --- | --- |
| `backend-skill-unloaded` | `.claude/skills/architecting-backend/backend-skill-gate.mjs` | NexusGPT/nexus |
| `frontend-skill-unloaded` | `.claude/hooks/frontend-skill-gate.mjs` | NexusGPT/nexus |
| (none minted) | `.claude/skills/sentinel/sentinel-gate.mjs` | NexusGPT/nexus |

- No row here writes the shared log, so a zero there means uninstrumented: the two skill gates log to `<git-dir>/backend-skill-gate.jsonl` and `<git-dir>/frontend-skill-gate.jsonl` through `.claude/hooks/skill-load-gate.mjs`, and the sentinel gate writes a marker, `<git-dir>/sentinel-pass`.
- The wiring names the launcher `with-node.sh`, which decides nothing; the gates it `exec`s decide.
