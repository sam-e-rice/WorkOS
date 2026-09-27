#!/usr/bin/env python3
"""Upload an approved item's own CV to a Notion file-upload URL. Nothing else, nowhere else."""
import argparse
import json
import mimetypes
import sys
import urllib.request
import uuid
from pathlib import Path

import statelib as sl

NOTION_PREFIX = "https://api.notion.com/"
DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _body(path: Path, filename: str, ctype: str, boundary: str) -> bytes:
    head = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            f"Content-Type: {ctype}\r\n\r\n").encode()
    return head + path.read_bytes() + f"\r\n--{boundary}--\r\n".encode()


def upload(key: str, url: str, headers: dict, opener=urllib.request.urlopen) -> dict:
    if not url.startswith(NOTION_PREFIX):
        raise sl.StateError("upload URL must be a Notion API URL")
    data = sl.load()
    doc_id = sl.resolve_key(data, key)
    item = data["items"][doc_id]
    if item["status"] != "drafting" or not item.get("approved_by"):
        raise sl.StateError(f"{doc_id}: CV upload is only for an approved draft")
    if not item.get("cv_path"):
        raise sl.StateError(f"{doc_id}: no CV file recorded")
    path = sl.check_cv_path(item["cv_path"])
    if not path.is_file():
        raise sl.StateError(f"{doc_id}: no CV file recorded")
    suffix = path.suffix.lower()
    ctype = DOCX if suffix == ".docx" else (mimetypes.guess_type(path.name)[0] or "application/pdf")
    filename = f"{item.get('candidate') or 'Candidate'} CV{suffix}"
    boundary = uuid.uuid4().hex
    req = urllib.request.Request(url, data=_body(path, filename, ctype, boundary), method="POST")
    for k, v in headers.items():
        req.add_header(k, v)
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    with opener(req, timeout=60) as r:
        body = json.loads(r.read().decode() or "{}")
        status = r.status
    return {"status": status, "suggested_markdown": body.get("suggested_markdown"),
            "markdown_source": body.get("markdown_source"), "file_upload_id": body.get("file_upload_id"),
            "content_type": ctype, "filename": filename}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="notion_upload.py")
    p.add_argument("key")
    p.add_argument("--url", required=True)
    p.add_argument("--headers", default="{}")
    args = p.parse_args(argv)
    try:
        print(json.dumps(upload(args.key, args.url, json.loads(args.headers))))
    except sl.StateError as e:
        print(str(e), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
