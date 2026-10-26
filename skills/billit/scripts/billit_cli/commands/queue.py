from .. import clearing, pages
from ..batch import each
from ..surface import group, new_command


def queued_files(app):
    seen = {}
    for entry in app.get("/v1/toProcess") or []:
        if isinstance(entry, dict) and entry.get("FileID") and entry["FileID"] not in seen:
            seen[entry["FileID"]] = bool(entry.get("Invalid"))
    return [{"FileID": fid, "FileName": app.file(fid)[0], "Invalid": invalid} for fid, invalid in seen.items()]


def grid_count(app):
    return len(pages.grid_tiles(app.portal_read("/BulkInput/BulkInputList")))


def list_queue(ns, app, out):
    files = queued_files(app)
    tiles = grid_count(app)
    if ns.json:
        out.dump({"files": files, "gridCount": tiles})
    elif not files and not tiles:
        out.say("The quick-entry queue is empty.")
    else:
        out.table(["file id", "file name", "invalid"], [[f["FileID"], f["FileName"], f["Invalid"]] for f in files])
        out.say("quick-entry grid: %d documents" % tiles)
    return 0


def clear_queue(ns, app, out):
    lines, code = each(out, ns.pairs, lambda pair: clearing.clear_pair(app, pair))
    for line in lines:
        out.say(line)
    return code


def register(commands):
    _, sub = group(commands, "queue", "List and clear the quick-entry queue.",
                   "Reads and clears the documents waiting in quick entry. Pick a command below.")
    lst = new_command(
        sub, "list", "List the documents waiting in quick entry.",
        "Reads the quick-entry queue from the API and from the portal grid, and prints each queued file with its "
        "name and whether Billit marked it invalid, then the portal grid's document count.",
        example="  billit queue list")
    lst.set_defaults(handler=list_queue)

    clear = new_command(
        sub, "clear", "Clear encoded documents out of quick entry.",
        "Writes to Billit through the portal: for each FILEID:ORDERID pair it proves that the queued file's bytes "
        "(length and sha256) equal the order's PDF or one of its attachments, deletes the matching quick-entry tile, "
        "and reads both surfaces and the order's file again. Bytes not proven exits 7 for that pair and deletes "
        "nothing. --dry-run does the proof and prints the delete it would post.",
        example="  billit queue clear 9c2a0cd3-00f6-4f0a-816c-01a0ca8be282:148812336 --dry-run", write=True)
    clear.add_argument("pairs", nargs="+", metavar="FILEID:ORDERID",
                       help="Queued file id and the order that must already carry its bytes (required).")
    clear.set_defaults(handler=clear_queue)
