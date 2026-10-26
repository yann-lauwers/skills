import base64
import json
import urllib.parse

from .errors import AUTH, FAILED, NOT_FOUND, USAGE, Fail, WriteRefused
from .render import file_marker

API = "https://api.billit.be"
PORTAL = "https://my.billit.be"
PAGE = 120
LOGIN_MARKER = "login-form-input-password"
JSON_HEADERS = {"Accept": "application/json"}
FORM = "application/x-www-form-urlencoded"


def parse(raw):
    if not raw or not raw.strip():
        return None
    try:
        return json.loads(raw)
    except ValueError:
        return raw.decode("utf-8", "replace")


def message_of(data):
    if isinstance(data, dict):
        for key in ("Message", "message", "ErrorMessage", "error"):
            if isinstance(data.get(key), str):
                return data[key]
    return ""


def on_host(base, path):
    url = base + path
    if not path.startswith("/") or path.startswith("//") or urllib.parse.urlsplit(url).netloc != urllib.parse.urlsplit(base).netloc:
        raise Fail(USAGE, "path %r must start with a single / and stay on %s" % (path, base))
    return url


def with_params(path, params):
    pairs = [p for p in (params or []) if p]
    if not pairs:
        return path
    return path + ("&" if "?" in path else "?") + "&".join(pairs)


def query(**fields):
    return [("%s=%s" % (k, urllib.parse.quote(str(v), safe=""))) for k, v in fields.items() if v is not None]


def items_of(data):
    if isinstance(data, dict):
        return data.get("Items") or []
    return data or []


def mask_files(value):
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if k == "FileContent" and isinstance(v, str):
                try:
                    out[k] = file_marker(base64.b64decode(v))
                except ValueError:
                    out[k] = v
            else:
                out[k] = mask_files(v)
        return out
    if isinstance(value, list):
        return [mask_files(v) for v in value]
    return value


class Billit:
    def __init__(self, rt, ctx, key, out, dry_run=False):
        self.rt = rt
        self.ctx = ctx
        self.key = key
        self.out = out
        self.dry_run = dry_run
        self.session = False

    def send(self, method, url, headers, body):
        return self.rt.transport.request(method, url, headers, body)

    def api_raw(self, method, path, body=None):
        headers = dict(JSON_HEADERS, apiKey=self.key)
        payload = None
        if body is not None:
            payload = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        status, _, raw = self.send(method, on_host(API, path), headers, payload)
        return status, parse(raw)

    def unauthorized(self, path):
        if path.split("?")[0].endswith("/v1/account/accountInformation") or "/ssoToken" in path:
            raise Fail(AUTH, "Billit refused the API key for %s" % path.split("?")[0])
        status, _ = self.api_raw("GET", "/v1/account/accountInformation")
        if status == 200:
            raise Fail(NOT_FOUND, "Billit answered 401 for %s while the key works: the id names nothing" % path.split("?")[0])
        raise Fail(AUTH, "Billit refused the API key")

    def get(self, path, params=None):
        full = with_params(path, params)
        status, data = self.api_raw("GET", full)
        if status == 401:
            self.unauthorized(full)
        if status == 404:
            raise Fail(NOT_FOUND, "%s not found" % path.split("?")[0])
        if status >= 400:
            raise Fail(FAILED, "GET %s answered %d %s" % (path.split("?")[0], status, message_of(data)))
        return data

    def pages(self, path, params=None):
        skip = 0
        while True:
            page = items_of(self.get(path, list(params or []) + ["$top=%d" % PAGE, "$skip=%d" % skip]))
            yield from page
            if len(page) < PAGE:
                return
            skip += PAGE

    def all(self, path, params=None):
        return list(self.pages(path, params))

    def announce(self, method, url, body=None, form=None):
        self.out.say("%s %s" % (method, url))
        if body is not None:
            self.out.say(json.dumps(mask_files(body), ensure_ascii=False, indent=2))
        if form is not None:
            self.out.say(urllib.parse.urlencode(form))

    def write(self, method, path, body=None):
        if self.dry_run:
            self.announce(method, on_host(API, path), body=body)
            return None
        status, data = self.api_raw(method, path, body)
        if status == 401:
            self.unauthorized(path)
        if status == 404:
            raise Fail(NOT_FOUND, "%s not found" % path)
        if status == 400:
            raise WriteRefused(400, "Billit refused the payload: %s" % (message_of(data) or "no message"))
        if status >= 500:
            raise WriteRefused(status, "Billit answered %d on %s %s" % (status, method, path))
        if status >= 400:
            raise Fail(FAILED, "%s %s answered %d %s" % (method, path, status, message_of(data)))
        return data

    def file(self, file_id):
        data = self.get("/v1/files/%s" % file_id)
        raw = base64.b64decode(data.get("FileContent") or "")
        return data.get("FileName"), data.get("MimeType"), raw

    def ensure_session(self):
        if self.session:
            return
        token = (self.get("/v1/account/ssoToken") or {}).get("ssoToken")
        if not token:
            raise Fail(AUTH, "Billit returned no SSO token")
        body = urllib.parse.urlencode({"ssoToken": token}).encode()
        self.send("POST", on_host(PORTAL, "/Account/LogOn"), {"Content-Type": FORM}, body)
        status, _, raw = self.send("GET", on_host(PORTAL, "/TimeRegistration/Index"), {}, None)
        if status != 200 or LOGIN_MARKER in raw.decode("utf-8", "replace"):
            raise Fail(AUTH, "no portal session after the SSO logon")
        self.session = True

    def portal_get(self, path, params=None):
        self.ensure_session()
        status, _, raw = self.send("GET", on_host(PORTAL, with_params(path, params)), {}, None)
        text = raw.decode("utf-8", "replace")
        if status == 404:
            raise Fail(NOT_FOUND, "portal %s not found" % path.split("?")[0])
        if status >= 400 or LOGIN_MARKER in text:
            raise Fail(FAILED, "portal GET %s answered %d" % (path.split("?")[0], status))
        return text

    def portal_read(self, path, fields=()):
        self.ensure_session()
        body = urllib.parse.urlencode(list(fields)).encode()
        status, _, raw = self.send("POST", on_host(PORTAL, path), {"Content-Type": FORM}, body)
        text = raw.decode("utf-8", "replace")
        if status >= 400 or LOGIN_MARKER in text:
            raise Fail(FAILED, "portal read %s answered %d" % (path, status))
        return text

    def portal_post(self, path, fields, headers=None):
        pairs = list(fields)
        if self.dry_run:
            self.announce("POST", on_host(PORTAL, path), form=pairs)
            return None
        self.ensure_session()
        head = {"Content-Type": FORM}
        head.update(headers or {})
        status, _, raw = self.send("POST", on_host(PORTAL, path), head, urllib.parse.urlencode(pairs).encode())
        text = raw.decode("utf-8", "replace")
        if status >= 400 or LOGIN_MARKER in text:
            raise Fail(FAILED, "portal POST %s answered %d" % (path, status))
        return text
