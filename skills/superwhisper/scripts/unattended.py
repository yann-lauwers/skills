from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path

from app_restart import app_running, apply, awaiting_restart, dictation_active, restart_app, stage
from live_config import obsolete
from skill_inventory import OUT_DIR


ENTRY = Path(__file__).resolve().with_name("sync-slash-commands.py")

# A job that reports its successes trains the reader to ignore it, and then the one
# message that matters arrives inside that noise. A notification fires only for a state
# that needs a hand, so its presence alone carries meaning.
STATE_PATH = OUT_DIR / "schedule.json"


# The pass runs every quarter hour, so counting runs measures nothing a person
# recognises. The calendar is what they read: days a name has been waiting, and whether
# today's single question has already been asked.
GRACE_DAYS = 1


# Keyboard and mouse quiet for this long means the machine is unattended, which is the
# only moment a relaunch costs nothing. Longer than a pause for thought, shorter than
# any real break -- so a normal day offers several windows without ever interrupting one.
IDLE_APPLY_SECONDS = 300


def today() -> str:
    return time.strftime("%Y-%m-%d")


def tomorrow() -> str:
    return time.strftime("%Y-%m-%d", time.localtime(time.time() + 86400))


def days_since(iso: str | None) -> int:
    if not iso:
        return 0
    try:
        then = time.mktime(time.strptime(iso, "%Y-%m-%d"))
    except ValueError:
        return 0
    return max(0, int((time.time() - then) // 86400))


def read_state() -> dict:
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def write_state(state: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def clear_state() -> None:
    STATE_PATH.unlink(missing_ok=True)


def muted_for(state: dict, missing: list[str], stale: bool) -> bool:
    """Whether a dismissal still covers what is pending.

    "Ne plus demander" answers the batch it was shown. A skill added afterwards is a new
    question, so the mute lifts on its own -- a permanent one freezes the vocabulary
    months later, and does it silently, which is the whole failure this job exists to fix.
    """
    if not state.get("muted"):
        return False
    if stale and not state.get("muted_roster"):
        return False
    return {n.lower() for n in missing} <= {n.lower() for n in state.get("muted_names", [])}


def user_idle_seconds() -> float:
    """Seconds since the last keyboard or mouse event.

    Idle at the keyboard is not idle at the microphone: a monologue moves no HID event,
    so this reads as unattended mid-sentence. It is the second gate and never the first
    -- dictation_active() rules on the microphone before this is consulted.
    """
    out = subprocess.run(["ioreg", "-c", "IOHIDSystem"], capture_output=True, text=True)
    for line in out.stdout.splitlines():
        if "HIDIdleTime" in line:
            try:
                return int(line.rsplit("=", 1)[1].strip()) / 1e9
            except (IndexError, ValueError):
                break
    return 0.0  # Unreadable reads as "someone is here", which is the answer that waits.


def wait_for_quiet(limit: int = 180) -> str | None:
    """Hold until the microphone goes quiet, or give up and say why.

    Reached from the notification's "Maintenant": the answer was given deliberately, so a
    burst that happens to be in flight is worth waiting out rather than refusing.
    """
    deadline = time.time() + limit
    while True:
        busy = dictation_active()
        if not busy:
            return None
        if time.time() >= deadline:
            return busy
        subprocess.run(["sleep", "5"], check=False)


# A command launched by clicking a notification inherits a bare PATH, not the user's --
# so a PATH lookup finds nothing exactly on the path that reports the outcome, and the
# click looks dead while having done its work. Known install locations come first.
NOTIFIER_CANDIDATES = (
    Path("/opt/homebrew/bin/terminal-notifier"),
    Path("/usr/local/bin/terminal-notifier"),
)


def notifier_binary() -> str | None:
    for candidate in NOTIFIER_CANDIDATES:
        if candidate.exists():
            return str(candidate)
    return shutil.which("terminal-notifier")


def notify_mac(title: str, message: str, execute: str | None = None) -> bool:
    """Native notification, optionally acting when clicked.

    Carries anything the user can resolve with one gesture on this machine. `execute`
    runs on click, so the notification is the button -- no chat round-trip for an action
    that only ever happens here.
    """
    binary = notifier_binary()
    if not binary:
        print("terminal-notifier not found -- nothing to notify with")
        return False
    cmd = [binary, "-title", title, "-message", message, "-group", "superwhisper-skills",
           # Focus swallows an ordinary banner without a trace, and this one is only ever
           # sent for a state that needs a hand.
           "-ignoreDnD"]
    if execute:
        cmd += ["-execute", execute]
    return subprocess.run(cmd, capture_output=True).returncode == 0


DIALOG_BUTTONS = ("Ne plus demander", "Plus tard", "Maintenant")


# Text reaches the dialog through argv, never through the script source. AppleScript
# claims « » for raw-chaining syntax, so a message carrying French quotation marks
# compiles to a syntax error -- and an error looks exactly like an unanswered dialog.
ASK_SCRIPT = (
    "on run {msg, b1, b2, b3}",
    "display dialog msg with title \"SuperWhisper\" buttons {b1, b2, b3} "
    "default button b3 with icon note giving up after 120",
    "end run",
)


def ask(message: str) -> str | None:
    """The three answers a person has, one gesture each. None when the dialog never ran.

    A dialog rather than buttons on the banner: this terminal-notifier build carries no
    `-actions`, and an osascript dialog needs no automation permission to appear. A
    dialog nobody answers is a "later" -- the same as ignoring the banner it came from.
    """
    cmd = ["osascript"]
    for line in ASK_SCRIPT:
        cmd += ["-e", line]
    cmd += ["--", message, *DIALOG_BUTTONS]
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        print(f"dialog failed -- {out.stderr.strip()}")
        return None
    for part in out.stdout.strip().split(", "):
        if part.startswith("button returned:"):
            return part.split(":", 1)[1] or DIALOG_BUTTONS[1]
    return DIALOG_BUTTONS[1]


def snooze(state: dict, note: str) -> None:
    """Tomorrow, not an hour: the question is worth one appearance a day, and a second
    one the same day teaches the reader to dismiss it without reading."""
    state.setdefault("pending_since", today())
    state["snoozed_until"] = tomorrow()
    write_state(state)
    notify_mac("SuperWhisper — reporté", note)


def fail(state: dict, reason: str) -> int:
    """Turn a failure under the unattended pass into a notification, since launchd prints
    to a log nobody opens and the same failure would repeat on every pass."""
    notify_mac("SuperWhisper — mise à jour échouée", f"{reason} Cliquer pour réessayer.".strip(),
               # Absolute: the click fires outside this process's working directory.
               execute=f"{ENTRY} --prompt")
    state["last_error"] = reason
    write_state(state)
    return 1


def auto(missing: list[str], roster: list[str], stale: bool,
         inventory: list[str]) -> int:
    """The unattended pass: write the update at once, restart the app to load it in a
    window nobody is using, and ask once a day when no such window comes.

    Silent by design. It runs every quarter hour, and a line per poll buries the one line
    that explains whatever sent the reader to the log.
    """
    state = read_state()

    if missing or stale or obsolete(inventory):
        # Written at once, whatever the app is doing: writing interrupts nothing, and a
        # restart by anyone -- the person at the machine, or this pass -- loads it. A
        # hand-edited prompt can lose the section F anchor, and set_roster refuses rather
        # than guess where the roster goes.
        try:
            stage(missing, roster, inventory)
        except SystemExit as refusal:
            return fail(state, str(refusal))
        state["pending"] = sorted(set(state.get("pending", [])) | set(missing))
        state["pending_roster"] = state.get("pending_roster", False) or stale

    if not awaiting_restart():
        clear_state()
        return 0

    state.setdefault("pending_since", today())
    pending = state.get("pending", [])

    if not app_running():
        # Quit: it loads the update when it is next opened, and opening an app the user
        # closed would be a change nobody asked for.
        write_state(state)
        return 0

    if dictation_active():
        write_state(state)
        return 0

    idle = user_idle_seconds()
    if idle >= IDLE_APPLY_SECONDS:
        print(f"unattended for {int(idle // 60)} min -- restarting to load {len(pending)} names")
        if restart_app() != 0:
            return fail(state, "L'app est peut-être restée fermée.")
        clear_state()
        return 0

    waited = days_since(state.get("pending_since"))
    spoken_for = state.get("snoozed_until", "") > today()
    if waited < GRACE_DAYS or spoken_for or muted_for(state, pending, state.get("pending_roster", False)):
        write_state(state)
        return 0

    label = f"{len(pending)} skills" if pending else "Le roster du mode"
    if not notify_mac(
        "SuperWhisper — mise à jour en attente",
        f"{label} prêts depuis {waited} j, chargés au prochain redémarrage. Cliquer pour choisir.",
        execute=f"{ENTRY} --prompt",
    ):
        print("could not notify -- update still pending")
    state["snoozed_until"] = tomorrow()
    write_state(state)
    return 1


def prompt_choice(missing: list[str], roster: list[str], stale: bool,
                  inventory: list[str]) -> int:
    """The banner's click target: ask, then carry the answer out."""
    state = read_state()

    if not missing and not stale and not obsolete(inventory) and not awaiting_restart():
        clear_state()
        notify_mac("SuperWhisper à jour", "Le vocabulaire contient déjà tous les skills.")
        return 0

    pending = sorted(set(state.get("pending", [])) | set(missing))
    waited = days_since(state.get("pending_since"))
    label = f"{len(pending)} nouveaux skills attendent" if pending else "Le roster du mode est en retard"
    answer = ask(f"{label} depuis {waited} j.\n\n"
                 "Appliquer redémarre SuperWhisper — deux secondes, "
                 "et la dictée reprend derrière.")

    if answer is None:
        # A dialog that never appeared is not an answer. Saying so beats snoozing on the
        # user's behalf, which would look like a banner they simply never clicked.
        notify_mac("SuperWhisper — dialogue indisponible",
                   "La question n'a pas pu s'afficher. Lancer le générateur à la main.")
        return 1

    if answer == DIALOG_BUTTONS[0]:
        state["muted"] = True
        state["muted_names"] = pending
        state["muted_roster"] = stale or state.get("pending_roster", False)
        state.setdefault("pending_since", today())
        write_state(state)
        notify_mac("SuperWhisper — en sourdine",
                   "Ces skills ne seront plus proposés. Un nouveau skill relance la question.")
        return 0

    if answer == DIALOG_BUTTONS[1]:
        snooze(state, "La question revient demain.")
        return 0

    # "Maintenant" is a deliberate answer, so a burst that happens to be in flight is
    # worth waiting out rather than refusing.
    busy = wait_for_quiet()
    if busy:
        snooze(state, f"Dictée en cours ({busy}). La question revient demain.")
        return 1

    if apply(missing, restart=True, roster=roster, inventory=inventory) != 0:
        notify_mac("SuperWhisper — mise à jour échouée",
                   "L'app est peut-être restée fermée. Cliquer pour réessayer.",
                   execute=f"{ENTRY} --prompt")
        return 1

    clear_state()
    notify_mac("SuperWhisper à jour",
               f"{len(pending)} skills chargés, {len(roster)} dans le roster.")
    return 0
