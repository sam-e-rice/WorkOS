#!/usr/bin/env python3
"""Find the CV for a candidate in ~/Downloads/CVs: dedupe, extract text, match by email then name."""
import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

import statelib as sl
from textnorm import norm, tokens

SUFFIXES = {".pdf", ".docx"}


def extract_text(path: Path) -> str:
    try:
        if path.suffix.lower() == ".pdf":
            from pypdf import PdfReader
            return "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
        import docx
        d = docx.Document(str(path))
        parts = [p.text for p in d.paragraphs]
        for table in d.tables:
            for row in table.rows:
                parts += [c.text for c in row.cells]
        return "\n".join(parts)
    except Exception as e:  # unreadable CVs are treated as empty, not fatal
        print(f"warn: could not read {path.name}: {e}", file=sys.stderr)
        return ""


def _cache_file(digest: str) -> Path:
    return sl.root() / "state" / "cv_text" / "cache" / f"{digest}.txt"


def cached_text(path: Path, digest: str) -> str:
    f = _cache_file(digest)
    if not f.exists():
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(extract_text(path))
    return f.read_text()


def pool(cv_dir: Path, meeting_at: str, window_days: int) -> dict[str, Path]:
    """digest -> newest path, for CVs modified within the window."""
    center = sl.parse_iso(meeting_at).timestamp()
    newest: dict[str, Path] = {}
    for p in cv_dir.rglob("*"):
        if not (p.is_file() and p.suffix.lower() in SUFFIXES):
            continue
        if abs(p.stat().st_mtime - center) > window_days * 86400:
            continue
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        if digest not in newest or p.stat().st_mtime > newest[digest].stat().st_mtime:
            newest[digest] = p
    return newest


def match(cv_dir: Path, name: str | None, email: str | None, meeting_at: str,
          window_days: int = 30) -> dict:
    name_toks = [t for t in tokens(name or "") if len(t) >= 2]
    full = " ".join(name_toks)
    email_hits, name_hits = [], []
    for digest, path in sorted(pool(cv_dir, meeting_at, window_days).items(), key=lambda kv: str(kv[1])):
        text = cached_text(path, digest)
        if email and email.lower() in text.lower():
            email_hits.append((digest, path))
        elif len(name_toks) >= 2 and (set(name_toks) <= set(tokens(path.stem))
                                      or f" {full} " in f" {norm(text)} "):
            name_hits.append((digest, path))
    for hits in (email_hits, name_hits):
        if len(hits) == 1:
            return {"match": str(hits[0][1]), "digest": hits[0][0]}
        if len(hits) > 1:
            return {"ambiguous": [str(p) for _, p in hits]}
    return {"none": True}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="match_cv.py")
    p.add_argument("--name")
    p.add_argument("--email")
    p.add_argument("--meeting-at", required=True)
    p.add_argument("--doc-id")
    p.add_argument("--dir", default=os.environ.get("DESK_CV_DIR") or str(Path.home() / "Downloads" / "CVs"))
    p.add_argument("--window-days", type=int, default=30)
    args = p.parse_args(argv)
    out = match(Path(args.dir), args.name, args.email or None, args.meeting_at, args.window_days)
    if "match" in out and args.doc_id:
        dest = sl.root() / "state" / "cv_text" / f"{args.doc_id}.txt"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(_cache_file(out["digest"]), dest)
        out["text"] = str(dest.relative_to(sl.root()))
        if args.doc_id in sl.load()["items"]:
            try:
                sl.record_cv(args.doc_id, out["match"])
                out["cv_path_recorded"] = True
            except sl.StateError as e:
                out["cv_warning"] = str(e)
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
