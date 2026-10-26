# skills

Yann Lauwers' Claude Code skills and plugins. Every machine installs from this repo with the same commands it uses for anyone else's.

```
skills/<name>/                   # one skill per folder, installed with npx skills
plugins/yann/                    # agents and hooks, installed as a plugin
plugins/continuous-compaction/   # the compaction plugin
repo-hooks/domain-canon/         # source of the domain-canon hook committed in nexus and nutshell; installs nothing
```

## A new machine

```sh
# the resolver every other skill and hook calls — first, and always with -g
npx skills add yann-lauwers/skills -g -a claude-code -y -s agents-config

# skills used everywhere
npx skills add yann-lauwers/skills -g -a claude-code -y -s analysing-recordings api-design apple-calendar apple-mail browser claude-artifacts claude-login cli-patterns close-session cloudflare-ops cmux contract-first cp dev-team disk-cleanup folding-adrs git github gitlab handoff-yann hetzner hook-development house-style keyless local-markdown loop-me managing-harness mcp-development obsidian persona-forging plain pr-cluster proton pull-request regex-vs-llm-structured-text relogin resurrect simplify-comments slack superwhisper tailscale things userjot validating voice watch-pr watching worktrunk x

# other authors' packs, everywhere
npx skills add mattpocock/skills -g -a claude-code -y -s ask-matt code-review codebase-design diagnosing-bugs domain-modeling grill-me grill-with-docs grilling handoff implement implement-spec improve-codebase-architecture pr prototype research retro setup-matt-pocock-skills tdd teach to-questionnaire to-spec to-tickets triage wait-what wayfinder writing-for-agents
npx skills add pbakaus/impeccable -g -a claude-code -y -s impeccable
npx skills add humanlayer/skills -g -a claude-code -y -s show-me
npx skills add cloudflare/skills -g -a claude-code -y -s cloudflare wrangler
npx skills add emilkowalski/skill -g -a claude-code -y -s animate apple-design emil-design-eng find-animation-opportunities improve-animations review-animations
npx skills add Leonxlnx/taste-skill -g -a claude-code -y -s design-taste-frontend
npx skills add nextlevelbuilder/ui-ux-pro-max-skill -g -a claude-code -y -s ui-ux-pro-max
npx skills add vojtaholik/good-css -g -a claude-code -y -s good-css

# plugins
claude plugin marketplace add yann-lauwers/skills   # then set "autoUpdate": true on it in ~/.claude/settings.json
claude plugin install yann@yannlauwers --scope user
claude plugin install continuous-compaction@yannlauwers --scope user
```

Then this host's two jobs:

```sh
# the commit size check, on every repo
git config --global hook.token-limit.event pre-commit
git config --global hook.token-limit.command "$HOME/.claude/skills/git/scripts/pre-commit-token-limit"

# the vault sync tick, every 5 minutes (macOS; Linux: obsidian's references/operate.md step 5)
mkdir -p ~/.local/state/vault && cp ~/.claude/skills/obsidian/jobs/com.yann.vault-tick.plist ~/Library/LaunchAgents/ && launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.yann.vault-tick.plist
```

## Skills one repo uses

Run in the repo: `npx skills add yann-lauwers/skills -a claude-code -y -s <names>`. Your own repos commit `.claude/skills/<name>` and `skills-lock.json`. In team repos, both go into `.git/info/exclude`, so teammates get nothing.

| Repo | Skills | Copies |
| --- | --- | --- |
| `~/Code/nexus-project/nexus` | linear sentry supabase daytona infisical prisma redis react-patterns react-performance react-testing frontend-accessibility typescript-patterns vite-patterns nestjs-patterns prisma-patterns postgres-patterns database-migrations redis-patterns docker-patterns | excluded |
| `~/Code/nexus-project/nexus-ui` | linear react-patterns react-performance react-testing frontend-accessibility typescript-patterns vite-patterns | excluded |
| `~/Code/nexus-project/nexus-landing` | linear react-patterns react-performance react-testing frontend-accessibility typescript-patterns nextjs-patterns | excluded |
| `~/Code/nexus-project/nutshell` | linear typescript-patterns swift-patterns sqlite-patterns ffi-boundaries native-app-verification | excluded |
| `~/Code/nexus-project/nexus-desktop` | linear docker-patterns swift-patterns sqlite-patterns ffi-boundaries native-app-verification | excluded |
| `~/Code/keyless` | docker-patterns | excluded |
| `~/Code/codeine` | linear | excluded |
| `~/Code/les-gites-du-haras` | sentry webflow react-patterns react-performance react-testing frontend-accessibility typescript-patterns vite-patterns | committed |
| `~/Code/effigest-site` | react-patterns react-performance react-testing frontend-accessibility typescript-patterns vite-patterns nextjs-patterns | committed |
| `~/Code/personal-coach` | react-patterns react-performance react-testing frontend-accessibility typescript-patterns | committed |
| `~/Code/playground` | react-patterns react-performance react-testing frontend-accessibility typescript-patterns nextjs-patterns | committed |
| `~/Code/personal-ops` | billit enable-banking unifi | committed |
| `~/Code/athlete-os` | garmin | committed |
| `~/Code/cswap-laxity` | docker-patterns | committed |
| `~/Code/immo` | sentry supabase trigger-dev nextjs-patterns | committed |
| `~/Code/mission-manager` | supabase | committed |

## Changing a skill or plugin

1. Edit it here, commit, push.
2. User level: `npx skills update -g -y`. Each repo using it: `npx skills update -p -y` in that repo, then commit in your own repos.
3. Plugins: background auto-update picks up the push (`"autoUpdate": true` on the `yannlauwers` marketplace in `~/.claude/settings.json`); to take it at once, `claude plugin marketplace update yannlauwers && claude plugin update yann@yannlauwers`, then `/reload-plugins` in open sessions. The `yann` plugin carries no `version`, so every pushed commit is a new version.

A new skill is a folder `skills/<name>/` with its `SKILL.md`, plus its row above.
