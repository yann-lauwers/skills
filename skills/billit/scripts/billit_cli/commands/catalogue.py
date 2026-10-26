from .. import pages
from ..render import trim
from ..surface import group, new_command


def list_projects(ns, app, out):
    found = app.all("/v1/projects")
    if ns.json:
        out.dump(found)
    elif not found:
        out.say("The account has no project.")
    else:
        out.table(["id", "name", "customer", "start", "status"], [
            [p.get("ProjectID"), p.get("ProjectName"), p.get("CustomerName"), (p.get("StartDate") or "")[:10],
             p.get("Status")] for p in found])
    return 0


def list_categories(ns, app, out):
    html = app.portal_get("/Company/Supplier/%s/CompanyEdit" % app.ctx.party_id)
    found = pages.categories(html)
    if ns.json:
        out.dump(found)
    elif not found:
        out.say("The portal lists no cost category.")
    else:
        out.table(["code", "name", "specification"],
                  [[c["code"], trim(c["name"], 70), c["specification"]] for c in found])
    return 0


def register(commands):
    _, projects = group(commands, "projects", "List the account's projects.",
                        "Reads the projects time registrations are booked on. Pick a command below.")
    lst = new_command(projects, "list", "List projects.",
                      "Reads every project Billit lists and prints id, name, customer, start date and status.",
                      example="  billit projects list")
    lst.set_defaults(handler=list_projects)

    _, cats = group(commands, "categories", "List the portal's cost categories.",
                    "Reads the cost category catalogue Billit shows only in its portal. Pick a command below.")
    lst = new_command(cats, "list", "List cost categories.",
                      "Reads the entity's company page in the portal and prints each distinct cost category code with "
                      "its name and specification.",
                      example="  billit categories list --json")
    lst.set_defaults(handler=list_categories)
