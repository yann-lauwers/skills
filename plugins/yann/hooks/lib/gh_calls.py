_GH_VALUED = frozenset(("-R", "--repo", "--hostname"))


def gh_args(argv):
    if not argv or argv[0] != "gh":
        return None, []
    repo, rest, i = None, [], 1
    while i < len(argv):
        word = argv[i]
        if word in _GH_VALUED:
            if word != "--hostname" and i + 1 < len(argv):
                repo = argv[i + 1]
            i += 2
            continue
        if word.startswith("--repo="):
            repo = word.split("=", 1)[1]
        elif word.startswith("-R") and len(word) > 2:
            repo = word[2:]
        elif not word.startswith("-") or rest:
            rest.append(word)
        i += 1
    return repo, rest


_GH_API_VALUED = frozenset(("-X", "--method", "-f", "-F", "--field", "--raw-field",
                            "--input", "-H", "--header", "-q", "--jq", "-t",
                            "--template", "-p", "--preview", "--cache", "--hostname"))


_GH_API_BODY = frozenset(("-f", "-F", "--field", "--raw-field", "--input"))


def gh_api_request(rest):
    if not rest or rest[0] != "api":
        return None
    method, body, endpoint, i = None, False, None, 1
    while i < len(rest):
        word = rest[i]
        flag, _eq, inline = word.partition("=")
        if flag in _GH_API_VALUED and word.startswith("--") and _eq:
            if flag == "--method":
                method = inline
            body = body or flag in _GH_API_BODY
            i += 1
            continue
        if word in _GH_API_VALUED:
            if word in ("-X", "--method") and i + 1 < len(rest):
                method = rest[i + 1]
            body = body or word in _GH_API_BODY
            i += 2
            continue
        if word.startswith("-X") and len(word) > 2:
            method = word[2:]
        elif not word.startswith("-") and endpoint is None:
            endpoint = word
        i += 1
    if endpoint is None:
        return None
    method = (method or ("POST" if body else "GET")).upper()
    return method, endpoint
