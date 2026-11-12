#!/usr/bin/env python3
"""Generate SuperWhisper dictation aids from the real Claude Code skill inventory.

It writes vocabulary.csv for a manual import through the app's own interface, and
`--apply` writes the live vocabulary directly. SuperVocab phonemises each entry in fr
AND en, so a French reading of "validate" becomes reachable and "slash validé" stops
winning -- biasing the recogniser is what makes a spoken command name land.

SuperWhisper reads its config once, at launch, and rewrites a file only when a setting
changes in its own UI. So `--apply` writes at any time, and the update loads at the next
start, whoever restarts the app -- this script, or a person quitting and reopening it. A
UI change made in between rewrites the file from memory and drops the write; the drift
reappears and the next pass writes it again.

A dictation in flight, or one that ended in the last few minutes, outranks any request
to restart: the update is already on disk, a cut-off sentence cannot be recovered.

`--auto` is the unattended pass, run every quarter hour. It writes an update as soon as
it finds one, then restarts the app in a window the machine is not being used -- no
dictation for minutes, no keyboard or mouse either -- so the two-second relaunch happens
while nobody is there to notice it. A restart by hand loads it just the same. A machine
that never goes quiet gets one notification a day instead, carrying the three answers a
person actually has: now, tomorrow, or stop asking about these.

Notifications are local (terminal-notifier) and fire only when the update needs a hand.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app_restart import app_running, awaiting_restart, dictation_active, restart_app, stage
from compliance import measure
from live_config import SW_DIR, SW_SETTINGS, drift, obsolete, roster_names, roster_stale
from skill_inventory import HOMOGRAPHS, OUT_DIR, collect, flatten, write_csv
from unattended import auto, clear_state, prompt_choice


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=OUT_DIR, help=f"output directory (default: {OUT_DIR})")
    ap.add_argument("--scope", choices=["all", "user", "user+nexus"], default="all",
                    help="which skills reach the vocabulary (default: all, projects included)")
    ap.add_argument("--json", action="store_true", help="print the inventory as JSON and write nothing")
    ap.add_argument("--measure", action="store_true",
                    help="count rule compliance on the recordings corpus; writes nothing")
    ap.add_argument("--check", action="store_true",
                    help="report which names are missing from the live vocabulary; exit 1 on drift")
    ap.add_argument("--apply", action="store_true",
                    help="write the missing names and the roster to disk; SuperWhisper loads "
                         "them at its next start, whoever restarts it")
    ap.add_argument("--restart", action="store_true",
                    help="with --apply: restart SuperWhisper so it loads them now")
    ap.add_argument("--auto", action="store_true",
                    help="unattended pass: write at once, restart while the machine is idle, "
                         "ask once a day otherwise")
    ap.add_argument("--prompt", action="store_true",
                    help="ask now / tomorrow / stop asking, then act; the banner's click target")
    args = ap.parse_args()

    inv = collect()

    if args.scope == "user":
        inv["project"] = {}
    elif args.scope == "user+nexus":
        inv["project"] = {k: v for k, v in inv["project"].items() if k == "nexus"}

    names = flatten(inv)

    if args.json:
        json.dump({"names": names, "inventory": inv}, sys.stdout, indent=2, ensure_ascii=False)
        print()
        return 0

    if args.measure:
        return measure("Code FR -> EN", roster_names(inv))

    args.out.mkdir(parents=True, exist_ok=True)

    roster = roster_names(inv)

    if args.check or args.apply or args.auto or args.prompt:
        if not SW_SETTINGS.is_file():
            print(f"SuperWhisper folder not found: {SW_DIR} -- point the app's folder setting there or move it")
            return 1
        if args.check:
            print(f"reading {SW_DIR}")
        missing = drift(names)
        # Two layers, one verdict: a roster naming a skill the vocabulary never learned
        # is as stale as a vocabulary missing one, and the same write fixes both.
        stale = roster_stale(roster)
        # A retired or renamed skill leaves its entry behind, where it goes on biasing the
        # recogniser toward a command nothing answers -- and toward the prefix of the name
        # that replaced it.
        gone = obsolete(names)

        if args.auto:
            return auto(missing, roster, stale, names)
        if args.prompt:
            return prompt_choice(missing, roster, stale, names)

        if missing:
            print(f"{len(missing)} missing from the live vocabulary: {', '.join(missing)}")
        if stale:
            print(f"mode prompt roster is stale -- {len(roster)} commands to write")
        if gone:
            print(f"{len(gone)} left in the live vocabulary by a retired skill: {', '.join(gone)}")

        if not args.apply:
            if missing or stale or gone:
                return 1
            if awaiting_restart():
                print("staged -- written to disk, loads the next time SuperWhisper starts")
                return 1
            print(f"in sync -- all {len(names)} commands are in the live vocabulary, "
                  f"{len(roster)} in the mode prompt roster, loaded by the running app")
            return 0

        if missing or stale or gone:
            stage(missing, roster, names)
        if not awaiting_restart():
            print(f"in sync -- {len(roster)} commands in the roster, loaded by the running app")
            clear_state()
            return 0
        if not args.restart:
            print("staged -- SuperWhisper loads it the next time it starts")
            return 0

        # Being mid-dictation outranks --restart: the update is already on disk and loads
        # at the next start, while a cut-off sentence cannot be recovered.
        busy = dictation_active() if app_running() else None
        if busy:
            print(f"{busy} -- staged; it loads the next time SuperWhisper starts")
            return 1
        if restart_app() != 0:
            return 1
        clear_state()
        return 0

    csv_path = args.out / "vocabulary.csv"

    previous = set()
    state_path = args.out / "last-run.json"
    if state_path.exists():
        try:
            previous = set(json.loads(state_path.read_text(encoding="utf-8")).get("names", []))
        except ValueError:
            pass

    write_csv(names, csv_path)
    state_path.write_text(json.dumps({"names": names}, indent=2, ensure_ascii=False), encoding="utf-8")

    added = sorted(set(names) - previous)
    removed = sorted(previous - set(names))
    project_total = sum(len(v) for v in inv["project"].values())

    print(f"{len(names)} commands  "
          f"({len(inv['user'])} user + {len(inv['builtin'])} built-in + {project_total} project)")
    for repo, repo_names in inv["project"].items():
        print(f"    {repo}: {len(repo_names)}")
    if previous:
        print(f"  added:   {', '.join(added) if added else '-'}")
        print(f"  removed: {', '.join(removed) if removed else '-'}")
    flagged = sorted(HOMOGRAPHS & set(names))
    if flagged:
        print(f"  homographs in the vocabulary ({len(flagged)}): {', '.join(flagged)}")
        print("    these bias ordinary speech too -- recount them on recordings/ after a few days")
    print()
    print(f"  {csv_path}")
    print("      Settings -> Vocabulary -> Import CSV (drag and drop)")
    print()
    print("  Applying without the UI needs --apply; the app loads it at its next start.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
