# skills

Yann Lauwers' Claude Code skills and plugins. Every machine installs from this repo with the same commands it uses for anyone else's.

```
skills/<name>/                   # one skill per folder, installed with npx skills
hooks/                           # the hook registry, and lib/: the one source of every module plugins share
plugins/agents/                  # browser-pilot and code-reviewer, dispatched as agents:<name>
plugins/bash-permissions/        # answers Bash permission prompts, refuses destructive commands
plugins/git-guards/              # refuses a commit carrying a tool's local config
plugins/house-style/             # flags an HTML page or stylesheet written without the house-style skill
plugins/auto-resume/             # resumes a turn an API error ended
plugins/yann/                    # the validation-report layout guard
plugins/continuous-compaction/   # Claude Code only: the compaction plugin; Codex loads no hooks from its `modules` hooks.json
plugins/domain-canon/            # refuses work in a directory until its GLOSSARY.md and ADRs are read; enabled per repo
plugins/codex-local-instructions/ # Codex only: injects a repo's AGENTS.local.md into each session
```

## A new machine

Naming both agents makes `npx skills` keep each skill in `~/.agents/skills`, where Codex reads it, and symlink it into `~/.claude/skills`. With `-a claude-code` alone it copies into `~/.claude/skills` only.

```sh
# the resolver every other skill and hook calls — first, and always with -g
npx skills add yann-lauwers/skills -g -a claude-code codex -y -s agents-config

# skills used everywhere
npx skills add yann-lauwers/skills -g -a claude-code codex -y -s analysing-recordings apple-calendar apple-mail cmux cp dev-team disk-cleanup garden-domain-docs git hook-development house-style keyless managing-harness plain proton simplify-comments slack superwhisper tailscale things voice watching worktrunk x

# other authors' packs, everywhere
npx skills add mattpocock/skills -g -a claude-code codex -y -s ask-matt grill-me grilling handoff retro teach to-questionnaire wait-what loop-me writing-for-agents
npx skills add humanlayer/skills -g -a claude-code codex -y -s show-me
npx skills add cloudflare/skills -g -a claude-code codex -y -s cloudflare wrangler

# coding skills, per code repo: run inside the repo, without -g
npx skills add mattpocock/skills -a claude-code codex -y -s code-review codebase-design diagnosing-bugs domain-modeling grill-with-docs implement implement-spec improve-codebase-architecture pr prototype research setup-matt-pocock-skills tdd to-spec to-tickets triage wayfinder wizard
npx skills add yann-lauwers/skills -a claude-code codex -y -s validating watch-pr

# plugins
claude plugin marketplace add yann-lauwers/skills   # then set "autoUpdate": true on it in ~/.claude/settings.json
claude plugin install agents@yannlauwers --scope user
claude plugin install bash-permissions@yannlauwers --scope user
claude plugin install git-guards@yannlauwers --scope user
claude plugin install house-style@yannlauwers --scope user
claude plugin install auto-resume@yannlauwers --scope user
claude plugin install yann@yannlauwers --scope user
claude plugin install continuous-compaction@yannlauwers --scope user

# Codex: one plugin list for every repo, so domain-canon gates each repo with canon
codex plugin marketplace add yann-lauwers/skills
codex plugin add agents@yannlauwers
codex plugin add bash-permissions@yannlauwers
codex plugin add git-guards@yannlauwers
codex plugin add house-style@yannlauwers
codex plugin add auto-resume@yannlauwers
codex plugin add yann@yannlauwers
codex plugin add domain-canon@yannlauwers
# Codex only: Claude Code reads AGENTS.local.md through CLAUDE.local.md
codex plugin add codex-local-instructions@yannlauwers
```

Then this host's two jobs:

```sh
# the commit size check, on every repo
git config --global hook.token-limit.event pre-commit
git config --global hook.token-limit.command "$HOME/.claude/skills/git/scripts/pre-commit-token-limit"

# the vault sync tick, every 5 minutes (macOS; Linux: the vault's scripts/README.md § Adding a machine)
mkdir -p ~/.local/state/vault && cp ~/Obsidian/yl/scripts/jobs/com.yann.vault-tick.plist ~/Library/LaunchAgents/ && launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.yann.vault-tick.plist
```

