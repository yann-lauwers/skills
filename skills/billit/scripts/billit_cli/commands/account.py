from ..surface import new_command


def listed(features, wanted):
    return ", ".join(sorted(name for name, on in features.items() if bool(on) is wanted)) or "none"


def whoami(ns, app, out):
    info = app.get("/v1/account/accountInformation")
    if ns.json:
        out.dump(info)
        return 0
    for company in info.get("Companies") or []:
        features = company.get("APIEnabledFeatures") or {}
        out.say("company: %s" % company.get("Name"))
        out.say("party id: %s" % company.get("PartyID"))
        out.say("enabled features: %s" % listed(features, True))
        out.say("disabled features: %s" % listed(features, False))
    return 0


def register(commands):
    sub = new_command(
        commands, "whoami", "Prove the API key and show the account.",
        "Reads the account information Billit holds for the resolved entity's key and prints, for each company, its "
        "name, its party id and the API features it has enabled and disabled. A refused key exits 4.",
        example="  billit whoami")
    sub.set_defaults(handler=whoami)
