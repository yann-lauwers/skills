from __future__ import annotations

import json
import re

from app_restart import SW_RECORDINGS


# A slash token in the final text. Anything already inside backticks or a path is not a
# command, so the lookbehind drops it rather than counting a URL segment as an invention.
COMMAND_TOKEN = re.compile(r"(?<![\w`/])/([a-z][a-z0-9-]*)")


def measure(mode_name: str, roster: list[str]) -> int:
    """The two numbers that say whether the prompt is working, counted on real output.

    The first one is the trigger for putting a roster in the prompt: a flat share of
    written command names matching a real skill. The second is rule 14,
    which no example demonstrated until the corpus said it was being ignored."""
    known = {n.lower() for n in roster}
    real = invented = glued = gapped = seen = 0
    unknown: dict[str, int] = {}
    for meta in sorted(SW_RECORDINGS.glob("*/meta.json")):
        try:
            d = json.loads(meta.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if d.get("modeName") != mode_name:
            continue
        text = d.get("llmResult") or ""
        if not text:
            continue
        seen += 1
        for m in COMMAND_TOKEN.finditer(text):
            name = m.group(1)
            if name.lower() in known:
                real += 1
            else:
                invented += 1
                unknown[name] = unknown.get(name, 0) + 1
            tail = text[m.end():m.end() + 2]
            if tail[:1] in ",.?!;:":
                glued += 1
            elif tail[:2] and tail[0] == " " and tail[1] in ",.?!;:":
                gapped += 1

    total = real + invented
    punct = glued + gapped
    print(f"{seen} recordings in \"{mode_name}\", {total} command tokens")
    if total:
        print(f"  rule 16  real names:  {real}/{total}  ({100 * real / total:.0f}%)")
    if punct:
        print(f"  rule 14  gap kept:    {gapped}/{punct}  ({100 * gapped / punct:.0f}%)")
    if unknown:
        top = sorted(unknown.items(), key=lambda kv: -kv[1])[:15]
        print("  not in the roster: " + ", ".join(f"{n}x{c}" for n, c in top))
    return 0
