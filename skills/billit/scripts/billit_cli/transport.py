import http.cookiejar
import urllib.error
import urllib.request

from .errors import FAILED, Fail

TIMEOUT = 90


class Transport:
    def request(self, method, url, headers, body):
        raise NotImplementedError


class Urllib(Transport):
    def __init__(self):
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))

    def request(self, method, url, headers, body):
        req = urllib.request.Request(url, data=body, method=method, headers=headers)
        try:
            with self.opener.open(req, timeout=TIMEOUT) as response:
                return response.status, lowered(response.headers), response.read()
        except urllib.error.HTTPError as error:
            return error.code, lowered(error.headers), error.read()
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise Fail(FAILED, "network failure on %s %s: %s" % (method, url.split("?")[0], error))


def lowered(headers):
    return {k.lower(): v for k, v in headers.items()}
