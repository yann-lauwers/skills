#!/usr/bin/env python3
"""Watches the fleet's credentials and re-logins a dead one unattended.

    credential-watch tick [--dry-run]     one reading; acts on at most one slot
    credential-watch status               the state file and the last readings, as JSON
    credential-watch notify <text>        one Slack DM to Yann, the channel every act reports on

The object is a cswap slot's credential. Its one source is `cswap list --json`, cswap's own
verdict on every slot: `usageStatus: "relogin_required"` means cswap's refresh of that slot's
credential was rejected and no fresher copy has healed it. Alone that is no verdict: a copy
that is stale while its login lives in a running session heals on cswap's next save of the
live login. Read unchanged on every tick across CONFIRM_S — readings, not elapsed time — the
heal has had every chance to land and the login is gone.

Verdicts, per slot:  DEAD · WAITING · LIVE.  DEAD is actionable (WAITING is an unconfirmed
DEAD, carried across ticks in the state file), and the act is /relogin's own tool, `oauth.py --email <slot's email>`, followed by the two
reads that skill names as the proof — the slot's usageStatus and laxity's servable — and
the manifest's `verified` stamp. One act per tick, in series: each run repoints the global
cswap account for about a minute, and two at once collide on it. A slot that cannot be
acted on — no email, or inside its backstop — is passed over, and the next one takes the
tick's act.

The backstop is per account: one attempt per 6 h, two per 24 h. Past it the watcher stops
acting on that account and says so once a day. Every act and every stop reaches Yann as a
Slack DM from the bot, the same channel the hook-review job uses.

SECRET DISCIPLINE — this script reads a Slack bot token and drives a login. Neither the
token, a magic link nor a credential ever reaches stdout, stderr or the log: the token is
an Authorization header only, oauth.py's output is filtered to its own log lines, and every
failure prints a status or an error name.

Exit codes: 0 nothing to do or acted and proven · 1 an act failed or could not be proven ·
2 the object could not be read.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HOME = Path.home()
MANIFEST = HOME / ".config" / "claude-login" / "accounts.json"
OAUTH = HOME / ".local" / "share" / "cswap-relogin" / "oauth.py"
STATE_DIR = Path(os.environ.get("CREDENTIAL_WATCH_STATE") or HOME / ".local" / "state" / "credential-watch")
STATE = STATE_DIR / "state.json"
LOG = STATE_DIR / "log"
LOCK = STATE_DIR / "tick.lock"
COOLDOWN_S = 6 * 3600
RELOGIN_TIMEOUT_S = 160 * 60
HANDOFF_EXPIRED = 3
DAILY_CAP = 2
# How long a slot must read `relogin_required` unchanged before that reading is a verdict:
# long enough for cswap to save a live session's fresher copy over a stale one.
CONFIRM_S = 15 * 60
# The launchd job's own interval (com.yann.credential-watch, StartInterval). A gap wider than
# one and a half of these means readings stopped, not that the slot held.
TICK_S = 600
KEYCHAIN_ITEM = "nexus-slack-bot-token"
RECIPIENT = os.environ.get("CREDENTIAL_WATCH_RECIPIENT") or "U09G0FDNUET"
API = "https://slack.com/api/"
CSWAP = os.environ.get("CSWAP", "cswap")
LAXITY = os.environ.get("CSWAP_LAXITY", "cswap-laxity")


class Unknown(Exception):
    """A read that answered nothing usable. Never a verdict."""


def now() -> float:
    return time.time()


def iso(ts: float | None) -> str | None:
    return dt.datetime.fromtimestamp(ts).isoformat(timespec="seconds") if isinstance(ts, (int, float)) else None


def log(line: str) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as fh:
        fh.write(f"{iso(now())} {line}\n")
    print(line, file=sys.stderr)


# --- the probe: cswap's own reading ---------------------------------------------------

def run_json(argv: list[str], timeout: int = 60) -> object:
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Unknown(f"{argv[0]}: {type(exc).__name__}")
    if r.returncode != 0:
        raise Unknown(f"{' '.join(argv[:3])} exited {r.returncode}")
    try:
        return json.loads(r.stdout)
    except ValueError:
        raise Unknown(f"{argv[0]} printed no JSON")


def read_slots() -> dict[int, dict]:
    d = run_json([CSWAP, "list", "--json"])
    rows = d.get("accounts") if isinstance(d, dict) else None
    if not rows:
        raise Unknown("cswap list: no accounts")
    return {int(a["number"]): a for a in rows if a.get("number") is not None}


def probe() -> list[dict]:
    """One reading of every slot. Raises Unknown rather than guessing."""
    slots = read_slots()
    readings = []
    for n, a in sorted(slots.items()):
        email = a.get("email")
        if a.get("usageStatus") == "relogin_required":
            v = {"verdict": "WAITING", "reason": "cswap reports relogin_required"}
        else:
            v = {"verdict": "LIVE", "reason": f"usageStatus {a.get('usageStatus')}"}
        readings.append({"slot": n, "email": email, **v})
    return readings


def confirm_dead(readings: list[dict], state: dict, t: float) -> list[dict]:
    """Age every WAITING reading against the state file, promoting the ones READINGS have
    covered for CONFIRM_S to DEAD. Pure but for the `waiting` map it maintains.

    The window is covered rather than merely elapsed, which is why each entry carries
    `last_seen`: time passing is not evidence, and the two ways of taking no reading — a
    source that failed (`_tick` returns before this runs) and a Mac asleep past the tick
    interval — are exactly when the heal this window waits for could not have landed either.
    A gap wider than one and a half ticks restarts the clock, so one missed tick never
    lands on the boundary; a failed read clears every clock outright. A slot that recovers, changes hands or
    leaves the listing drops its entry, so what is timed is one unbroken run of readings.
    """
    waiting = state.setdefault("waiting", {})
    out = []
    for r in readings:
        key = str(r["slot"])
        if r["verdict"] != "WAITING":
            waiting.pop(key, None)
            out.append(r)
            continue
        seen = waiting.get(key)
        if not isinstance(seen, dict):
            seen = {}
        since = seen.get("since")
        last_seen = seen.get("last_seen")
        if (seen.get("email") != r["email"]
                or not isinstance(since, (int, float))
                or not isinstance(last_seen, (int, float))
                or t - float(last_seen) > 1.5 * TICK_S):
            # First sighting, the slot changed hands, or readings stopped covering it.
            since = t
        waiting[key] = {"email": r["email"], "since": float(since), "last_seen": t}
        held = t - float(since)
        if held >= CONFIRM_S:
            out.append({**r, "verdict": "DEAD",
                        "reason": f"cswap has read relogin_required on every tick since {iso(since)}, "
                                  f"long enough for a live session's fresher copy to have healed it"})
        else:
            out.append({**r, "reason": f"{r['reason']} since {iso(since)} — "
                                       f"confirms in {int(CONFIRM_S - held)}s of covered readings"})
    # A slot absent from this reading keeps no clock: cswap re-uses a freed slot number, so a
    # stale entry would make the next account on it actionable without a window of its own.
    for gone in set(waiting) - {str(r["slot"]) for r in readings}:
        waiting.pop(gone)
    return out


# --- the state file: attempts per account, and what was last seen -------------------------

def read_state() -> dict:
    try:
        return json.loads(STATE.read_text())
    except (OSError, ValueError):
        return {"attempts": {}, "backstop_told": {}, "last": None}


def write_state(s: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(s, indent=2) + "\n")
    os.replace(tmp, STATE)


def cooldown_left(state: dict, email: str, t: float | None = None) -> tuple[int, str]:
    """(seconds to wait, why) — 0 when an attempt may run now. Pure, so a test can drive it."""
    t = t or now()
    stamps = [float(x) for x in state.get("attempts", {}).get(email, [])]
    recent = [x for x in stamps if t - x < 24 * 3600]
    if len(recent) >= DAILY_CAP:
        return int(min(recent) + 24 * 3600 - t), f"{DAILY_CAP} attempts in 24 h"
    if stamps and t - max(stamps) < COOLDOWN_S:
        return int(max(stamps) + COOLDOWN_S - t), "last attempt under 6 h ago"
    return 0, ""


# --- the act: relogin, prove, stamp ---------------------------------------------------------

def relogin(email: str, old_slot: int) -> tuple[bool | None, str]:
    """Runs oauth.py and proves the result the way the relogin skill says. Returns (ok, why);
    ok is None when oauth.py handed the browser to Yann and nobody finished it."""
    r = subprocess.run([sys.executable, str(OAUTH), "--email", email],
                       capture_output=True, text=True, timeout=RELOGIN_TIMEOUT_S)
    for ln in r.stderr.splitlines():
        if ln.startswith(("oauth-relogin:", "[claude-login]", "[browser]")):
            log(f"  {ln[:200]}")
    if r.returncode == HANDOFF_EXPIRED:
        return None, "the browser window waited for Yann and closed unfinished"
    if r.returncode != 0:
        return False, f"oauth.py exited {r.returncode}"
    try:
        slots = read_slots()
    except Unknown as exc:
        return False, f"after login, {exc}"
    mine = [n for n, a in slots.items() if a.get("email") == email]
    new = max(mine) if mine else None
    if new is None or new == old_slot:
        return False, "no new slot captured"
    status = slots[new].get("usageStatus")
    if status != "ok":
        return False, f"slot {new} usageStatus {status}"
    try:
        rank = run_json([LAXITY, "rank", "--json"], timeout=120)
    except Unknown as exc:
        return False, f"rank: {exc}"
    rows = rank.get("rows", []) if isinstance(rank, dict) else []
    row = next((x for x in rows if x.get("email") == email and int(x.get("account", -1)) == new), None)
    if row is None or not row.get("servable"):
        return False, f"slot {new} not servable per laxity ({(row or {}).get('reason') or 'absent from rank'})"
    remove_slot(old_slot)
    stamp_verified(email)
    return True, f"slot {old_slot} → {new}, usageStatus ok, servable"


def remove_slot(n: int) -> None:
    """The dead slot goes, as the skill says; cswap asks for a y."""
    r = subprocess.run([CSWAP, "remove", str(n)], input="y\n", capture_output=True, text=True, timeout=60)
    log(f"  cswap remove {n}: exit {r.returncode}")


def stamp_verified(email: str) -> None:
    try:
        m = json.loads(MANIFEST.read_text())
        m.setdefault("accounts", {}).setdefault(email, {})["verified"] = dt.date.today().isoformat()
        tmp = MANIFEST.with_suffix(".tmp")
        tmp.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n")
        os.replace(tmp, MANIFEST)
    except (OSError, ValueError) as exc:
        log(f"  manifest stamp failed: {type(exc).__name__}")


# --- reaching the person ----------------------------------------------------------------------

def token() -> str | None:
    tok = os.environ.get("SLACK_BOT_TOKEN")
    if tok:
        return tok
    try:
        out = subprocess.run(["security", "find-generic-password", "-s", KEYCHAIN_ITEM, "-w"],
                             capture_output=True, text=True, timeout=30)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except Exception:
        pass
    if os.environ.get("NOTIFY_REEXEC") != "1":
        env = dict(os.environ, NOTIFY_REEXEC="1")
        name = re.sub(r"[^A-Za-z0-9]", "_", KEYCHAIN_ITEM).upper()
        try:
            os.execvpe("keyless", ["keyless", "run", "-s", "SLACK_BOT_TOKEN=" + name, "--",
                                   sys.executable, os.path.abspath(__file__)] + sys.argv[1:], env)
        except OSError:
            return None
    return None


def slack(method: str, tok: str, payload: dict) -> tuple[bool, dict]:
    req = urllib.request.Request(API + method, data=json.dumps(payload).encode(),
                                 headers={"Authorization": "Bearer " + tok,
                                          "Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as exc:
        return False, {"error": f"http_{exc.code}"}
    except Exception as exc:
        return False, {"error": type(exc).__name__}
    return bool(data.get("ok")), data


def notify(text: str) -> None:
    """A DM, and the same line in the log whatever the DM does."""
    log(f"NOTIFY {text}")
    tok = token()
    if not tok:
        log("  (no Slack token — the DM was not sent)")
        return
    ok, data = slack("conversations.open", tok, {"users": RECIPIENT})
    if not ok:
        log(f"  conversations.open failed: {data.get('error')}")
        return
    ok, data = slack("chat.postMessage", tok, {"channel": data["channel"]["id"], "text": "credential-watch — " + text})
    if not ok:
        log(f"  chat.postMessage failed: {data.get('error')}")


# --- the tick --------------------------------------------------------------------------------

def hold_lock() -> bool:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if LOCK.exists():
        try:
            pid = int(LOCK.read_text().strip() or 0)
            os.kill(pid, 0)
            return False
        except (ValueError, ProcessLookupError):
            LOCK.unlink(missing_ok=True)
        except PermissionError:
            return False
    LOCK.write_text(str(os.getpid()))
    return True


def tick(dry_run: bool) -> int:
    if not hold_lock():
        log("a tick is already running")
        return 0
    try:
        return _tick(dry_run)
    finally:
        LOCK.unlink(missing_ok=True)


def _tick(dry_run: bool) -> int:
    state = read_state()
    try:
        readings = probe()
    except Unknown as exc:
        # A failed read covers nothing, so every WAITING clock restarts from the next good one.
        state.pop("waiting", None)
        state["last"] = {"at": now(), "unknown": str(exc)}
        write_state(state)
        log(f"UNKNOWN {exc}")
        return 2
    readings = confirm_dead(readings, state, now())
    state["last"] = {"at": now(), "readings": readings}
    write_state(state)

    todo = sorted((r for r in readings if r["verdict"] == "DEAD"), key=lambda r: r["slot"])
    if not todo:
        return 0
    for r in todo:
        log(f"{r['verdict']} slot {r['slot']} {r['email']} — {r['reason']}")

    # One ACT per tick, in series — that is how each run gets the global cswap account to
    # itself. A slot that cannot be acted on is passed over rather than ending the tick: two
    # accounts lose their logins in the same second often enough (measured 2026-09-22), and
    # one of them sitting in its 6 h cooldown must not hold the other dead all day.
    day = dt.date.today().isoformat()
    for r in todo:
        email = r["email"]
        if not email:
            if state.setdefault("backstop_told", {}).get(f"slot{r['slot']}") != day:
                state["backstop_told"][f"slot{r['slot']}"] = day
                write_state(state)
                notify(f"slot {r['slot']} is {r['verdict']} and cswap lists no email for it — not drivable, look by hand")
            continue
        wait, why = cooldown_left(state, email)
        if wait:
            if state.setdefault("backstop_told", {}).get(email) != day:
                state["backstop_told"][email] = day
                write_state(state)
                notify(f"{email} (slot {r['slot']}) is {r['verdict']} and the watcher has stopped: {why}. "
                       f"Run it by hand: python3 {OAUTH} --email {email}")
            continue
        if dry_run:
            log(f"dry run — would relogin {email} (slot {r['slot']})")
            return 0

        state.setdefault("attempts", {}).setdefault(email, []).append(now())
        write_state(state)
        log(f"relogin {email} (slot {r['slot']}) — the global cswap account moves for ~1 min")
        ok, why = relogin(email, r["slot"])
        if ok:
            # The slot number is freed and cswap re-uses it; the clock goes with it.
            state.setdefault("waiting", {}).pop(str(r["slot"]), None)
            write_state(state)
            notify(f"{email} re-logged in unattended: {why}. The old slot {r['slot']} is removed and the manifest stamped.")
            return 0
        if ok is None:
            notify(f"{email} (slot {r['slot']}): {why}. It asks again after 6 h, twice a day at most.")
            return 0
        notify(f"{email} (slot {r['slot']}) relogin FAILED: {why}. Log: {LOG}. "
               f"It retries after 6 h, twice a day at most; by hand: python3 {OAUTH} --email {email}")
        return 1
    return 1


def status() -> int:
    s = read_state()
    out = {"state": str(STATE), "log": str(LOG), "attempts": {k: [iso(x) for x in v] for k, v in s.get("attempts", {}).items()},
           "waiting": {k: {**v, "since": iso(v.get("since")), "last_seen": iso(v.get("last_seen"))}
                       for k, v in (s.get("waiting") or {}).items() if isinstance(v, dict)},
           "last": s.get("last")}
    if out["last"] and "at" in out["last"]:
        out["last"] = {**out["last"], "at": iso(out["last"]["at"])}
    print(json.dumps(out, indent=2))
    return 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["notify"] and len(argv) == 2:
        notify(argv[1])
        return 0
    if not argv or argv[0] not in ("tick", "status"):
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        print(__doc__.strip().splitlines()[3].strip(), file=sys.stderr)
        return 2
    if argv[0] == "status":
        return status()
    return tick("--dry-run" in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
