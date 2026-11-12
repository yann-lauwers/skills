# Installing

## A new machine

```sh
# skills, user level: pick from each pack's prompt
npx skills add yann-lauwers/skills -g -a claude-code codex
npx skills add mattpocock/skills -g -a claude-code codex
npx skills add cloudflare/skills -g -a claude-code codex
npx skills add humanlayer/skills -g -a claude-code codex -y -s show-me

# plugins: every <plugin> in .claude-plugin/marketplace.json
claude plugin marketplace add yann-lauwers/skills   # then "autoUpdate": true on it in ~/.claude/settings.json
claude plugin install <plugin>@yannlauwers --scope user
codex plugin marketplace add yann-lauwers/skills
codex plugin add <plugin>@yannlauwers

# the commit size check, on every repo
git config --global hook.token-limit.event pre-commit
git config --global hook.token-limit.command "$HOME/.claude/skills/git/scripts/pre-commit-token-limit"

# in this repo: the shared hook modules' copies stay in step, and a changed plugin carries a new version
git -C ~/Code/skills config hook.hooks-lib-sync.event pre-commit
git -C ~/Code/skills config hook.hooks-lib-sync.command 'hooks/sync-lib --check'
git -C ~/Code/skills config hook.plugin-version.event pre-commit
git -C ~/Code/skills config hook.plugin-version.command 'hooks/bump-plugins --check'
```

- `-a claude-code codex` keeps each skill in `~/.agents/skills`, where Codex reads it, and symlinks it into `~/.claude/skills`; `-a claude-code` alone copies.
- `continuous-compaction` is Claude Code only, `codex-local-instructions` Codex only.

## A skill one repo uses

Add it inside the repo, without `-g`. Your own repos commit `.claude/skills/<name>` and `skills-lock.json`; a team repo lists both in `.git/info/exclude`.
