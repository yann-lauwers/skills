from __future__ import annotations

import json
import subprocess
import time

from live_config import LEDGER_PATH, SW_DIR, SW_SETTINGS, obsolete_in, write_roster
from skill_inventory import OUT_DIR


def app_running() -> bool:
    return subprocess.run(["pgrep", "-x", "superwhisper"], capture_output=True).returncode == 0


SW_RECORDINGS = SW_DIR / "recordings"


# A dictation lands in bursts, so quitting moments after one ends cuts the next sentence
# just as surely as quitting mid-word. Three minutes covers a pause for thought without
# deferring a genuinely idle machine to tomorrow.
DICTATION_IDLE_SECONDS = 180


def dictation_active() -> str | None:
    """Reason the app is in use, or None when it is idle.

    A recording's directory appears when it starts and gains meta.json when it finishes,
    so a directory without one is a dictation in flight. Recency covers the gap between
    two sentences of the same burst.
    """
    try:
        # A recording's directory is named for the moment it started, so the newest name is
        # the newest recording. Reading names costs one directory listing; ranking by mtime
        # stats every recording ever made, on a cloud-synced folder, and grows with the corpus.
        recent = max((p for p in SW_RECORDINGS.iterdir() if p.name.isdigit()),
                     key=lambda p: int(p.name))
    except (OSError, ValueError):
        return None  # No recordings to read -- absence of evidence blocks nothing.
    if not (recent / "meta.json").exists():
        return "a dictation is in flight"
    idle = time.time() - recent.stat().st_mtime
    if idle < DICTATION_IDLE_SECONDS:
        return f"a dictation ended {int(idle)}s ago"
    return None


def quit_app() -> bool:
    busy = dictation_active()
    if busy:
        print(f"superwhisper is in use -- {busy}; leaving it alone")
        return False
    subprocess.run(["osascript", "-e", "with timeout of 15 seconds",
                    "-e", 'tell application "superwhisper" to quit', "-e", "end timeout"],
                   check=False, capture_output=True)
    if wait_for_exit():
        return True
    # A running instance can accept the quit event and never answer it -- the process stays
    # up, logs nothing, and every later pass defers behind it. It traps SIGTERM into that
    # same stuck terminate handler, so only SIGKILL ends it. That loses nothing here: the
    # app writes config as it changes rather than on quit, its recordings database is
    # SQLite in WAL mode and survives a kill, and the busy check above cleared a dictation.
    subprocess.run(["pkill", "-KILL", "-x", "superwhisper"], check=False)
    if wait_for_exit():
        print("superwhisper ignored the quit request -- stopped it with SIGKILL")
        return True
    print("superwhisper did not quit -- nothing written.")
    return False


def wait_for_exit(seconds: float = 10) -> bool:
    for _ in range(int(seconds / 0.2)):
        if not app_running():
            return True
        subprocess.run(["sleep", "0.2"], check=False)
    return False


def relaunch() -> int:
    # `open -g` races LaunchServices right after a quit and fails with -600, which leaves
    # the app down and the new config un-ingested. Retry, then verify it is really up.
    for _ in range(5):
        subprocess.run(["open", "-a", "superwhisper"], check=False, capture_output=True)
        for _ in range(20):
            if app_running():
                print("superwhisper relaunched")
                return 0
            subprocess.run(["sleep", "0.25"], check=False)
    print("superwhisper did not relaunch -- config written, start it by hand")
    return 1


# The app reads its config once, at launch, so a write newer than the running app's launch
# is on disk and nowhere else. The files look identical either way; this marker is what
# tells a loaded update from one still waiting for a restart.
STAGED_PATH = OUT_DIR / "staged.json"


def app_launched_at() -> float | None:
    pids = subprocess.run(["pgrep", "-x", "superwhisper"], capture_output=True, text=True).stdout.split()
    if not pids:
        return None
    started = subprocess.run(["ps", "-o", "lstart=", "-p", pids[0]],
                             capture_output=True, text=True).stdout.strip()
    try:
        return time.mktime(time.strptime(started, "%a %b %d %H:%M:%S %Y"))
    except ValueError:
        return None


def awaiting_restart() -> bool:
    """Whether a staged update is on disk but not yet in the running app.

    `ps` reports the launch to the second, so a launch in the same second as the write
    reads as not yet loaded -- the answer that costs one extra restart rather than none."""
    try:
        staged_at = json.loads(STAGED_PATH.read_text(encoding="utf-8"))["at"]
    except (OSError, ValueError, KeyError):
        return False
    launched = app_launched_at()
    if launched is not None and launched >= staged_at:
        STAGED_PATH.unlink(missing_ok=True)
        return False
    return True


def stage(names: list[str], roster: list[str] | None,
          inventory: list[str] | None = None) -> bool:
    """Write both layers to disk, whether or not the app is running; returns whether
    anything changed.

    `names` is what is missing; `inventory` is every name the run collected, and only a
    caller that passes it gets removals — a caller that omits it is adding, so nothing it
    did not name can be dropped on its behalf.

    The app rewrites a config file only when a setting changes in its own UI -- not on
    quit and not on a dictation, both measured by the file's mtime -- so disk is always
    current and merging into it loses nothing. It reads the files only at launch, so what
    lands here loads at the next start, whoever restarts it. A UI change made in between
    rewrites the file from memory and drops the write; the drift reappears, and the next
    pass writes it again."""
    settings = json.loads(SW_SETTINGS.read_text(encoding="utf-8"))
    vocab = settings.get("vocabulary", [])
    have = {v.strip().lower() for v in vocab}
    added = [n for n in names if n.lower() not in have]
    dropped = obsolete_in(vocab, inventory) if inventory is not None else []
    if added or dropped:
        gone = {v.strip().lower() for v in dropped}
        kept = [v for v in vocab if v.strip().lower() not in gone]
        settings["vocabulary"] = kept + added
        SW_SETTINGS.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        moved = f"added {len(added)}"
        if dropped:
            moved += f", dropped {len(dropped)} ({', '.join(dropped)})"
        print(f"{moved} -> {len(settings['vocabulary'])} in the vocabulary")
    if inventory is not None:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        LEDGER_PATH.write_text(
            json.dumps({"names": sorted(inventory)}, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")

    # Both layers land together: the recogniser gets the names, the cleanup model gets the
    # roster it checks a near miss against. Splitting them would leave a roster naming
    # skills the recogniser cannot hear.
    changed = len(added) + len(dropped) + (write_roster(roster) if roster is not None else 0)
    if changed:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        STAGED_PATH.write_text(json.dumps({"at": time.time()}) + "\n", encoding="utf-8")
    return changed > 0


def restart_app() -> int:
    """Quit and relaunch, so the running app loads what is on disk now."""
    if app_running() and not quit_app():
        return 1
    rc = relaunch()
    if rc == 0:
        STAGED_PATH.unlink(missing_ok=True)
    return rc


def apply(names: list[str], restart: bool, roster: list[str] | None = None,
          inventory: list[str] | None = None) -> int:
    """Stage the update, then load it now when asked to."""
    stage(names, roster, inventory)
    if not restart:
        if app_running() and awaiting_restart():
            print("staged -- SuperWhisper loads it the next time it starts")
        return 0
    return restart_app()
