"""Open Roles lookup: match calendar text or Sam's reply to one open role."""
import argparse
import json
import sys

import statelib as sl
from textnorm import norm, tokens

REQUIRED = ("id", "role", "client", "submissions_page", "status")


def _path():
    return sl.root() / "state" / "open_roles.json"


def load_roles() -> list[dict]:
    p = _path()
    return json.loads(p.read_text()) if p.exists() else []


def save_roles(rows: list[dict]) -> None:
    if not isinstance(rows, list):
        raise sl.StateError("roles must be a list")
    for r in rows:
        missing = [k for k in REQUIRED if not r.get(k)]
        if missing:
            raise sl.StateError(f"role {r.get('id')!r} missing {missing}")
    sl.atomic_write(_path(), json.dumps(rows, indent=2) + "\n")


def allowed_submission_pages() -> set[str]:
    """Submissions pages Sam has listed in config/notion.json (the agent can't edit config)."""
    p = sl.root() / "config" / "notion.json"
    pages = json.loads(p.read_text()).get("submission_pages", []) if p.exists() else []
    return {sl.notion_id(x) or x for x in pages}


def page_allowed(page: str) -> bool:
    return bool(page) and (sl.notion_id(page) or page) in allowed_submission_pages()


def is_open(r: dict) -> bool:
    return (r.get("status") or "").lower() == "open"


def _has(hay: str, needle: str) -> bool:
    return bool(needle) and f" {needle} " in f" {hay} "


def describe(r: dict) -> str:
    return f'{r["role"]} ({r["client"]})'


def match_role(text: str, roles: list[dict]) -> dict:
    t = norm(text)
    open_ = [r for r in roles if is_open(r)]
    by_name = [r for r in open_ if any(_has(t, norm(n)) for n in [r["role"], *r.get("aliases", [])])]
    by_client = [r for r in open_ if _has(t, norm(r["client"]))]
    if len(by_name) == 1:
        return {"match": by_name[0]["id"]}
    if len(by_name) > 1:
        both = [r for r in by_name if r in by_client]
        if len(both) == 1:
            return {"match": both[0]["id"]}
    elif len(by_client) == 1:
        return {"match": by_client[0]["id"]}
    words = set(tokens(text))
    pool = by_name or by_client or open_
    scored = [(len(words & set(tokens(r["role"] + " " + r["client"]))), r) for r in pool]
    hints = [describe(r) for score, r in sorted(scored, key=lambda s: -s[0]) if score > 0][:2]
    return {"none": True, "hints": hints}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="roles.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("match")
    m.add_argument("--text", required=True)
    args = p.parse_args(argv)
    print(json.dumps(match_role(args.text, load_roles())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
