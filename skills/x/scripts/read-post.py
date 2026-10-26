#!/usr/bin/env python3
"""Read a public post on X and print its JSON. Takes a post URL or a bare post id.

No credential is involved: X serves this to its own embed widgets.

The endpoint requires a non-empty `token` query parameter and does not check its value.
Measured 2026-08-25 on a live id, reading bodies rather than status codes, which all read
200: a token absent or empty answers `{}`; any non-empty token — including `garbage` —
answers the post. The value below is derived from the id the way X's own widget does,
approximately: `((id / 1e15) * pi)` rendered in base 36. It is NOT byte-identical to
JavaScript's `Number.toString(36)`, which emits the shortest round-tripping form and rounds
its last digit where this emits twenty fixed fractional digits. That difference costs
nothing while the value goes unchecked, and a faithful shape is the better bet if it stops
being unchecked.

Exit codes: 0 answered · 2 the argument names no post · 3 the endpoint has no such post
            · 4 the endpoint answered a payload that is not a post
            · 5 the endpoint could not be reached, answered unreadably, or answered the
              empty object that means the token was not accepted
"""
import json
import re
import sys
import urllib.error
import urllib.request

ENDPOINT = "https://cdn.syndication.twimg.com/tweet-result"
DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"


def base36(x):
    """Render a float in base 36. Approximates JS Number.toString(36); see the module docstring."""
    whole, frac = int(x), x - int(x)
    head = "" if whole else "0"
    while whole:
        head = DIGITS[whole % 36] + head
        whole //= 36
    tail = ""
    for _ in range(20):
        frac *= 36
        digit = int(frac)
        tail += DIGITS[digit]
        frac -= digit
    return head + "." + tail


def token(pid):
    """Derive the endpoint's token. Empty is not a token — the endpoint reads it as absent."""
    derived = re.sub(r"(0+|\.)", "", base36((int(pid) / 1e15) * 3.141592653589793))
    return derived or "1"


# A snowflake id is 18-19 digits. The bound keeps a mangled paste out of int(), whose result
# feeds a float division that overflows past ~309 digits.
ID_RE = re.compile(r"^[0-9]{1,25}$")


def post_id(arg):
    r"""Accept a status URL or a bare id; return the id, or None if the argument names no post.

    Both paths go through ID_RE rather than `\d` or `isdigit()`: those accept non-ASCII
    digits, which int() and the URL encoder then reject with a traceback.
    """
    m = re.search(r"/status/([^/?#]+)", arg)
    candidate = m.group(1) if m else arg.strip().split("?", 1)[0]
    return candidate if ID_RE.match(candidate) else None


def fetch(pid):
    url = f"{ENDPOINT}?id={pid}&token={token(pid)}&lang=en"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


def die(code, message):
    print(message, file=sys.stderr)
    sys.exit(code)


def main():
    if len(sys.argv) != 2:
        die(2, "usage: read-post.py <post-url-or-id>")
    pid = post_id(sys.argv[1])
    if pid is None:
        die(2, f"not a post: {sys.argv[1]!r} — pass a post id, or an x.com URL "
               "containing /status/<id>")
    try:
        data = fetch(pid)
    except urllib.error.HTTPError as err:
        if err.code == 404:
            die(3, f"no such post: {pid} — deleted, or the account is protected")
        die(5, f"the endpoint answered {err.code}")
    except (urllib.error.URLError, TimeoutError) as err:
        die(5, f"could not reach the endpoint: {err}")
    except ValueError:  # JSONDecodeError and UnicodeDecodeError both land here
        die(5, "the endpoint answered a 200 that is not readable JSON — a challenge or an "
               "interstitial page, not a post")
    except OSError as err:
        die(5, f"the connection broke while reading the answer: {err}")
    if not isinstance(data, dict):
        die(5, f"the endpoint answered a JSON {type(data).__name__}, not an object")
    if not data:
        die(5, "the endpoint answered an empty object — the token this call sends was "
               "rejected, so the derivation needs revisiting")
    if data.get("__typename") != "Tweet":
        die(4, f"the endpoint answered a {data.get('__typename')!r} rather than a post; "
               "an unavailable post arrives this way rather than as a 404")
    json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
