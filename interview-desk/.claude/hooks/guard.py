#!/usr/bin/env python3
"""Interview Desk hook.

PreToolUse (default): Slack posts only to Sam's DM; Notion pages only under a parent Sam approved
(or the Candidates DB); Notion updates only on pages this loop created.
PostToolUse (--record): remember the ids of pages notion-create-pages just made.
The allowlists come from state the agent can't write directly: approvals are set only by
replies.apply_reply, and created_pages.json only by this hook.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import statelib as sl  # noqa: E402

UUID = re.compile(r"([0-9a-f]{8})-([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{12})")
HEX = re.compile(r"(?<![0-9a-f])[0-9a-f]{32}(?![0-9a-f])")
PARENT_KEYS = {"page_id", "database_id", "data_source_id"}


def _ids(value) -> set[str]:
    return set(HEX.findall(UUID.sub(r"\1\2\3\4\5", str(value or "").lower())))


def notion_id(value) -> str | None:
    """The one Notion id in a URL, dashed UUID or bare id; None if there are none or several."""
    found = _ids(value)
    return found.pop() if len(found) == 1 else None


def collect(obj, keys: set[str]) -> list[str]:
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in keys and isinstance(v, str):
                out.append(v)
            else:
                out += collect(v, keys)
    elif isinstance(obj, list):
        for v in obj:
            out += collect(v, keys)
    return out


def _config(name: str) -> dict:
    p = sl.root() / "config" / name
    return json.loads(p.read_text()) if p.exists() else {}


def _created_path() -> Path:
    return sl.root() / "state" / "created_pages.json"


def created_pages() -> set[str]:
    p = _created_path()
    return set(json.loads(p.read_text())) if p.exists() else set()


def allowed() -> tuple[str | None, set[str], set[str]]:
    notion = _config("notion.json")
    parents = {notion_id(notion.get(k)) for k in ("candidates_db", "candidates_data_source")}
    parents |= {notion_id(i.get("approved_parent")) for i in sl.load()["items"].values()
                if i["status"] == "drafting" and i.get("approved_by")}
    return _config("slack.json").get("dm_channel_id") or None, parents - {None}, created_pages()


def record(payload: dict) -> None:
    if not payload.get("tool_name", "").endswith("notion-create-pages"):
        return
    parent_ids = _ids(json.dumps(payload.get("tool_input") or {}))
    new = _ids(json.dumps(payload.get("tool_response") or {})) - parent_ids
    if new:
        sl.atomic_write(_created_path(), json.dumps(sorted(created_pages() | new)) + "\n")


def decide(payload: dict) -> str | None:
    tool = payload.get("tool_name", "")
    inp = payload.get("tool_input") or {}
    if not tool.endswith(("slack_send_message", "notion-create-pages", "notion-update-page")):
        return None
    dm, parents, pages = allowed()
    if tool.endswith("slack_send_message"):
        channel = inp.get("channel_id") or inp.get("channel")
        return None if dm and channel == dm else f"Slack posts are only allowed to Sam's DM, not {channel!r}."
    if tool.endswith("notion-create-pages"):
        parent = inp.get("parent")
        raw = collect(parent, PARENT_KEYS) if isinstance(parent, dict) else ([parent] if parent else [])
        ids = [notion_id(v) for v in raw]
        if not ids or any(i not in parents for i in ids):
            return "Notion pages may only be created under a Submissions page Sam approved, or the Candidates DB."
        return None
    ids = [notion_id(v) for v in collect(inp, {"page_id"})]
    if not ids or any(i not in pages for i in ids):
        return "Notion updates are only allowed on pages Interview Desk created and recorded in state."
    return None


def main() -> int:
    if "--record" in sys.argv:
        try:
            record(json.loads(sys.stdin.read()))
        except Exception as e:  # recording must never block the tool result
            print(f"guard record error: {e}", file=sys.stderr)
        return 0
    try:
        reason = decide(json.loads(sys.stdin.read()))
    except Exception as e:  # fail closed
        reason = f"guard error: {e}"
    if reason:
        print(reason, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
