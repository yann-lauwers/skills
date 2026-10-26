from . import pages
from .errors import DISAGREES, PRECONDITION, USAGE, Fail
from .render import digest

GRID = "/BulkInput/BulkInputList"
DELETE = "/BulkInput/DeleteBulkInput"


def parse_pair(text):
    file_id, sep, order_id = text.partition(":")
    if not sep or not file_id or not order_id.isdigit():
        raise Fail(USAGE, "expected FILEID:ORDERID, got %r" % text)
    return file_id, int(order_id)


def queued_ids(app):
    return {e.get("FileID") for e in app.get("/v1/toProcess") or [] if isinstance(e, dict)}


def fingerprint(app, file_id):
    name, _, raw = app.file(file_id)
    return name, len(raw), digest(raw)


def order_files(order):
    held = [order.get("OrderPDF") or {}] + list(order.get("Attachments") or [])
    return [f["FileID"] for f in held if f.get("FileID")]


def prove(app, file_id, order_id):
    name, length, sha = fingerprint(app, file_id)
    order = app.get("/v1/orders/%d" % order_id)
    files = order_files(order)
    if not files:
        raise Fail(PRECONDITION, "order %d carries no file; the queued bytes are unproven" % order_id)
    for held in files:
        _, other_length, other_sha = fingerprint(app, held)
        if (other_length, other_sha) == (length, sha):
            return name, length, sha, held
    raise Fail(PRECONDITION, "no file of order %d has the queued bytes (%d bytes, sha256 %s)" % (order_id, length, sha))


def tile_for(app, name):
    tiles = [t for t in pages.grid_tiles(app.portal_read(GRID)) if t["name"] == name]
    if not tiles:
        raise Fail(PRECONDITION, "the quick-entry grid shows no tile named %s" % name)
    if len(tiles) > 1:
        raise Fail(PRECONDITION, "the quick-entry grid shows %d tiles named %s" % (len(tiles), name))
    return tiles[0]


def clear_pair(app, text):
    file_id, order_id = parse_pair(text)
    if file_id not in queued_ids(app):
        return "%s: not in the queue, nothing to clear" % file_id
    name, length, sha, held = prove(app, file_id, order_id)
    tile = tile_for(app, name)
    sent = app.portal_post(DELETE, [("BulkInputListSelectedMergeIDs", tile["merge_id"])])
    proof = "%d bytes, sha256 %s" % (length, sha)
    if app.dry_run:
        return "%s: proven against order %d (%s); nothing deleted" % (file_id, order_id, proof)
    still_api = file_id in queued_ids(app)
    still_grid = any(t["name"] == name for t in pages.grid_tiles(app.portal_read(GRID)))
    if still_api or still_grid:
        raise Fail(DISAGREES, "still queued after the delete (api=%s, grid=%s, answer=%s)" % (
            still_api, still_grid, (sent or "").strip()[:20]))
    if fingerprint(app, held)[1:] != (length, sha):
        raise Fail(DISAGREES, "the file of order %d changed after the delete" % order_id)
    return "%s: cleared; order %d keeps the file (%s)" % (file_id, order_id, proof)