## Skills one repo uses

Run in the repo: `npx skills add yann-lauwers/skills -a claude-code -y -s <names>`. Your own repos commit `.claude/skills/<name>` and `skills-lock.json`. In team repos, both go into `.git/info/exclude`, so teammates get nothing.

| Repo | Skills | Copies |
| --- | --- | --- |
| `~/Code/nexus-project/nexus` | pr-cluster sentry supabase daytona infisical prisma redis react-patterns react-performance react-testing frontend-accessibility typescript-patterns vite-patterns nestjs-patterns prisma-patterns postgres-patterns redis-patterns docker-patterns | excluded |
| `~/Code/nexus-project/nexus-ui` | react-patterns react-performance react-testing frontend-accessibility typescript-patterns vite-patterns | excluded |
| `~/Code/nexus-project/nexus-landing` | linear react-patterns react-performance react-testing frontend-accessibility typescript-patterns nextjs-patterns | excluded |
| `~/Code/nexus-project/nutshell` | typescript-patterns swift-patterns sqlite-patterns | committed |
| `~/Code/nexus-project/nexus-desktop` | docker-patterns swift-patterns sqlite-patterns ffi-boundaries | excluded |
| `~/Code/keyless` | docker-patterns | excluded |
| `~/Code/les-gites-du-haras` | sentry webflow react-patterns react-performance react-testing frontend-accessibility typescript-patterns vite-patterns | committed |
| `~/Code/effigest-site` | react-patterns react-performance react-testing frontend-accessibility typescript-patterns vite-patterns nextjs-patterns | committed |
| `~/Code/personal-coach` | react-patterns react-performance react-testing frontend-accessibility typescript-patterns | committed |
| `~/Code/playground` | react-patterns react-performance react-testing frontend-accessibility typescript-patterns nextjs-patterns | committed |
| `~/Code/personal-ops` | billit enable-banking unifi local-markdown | committed |
| `~/Code/athlete-os` | garmin | committed |
| `~/Code/cswap-laxity` | docker-patterns | committed |
| `~/Code/immo` | sentry supabase trigger-dev nextjs-patterns | committed |
| `~/Code/mission-manager` | supabase | committed |

## Plugins one repo uses

`domain-canon` goes in every repo holding a `GLOSSARY.md` or `docs/adr/`. Run `claude plugin install domain-canon@yannlauwers --scope project` in the repo, add the `yannlauwers` marketplace under `extraKnownMarketplaces` in the `.claude/settings.json` it writes, and commit that file, team repos included.

| Repo | Plugins |
| --- | --- |
| `~/Code/nexus-project/nexus` | domain-canon |
| `~/Code/nexus-project/nexus-ui` | domain-canon |
| `~/Code/nexus-project/nutshell` | domain-canon |
| `~/Code/les-gites-du-haras` | domain-canon |
| `~/Code/personal-ops` | domain-canon |
| `~/Code/athlete-os` | domain-canon |
| `~/Code/lapepite/lapepite` | domain-canon |
| `~/Code/cswap-laxity` | domain-canon |

## Changing a skill or plugin

1. Edit it here, commit, push.
2. User level: `npx skills update -g -y`. Each repo using it: `npx skills update -p -y` in that repo, then commit in your own repos.
3. Plugins: background auto-update picks up the push (`"autoUpdate": true` on the `yannlauwers` marketplace in `~/.claude/settings.json`); to take it at once, `claude plugin marketplace update yannlauwers && claude plugin update <plugin>@yannlauwers`, then `/reload-plugins` in open sessions. Every plugin but `continuous-compaction` carries no `version`, so every pushed commit is a new version.
4. A module in `hooks/lib/` reaches a plugin as a real copy in that plugin's `hooks/lib/`, since both installers drop a symlink leaving the plugin: `hooks/sync-lib` refreshes every copy, `hooks/sync-lib --check` lists the stale ones.

A new skill is a folder `skills/<name>/` with its `SKILL.md`, plus its row above.
