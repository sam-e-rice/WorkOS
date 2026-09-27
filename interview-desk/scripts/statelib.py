"""Shared Interview Desk state. Every read and write of state/debriefs.json goes through here."""
from __future__ import annotations

import json
import os
import re
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
    "approved_by": None, "approved_ts": None, "approved_parent": None,
}
# Set only by replies.apply_reply via set_status(approval=...), never through fields.
PROTECTED = {"status", "attempts", "approved_by", "approved_ts", "approved_parent", "cv_path"}
# Once recorded, a Notion id can't be pointed somewhere else.
WRITE_ONCE = {"notion_row", "submission_page"}
APPROVAL_KEYS = ("approved_by", "approved_ts", "approved_parent")
NEEDS_APPROVAL = {"awaiting_decision", "parked"}


class StateError(Exception):
    pass


_UUID = re.compile(r"([0-9a-f]{8})-([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{12})")
_HEX = re.compile(r"(?<![0-9a-f])[0-9a-f]{32}(?![0-9a-f])")
CV_SUFFIXES = (".pdf", ".docx")


def notion_ids(value) -> set[str]:
    return set(_HEX.findall(_UUID.sub(r"\1\2\3\4\5", str(value or "").lower())))


def notion_id(value) -> str | None:
    """The one Notion id in a URL, dashed UUID or bare id; None if there are none or several."""
    found = notion_ids(value)
    return found.pop() if len(found) == 1 else None


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


def _apply(doc_id: str, item: dict, fields: dict | None) -> None:
    clean = {k: v for k, v in (fields or {}).items() if k not in PROTECTED}
    for k in WRITE_ONCE & clean.keys():
        if item.get(k) and clean[k] != item[k]:
            raise StateError(f"{doc_id}: {k} is write-once (already {item[k]!r})")
    item.update(clean)


def _check_not_terminal(doc_id: str, item: dict) -> None:
    if item["status"] in TERMINAL:
        raise StateError(f"{doc_id} is {item['status']}; terminal items can't change")


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
        item = {"status": "new", "attempts": 0, **ITEM_DEFAULTS}
        _apply(doc_id, item, fields)
        data["items"][doc_id] = item
        _log({"ts": iso(now), "doc_id": doc_id, "from": None, "to": "new"})
    else:
        _check_not_terminal(doc_id, item)
        _apply(doc_id, item, fields)
    item["updated"] = iso(now)
    save(data)
    return item


def set_status(key: str, status: str, fields: dict | None = None,
               now: datetime | None = None, approval: dict | None = None) -> tuple[str, dict]:
    now = now or utcnow()
    if status not in TRANSITIONS:
        raise StateError(f"unknown status {status!r}")
    data = load()
    doc_id = resolve_key(data, key)
    item = data["items"][doc_id]
    cur = item["status"]
    _check_not_terminal(doc_id, item)
    if not (status == cur and status not in COUNTED) and status not in TRANSITIONS[cur]:
        raise StateError(f"{doc_id}: {cur} -> {status} not allowed")
    if status == "drafting" and cur in NEEDS_APPROVAL:
        if not approval or not all(approval.get(k) for k in APPROVAL_KEYS):
            raise StateError(f"{doc_id}: {cur} -> drafting needs Sam's approval")
        item.update({k: approval[k] for k in APPROVAL_KEYS})
    _apply(doc_id, item, fields)
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


LOCK_STALE = timedelta(minutes=30)
WATERMARK_OVERLAP = timedelta(hours=24)
DEFAULT_LOOKBACK = timedelta(days=7)
PRUNE_DIRS = ("inbox", "state/briefs", "state/drafts", "state/cv_text")


def acquire_lock(pid: int, now: datetime | None = None) -> bool:
    now = now or utcnow()
    p = state_dir() / "lock.json"
    payload = json.dumps({"pid": pid, "ts": iso(now)})
    try:
        fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        held = json.loads(p.read_text() or "{}")
        if held.get("ts") and now - parse_iso(held["ts"]) < LOCK_STALE:
            return False
        atomic_write(p, payload)
        return True
    with os.fdopen(fd, "w") as f:
        f.write(payload)
    return True


def release_lock(advance_watermark: bool) -> None:
    p = state_dir() / "lock.json"
    if not p.exists():
        return
    held = json.loads(p.read_text() or "{}")
    if advance_watermark and held.get("ts"):
        data = load()
        data["watermark"] = iso(parse_iso(held["ts"]) - WATERMARK_OVERLAP)
        save(data)
    p.unlink()


def get_watermark(now: datetime | None = None) -> str:
    return load()["watermark"] or iso((now or utcnow()) - DEFAULT_LOOKBACK)


def recover(now: datetime | None = None) -> list[str]:
    stuck = [d for d, i in load()["items"].items() if i["status"] == "drafting"]
    for doc_id in stuck:
        set_status(doc_id, "draft_failed", {"error": "recovered: previous run ended mid-draft"}, now)
    return stuck


def prune(days: int = 30, now: datetime | None = None) -> int:
    cutoff = ((now or utcnow()) - timedelta(days=days)).timestamp()
    open_ids = {d for d, i in load()["items"].items() if i["status"] not in TERMINAL}
    removed = 0
    for rel in PRUNE_DIRS:
        d = root() / rel
        if not d.exists():
            continue
        for f in d.rglob("*"):
            if f.is_file() and f.stat().st_mtime < cutoff and f.stem not in open_ids:
                f.unlink()
                removed += 1
    return removed


def short_keys(ids: list[str], min_len: int = 6) -> dict[str, str]:
    out = {}
    for doc_id in ids:
        others = [o for o in ids if o != doc_id]
        n = min(min_len, len(doc_id))
        while n < len(doc_id) and any(o.startswith(doc_id[:n]) for o in others):
            n += 1
        out[doc_id] = doc_id[:n]
    return out


def cv_dir() -> Path:
    return Path(os.environ.get("DESK_CV_DIR") or Path.home() / "Downloads" / "CVs").resolve()


def check_cv_path(path) -> Path:
    """A CV must be a .pdf/.docx inside the CV folder; nothing else may be uploaded."""
    p = Path(path).resolve()
    if cv_dir() not in p.parents:
        raise StateError(f"CV must be inside the CV folder {cv_dir()}")
    if p.suffix.lower() not in CV_SUFFIXES:
        raise StateError("CV must be a .pdf or .docx file")
    return p


def record_cv(key: str, path, now: datetime | None = None) -> dict:
    p = check_cv_path(path)
    data = load()
    doc_id = resolve_key(data, key)
    item = data["items"][doc_id]
    _check_not_terminal(doc_id, item)
    item["cv_path"] = str(p)
    item["updated"] = iso(now or utcnow())
    save(data)
    return item
