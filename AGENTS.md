# skills

- An install is a copy: a pushed skill reaches it through `npx skills update`.
- A changed plugin ships on a `version` bump: `hooks/bump-plugins`.
- A shared hook module is edited in `hooks/lib/`; `hooks/sync-lib` then overwrites each plugin's copy and bumps that plugin.
- Installing on a machine or into a repo → `docs/installing.md`.
