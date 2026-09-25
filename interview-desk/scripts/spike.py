#!/usr/bin/env python3
"""Throwaway helpers for the Plan C connector test run. Delete after the spike."""
import argparse
import json
import mimetypes
import os
import sys
import urllib.request
import uuid
from pathlib import Path

import statelib as sl


def record(key: str, value) -> None:
    p = sl.state_dir() / "spike.json"
    data = json.loads(p.read_text()) if p.exists() else {}
    data[key] = value
    sl.atomic_write(p, json.dumps(data, indent=2) + "\n")


def make_pdf(path: Path) -> None:
    from pypdf import PdfWriter
    w = PdfWriter()
    w.add_blank_page(width=200, height=200)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        w.write(f)


def upload(url: str, headers: dict, path: Path) -> dict:
    boundary = uuid.uuid4().hex
    ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{path.name}\"\r\n"
            f"Content-Type: {ctype}\r\n\r\n").encode() + path.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(url, data=body, method="POST")
    for k, v in headers.items():
        req.add_header(k, v)
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    with urllib.request.urlopen(req, timeout=60) as r:
        text = r.read().decode()
        return {"status": r.status, "body": json.loads(text) if text.startswith("{") else text}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="spike.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("env")
    r = sub.add_parser("record")
    r.add_argument("key")
    r.add_argument("json")
    sub.add_parser("make-pdf")
    u = sub.add_parser("upload")
    u.add_argument("--url", required=True)
    u.add_argument("--headers", default="{}")
    a = p.parse_args(argv)
    pdf = sl.root() / "state" / "spike" / "interview-desk-test.pdf"
    if a.cmd == "env":
        out = {"cwd": os.getcwd(), "desk_root": str(sl.root()),
               "CLAUDE_PROJECT_DIR": os.environ.get("CLAUDE_PROJECT_DIR"),
               "created_pages_exists": (sl.root() / "state" / "created_pages.json").exists()}
        record("env", out)
    elif a.cmd == "record":
        record(a.key, json.loads(a.json))
        out = {"recorded": a.key}
    elif a.cmd == "make-pdf":
        make_pdf(pdf)
        out = {"pdf": str(pdf)}
    else:
        out = upload(a.url, json.loads(a.headers), pdf)
        record("upload", out)
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
