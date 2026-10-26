import hashlib
import json


class Out:
    def __init__(self, stdout, stderr, as_json):
        self.stdout = stdout
        self.stderr = stderr
        self.as_json = as_json

    def say(self, text=""):
        self.stdout.write(text + "\n")

    def note(self, text):
        self.stderr.write(text + "\n")

    def dump(self, obj):
        self.say(json.dumps(obj, ensure_ascii=False, indent=2))

    def table(self, headers, rows):
        cells = [[str(c) for c in headers]] + [["" if c is None else str(c) for c in row] for row in rows]
        widths = [max(len(row[i]) for row in cells) for i in range(len(headers))]
        for row in cells:
            self.say("  ".join(c.ljust(w) for c, w in zip(row, widths)).rstrip())


def money(value):
    return "%.2f" % float(value or 0)


def day(value):
    return (value or "")[:10]


def trim(text, width=60):
    flat = " ".join((text or "").split())
    return flat if len(flat) <= width else flat[: width - 1] + "…"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def file_marker(raw):
    return "<%d bytes sha256:%s>" % (len(raw), digest(raw))
