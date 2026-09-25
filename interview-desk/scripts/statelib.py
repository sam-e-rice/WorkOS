"""Shared Interview Desk state. Every read and write of state/debriefs.json goes through here."""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

TRANSITIONS: dict[str, set[str]] = {
    "new": {"skipped", "pending_transcript", "awaiting_decision", "failed", "abandoned"},
    "pending_transcript": {"awaiting_decision", "failed", "abandoned"},
    "skipped": {"pending_transcript"},
    "awaiting_decision": {"parked", "drafting"},
    "parked": {"drafting"},
    "drafting": {"submitted", "needs_input", "draft_failed"},
    "needs_input": {"drafting"},
    "draft_failed": {"drafting", "abandoned"},
    "failed": {"awaiting_decision", "failed", "abandoned"},
    "submitted": set(),
    "abandoned": set(),
}
TERMINAL = {"submitted", "abandoned"}
BRIEFABLE = {"new", "pending_transcript", "failed"}
DRAFTABLE = {"drafting", "draft_failed"}
COUNTED = {"failed", "draft_failed"}
MAX_ATTEMPTS = 3
ITEM_DEFAULTS = {
    "candidate": None, "email": None, "meeting_at": None, "role_text": None,
    "role_row": None, "cv_path": None, "slack_ts": None, "last_reply_ts": None,
    "notion_row": None, "submission_page": None, "question": None, "answer": None,
    "park_reason": None, "error": None,
}


class StateError(Exception):
    pass


def root() -> Path:
    return Path(os.environ.get("DESK_ROOT") or Path(__file__).resolve().parent.parent)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def state_dir() -> Path:
    d = root() / "state"
    d.mkdir(parents=True, exist_ok=True)
    return d


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    with os.fdopen(fd, "w") as f:
        f.write(text)
    os.replace(tmp, path)


def load() -> dict:
    p = state_dir() / "debriefs.json"
    if not p.exists():
        return {"watermark": None, "items": {}}
    return json.loads(p.read_text())


def save(data: dict) -> None:
    atomic_write(state_dir() / "debriefs.json", json.dumps(data, indent=2, sort_keys=True) + "\n")


def _log(entry: dict) -> None:
    with open(state_dir() / "log.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")


def _clean(fields: dict | None) -> dict:
    return {k: v for k, v in (fields or {}).items() if k not in ("status", "attempts")}


def resolve_key(data: dict, key: str) -> str:
    if key in data["items"]:
        return key
    hits = [d for d in data["items"] if d.startswith(key)]
    if len(hits) != 1:
        raise StateError(f"key {key!r} matches {len(hits)} items")
    return hits[0]


def upsert(doc_id: str, fields: dict, now: datetime | None = None) -> dict:
    now = now or utcnow()
    data = load()
    item = data["items"].get(doc_id)
    if item is None:
        item = {"status": "new", "attempts": 0, **ITEM_DEFAULTS, **_clean(fields)}
        data["items"][doc_id] = item
        _log({"ts": iso(now), "doc_id": doc_id, "from": None, "to": "new"})
    else:
        item.update(_clean(fields))
    item["updated"] = iso(now)
    save(data)
    return item


def set_status(key: str, status: str, fields: dict | None = None,
               now: datetime | None = None) -> tuple[str, dict]:
    now = now or utcnow()
    if status not in TRANSITIONS:
        raise StateError(f"unknown status {status!r}")
    data = load()
    doc_id = resolve_key(data, key)
    item = data["items"][doc_id]
    cur = item["status"]
    if not (status == cur and status not in COUNTED) and status not in TRANSITIONS[cur]:
        raise StateError(f"{doc_id}: {cur} -> {status} not allowed")
    item.update(_clean(fields))
    new = status
    if status in COUNTED:
        item["attempts"] += 1
        if item["attempts"] >= MAX_ATTEMPTS:
            new = "abandoned"
    if new == "awaiting_decision":
        item["attempts"] = 0
    item["status"] = new
    item["updated"] = iso(now)
    save(data)
    if new != cur:
        _log({"ts": iso(now), "doc_id": doc_id, "from": cur, "to": new,
              "cv_path": item.get("cv_path"), "notion_page": item.get("submission_page"),
              "slack_ts": item.get("slack_ts")})
    return doc_id, item
