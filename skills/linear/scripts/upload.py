#!/usr/bin/env python3
import argparse
import json
import mimetypes
import os
import subprocess
import tempfile

QUERY = ("mutation($c:String!,$f:String!,$s:Int!){ fileUpload(contentType:$c, filename:$f, size:$s)"
         "{ success uploadFile { uploadUrl assetUrl headers { key value } } } }")


def upload(path):
    ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
    body = {"query": QUERY, "variables": {"c": ctype, "f": os.path.basename(path), "s": os.path.getsize(path)}}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(body, f)
    try:
        out = subprocess.run(
            ["curl", "-s", "-X", "POST",
             "https://api.linear.app/graphql", "-H", "Content-Type: application/json",
             "--variable", "%LINEAR_API_KEY=", "--expand-header", "Authorization: {{LINEAR_API_KEY}}",
             "--data", "@" + f.name],
            capture_output=True, text=True).stdout
    finally:
        os.unlink(f.name)
    up = json.loads(out)["data"]["fileUpload"]["uploadFile"]
    args = ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-X", "PUT", up["uploadUrl"],
            "-H", "Content-Type: " + ctype, "-H", "Cache-Control: public, max-age=31536000"]
    for h in up["headers"]:
        args += ["-H", f"{h['key']}: {h['value']}"]
    args += ["--data-binary", "@" + path]
    code = subprocess.run(args, capture_output=True, text=True).stdout
    if code != "200":
        raise SystemExit(f"{path}: the storage PUT answered {code}")
    return up["assetUrl"]


def main():
    p = argparse.ArgumentParser(description="Upload files to Linear; prints '<file>\\t<assetUrl>' per file.")
    p.add_argument("files", nargs="+")
    a = p.parse_args()
    for path in a.files:
        print(f"{path}\t{upload(path)}", flush=True)


if __name__ == "__main__":
    main()
