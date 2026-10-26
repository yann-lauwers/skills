# Vendored

- A file in a vendored pack — registered here, listed in `~/.agents/.skill-lock.json`, or in a directory whose own `VENDORED.md` declares it vendored → never rewrite it to SKILL.md § How we write, by hand or in an optimize sweep.
- Text authored elsewhere, this copy replaceable — a git checkout under the pack's own directory, an update script, a submodule, a scheduled job, an app that rewrites it, or a named upstream re-downloaded by hand → register its pack, unless the lock lists it or its own repo's `VENDORED.md` declares it.
- A block authored elsewhere inside a file this setup owns, between its own begin and end markers → register it under `## Blocks`; edit the file around it, never inside it.
- A provenance marker alone — an `origin` key, a `source:` URL, an upstream name in prose — registers nothing.
- Every skill `~/.agents/.skill-lock.json` lists → vendored.
- Every agent `~/Code/skills/plugins/yann/packs.toml` lists → vendored, and registered under `## Agents` too, which the sweep's scanner reads; refreshing it → `references/agents.md` § The agents layer.
- None present → nothing is vendored; everything is judged as authored here.
- A `## Skills` entry with a `/` → that path inside the skill, the rest of the skill authored here.
- `## Skills`, `## Agents`, `## Blocks`, each row's first cell and a Blocks row's File cell are parsed by the sweep's scanner → keep them verbatim.

## Skills

| Entry | Upstream |
| --- | --- |
| `impeccable` | the Impeccable frontend-critique pack |
| `synced` | account-synced skill copies Claude Code writes, one `.bucket-<id>` marker per bucket |
| `xcode-integration` | Apple's agent plugin shipped with Xcode, copied by /swift-patterns , `scripts/sync-apple-skills.sh` |

## Patches

- A local patch to a vendored file → one row here; Entry is the path under `~/.claude/skills/`, Check is `absent` or `present` and a backticked regex, read per line after the pack updates: a row whose file no longer holds its patch → reapply it.

| Entry | Patch | Check |
| --- | --- | --- |
| `triage/SKILL.md` | the `disable-model-invocation: true` frontmatter line removed, so a session can start it | absent `^disable-model-invocation:` |
| `ui-ux-pro-max/SKILL.md` | every `search.py` command reads `${CLAUDE_SKILL_DIR}/scripts/search.py`, since `CLAUDE_PLUGIN_ROOT` is unset for a user skill | absent `skills/ui-ux-pro-max/scripts` |

## Agents

| Entry | Upstream |
| --- | --- |
| `impeccable-asset-producer.md` | the Impeccable pack |
| `impeccable-documenter.md` | the Impeccable pack |
| `impeccable-finish-reviewer.md` | the Impeccable pack |
| `impeccable-manual-edit-applier.md` | the Impeccable pack |

## Blocks

| Markers | File | Upstream |
| --- | --- | --- |
