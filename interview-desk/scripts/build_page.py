#!/usr/bin/env python3
"""Turn a submission draft (from ids-recruitment-submissions) into Notion page title + content."""
import argparse
import json
import sys
from pathlib import Path

REQUIRED_SECTIONS = ("🔍 Overview", "🧩 Why", "📍 Current Situation")
FORBIDDEN_TAGS = ("<page", "<database", "<folder", "<synced_block_reference")


class BuildError(Exception):
    pass


def _check_tags(*texts: str) -> None:
    for t in texts:
        if t and any(tag in t.lower() for tag in FORBIDDEN_TAGS):
            raise BuildError("draft contains a page/database/folder tag, which would move an existing page")


def build(draft_md: str, candidate: str, role_title: str, cv_markdown: str | None = None) -> dict:
    if cv_markdown and cv_markdown.strip().lower() in ("none", "null"):
        cv_markdown = None
    _check_tags(draft_md, cv_markdown or "")
    lines = draft_md.strip().splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    headings = [l for l in lines if l.startswith("#")]
    missing = [s for s in REQUIRED_SECTIONS if not any(s in h for h in headings)]
    if missing:
        raise BuildError(f"draft is missing sections: {', '.join(missing)}")
    first = next(i for i, l in enumerate(lines) if l.startswith("#"))
    header = [l for l in lines[:first] if l.strip()]
    body = "\n".join(lines[first:]).strip()
    if header and header[0].lstrip().startswith("<callout"):
        callout = "\n".join(header)
    elif header and header[0].lstrip().startswith("<aside"):
        # The submission skill emits its header as <aside>; Notion needs a callout.
        inner = [l for l in header[1:] if not l.strip().startswith("</aside")]
        callout = '<callout icon="📌" color="gray_bg">\n' + "\n".join("\t" + l.strip() for l in inner) + "\n</callout>"
    elif header:
        callout = '<callout icon="📌" color="gray_bg">\n' + "\n".join("\t" + l.strip() for l in header) + "\n</callout>"
    else:
        raise BuildError("draft has no header lines for the callout")
    parts = [callout, body]
    if cv_markdown:
        parts += ["## 📎 CV", cv_markdown.strip()]
    return {"title": f"{candidate} | {role_title}", "content": "\n\n".join(parts) + "\n"}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="build_page.py")
    p.add_argument("--draft", required=True)
    p.add_argument("--candidate", required=True)
    p.add_argument("--role", required=True)
    p.add_argument("--cv-markdown")
    args = p.parse_args(argv)
    try:
        print(json.dumps(build(Path(args.draft).read_text(), args.candidate, args.role, args.cv_markdown)))
    except BuildError as e:
        print(str(e), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
