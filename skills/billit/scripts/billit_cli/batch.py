from .errors import DISAGREES, Fail


def final_code(codes):
    if DISAGREES in codes:
        return DISAGREES
    for code in codes:
        if code:
            return code
    return 0


def each(out, items, action):
    results, codes = [], []
    for item in items:
        try:
            results.append(action(item))
        except Fail as fail:
            out.note("billit: %s: %s" % (item, fail.message))
            codes.append(fail.code)
    return results, final_code(codes)
