import os

from ..batch import each
from ..errors import FAILED, PRECONDITION, Fail
from ..pages import embedded_documents
from ..surface import group, new_command

UBL_MIME = "text/xml"


def safe_name(name):
    base = os.path.basename(name or "")
    if base in ("", ".", ".."):
        raise Fail(FAILED, "Billit returned an unusable file name %r" % name)
    return base


def save(app, file_id, directory):
    name, mime, raw = app.file(file_id)
    outputs = [(safe_name(name), raw)]
    if mime == UBL_MIME:
        outputs += [(safe_name(n), b) for n, b in embedded_documents(raw)]
    names = [n for n, _ in outputs]
    if len(set(names)) != len(names):
        raise Fail(PRECONDITION, "file %s would save two files named alike" % file_id)
    os.makedirs(directory, exist_ok=True)
    paths = []
    for fname, content in outputs:
        path = os.path.join(directory, fname)
        with open(path, "wb") as handle:
            handle.write(content)
        paths.append(path)
    return {"FileID": file_id, "paths": paths}


def get_files(ns, app, out):
    saved, code = each(out, ns.ids, lambda file_id: save(app, file_id, ns.out))
    if ns.json:
        out.dump(saved)
    else:
        for entry in saved:
            for path in entry["paths"]:
                out.say(path)
    return code


def register(commands):
    _, sub = group(commands, "files", "Download files held by Billit.",
                   "Downloads documents Billit holds, such as order PDFs and queued uploads. Pick a command below.")
    get = new_command(
        sub, "get", "Download files into a directory.",
        "Fetches each file by id, decodes it and saves it under its own name in the output directory, then prints "
        "the paths. A Peppol UBL (text/xml) also has every embedded document saved beside it under its own name.",
        example="  billit files get 9c2a0cd3-00f6-4f0a-816c-01a0ca8be282 --out ./files")
    get.add_argument("ids", nargs="+", metavar="FILEID", help="File ids to download (required).")
    get.add_argument("--out", metavar="DIR", required=True, help="Directory the files are saved in (required).")
    get.set_defaults(handler=get_files)
