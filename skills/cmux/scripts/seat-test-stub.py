"""A stateful stand-in for the cmux CLI, enough of it for seat.sh and self-close.sh to run against."""
import json
import os
import sys

T = os.environ["T"]
st = json.load(open(f"{T}/state.json"))
a = sys.argv[1:]


def save():
    json.dump(st, open(f"{T}/state.json", "w"))


open(f"{T}/calls.log", "a").write(" ".join(a) + "\n")

if a[:3] == ["workspace-group", "list", "--json"]:
    print(json.dumps({"groups": st["groups"]}))
elif a[:3] == ["workspace", "list", "--json"]:
    print(json.dumps({"workspaces": st["workspaces"]}))
elif a[:2] == ["workspace-group", "create"]:
    name, cwd = a[a.index("--name") + 1], a[a.index("--cwd") + 1]
    ref = f"workspace_group:{90 + len(st['groups'])}"
    anchor = f"workspace:{700 + len(st['workspaces'])}"
    st["workspaces"].append({"ref": anchor, "current_directory": cwd, "custom_color": None})
    st["groups"].append({"ref": ref, "name": name, "custom_color": None,
                         "anchor_workspace_ref": anchor, "member_workspace_refs": [anchor]})
    save()
    print("OK " + ref)
elif a[:2] == ["workspace-group", "set-color"]:
    for g in st["groups"]:
        if g["ref"] == a[2]:
            g["custom_color"] = a[a.index("--hex") + 1]
    save()
    print("OK")
elif a[:2] == ["workspace", "create"]:
    ref = f"workspace:{800 + len(st['workspaces'])}"
    st["workspaces"].append({"ref": ref, "current_directory": a[a.index("--cwd") + 1],
                             "custom_color": None,
                             "title": a[a.index("--name") + 1] if "--name" in a else None})
    if "--group" in a:
        for g in st["groups"]:
            if g["ref"] == a[a.index("--group") + 1]:
                g["member_workspace_refs"].append(ref)
    save()
    print("OK " + ref)
elif a[:2] == ["workspace", "close"]:
    # `close-noop` beside the state file is the forced failure: the close returns 0 and
    # removes nothing, which is what self-close.sh's two confirming reads exist to catch.
    ref = a[a.index("--workspace") + 1] if "--workspace" in a else a[2]
    if "--force" not in a:
        print("Error: confirmation_required: Workspace has a running process; retry with --force", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(f"{T}/close-noop"):
        st["workspaces"] = [w for w in st["workspaces"] if w["ref"] != ref]
        save()
    print("OK")
elif a[:1] == ["workspace-action"]:
    for w in st["workspaces"]:
        if w["ref"] == a[a.index("--workspace") + 1]:
            w["custom_color"] = a[a.index("--color") + 1]
    save()
    print("OK")
