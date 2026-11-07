from dataclasses import dataclass

TOOL_CONFIG_ROOT = "docs/agents/integrations"
LINE_RULE_ROOT_DIRS = ("docs/",)
LINE_RULE_LOADED_DIRS = (".claude/",)
INSTRUCTION_FILES = ("AGENTS.md", "CLAUDE.md")


def is_tool_config(rel):
    rel = rel.strip("/")
    return rel == TOOL_CONFIG_ROOT or rel.startswith(TOOL_CONFIG_ROOT + "/")


@dataclass(frozen=True)
class LineRule:
    pattern: str
    merge_exempt: bool

    def governs(self, rel: str) -> bool:
        rel = rel.strip("/")
        return (("/" not in rel and rel.endswith(".md")) or rel.startswith(LINE_RULE_ROOT_DIRS)
                or any("/" + d in "/" + rel for d in LINE_RULE_LOADED_DIRS)
                or rel.rsplit("/", 1)[-1] in INSTRUCTION_FILES)


POINTER = LineRule(pattern=r"docs/agents/integrations(?![\w-])", merge_exempt=True)
