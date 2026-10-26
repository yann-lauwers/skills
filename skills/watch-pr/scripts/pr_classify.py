"""The verdict over one reading of a pull request: pure, no I/O.

`classify(facts)` takes the facts `pr_reads.Reader.read` returns and answers the verdict,
its reason and the measured fields. The order of the rules is the contract
(references/green-detection.md).
"""
from __future__ import annotations

import re
from datetime import datetime, timezone

BOT_TOKENS = re.compile(r"cursor|coderabbit|bugbot", re.IGNORECASE)
NON_REVIEW_BOT_JOBS = re.compile(r"autofix", re.IGNORECASE)
CI_APP_SLUGS = {"github-actions"}
CI_OK_CONCLUSIONS = {"success", "neutral", "skipped"}


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_iso(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def _run_order(cr: dict) -> tuple[int, datetime]:
    """Creation order of a check run: its check suite id (monotonic, assigned at creation),
    then started_at. started_at alone misorders a burst: a run cancelled by a concurrency
    group can sit queued and *start* after the sibling that superseded it."""
    suite_id = int(((cr.get("check_suite") or {}).get("id")) or 0)
    started = parse_iso(cr.get("started_at")) or datetime.min.replace(tzinfo=timezone.utc)
    return suite_id, started


def dedupe_check_runs(runs: list[dict]) -> list[dict]:
    """Keep the most recently created run per (app slug, name); an earlier run, cancelled or
    not, is superseded by it. A cancelled run that is the newest for its name still fails."""
    latest: dict[tuple[str, str], dict] = {}
    for cr in runs:
        key = (((cr.get("app") or {}).get("slug")) or "", cr.get("name") or "")
        prev = latest.get(key)
        if prev is None or _run_order(cr) >= _run_order(prev):
            latest[key] = cr
    return list(latest.values())


def pending_seconds(cr: dict) -> float:
    started = parse_iso(cr.get("started_at"))
    return 0.0 if started is None else (now_utc() - started).total_seconds()


def classify(facts: dict) -> dict:
    """Facts: `pull`, `check_runs`, `threads` (reviews, comments, threads), `head_age`,
    `reviewable_age`, `scm`, `integration_base`, `fresh_window`, `bot_pending_timeout`."""
    pull = facts["pull"]
    threads = facts["threads"]
    head_age = facts.get("head_age")
    reviewable_age = facts.get("reviewable_age")
    scm = facts.get("scm")
    integration_base = facts.get("integration_base", "unknown")
    fresh_window = facts["fresh_window"]
    bot_pending_timeout = facts["bot_pending_timeout"]
    head = pull["head"]["sha"]
    runs = dedupe_check_runs(facts["check_runs"])

    bot_pending = bot_completed = False
    stalled: list[str] = []
    for cr in runs:
        slug = ((cr.get("app") or {}).get("slug")) or ""
        name = cr.get("name") or ""
        if not (BOT_TOKENS.search(slug) or BOT_TOKENS.search(name)) or NON_REVIEW_BOT_JOBS.search(name):
            continue
        if cr.get("status") in ("queued", "in_progress"):
            if pending_seconds(cr) > bot_pending_timeout:
                stalled.append(name)
            else:
                bot_pending = True
        elif cr.get("status") == "completed":
            bot_completed = True

    def login(n):
        return ((n or {}).get("author") or {}).get("login") or ""

    bot_review_on_head = any(BOT_TOKENS.search(login(r)) and ((r.get("commit") or {}).get("oid") == head)
                             for r in threads["reviews"])
    participates = bot_completed or bot_pending or bot_review_on_head or any(
        BOT_TOKENS.search(login(x)) for x in threads["reviews"] + threads["comments"])
    bot_done = bot_completed or bot_review_on_head

    ci_pending = ci_failed = False
    ci_seen = 0
    for cr in runs:
        if (((cr.get("app") or {}).get("slug")) or "") not in CI_APP_SLUGS:
            continue
        ci_seen += 1
        if cr.get("status") != "completed":
            ci_pending = True
        elif cr.get("conclusion") not in CI_OK_CONCLUSIONS:
            ci_failed = True
    ci = ("failed" if ci_failed else "pending" if ci_pending
          else "green" if ci_seen else "none")

    unresolved = sum(
        1 for t in threads["threads"]
        if not t.get("isResolved")
        and BOT_TOKENS.search(login((((t.get("comments") or {}).get("nodes") or [None])[0])))
    )

    window_age = reviewable_age if reviewable_age is not None else head_age
    fresh = window_age is not None and window_age < fresh_window
    mstate = (pull.get("mergeable_state") or "unknown").upper()
    scm_conflicted = (scm or {}).get("conflicted")
    conflicted = (scm_conflicted if scm_conflicted is not None
                  else pull.get("mergeable") is False or mstate == "DIRTY")
    conflict_source = "git" if scm_conflicted is not None else "forge"
    behind_by = (scm or {}).get("behind_by", 0)
    base_changed_files = (scm or {}).get("base_changed_files", 0)
    base_advanced = bool(scm) and integration_base is True and base_changed_files > 0

    if pull.get("merged"):
        verdict, reason = "MERGED", f"merged by {(pull.get('merged_by') or {}).get('login')} into {pull['base']['ref']}"
    elif pull.get("state") == "closed":
        verdict, reason = "CLOSED", "closed without merge"
    elif pull.get("draft"):
        verdict, reason = "DRAFT", "draft: checks report skipped, nothing is measured"
    elif conflicted:
        verdict, reason = "CONFLICT", (
            f"a trial merge of {head[:10]} with {str((scm or {}).get('base_tip_sha'))[:10]} conflicts"
            if conflict_source == "git"
            else f"mergeable={pull.get('mergeable')} mergeable_state={mstate.lower()}")
    elif bot_pending:
        verdict, reason = "WAITING", "review bot check pending on HEAD"
    elif participates and not bot_done and fresh:
        verdict, reason = "WAITING", f"reviewable for {round(window_age)}s, bots have not registered yet"
    elif unresolved > 0:
        verdict, reason = "NEW_COMMENTS", f"{unresolved} unresolved bot thread(s)"
    elif ci == "failed":
        verdict, reason = "CI_RED", "a CI check on HEAD failed"
    elif ci == "pending":
        verdict, reason = "WAITING", "CI still running"
    elif ci == "none" and fresh:
        verdict, reason = "WAITING", "no CI check has registered on HEAD yet"
    elif ci == "none":
        verdict, reason = "CLEAN", "bots done, no unresolved threads, no CI runs on this base"
    else:
        verdict, reason = "CLEAN", "bots done, no unresolved threads, CI green"

    if verdict == "CLEAN" and base_advanced:
        verdict = "BASE_ADVANCED"
        reason = (f"{pull['base']['ref']} carries {behind_by} commit(s) and "
                  f"{base_changed_files} changed file(s) this head lacks")

    return {
        "verdict": verdict, "reason": reason, "head_sha": head, "ci": ci,
        "unresolved_bot_threads": unresolved, "merge_state_status": mstate,
        "conflict_source": conflict_source, "integration_base": integration_base,
        "base_tip_sha": (scm or {}).get("base_tip_sha"),
        "behind_by": behind_by, "base_changed_files": base_changed_files,
        "bots": {"participates": participates, "pending_on_head": bot_pending,
                 "done_on_head": bot_done, "stalled_checks": stalled},
        "head_age_seconds": None if head_age is None else round(head_age),
        "reviewable_age_seconds": None if window_age is None else round(window_age),
    }
