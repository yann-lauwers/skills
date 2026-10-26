import re
from datetime import date

from .errors import DISAGREES, NOT_FOUND, USAGE, Fail


def parse_hours(text):
    clock = re.fullmatch(r"(\d{1,2}):(\d{2})", text)
    try:
        hours = int(clock.group(1)) + int(clock.group(2)) / 60 if clock else float(text)
    except ValueError:
        raise Fail(USAGE, "hours must be a number or H:MM, got %r" % text)
    if not 0 < hours <= 24:
        raise Fail(USAGE, "hours must be above 0 and at most 24, got %r" % text)
    return int(round(hours * 3600))


def parse_day(text):
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError:
        raise Fail(USAGE, "expected a date as YYYY-MM-DD, got %r" % text)


def parse_entry(text):
    day, sep, hours = text.partition("=")
    if not sep:
        raise Fail(USAGE, "expected DATE=HOURS, got %r" % text)
    return parse_day(day), parse_hours(hours)


def add_one(app, project, description, day, seconds):
    body = {"ProjectID": project, "Date": day, "Duration": seconds, "Billable": True}
    if description:
        body["Description"] = description
    data = app.write("POST", "/v1/timeregistrations", body)
    if app.dry_run:
        return "%s: previewed; nothing sent" % day
    if isinstance(data, dict):
        data = data.get("TimeRegistrationID")
    if not isinstance(data, int) or isinstance(data, bool):
        raise Fail(DISAGREES, "Billit named no registration id")
    back = app.get("/v1/timeregistrations/%d" % data)
    problems = []
    if back.get("ProjectID") != project:
        problems.append("ProjectID %s" % back.get("ProjectID"))
    if (back.get("Date") or "")[:10] != day:
        problems.append("Date %s" % back.get("Date"))
    if back.get("Duration") != seconds:
        problems.append("Duration %s" % back.get("Duration"))
    if description and back.get("Description") != description:
        problems.append("Description %r" % back.get("Description"))
    if problems:
        raise Fail(DISAGREES, "registration %d reads back with %s" % (data, ", ".join(problems)))
    return "%s: %d verified" % (day, data)


def delete_one(app, entry_id):
    app.get("/v1/timeregistrations/%d" % entry_id)
    app.write("DELETE", "/v1/timeregistrations/%d" % entry_id)
    if app.dry_run:
        return "%d: deletion previewed; nothing sent" % entry_id
    try:
        app.get("/v1/timeregistrations/%d" % entry_id)
    except Fail as fail:
        if fail.code == NOT_FOUND:
            return "%d: deleted, verified gone" % entry_id
        raise
    raise Fail(DISAGREES, "still reads back after the delete")
