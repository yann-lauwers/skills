from .. import pages, timeentries
from ..batch import each
from ..errors import USAGE, Fail
from ..surface import day_arg, group, new_command


def portal_day(text):
    return "%s/%s/%s" % (text[8:10], text[5:7], text[0:4]) if text else ""


def hours(seconds):
    return "%02d:%02d" % (seconds // 3600, seconds % 3600 // 60)


def entries(app, ns):
    found, page = [], 0
    while True:
        params = ["F.DateFrom=%s" % portal_day(ns.date_from), "F.DateTill=%s" % portal_day(ns.date_to),
                  "F.ProjectID=%s" % (ns.project if ns.project is not None else ""), "F.CurrentPage=%d" % page]
        rows = pages.time_rows(app.portal_get("/TimeRegistration/TimeRegistrationEntriesList", params))
        found += rows
        if len(rows) < pages.TIME_PAGE:
            return found
        page += 1


def list_time(ns, app, out):
    if ns.date_from and ns.date_to and ns.date_from > ns.date_to:
        raise Fail(USAGE, "--from is after --to")
    found = entries(app, ns)
    if ns.json:
        out.dump(found)
    elif not found:
        out.say("No time registration matches.")
    else:
        out.table(["id", "date", "hours", "client", "project", "invoiced", "description"], [
            [r["TimeRegistrationID"], r["Date"], hours(r["DurationSeconds"]), r["Client"], r["Project"], r["Invoiced"],
             r["Description"]] for r in found])
    return 0


def add_time(ns, app, out):
    entries = [timeentries.parse_entry(text) for text in ns.entries]
    days = [d for d, _ in entries]
    if len(set(days)) != len(days):
        raise Fail(USAGE, "a date is given twice")
    lines, code = each(out, days, lambda day: timeentries.add_one(
        app, ns.project, ns.description, day, dict(entries)[day]))
    for line in lines:
        out.say(line)
    return code


def delete_time(ns, app, out):
    lines, code = each(out, ns.ids, lambda entry_id: timeentries.delete_one(app, entry_id))
    for line in lines:
        out.say(line)
    return code


def register(commands):
    _, sub = group(commands, "time", "List, add and delete time registrations.",
                   "Reads and writes the hours booked on projects. Pick a command below.")
    lst = new_command(
        sub, "list", "List time registrations from the portal.",
        "Reads the portal's time registration list page by page, twenty rows each, sending every filter on every "
        "request, and prints id, date, hours, client, project, invoiced state and description.",
        example="  billit time list --from 2026-09-01 --to 2026-09-30")
    lst.add_argument("--from", dest="date_from", type=day_arg, metavar="D", default=None,
                     help="Keep entries dated on or after D as YYYY-MM-DD (default: no lower bound).")
    lst.add_argument("--to", dest="date_to", type=day_arg, metavar="D", default=None,
                     help="Keep entries dated on or before D as YYYY-MM-DD (default: no upper bound).")
    lst.add_argument("--project", type=int, metavar="ID", default=None,
                     help="Keep entries of this project id (default: every project).")
    lst.set_defaults(handler=list_time)

    add = new_command(
        sub, "add", "Book hours on a project, one registration per day.",
        "Writes to Billit: posts one time registration per DATE=HOURS pair on the project, then reads each back by id "
        "and compares project, date and duration. Hours are a decimal or H:MM. --dry-run prints the requests and "
        "sends nothing. Running it twice books the hours twice.",
        example="  billit time add --project 35042 2026-09-30=7:30 2026-09-29=8 --dry-run", write=True)
    add.add_argument("--project", type=int, required=True, metavar="ID", help="Project id the hours are booked on (required).")
    add.add_argument("--description", metavar="T", default=None,
                     help="Description stored on every registration (default: none).")
    add.add_argument("entries", nargs="+", metavar="DATE=HOURS",
                     help="Day as YYYY-MM-DD, an equals sign and the hours, such as 2026-09-30=7:30 (required).")
    add.set_defaults(handler=add_time)

    delete = new_command(
        sub, "delete", "Delete time registrations.",
        "Writes to Billit: reads each registration, deletes it, then reads it again to confirm it is gone. A "
        "registration that cannot be read exits 3 and is not deleted. --dry-run prints the requests and sends nothing.",
        example="  billit time delete 607820 --dry-run", write=True)
    delete.add_argument("ids", nargs="+", type=int, metavar="ID", help="Registration ids to delete (required).")
    delete.set_defaults(handler=delete_time)
