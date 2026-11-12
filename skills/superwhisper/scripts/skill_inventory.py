from __future__ import annotations

import json
import re
from pathlib import Path


HOME = Path.home()


USER_SKILLS = HOME / ".claude" / "skills"


USER_COMMANDS = HOME / ".claude" / "commands"


CODE_DIR = HOME / "Code"


SETTINGS = HOME / ".claude" / "settings.json"


OUT_DIR = HOME / ".local" / "share" / "superwhisper-skills"


# Built-in skills ship inside the claude binary -- no SKILL.md exists on disk, so the
# inventory has to be stated. Verify against a session's skill listing after a CLI
# upgrade; `claude plugin list` does not cover built-ins.
BUILTIN = [
    "artifact-capabilities", "artifact-design", "artifact-diagramming", "claude-api",
    "commit", "dataviz", "fewer-permission-prompts", "init", "keybindings-help",
    "loop", "run", "schedule", "security-review", "simplify", "update-config",
]


# Skill names that are also ordinary French or English words. Kept in the vocabulary
# by explicit decision -- the point is to measure the cost on the recordings corpus
# rather than assume it. Flagged in the run summary so the measurement has a target.
HOMOGRAPHS = {
    "git", "mission", "implement", "triage", "plain", "research",
    "linear", "migrate", "setup", "handoff", "prototype", "grilling",
}


FRONTMATTER_NAME = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)


def read_skill_name(skill_md: Path) -> str:
    """Frontmatter `name:` wins; the directory name is the fallback."""
    try:
        head = skill_md.read_text(encoding="utf-8", errors="replace")[:4096]
    except OSError:
        return skill_md.parent.name
    if head.lstrip().startswith("---"):
        body = head.split("---", 2)
        if len(body) >= 3:
            m = FRONTMATTER_NAME.search(body[1])
            if m:
                return m.group(1).strip().strip("\"'")
    return skill_md.parent.name


def disabled_names() -> set[str]:
    try:
        settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    off = {name for name, state in settings.get("skillOverrides", {}).items() if state == "off"}
    floor_off = {k[:-len("@skills-dir")] for k, v in (settings.get("enabledPlugins") or {}).items()
                 if v is False and k.endswith("@skills-dir")}
    for local in [*HOME.glob("Code/*/.claude/settings.local.json"), *HOME.glob("Code/*/*/.claude/settings.local.json")]:
        try:
            enabled = json.loads(local.read_text(encoding="utf-8")).get("enabledPlugins") or {}
        except (OSError, ValueError):
            continue
        floor_off -= {k[:-len("@skills-dir")] for k, v in enabled.items() if v is True and k.endswith("@skills-dir")}
    return off | floor_off


def collect() -> dict[str, list[str]]:
    """Every skill name, grouped by the source that owns it."""
    off = disabled_names()

    def keep(names):
        return sorted({n for n in names if n and n not in off})

    # A command file is spoken as a slash command exactly like a skill is, and its name is
    # the filename -- it carries no frontmatter `name:` to read.
    user = keep([read_skill_name(p) for p in USER_SKILLS.glob("*/SKILL.md")]
                + [p.stem for p in USER_COMMANDS.glob("*.md")])
    builtin = keep(BUILTIN)

    project: dict[str, list[str]] = {}
    for skill_md in sorted(CODE_DIR.glob("*/.claude/skills/*/SKILL.md")):
        repo = skill_md.parents[3].name
        project.setdefault(repo, []).append(read_skill_name(skill_md))
    for command_md in sorted(CODE_DIR.glob("*/.claude/commands/*.md")):
        repo = command_md.parents[2].name
        project.setdefault(repo, []).append(command_md.stem)
    project = {repo: keep(names) for repo, names in sorted(project.items())}

    return {"user": user, "builtin": builtin, "project": project}


def flatten(inv: dict) -> list[str]:
    names = set(inv["user"]) | set(inv["builtin"])
    for repo_names in inv["project"].values():
        names |= set(repo_names)
    return sorted(names)


def write_csv(names: list[str], path: Path) -> None:
    """SuperWhisper's import format. An empty `replacement` makes a vocabulary-only
    entry -- a recogniser hint, never an output rewrite."""
    lines = ["word,replacement"]
    lines += [f"{n}," for n in names]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
