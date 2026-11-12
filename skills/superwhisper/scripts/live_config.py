from __future__ import annotations

import json
import os
import pwd
import subprocess
from pathlib import Path

from skill_inventory import HOME, OUT_DIR, disabled_names


def superwhisper_dir() -> Path:
    result = subprocess.run(["defaults", "read", "com.superduper.superwhisper", "appFolderDirectory"],
                            capture_output=True, text=True)
    base = result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else str(HOME)
    real_home = pwd.getpwuid(os.getuid()).pw_dir
    if base == real_home or base.startswith(real_home + "/"):
        base = str(HOME) + base[len(real_home):]
    return Path(base) / "superwhisper"


SW_DIR = superwhisper_dir()


# The live vocabulary is the ground truth for what has actually been imported, so drift
# needs no bookkeeping of its own. Read-only: SuperWhisper rewrites it wholesale from memory.
SW_SETTINGS = SW_DIR / "settings" / "settings.json"


# The cleanup model never sees the vocabulary, so a name the recogniser mangles can only
# be repaired downstream -- section F of this mode's prompt carries the roster the model
# checks a near miss against. Measured trigger: 32% of written command names matched no
# real skill across the recordings corpus, which is what the roster exists to close.
# Each mode carries the roster in its own language, so the anchor is per mode: section F
# is bounded by a heading the prompt already owns rather than by a machine marker -- every
# byte of a mode prompt travels to the model on every dictation, and a marker would be
# noise it receives in full.
SW_MODES = [
    (SW_DIR / "modes" / "code-fr-en.json",
     "24. The list below is every slash command that exists."),
    (SW_DIR / "modes" / "code-fr.json",
     "24. La liste ci-dessous est l'intégralité des slash commands qui existent."),
]


ROSTER_REPO = "nexus"


def roster_names(inv: dict) -> list[str]:
    """What reaches the prompt: user skills, built-ins, and the one repo dictated at.

    The near-miss rule turns every entry into a target a misheard word can snap to, so
    breadth costs accuracy rather than buying coverage. Other repos hold Cue agent
    personas and archived product skills -- names never said out loud at a coding agent.
    """
    names = set(inv["user"]) | set(inv["builtin"]) | set(inv["project"].get(ROSTER_REPO, []))
    return sorted(names)


def roster_block(names: list[str], per_line: int = 6) -> str:
    rows = [", ".join(names[i:i + per_line]) for i in range(0, len(names), per_line)]
    return "\n".join(rows)


def set_roster(prompt: str, names: list[str], anchor: str) -> str:
    """Rewrite everything after the section F rule with the current roster."""
    head, sep, _tail = prompt.partition(anchor)
    if not sep:
        raise SystemExit("mode prompt carries no section F anchor -- refusing to guess where it goes")
    rule_end = _tail.find("\n")
    rule = _tail[:rule_end] if rule_end != -1 else _tail
    return f"{head}{sep}{rule}\n\n{roster_block(names)}\n"


def live_prompt(path: Path) -> str:
    return json.loads(path.read_text(encoding="utf-8")).get("prompt", "")


def roster_stale(names: list[str]) -> bool:
    """Stale as soon as ONE mode is behind -- every mode is written in the same pass."""
    for path, anchor in SW_MODES:
        if not path.exists():
            continue
        current = live_prompt(path)
        if anchor not in current:
            return True
        if current.rstrip() != set_roster(current, names, anchor).rstrip():
            return True
    return False


def write_roster(names: list[str]) -> int:
    """Rewrite section F in every installed mode whose roster differs; returns how many
    files changed. An unchanged file is left alone, since any write marks the update as
    waiting for a restart."""
    changed = 0
    for path, anchor in SW_MODES:
        if not path.exists():
            continue
        mode = json.loads(path.read_text(encoding="utf-8"))
        prompt = set_roster(mode["prompt"], names, anchor)
        if prompt.rstrip() == mode["prompt"].rstrip():
            continue
        mode["prompt"] = prompt
        path.write_text(json.dumps(mode, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"roster refreshed -> {len(names)} commands in {path.name}")
        changed += 1
    return changed


def live_vocabulary() -> list[str]:
    return json.loads(SW_SETTINGS.read_text(encoding="utf-8")).get("vocabulary", [])


def drift(names: list[str]) -> list[str]:
    """Generated names absent from the live vocabulary. Entries the vocabulary holds
    for other reasons are none of this script's business and stay untouched."""
    live = {v.strip().lower() for v in live_vocabulary()}
    return [n for n in names if n.lower() not in live]


LEDGER_PATH = OUT_DIR / "written-names.json"


def written_before() -> set[str]:
    """Names this script has put in the live vocabulary, so a skill that is renamed or
    retired takes its old entry with it. Seeded from the CSV path's own record, which
    predates this ledger, so entries written before it exist are still ours to withdraw.
    A name outside it was typed for some other reason and is never removed."""
    for path in (LEDGER_PATH, OUT_DIR / "last-run.json"):
        try:
            recorded = json.loads(path.read_text(encoding="utf-8")).get("names", [])
        except (OSError, ValueError):
            continue
        return {n.strip().lower() for n in recorded}
    return set()


def obsolete_in(vocab: list[str], names: list[str]) -> list[str]:
    """Vocabulary entries this script wrote that the inventory no longer holds.

    A skill switched off in settings.json keeps its entry: it still exists and is still
    spoken, and what being off costs it is a place in the roster the model offers, not the
    recogniser's ear. Only a name with no skill behind it any more is withdrawn."""
    current = {n.lower() for n in names} | {n.lower() for n in disabled_names()}
    ours = written_before()
    return [v for v in vocab if v.strip().lower() in ours and v.strip().lower() not in current]


def obsolete(names: list[str]) -> list[str]:
    return obsolete_in(live_vocabulary(), names)
