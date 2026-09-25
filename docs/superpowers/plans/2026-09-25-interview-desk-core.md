# Interview Desk Core (Plan A of 3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and test the deterministic core of Interview Desk: state machine, transcript parsing, quote and fact checks, CV matching, role matching, Slack reply handling, and the PreToolUse guard. No network calls.

**Architecture:** A small uv-managed Python project in `interview-desk/` inside the WorkOS repo. Plain scripts in `scripts/` share one state module (`statelib.py`); the agent (Plan C) only ever changes state through `scripts/state.py`. Everything is pure functions plus thin argparse CLIs, tested with pytest against a temp `DESK_ROOT`.

**Tech Stack:** Python 3.12 (via uv), pytest, pypdf, python-docx, zoneinfo.

**Spec:** `Auto Submission Loop_v3.md` (repo root). Plans B (Google Drive/Calendar/Docs discovery) and C (connectors spike, Notion DBs, agent skill, schedule) follow this one; see "After this plan" at the end.

## Global Constraints

- Project root: `interview-desk/` in the WorkOS repo; venv at `interview-desk/.venv` (settings allow `.venv/bin/python scripts/*`).
- `requires-python = ">=3.12"`; deps limited to `pypdf`, `python-docx`; dev dep `pytest`.
- All state writes go through `statelib.py`; writes atomic (temp file + `os.replace`).
- Statuses exactly: `new`, `pending_transcript`, `skipped`, `awaiting_decision`, `parked`, `drafting`, `needs_input`, `draft_failed`, `failed`, `submitted`, `abandoned`. Terminal: `submitted`, `abandoned`.
- `MAX_ATTEMPTS = 3`; lock stale after 30 min; watermark = run start − 24h; default watermark = now − 7 days; prune after 30 days.
- Title regex (en dashes, NZST or NZDT): `^Hang Out With Sam Rice \((?P<name>.+?)\) – (?P<when>\d{4}/\d{2}/\d{2} \d{2}:\d{2}) NZ[SD]T – Notes by Gemini$`; times are `Pacific/Auckland`.
- Sam's transcript speaker label: `Sam Rice | We Are Eight`. Never a candidate quote.
- Quote block format: `> "exact words" (Name, HH:MM:SS)`.
- CV folder default `~/Downloads/CVs`, window ±30 days of the meeting, dedupe by SHA-256.
- Guard fails closed: a matched tool call with a missing or unknown target is blocked (exit 2).
- Every `scripts/*.py` CLI prints JSON to stdout; `state.py` exit codes: 0 ok, 2 state error, 3 lock held.

## Review Focus

1. A transcript continuation line that looks like `Word: text` (e.g. `So basically: it was two years`) should stay part of the previous speaker's segment, not become a new speaker. Test in Task 3.
2. A Slack reply of `no worries, go for it` should not park the candidate. Test in Task 7.
3. Money said out loud (`180 grand`, `between 170 and 190k`) should support a draft's `$180k` / `$170–190k`. Test in Task 5.
4. The transcript labels the candidate by first name only (`Jane`) while the calendar says `Jane Doe`; real quotes should still verify. Test in Task 4.
5. The same CV downloaded twice (`Jane Doe CV.pdf`, `Jane Doe CV (1).pdf`) should be one match, not ambiguous. Test in Task 6.

---

## File Structure

```
interview-desk/
  pyproject.toml
  .gitignore
  config/
    patterns.json          # title regex, Sam's speaker label
    domains.json           # internal + client email domains (classification, Plan B)
    slack.json             # sam_user_id, dm_channel_id (filled in Plan C)
    notion.json            # open_roles_db, candidates_db, candidates_data_source (Plan C)
  scripts/
    statelib.py            # state file, transitions, lock, watermark, recover, prune
    state.py               # CLI over statelib (+ apply-reply, save-roles)
    textnorm.py            # norm(), tokens()
    transcript.py          # title parse, transcript → segments
    verify_quotes.py       # brief quote blocks vs candidate segments
    verify_facts.py        # draft money / % / notice / employers vs sources
    match_cv.py            # CV pool, dedupe, text cache, match
    roles.py               # Open Roles matching
    replies.py             # Slack reply parsing + apply
  .claude/
    settings.json          # permissions + PreToolUse hook
    hooks/guard.py
  tests/
    conftest.py
    helpers.py
    fixtures/transcript_md.txt
    fixtures/transcript_plain.txt
    test_statelib.py  test_state_cli.py  test_transcript.py  test_verify_quotes.py
    test_verify_facts.py  test_match_cv.py  test_roles_replies.py  test_guard.py
```

---

### Task 1: Project scaffold + state core

**Files:**
- Create: `interview-desk/pyproject.toml`, `interview-desk/.gitignore`, `interview-desk/config/{patterns,domains,slack,notion}.json`
- Create: `interview-desk/scripts/statelib.py`
- Create: `interview-desk/tests/conftest.py`, `interview-desk/tests/helpers.py`, `interview-desk/tests/test_statelib.py`
- Modify: `scripts/check.sh` (repo root) — add one case

**Interfaces:**
- Produces:
  - `statelib.root() -> Path` (env `DESK_ROOT`, else `interview-desk/`)
  - `statelib.utcnow() -> datetime`, `iso(dt) -> str` (`YYYY-MM-DDTHH:MM:SSZ`), `parse_iso(s) -> datetime`
  - `statelib.load() -> dict` (`{"watermark": str|None, "items": {doc_id: item}}`), `save(data) -> None`, `atomic_write(path, text) -> None`
  - `statelib.StateError(Exception)`
  - `statelib.resolve_key(data, key) -> str`
  - `statelib.upsert(doc_id, fields, now=None) -> dict` (never changes `status`/`attempts`)
  - `statelib.set_status(key, status, fields=None, now=None) -> tuple[str, dict]`
  - constants `TRANSITIONS`, `TERMINAL`, `BRIEFABLE = {"new","pending_transcript","failed"}`, `DRAFTABLE = {"drafting","draft_failed"}`, `MAX_ATTEMPTS`, `ITEM_DEFAULTS`
  - test fixture `desk` (temp DESK_ROOT with `config/` copied), helper `run_script(name, *args) -> CompletedProcess`

- [ ] **Step 1: Create the project files**

`interview-desk/pyproject.toml`:

```toml
[project]
name = "interview-desk"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["pypdf>=5", "python-docx>=1.1"]

[dependency-groups]
dev = ["pytest>=8"]

[tool.uv]
package = false

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["scripts"]
```

`interview-desk/.gitignore`:

```
.venv/
state/
inbox/
__pycache__/
```

`interview-desk/config/patterns.json`:

```json
{
  "title_regex": "^Hang Out With Sam Rice \\((?P<name>.+?)\\) – (?P<when>\\d{4}/\\d{2}/\\d{2} \\d{2}:\\d{2}) NZ[SD]T – Notes by Gemini$",
  "sam_speaker": "Sam Rice | We Are Eight"
}
```

`interview-desk/config/domains.json`:

```json
{ "internal": ["weareeight.com.au"], "client": [] }
```

`interview-desk/config/slack.json`:

```json
{ "sam_user_id": "", "dm_channel_id": "" }
```

`interview-desk/config/notion.json`:

```json
{ "open_roles_db": "", "candidates_db": "", "candidates_data_source": "" }
```

`interview-desk/tests/conftest.py`:

```python
import shutil
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent


@pytest.fixture
def desk(tmp_path, monkeypatch):
    shutil.copytree(PROJECT / "config", tmp_path / "config")
    monkeypatch.setenv("DESK_ROOT", str(tmp_path))
    monkeypatch.setenv("DESK_NO_NOTIFY", "1")
    return tmp_path
```

`interview-desk/tests/helpers.py`:

```python
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent


def run_script(name, *args, stdin=None):
    return subprocess.run(
        [sys.executable, str(PROJECT / "scripts" / name), *args],
        capture_output=True, text=True, input=stdin,
    )
```

- [ ] **Step 2: Write the failing tests**

`interview-desk/tests/test_statelib.py`:

```python
import json

import pytest

import statelib as sl


def log_lines(desk):
    return [json.loads(l) for l in (desk / "state" / "log.jsonl").read_text().splitlines()]


def test_upsert_creates_new_item_with_defaults(desk):
    item = sl.upsert("doc123abc", {"candidate": "Jane Doe"})
    assert item["status"] == "new"
    assert item["attempts"] == 0
    assert item["slack_ts"] is None
    assert sl.load()["items"]["doc123abc"]["candidate"] == "Jane Doe"


def test_upsert_existing_keeps_status(desk):
    sl.upsert("doc1", {})
    sl.set_status("doc1", "pending_transcript")
    item = sl.upsert("doc1", {"status": "new", "email": "j@x.com"})
    assert item["status"] == "pending_transcript"
    assert item["email"] == "j@x.com"


def test_resolve_key_prefix(desk):
    sl.upsert("abc111", {})
    sl.upsert("abd222", {})
    data = sl.load()
    assert sl.resolve_key(data, "abc") == "abc111"
    with pytest.raises(sl.StateError):
        sl.resolve_key(data, "ab")
    with pytest.raises(sl.StateError):
        sl.resolve_key(data, "zzz")


def test_legal_transition_logs(desk):
    sl.upsert("d1", {})
    sl.set_status("d1", "awaiting_decision", {"slack_ts": "1.2"})
    last = log_lines(desk)[-1]
    assert (last["from"], last["to"], last["slack_ts"]) == ("new", "awaiting_decision", "1.2")


def test_illegal_transition_raises(desk):
    sl.upsert("d1", {})
    with pytest.raises(sl.StateError, match="not allowed"):
        sl.set_status("d1", "submitted")


def test_unknown_status_raises(desk):
    sl.upsert("d1", {})
    with pytest.raises(sl.StateError, match="unknown status"):
        sl.set_status("d1", "done")


def test_third_failure_abandons(desk):
    sl.upsert("d1", {})
    sl.set_status("d1", "failed")
    sl.set_status("d1", "failed")
    _, item = sl.set_status("d1", "failed", {"error": "boom"})
    assert item["status"] == "abandoned"
    assert item["attempts"] == 3
    assert item["error"] == "boom"


def test_awaiting_decision_resets_attempts(desk):
    sl.upsert("d1", {})
    sl.set_status("d1", "failed")
    _, item = sl.set_status("d1", "awaiting_decision")
    assert item["attempts"] == 0


def test_draft_failure_keeps_the_yes(desk):
    sl.upsert("d1", {})
    sl.set_status("d1", "awaiting_decision")
    sl.set_status("d1", "drafting")
    _, item = sl.set_status("d1", "draft_failed")
    assert item["status"] == "draft_failed"
    _, item = sl.set_status("d1", "drafting")
    assert item["status"] == "drafting"


def test_same_status_updates_fields_without_logging(desk):
    sl.upsert("d1", {})
    sl.set_status("d1", "pending_transcript")
    n = len(log_lines(desk))
    _, item = sl.set_status("d1", "pending_transcript", {"error": "still waiting"})
    assert item["error"] == "still waiting"
    assert len(log_lines(desk)) == n


def test_save_leaves_no_temp_files(desk):
    sl.upsert("d1", {})
    assert [p.name for p in (desk / "state").iterdir() if p.name.endswith(".tmp")] == []
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd interview-desk && uv sync && uv run pytest tests/test_statelib.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'statelib'`

- [ ] **Step 4: Implement `statelib.py` (core)**

`interview-desk/scripts/statelib.py`:

```python
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
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd interview-desk && uv run pytest tests/test_statelib.py -q`
Expected: PASS (all tests in the file)

- [ ] **Step 6: Add the repo check case**

In `scripts/check.sh` (repo root), insert before the final `[ "$fails" -eq 0 ]` line:

```sh
# test: interview_desk_tests — the interview-desk pytest suite passes.
(cd interview-desk && uv run --quiet pytest -q >/dev/null 2>&1) || fail interview_desk_tests
```

Run: `sh scripts/check.sh`
Expected: `ok`

- [ ] **Step 7: Commit**

```bash
git add interview-desk scripts/check.sh
git commit -m "feat(interview-desk): scaffold project and state core"
```

---

### Task 2: Run lifecycle + `state.py` CLI

**Files:**
- Modify: `interview-desk/scripts/statelib.py` (append)
- Create: `interview-desk/scripts/state.py`
- Test: `interview-desk/tests/test_statelib.py` (append), `interview-desk/tests/test_state_cli.py`

**Interfaces:**
- Consumes: Task 1 `statelib` API.
- Produces:
  - `statelib.acquire_lock(pid, now=None) -> bool`, `release_lock(advance_watermark: bool) -> None`
  - `statelib.get_watermark(now=None) -> str`, `recover(now=None) -> list[str]`, `prune(days=30, now=None) -> int`
  - `statelib.short_keys(ids: list[str]) -> dict[str, str]`
  - CLI `state.py lock | unlock [--advance-watermark] | watermark | upsert DOC_ID [--data JSON] | set KEY STATUS [--data JSON] [--error MSG] | recover | list [--open] [--status S]... | prune [--days N] | notify MSG`

- [ ] **Step 1: Write the failing tests**

Append to `interview-desk/tests/test_statelib.py`:

```python
import os
from datetime import datetime, timedelta, timezone

T0 = datetime(2026, 9, 25, 3, 0, tzinfo=timezone.utc)


def test_lock_held_then_stale(desk):
    assert sl.acquire_lock(1, T0)
    assert not sl.acquire_lock(2, T0 + timedelta(minutes=5))
    assert sl.acquire_lock(3, T0 + timedelta(minutes=31))


def test_release_advances_watermark(desk):
    sl.acquire_lock(1, T0)
    sl.release_lock(advance_watermark=True)
    assert sl.load()["watermark"] == "2026-09-24T03:00:00Z"
    assert not (desk / "state" / "lock.json").exists()


def test_release_without_advance_keeps_watermark(desk):
    sl.acquire_lock(1, T0)
    sl.release_lock(advance_watermark=False)
    assert sl.load()["watermark"] is None


def test_default_watermark_is_seven_days_back(desk):
    assert sl.get_watermark(T0) == "2026-09-18T03:00:00Z"


def test_recover_moves_drafting_to_draft_failed(desk):
    sl.upsert("d1", {})
    sl.set_status("d1", "awaiting_decision")
    sl.set_status("d1", "drafting")
    assert sl.recover() == ["d1"]
    assert sl.load()["items"]["d1"]["status"] == "draft_failed"


def test_prune_keeps_files_of_open_items(desk):
    inbox = desk / "inbox"
    inbox.mkdir()
    old, keep = inbox / "gone.json", inbox / "d1.json"
    for p in (old, keep):
        p.write_text("[]")
        os.utime(p, (0, 0))
    sl.upsert("d1", {})
    assert sl.prune(days=30) == 1
    assert keep.exists() and not old.exists()


def test_short_keys_are_unique_prefixes():
    keys = sl.short_keys(["abcdef111", "abcdef222", "zz"])
    assert keys == {"abcdef111": "abcdef1", "abcdef222": "abcdef2", "zz": "zz"}
```

`interview-desk/tests/test_state_cli.py`:

```python
import json

from helpers import run_script


def test_lock_twice_exits_3(desk):
    assert run_script("state.py", "lock").returncode == 0
    assert run_script("state.py", "lock").returncode == 3


def test_illegal_set_exits_2(desk):
    run_script("state.py", "upsert", "d1", "--data", "{}")
    r = run_script("state.py", "set", "d1", "submitted")
    assert r.returncode == 2
    assert "not allowed" in r.stderr


def test_set_with_error_flag(desk):
    run_script("state.py", "upsert", "d1", "--data", "{}")
    r = run_script("state.py", "set", "d1", "failed", "--error", "drive 500")
    assert json.loads(r.stdout)["error"] == "drive 500"


def test_list_open_includes_key(desk):
    run_script("state.py", "upsert", "d1", "--data", '{"candidate": "Jane"}')
    rows = json.loads(run_script("state.py", "list", "--open").stdout)
    assert rows[0]["doc_id"] == "d1"
    assert rows[0]["key"] == "d1"
    assert rows[0]["candidate"] == "Jane"


def test_notify_is_quiet_in_tests(desk):
    r = run_script("state.py", "notify", '2 new "briefs"')
    assert r.returncode == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd interview-desk && uv run pytest tests/test_statelib.py tests/test_state_cli.py -q`
Expected: FAIL with `AttributeError: module 'statelib' has no attribute 'acquire_lock'` and missing `state.py`

- [ ] **Step 3: Implement lifecycle functions**

Append to `interview-desk/scripts/statelib.py`:

```python
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
```

- [ ] **Step 4: Implement `state.py`**

`interview-desk/scripts/state.py`:

```python
#!/usr/bin/env python3
"""CLI over statelib. The only way the agent changes Interview Desk state."""
import argparse
import json
import os
import subprocess
import sys

import statelib as sl


def notify(message: str) -> None:
    if os.environ.get("DESK_NO_NOTIFY"):
        print(message)
        return
    script = f'display notification {json.dumps(message)} with title "Interview Desk"'
    subprocess.run(["osascript", "-e", script], check=False)


def cmd_list(args) -> None:
    data = sl.load()
    keys = sl.short_keys(list(data["items"]))
    rows = []
    for doc_id, item in data["items"].items():
        if args.open and item["status"] in sl.TERMINAL:
            continue
        if args.status and item["status"] not in args.status:
            continue
        rows.append({"doc_id": doc_id, "key": keys[doc_id], **item})
    print(json.dumps(rows, indent=2))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="state.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("lock")
    u = sub.add_parser("unlock")
    u.add_argument("--advance-watermark", action="store_true")
    sub.add_parser("watermark")
    up = sub.add_parser("upsert")
    up.add_argument("doc_id")
    up.add_argument("--data", default="{}")
    s = sub.add_parser("set")
    s.add_argument("key")
    s.add_argument("status")
    s.add_argument("--data", default="{}")
    s.add_argument("--error")
    sub.add_parser("recover")
    ls = sub.add_parser("list")
    ls.add_argument("--open", action="store_true")
    ls.add_argument("--status", action="append")
    pr = sub.add_parser("prune")
    pr.add_argument("--days", type=int, default=30)
    n = sub.add_parser("notify")
    n.add_argument("message")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.cmd == "lock":
            if not sl.acquire_lock(os.getpid()):
                print("lock held", file=sys.stderr)
                return 3
        elif args.cmd == "unlock":
            sl.release_lock(advance_watermark=args.advance_watermark)
        elif args.cmd == "watermark":
            print(sl.get_watermark())
        elif args.cmd == "upsert":
            print(json.dumps(sl.upsert(args.doc_id, json.loads(args.data))))
        elif args.cmd == "set":
            fields = json.loads(args.data)
            if args.error is not None:
                fields["error"] = args.error
            doc_id, item = sl.set_status(args.key, args.status, fields)
            print(json.dumps({"doc_id": doc_id, **item}))
        elif args.cmd == "recover":
            print(json.dumps(sl.recover()))
        elif args.cmd == "list":
            cmd_list(args)
        elif args.cmd == "prune":
            print(sl.prune(days=args.days))
        elif args.cmd == "notify":
            notify(args.message)
    except sl.StateError as e:
        print(str(e), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd interview-desk && uv run pytest -q`
Expected: PASS (all tests in test_statelib.py and test_state_cli.py)

- [ ] **Step 6: Commit**

```bash
git add interview-desk
git commit -m "feat(interview-desk): lock, watermark, recover, prune and state CLI"
```

---

### Task 3: Text normalisation + transcript parsing

**Files:**
- Create: `interview-desk/scripts/textnorm.py`, `interview-desk/scripts/transcript.py`
- Create: `interview-desk/tests/fixtures/transcript_md.txt`, `interview-desk/tests/fixtures/transcript_plain.txt`
- Test: `interview-desk/tests/test_transcript.py`

**Interfaces:**
- Consumes: `statelib.root()`, `statelib.iso()`.
- Produces:
  - `textnorm.norm(s) -> str` (accent-folded, lower-case, punctuation and `_` → space, single spaces), `textnorm.tokens(s) -> list[str]`
  - `transcript.patterns() -> dict` (reads `config/patterns.json`)
  - `transcript.parse_title(title, regex=None) -> {"name": str, "meeting_at": iso} | None`
  - `transcript.parse_transcript(text) -> {"segments": [{"speaker","start","text"}], "complete": bool, "ended_after": str|None}`
  - CLI `transcript.py title TITLE` / `transcript.py segments FILE` (prints the dict above)

- [ ] **Step 1: Create fixtures**

`interview-desk/tests/fixtures/transcript_md.txt`:

```
## Hang Out With Sam Rice (Jane Doe) - Transcript
### **00:00:00**
**Sam Rice | We Are Eight:** Thanks for jumping on.
**Jane Doe:** No worries, happy to chat.
### **00:00:45**
**Jane Doe:** I led the payments rebuild at Canva, we cut checkout latency by 40%.
So basically: it was a two year project.
**Sam Rice | We Are Eight:** What are you looking for on salary?
**Jane Doe:** Around 180 grand base, maybe between 170 and 190k all in, and I'm on four weeks notice.
Transcription ended after 00:12:31
This editable transcript was computer generated and might contain errors.
```

`interview-desk/tests/fixtures/transcript_plain.txt` (same content, no markdown):

```
Hang Out With Sam Rice (Jane Doe) - Transcript
00:00:00
Sam Rice | We Are Eight: Thanks for jumping on.
Jane Doe: No worries, happy to chat.
00:00:45
Jane Doe: I led the payments rebuild at Canva, we cut checkout latency by 40%.
So basically: it was a two year project.
Sam Rice | We Are Eight: What are you looking for on salary?
Jane Doe: Around 180 grand base, maybe between 170 and 190k all in, and I'm on four weeks notice.
Transcription ended after 00:12:31
This editable transcript was computer generated and might contain errors.
```

- [ ] **Step 2: Write the failing tests**

`interview-desk/tests/test_transcript.py`:

```python
import json
from pathlib import Path

import pytest

import transcript as tr
from helpers import run_script
from textnorm import norm, tokens

FIX = Path(__file__).parent / "fixtures"


def test_norm_folds_accents_punctuation_and_underscores():
    assert norm("José O’Brien_CV!") == "jose o brien cv"
    assert tokens("Sam Rice | We Are Eight") == ["sam", "rice", "we", "are", "eight"]


def test_title_nzst(desk):
    t = "Hang Out With Sam Rice (Jane Doe) – 2026/09/20 14:00 NZST – Notes by Gemini"
    assert tr.parse_title(t) == {"name": "Jane Doe", "meeting_at": "2026-09-20T02:00:00Z"}


def test_title_nzdt_after_dst_switch(desk):
    t = "Hang Out With Sam Rice (Jane Doe) – 2026/09/28 10:00 NZDT – Notes by Gemini"
    assert tr.parse_title(t)["meeting_at"] == "2026-09-27T21:00:00Z"


def test_title_with_hyphens_is_rejected(desk):
    assert tr.parse_title("Hang Out With Sam Rice (Jane Doe) - 2026/09/20 14:00 NZST - Notes by Gemini") is None


def test_title_other_meeting_is_rejected(desk):
    assert tr.parse_title("Time with Danny (Jane Doe) – 2026/09/20 14:00 AEST – Notes by Gemini") is None


@pytest.mark.parametrize("name", ["transcript_md.txt", "transcript_plain.txt"])
def test_segments_both_formats(name):
    out = tr.parse_transcript((FIX / name).read_text())
    segs = out["segments"]
    assert [s["speaker"] for s in segs] == [
        "Sam Rice | We Are Eight", "Jane Doe", "Jane Doe", "Sam Rice | We Are Eight", "Jane Doe"]
    assert segs[2]["start"] == "00:00:45"
    assert out["complete"] is True
    assert out["ended_after"] == "00:12:31"


def test_continuation_line_that_looks_like_a_speaker_stays_attached():
    segs = tr.parse_transcript((FIX / "transcript_md.txt").read_text())["segments"]
    assert segs[2]["text"].endswith("So basically: it was a two year project.")
    assert "So basically" not in {s["speaker"] for s in segs}


def test_disclaimer_after_end_marker_is_ignored():
    segs = tr.parse_transcript((FIX / "transcript_md.txt").read_text())["segments"]
    assert "computer generated" not in segs[-1]["text"]


def test_incomplete_transcript():
    text = (FIX / "transcript_md.txt").read_text().split("Transcription ended")[0]
    assert tr.parse_transcript(text)["complete"] is False


def test_cli_segments(desk):
    r = run_script("transcript.py", "segments", str(FIX / "transcript_plain.txt"))
    assert json.loads(r.stdout)["complete"] is True
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd interview-desk && uv run pytest tests/test_transcript.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'transcript'`

- [ ] **Step 4: Implement**

`interview-desk/scripts/textnorm.py`:

```python
"""Normalisation shared by quote, fact, CV and role matching."""
import re
import unicodedata


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"[\W_]+", " ", s)
    return " ".join(s.split())


def tokens(s: str) -> list[str]:
    return norm(s).split()
```

`interview-desk/scripts/transcript.py`:

```python
#!/usr/bin/env python3
"""Parse Gemini hang titles and Transcript-tab text into segments."""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import statelib as sl

AUCKLAND = ZoneInfo("Pacific/Auckland")
TS_RE = re.compile(r"^\s*(?:#{1,6}\s*)?(?:\*\*)?(\d{1,2}:\d{2}:\d{2})(?:\*\*)?\s*$")
SPK_RE = re.compile(r"^\s*(?:\*\*)?([A-Z0-9][^:*\n]{0,79}?):(?:\*\*)?\s+(\S.*)$")
END_RE = re.compile(r"Transcription ended after (\d{1,2}:\d{2}:\d{2})")


def patterns() -> dict:
    return json.loads((sl.root() / "config" / "patterns.json").read_text())


def parse_title(title: str, regex: str | None = None) -> dict | None:
    m = re.match(regex or patterns()["title_regex"], title.strip())
    if not m:
        return None
    local = datetime.strptime(m["when"], "%Y/%m/%d %H:%M").replace(tzinfo=AUCKLAND)
    return {"name": m["name"].strip(), "meeting_at": sl.iso(local)}


def _speaker_counts(lines: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for line in lines:
        m = SPK_RE.match(line)
        if m and not TS_RE.match(line):
            label = m[1].strip()
            counts[label] = counts.get(label, 0) + 1
    return counts


def parse_transcript(text: str) -> dict:
    lines = text.splitlines()
    # A label is a speaker only if it recurs; one-off "Word: text" lines are continuations.
    speakers = {s for s, c in _speaker_counts(lines).items() if c >= 2}
    segs: list[dict] = []
    start, ended = "00:00:00", None
    for line in lines:
        e = END_RE.search(line)
        if e:
            ended = e[1].zfill(8)
            break
        if not line.strip():
            continue
        t = TS_RE.match(line)
        if t:
            start = t[1].zfill(8)
            continue
        m = SPK_RE.match(line)
        if m and m[1].strip() in speakers:
            segs.append({"speaker": m[1].strip(), "start": start, "text": m[2].strip()})
        elif segs:
            segs[-1]["text"] += " " + line.strip().strip("*").strip()
    return {"segments": segs, "complete": ended is not None, "ended_after": ended}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="transcript.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("title")
    t.add_argument("title")
    s = sub.add_parser("segments")
    s.add_argument("file")
    args = p.parse_args(argv)
    if args.cmd == "title":
        print(json.dumps(parse_title(args.title)))
    else:
        print(json.dumps(parse_transcript(Path(args.file).read_text()), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd interview-desk && uv run pytest tests/test_transcript.py -q`
Expected: PASS (all tests in the file)

- [ ] **Step 6: Commit**

```bash
git add interview-desk
git commit -m "feat(interview-desk): parse hang titles and transcript segments"
```

---

### Task 4: Quote verifier

**Files:**
- Create: `interview-desk/scripts/verify_quotes.py`
- Test: `interview-desk/tests/test_verify_quotes.py`

**Interfaces:**
- Consumes: `textnorm.norm`, `transcript.patterns()`, `transcript.parse_transcript` (tests only).
- Produces:
  - `verify_quotes.QUOTE_RE`, `same_person(label, name) -> bool`
  - `verify_quotes.check(md, segments, name, sam_label) -> list[{"quote","line","reason"}]`
  - `verify_quotes.drop(md, failures) -> str`
  - CLI `verify_quotes.py MD SEGMENTS_JSON --speaker NAME [--drop]` → exit 0; exit 1 + `{"failures": [...]}`; with `--drop` rewrites MD, prints `{"dropped": [...]}`, exit 0. `SEGMENTS_JSON` is a list of segments (the `inbox/<id>.json` format).

- [ ] **Step 1: Write the failing tests**

`interview-desk/tests/test_verify_quotes.py`:

```python
import json
from pathlib import Path

import transcript as tr
import verify_quotes as vq
from helpers import run_script

FIX = Path(__file__).parent / "fixtures"
SAM = "Sam Rice | We Are Eight"


def segs():
    return tr.parse_transcript((FIX / "transcript_md.txt").read_text())["segments"]


def test_exact_quote_passes():
    md = '> "we cut checkout latency by 40%" (Jane Doe, 00:00:45)\n'
    assert vq.check(md, segs(), "Jane Doe", SAM) == []


def test_quote_spanning_continuation_passes():
    md = '> "by 40%. So basically: it was a two year project" (Jane Doe, 00:00:45)\n'
    assert vq.check(md, segs(), "Jane Doe", SAM) == []


def test_paraphrase_fails():
    md = '> "we halved checkout latency" (Jane Doe, 00:00:45)\n'
    [f] = vq.check(md, segs(), "Jane Doe", SAM)
    assert f["reason"] == "not found in the candidate's words"


def test_sams_words_attributed_to_candidate_fail():
    md = '> "Thanks for jumping on" (Jane Doe, 00:00:00)\n'
    assert len(vq.check(md, segs(), "Jane Doe", SAM)) == 1


def test_quote_attributed_to_sam_fails():
    md = '> "Thanks for jumping on" (Sam Rice, 00:00:00)\n'
    [f] = vq.check(md, segs(), "Jane Doe", SAM)
    assert f["reason"].startswith("attributed to Sam Rice")


def test_first_name_speaker_label_still_verifies():
    s = [{"speaker": "Jane", "start": "00:01:00", "text": "I want a smaller team."}]
    md = '> "I want a smaller team" (Jane Doe, 00:01:00)\n'
    assert vq.check(md, s, "Jane Doe", SAM) == []


def test_partial_word_does_not_match():
    md = '> "ut checkout" (Jane Doe, 00:00:45)\n'
    assert len(vq.check(md, segs(), "Jane Doe", SAM)) == 1


def test_drop_removes_only_failing_lines():
    md = ('Fit: strong.\n'
          '> "we cut checkout latency by 40%" (Jane Doe, 00:00:45)\n'
          '> "we halved checkout latency" (Jane Doe, 00:00:45)\n')
    out = vq.drop(md, vq.check(md, segs(), "Jane Doe", SAM))
    assert "halved" not in out
    assert "40%" in out and "Fit: strong." in out


def test_cli_exit_codes_and_drop(desk, tmp_path):
    seg_file = tmp_path / "segs.json"
    seg_file.write_text(json.dumps(segs()))
    md = tmp_path / "brief.md"
    md.write_text('> "we halved checkout latency" (Jane Doe, 00:00:45)\n')
    r = run_script("verify_quotes.py", str(md), str(seg_file), "--speaker", "Jane Doe")
    assert r.returncode == 1
    assert json.loads(r.stdout)["failures"][0]["quote"] == "we halved checkout latency"
    r = run_script("verify_quotes.py", str(md), str(seg_file), "--speaker", "Jane Doe", "--drop")
    assert r.returncode == 0
    assert "halved" not in md.read_text()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd interview-desk && uv run pytest tests/test_verify_quotes.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'verify_quotes'`

- [ ] **Step 3: Implement**

`interview-desk/scripts/verify_quotes.py`:

```python
#!/usr/bin/env python3
"""Check brief quote blocks against the candidate's transcript segments."""
import argparse
import json
import re
import sys
from pathlib import Path

import transcript
from textnorm import norm

QUOTE_RE = re.compile(
    r'^>[ \t]*["“](?P<q>.+?)["”][ \t]*\((?P<who>[^,()]+),[ \t]*(?P<ts>\d{1,2}:\d{2}:\d{2})\)[ \t]*$',
    re.M,
)


def same_person(label: str, name: str) -> bool:
    a, b = norm(label).split(), norm(name).split()
    return bool(a and b) and (a == b or a[0] == b[0])


def candidate_runs(segments: list[dict], name: str, sam_label: str) -> list[str]:
    """Normalised text of each unbroken run of the candidate speaking."""
    runs, cur = [], []
    for s in segments:
        if norm(s["speaker"]) != norm(sam_label) and same_person(s["speaker"], name):
            cur.append(norm(s["text"]))
        elif cur:
            runs.append(" ".join(cur))
            cur = []
    if cur:
        runs.append(" ".join(cur))
    return runs


def check(md: str, segments: list[dict], name: str, sam_label: str) -> list[dict]:
    runs = [f" {r} " for r in candidate_runs(segments, name, sam_label)]
    fails = []
    for m in QUOTE_RE.finditer(md):
        q = norm(m["q"])
        who = m["who"].strip()
        if norm(who) == norm(sam_label) or not same_person(who, name):
            fails.append({"quote": m["q"], "line": m[0], "reason": f"attributed to {who}, not the candidate"})
        elif not q or not any(f" {q} " in r for r in runs):
            fails.append({"quote": m["q"], "line": m[0], "reason": "not found in the candidate's words"})
    return fails


def drop(md: str, failures: list[dict]) -> str:
    bad = {f["line"] for f in failures}
    return "\n".join(line for line in md.split("\n") if line not in bad)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="verify_quotes.py")
    p.add_argument("md")
    p.add_argument("segments")
    p.add_argument("--speaker", required=True)
    p.add_argument("--drop", action="store_true")
    args = p.parse_args(argv)
    md = Path(args.md).read_text()
    segments = json.loads(Path(args.segments).read_text())
    fails = check(md, segments, args.speaker, transcript.patterns()["sam_speaker"])
    if fails and args.drop:
        Path(args.md).write_text(drop(md, fails))
        print(json.dumps({"dropped": fails}))
        return 0
    if fails:
        print(json.dumps({"failures": fails}))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd interview-desk && uv run pytest tests/test_verify_quotes.py -q`
Expected: PASS (all tests in the file)

- [ ] **Step 5: Commit**

```bash
git add interview-desk
git commit -m "feat(interview-desk): verify brief quotes against candidate speech"
```

---

### Task 5: Fact verifier

**Files:**
- Create: `interview-desk/scripts/verify_facts.py`
- Test: `interview-desk/tests/test_verify_facts.py`

**Interfaces:**
- Consumes: `textnorm.norm`.
- Produces:
  - `verify_facts.money(text, loose=False) -> set[int]` (dollars; `loose` also counts bare comma numbers like `180,000`)
  - `verify_facts.percents(text) -> set[float]`, `notices(text) -> set[tuple[int, str]]`, `employers(draft) -> list[str]`
  - `verify_facts.check(draft, sources, allow=()) -> list[{"kind","value"}]`
  - CLI `verify_facts.py DRAFT --segments SEGMENTS_JSON [--cv CV_TXT] [--allow NAME]...` → exit 0; exit 1 + `{"unsupported": [...]}`

- [ ] **Step 1: Write the failing tests**

`interview-desk/tests/test_verify_facts.py`:

```python
import json
from pathlib import Path

import transcript as tr
import verify_facts as vf
from helpers import run_script

FIX = Path(__file__).parent / "fixtures"
CV = "Jane Doe. Staff Engineer, Canva (2021-present). Super 12% salary sacrifice."
DRAFT = """**Current:** Staff Engineer at Canva | **Location:** Sydney
**Salary:** $180k base + 12% super | **Notice:** 4 weeks

At Canva: Jane led the payments rebuild and cut checkout latency by **40%**.
Why EQL? She wants a smaller team.
"""


def sources():
    segs = tr.parse_transcript((FIX / "transcript_md.txt").read_text())["segments"]
    return " ".join(s["text"] for s in segs) + "\n" + CV


def test_supported_draft_passes():
    assert vf.check(DRAFT, sources(), allow=["EQL"]) == []


def test_unsupported_salary_flagged():
    out = vf.check(DRAFT.replace("$180k", "$200k"), sources(), allow=["EQL"])
    assert {"kind": "money", "value": 200000} in out


def test_spoken_range_supports_written_range():
    draft = DRAFT.replace("$180k base", "$170–190k base")
    assert vf.check(draft, sources(), allow=["EQL"]) == []


def test_unsupported_notice_flagged():
    out = vf.check(DRAFT.replace("4 weeks", "8 weeks"), sources(), allow=["EQL"])
    assert {"kind": "notice", "value": "8 week"} in out


def test_unsupported_employer_flagged():
    out = vf.check(DRAFT.replace("at Canva |", "at Atlassian |"), sources(), allow=["EQL"])
    assert {"kind": "employer", "value": "Atlassian"} in out


def test_unsupported_percent_flagged():
    out = vf.check(DRAFT.replace("40%", "60%"), sources(), allow=["EQL"])
    assert {"kind": "percent", "value": 60.0} in out


def test_money_parsing():
    assert vf.money("$180,000 or 1.5m or 95k") == {180000, 1500000, 95000}
    assert vf.money("40% of 2019") == set()
    assert vf.money("about 180,000", loose=True) == {180000}


def test_cli(desk, tmp_path):
    segs = tr.parse_transcript((FIX / "transcript_md.txt").read_text())["segments"]
    (tmp_path / "s.json").write_text(json.dumps(segs))
    (tmp_path / "cv.txt").write_text(CV)
    (tmp_path / "d.md").write_text(DRAFT.replace("$180k", "$250k"))
    r = run_script("verify_facts.py", str(tmp_path / "d.md"), "--segments", str(tmp_path / "s.json"),
                   "--cv", str(tmp_path / "cv.txt"), "--allow", "EQL")
    assert r.returncode == 1
    assert {"kind": "money", "value": 250000} in json.loads(r.stdout)["unsupported"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd interview-desk && uv run pytest tests/test_verify_facts.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'verify_facts'`

- [ ] **Step 3: Implement**

`interview-desk/scripts/verify_facts.py`:

```python
#!/usr/bin/env python3
"""Check a submission draft's money, percentages, notice period and employers against transcript + CV."""
import argparse
import json
import re
import sys
from pathlib import Path

from textnorm import norm

MULT = {"k": 1_000, "grand": 1_000, "thousand": 1_000, "m": 1_000_000, "million": 1_000_000}
SUFFIX = r"(k|m|grand|thousand|million)\b"
RANGE_RE = re.compile(
    r"\$?(\d+(?:\.\d+)?)\s*(?:to|and|-|–)\s*\$?(\d+(?:\.\d+)?)\s?" + SUFFIX, re.I)
MONEY_RE = re.compile(r"(?<![\w.,])(\$)?\s?(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s?(?:" + SUFFIX + ")?", re.I)
PCT_RE = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)\s?(?:%|percent\b)", re.I)
WORDNUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
           "eight": 8, "ten": 10, "twelve": 12}
NOTICE_RE = re.compile(r"\b(\d+|" + "|".join(WORDNUM) + r")[\s-]+(week|month)s?\b", re.I)
NAME = r"([A-Z][\w&.'-]*(?:\s+[A-Z][\w&.'-]*){0,3})"
AT_LABEL_RE = re.compile(r"\bAt " + NAME + ":")
AT_INLINE_RE = re.compile(r"\bat " + NAME)


def money(text: str, loose: bool = False) -> set[int]:
    vals = set()
    for m in RANGE_RE.finditer(text):
        mult = MULT[m[3].lower()]
        vals |= {round(float(m[1]) * mult), round(float(m[2]) * mult)}
    for m in MONEY_RE.finditer(RANGE_RE.sub(" ", text)):
        dollar, num, suf = m[1], m[2], m[3]
        if not (dollar or suf or (loose and "," in num)):
            continue
        vals.add(round(float(num.replace(",", "")) * (MULT[suf.lower()] if suf else 1)))
    return vals


def percents(text: str) -> set[float]:
    return {float(m[1]) for m in PCT_RE.finditer(text)}


def notices(text: str) -> set[tuple[int, str]]:
    out = set()
    for m in NOTICE_RE.finditer(text):
        n = m[1].lower()
        out.add((int(n) if n.isdigit() else WORDNUM[n], m[2].lower()))
    return out


def employers(draft: str) -> list[str]:
    found = [m[1] for m in AT_LABEL_RE.finditer(draft)]
    for line in draft.splitlines():
        if "current" in line.lower():
            found += [m[1] for m in AT_INLINE_RE.finditer(line)]
    return list(dict.fromkeys(e.strip(" .") for e in found))


def check(draft: str, sources: str, allow=()) -> list[dict]:
    out = []
    src_money = money(sources, loose=True)
    out += [{"kind": "money", "value": v} for v in sorted(money(draft) - src_money)]
    out += [{"kind": "percent", "value": v} for v in sorted(percents(draft) - percents(sources))]
    notice_lines = "\n".join(l for l in draft.splitlines() if "notice" in l.lower())
    out += [{"kind": "notice", "value": f"{n} {u}"}
            for n, u in sorted(notices(notice_lines) - notices(sources))]
    src_norm = f" {norm(sources)} "
    allowed = {norm(a) for a in allow}
    for e in employers(draft):
        ne = norm(e)
        if ne not in allowed and f" {ne} " not in src_norm:
            out.append({"kind": "employer", "value": e})
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="verify_facts.py")
    p.add_argument("draft")
    p.add_argument("--segments", required=True)
    p.add_argument("--cv")
    p.add_argument("--allow", action="append", default=[])
    args = p.parse_args(argv)
    segs = json.loads(Path(args.segments).read_text())
    sources = " ".join(s["text"] for s in segs)
    if args.cv and Path(args.cv).exists():
        sources += "\n" + Path(args.cv).read_text()
    out = check(Path(args.draft).read_text(), sources, args.allow)
    if out:
        print(json.dumps({"unsupported": out}))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd interview-desk && uv run pytest tests/test_verify_facts.py -q`
Expected: PASS (all tests in the file)

- [ ] **Step 5: Commit**

```bash
git add interview-desk
git commit -m "feat(interview-desk): verify submission facts against transcript and CV"
```

---

### Task 6: CV matcher

**Files:**
- Create: `interview-desk/scripts/match_cv.py`
- Test: `interview-desk/tests/test_match_cv.py`

**Interfaces:**
- Consumes: `statelib.root()`, `statelib.parse_iso()`, `textnorm.norm/tokens`.
- Produces:
  - `match_cv.extract_text(path) -> str` (pypdf / python-docx; `""` on error)
  - `match_cv.match(cv_dir, name, email, meeting_at, window_days=30) -> {"match": path, "digest": sha} | {"ambiguous": [paths]} | {"none": True}`
  - CLI `match_cv.py --name N --email E --meeting-at ISO [--doc-id ID] [--dir DIR] [--window-days N]`; with `--doc-id` and a match, copies text to `state/cv_text/<doc_id>.txt` and adds `"text"` (path relative to DESK_ROOT). `--dir` default: env `DESK_CV_DIR`, else `~/Downloads/CVs`.

- [ ] **Step 1: Write the failing tests**

`interview-desk/tests/test_match_cv.py`:

```python
import json
import os

import docx
import pytest

import match_cv
from helpers import run_script

MEETING = "2026-09-20T02:00:00Z"
MEETING_TS = 1789869600  # 2026-09-20T02:00:00Z


@pytest.fixture
def cvs(tmp_path, monkeypatch):
    d = tmp_path / "CVs"
    d.mkdir()
    texts = {}

    def add(name, text, content=None, days_off=0):
        p = d / name
        p.write_bytes((content or name).encode())
        os.utime(p, (MEETING_TS + days_off * 86400,) * 2)
        texts[name] = text
        return p

    monkeypatch.setattr(match_cv, "extract_text", lambda p: texts[p.name])
    return d, add


def test_email_in_text_wins(desk, cvs):
    d, add = cvs
    add("Resume.pdf", "Contact: jane@example.com")
    add("Jane Doe CV.pdf", "Jane Doe engineer")
    out = match_cv.match(d, "Jane Doe", "jane@example.com", MEETING)
    assert out["match"].endswith("Resume.pdf")


def test_identical_duplicates_are_one_match(desk, cvs):
    d, add = cvs
    add("Jane Doe CV.pdf", "Jane Doe", content="same-bytes")
    add("Jane Doe CV (1).pdf", "Jane Doe", content="same-bytes", days_off=1)
    out = match_cv.match(d, "Jane Doe", None, MEETING)
    assert out["match"].endswith("Jane Doe CV (1).pdf")


def test_two_different_cvs_are_ambiguous(desk, cvs):
    d, add = cvs
    add("Jane Doe CV.pdf", "v1", content="a")
    add("Jane_Doe_Resume.pdf", "v2", content="b")
    out = match_cv.match(d, "Jane Doe", None, MEETING)
    assert len(out["ambiguous"]) == 2


def test_name_found_in_text_only(desk, cvs):
    d, add = cvs
    add("20260730 - Resume.pdf", "JANE DOE\nStaff Engineer")
    assert match_cv.match(d, "Jane Doe", None, MEETING)["match"].endswith("Resume.pdf")


def test_outside_window_is_ignored(desk, cvs):
    d, add = cvs
    add("Jane Doe CV.pdf", "Jane Doe", days_off=45)
    assert match_cv.match(d, "Jane Doe", None, MEETING) == {"none": True}


def test_first_name_only_does_not_match_by_filename(desk, cvs):
    d, add = cvs
    add("Jane CV.pdf", "nothing useful")
    assert match_cv.match(d, "Jane", None, MEETING) == {"none": True}


def test_cli_with_real_docx_copies_text(desk, tmp_path, monkeypatch):
    d = tmp_path / "real"
    d.mkdir()
    doc = docx.Document()
    doc.add_paragraph("Jane Doe - jane@example.com - Staff Engineer at Canva")
    p = d / "Resume.docx"
    doc.save(p)
    os.utime(p, (MEETING_TS,) * 2)
    r = run_script("match_cv.py", "--name", "Jane Doe", "--email", "jane@example.com",
                   "--meeting-at", MEETING, "--doc-id", "doc1", "--dir", str(d))
    out = json.loads(r.stdout)
    assert out["match"].endswith("Resume.docx")
    assert "Canva" in (desk / out["text"]).read_text()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd interview-desk && uv run pytest tests/test_match_cv.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'match_cv'`

- [ ] **Step 3: Implement**

`interview-desk/scripts/match_cv.py`:

```python
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
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd interview-desk && uv run pytest tests/test_match_cv.py -q`
Expected: PASS (all tests in the file)

- [ ] **Step 5: Commit**

```bash
git add interview-desk
git commit -m "feat(interview-desk): match candidate CVs with dedupe and text search"
```

---

### Task 7: Role matching + Slack replies

**Files:**
- Create: `interview-desk/scripts/roles.py`, `interview-desk/scripts/replies.py`
- Modify: `interview-desk/scripts/state.py` (add `apply-reply`, `save-roles`)
- Test: `interview-desk/tests/test_roles_replies.py`

**Interfaces:**
- Consumes: `statelib.load/resolve_key/upsert/set_status/atomic_write/root`, `textnorm.norm/tokens`.
- Produces:
  - Open Roles file `state/open_roles.json`: list of `{"id","role","client","aliases":[str],"brief","submissions_page","status"}`
  - `roles.load_roles() -> list[dict]`, `roles.save_roles(rows) -> None` (validates required keys `id, role, client, submissions_page, status`)
  - `roles.match_role(text, roles) -> {"match": id} | {"none": True, "hints": [str]}`
  - `replies.parse(text) -> {"cmd": "yes","arg": str|None} | {"cmd":"no","reason": str|None} | {"cmd":"other","text": str}`
  - `replies.apply_reply(key, text, user, ts, roles, sam_user_id) -> {"action": "draft"|"parked"|"resume"|"refuse"|"ignore", ...}`
  - CLI `state.py apply-reply KEY --text T --user U [--ts TS]` (reads roles from `state/open_roles.json`, Sam's id from `config/slack.json`), `state.py save-roles --data JSON`

- [ ] **Step 1: Write the failing tests**

`interview-desk/tests/test_roles_replies.py`:

```python
import json

import pytest

import replies
import roles
import statelib as sl
from helpers import run_script

ROLES = [
    {"id": "r1", "role": "Chief Engineer (AI-Native)", "client": "EQL", "aliases": ["Chief Engineer"],
     "brief": "b1", "submissions_page": "p1", "status": "Open"},
    {"id": "r2", "role": "Staff Data Engineer", "client": "EQL", "aliases": [],
     "brief": "b2", "submissions_page": "p2", "status": "Open"},
    {"id": "r3", "role": "Senior Growth Marketer", "client": "Optimal", "aliases": ["Growth Marketer"],
     "brief": "b3", "submissions_page": "p3", "status": "Open"},
    {"id": "r4", "role": "Platform Engineer", "client": "Stile", "aliases": [],
     "brief": "b4", "submissions_page": "p4", "status": "Closed"},
]
SAM = "U_SAM"


def test_match_by_alias():
    assert roles.match_role("Hang re: Chief Engineer chat", ROLES) == {"match": "r1"}


def test_match_by_client_with_single_open_role():
    assert roles.match_role("optimal", ROLES) == {"match": "r3"}


def test_client_with_two_roles_gives_hints():
    out = roles.match_role("EQL", ROLES)
    assert out["none"] is True
    assert len(out["hints"]) == 2


def test_closed_role_never_matches():
    assert "match" not in roles.match_role("Platform Engineer at Stile", ROLES)


@pytest.mark.parametrize("text,cmd", [
    ("yes", "yes"), ("Yes!", "yes"), ("yes Chief Engineer", "yes"),
    ("no too junior", "no"), ("park", "no"),
    ("no worries, go for it", "other"), ("love her", "other"),
])
def test_parse(text, cmd):
    assert replies.parse(text)["cmd"] == cmd


def awaiting(desk, role_row=None):
    sl.upsert("doc1", {"role_row": role_row})
    sl.set_status("doc1", "awaiting_decision", {"slack_ts": "100.0"})


def test_yes_with_role_drafts(desk):
    awaiting(desk, "r1")
    assert replies.apply_reply("doc1", "yes", SAM, "101.0", ROLES, SAM)["action"] == "draft"
    assert sl.load()["items"]["doc1"]["status"] == "drafting"


def test_plain_yes_without_role_is_refused(desk):
    awaiting(desk)
    out = replies.apply_reply("doc1", "yes", SAM, "101.0", ROLES, SAM)
    assert out["action"] == "refuse"
    assert sl.load()["items"]["doc1"]["status"] == "awaiting_decision"


def test_yes_naming_role_sets_role_row(desk):
    awaiting(desk)
    replies.apply_reply("doc1", "yes growth marketer", SAM, "101.0", ROLES, SAM)
    assert sl.load()["items"]["doc1"]["role_row"] == "r3"


def test_no_parks_with_reason(desk):
    awaiting(desk, "r1")
    replies.apply_reply("doc1", "no pay gap too big", SAM, "101.0", ROLES, SAM)
    item = sl.load()["items"]["doc1"]
    assert (item["status"], item["park_reason"]) == ("parked", "pay gap too big")


def test_no_worries_does_not_park(desk):
    awaiting(desk, "r1")
    out = replies.apply_reply("doc1", "no worries, go for it", SAM, "101.0", ROLES, SAM)
    assert out["action"] == "ignore"
    assert sl.load()["items"]["doc1"]["status"] == "awaiting_decision"


def test_other_users_are_ignored(desk):
    awaiting(desk, "r1")
    assert replies.apply_reply("doc1", "yes", "U_OTHER", "101.0", ROLES, SAM)["action"] == "ignore"
    assert sl.load()["items"]["doc1"]["status"] == "awaiting_decision"


def test_already_seen_reply_is_ignored(desk):
    awaiting(desk, "r1")
    sl.upsert("doc1", {"last_reply_ts": "105.0"})
    assert replies.apply_reply("doc1", "yes", SAM, "104.0", ROLES, SAM)["action"] == "ignore"


def test_answer_resumes_needs_input(desk):
    awaiting(desk, "r1")
    sl.set_status("doc1", "drafting")
    sl.set_status("doc1", "needs_input", {"question": "Base or package?"})
    assert replies.apply_reply("doc1", "base", SAM, "101.0", ROLES, SAM)["action"] == "resume"
    item = sl.load()["items"]["doc1"]
    assert (item["status"], item["answer"], item["question"]) == ("drafting", "base", None)


def test_cli_save_roles_and_apply_reply(desk):
    (desk / "config" / "slack.json").write_text(json.dumps({"sam_user_id": SAM, "dm_channel_id": "D1"}))
    assert run_script("state.py", "save-roles", "--data", json.dumps(ROLES)).returncode == 0
    awaiting(desk)
    r = run_script("state.py", "apply-reply", "doc1", "--text", "yes chief engineer", "--user", SAM, "--ts", "101.0")
    assert json.loads(r.stdout)["action"] == "draft"


def test_save_roles_rejects_missing_keys(desk):
    r = run_script("state.py", "save-roles", "--data", json.dumps([{"id": "x"}]))
    assert r.returncode == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd interview-desk && uv run pytest tests/test_roles_replies.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'replies'`

- [ ] **Step 3: Implement `roles.py`**

`interview-desk/scripts/roles.py`:

```python
"""Open Roles lookup: match calendar text or Sam's reply to one open role."""
import json

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
```

- [ ] **Step 4: Implement `replies.py`**

`interview-desk/scripts/replies.py`:

```python
"""Turn Sam's Slack thread replies into state transitions."""
import statelib as sl
from roles import describe, match_role

YES = {"yes", "y", "yep", "yeah", "submit"}
NO = {"no", "n", "nah", "nope", "park"}
NOT_A_NO = ("no worries", "no problem", "no rush", "no stress", "no dramas")


def parse(text: str) -> dict:
    clean = text.strip()
    if clean.lower().startswith(NOT_A_NO):
        return {"cmd": "other", "text": clean}
    words = clean.split(maxsplit=1)
    if not words:
        return {"cmd": "other", "text": ""}
    head = words[0].lower().strip(".,!:;-")
    rest = words[1].strip() if len(words) > 1 else ""
    if head in YES:
        return {"cmd": "yes", "arg": rest or None}
    if head in NO:
        return {"cmd": "no", "reason": rest or None}
    return {"cmd": "other", "text": clean}


def apply_reply(key: str, text: str, user: str, ts: str | None,
                roles: list[dict], sam_user_id: str) -> dict:
    data = sl.load()
    doc_id = sl.resolve_key(data, key)
    item = data["items"][doc_id]
    last = item.get("last_reply_ts")
    if ts and last and float(ts) <= float(last):
        return {"action": "ignore", "reason": "already seen"}
    if ts:
        sl.upsert(doc_id, {"last_reply_ts": ts})
    if not sam_user_id or user != sam_user_id:
        return {"action": "ignore", "reason": "not from Sam"}
    status = item["status"]
    if status == "needs_input":
        sl.set_status(doc_id, "drafting", {"answer": text.strip(), "question": None})
        return {"action": "resume"}
    if status not in ("awaiting_decision", "parked"):
        return {"action": "ignore", "reason": f"status {status}"}
    r = parse(text)
    if r["cmd"] == "no":
        sl.set_status(doc_id, "parked", {"park_reason": r["reason"]})
        return {"action": "parked", "reason": r["reason"]}
    if r["cmd"] != "yes":
        return {"action": "ignore", "reason": "not a decision"}
    role_row = item.get("role_row")
    if r["arg"]:
        m = match_role(r["arg"], roles)
        if "match" not in m:
            hint = f" Did you mean: {', '.join(m['hints'])}?" if m["hints"] else ""
            return {"action": "refuse", "message": f'Couldn\'t match "{r["arg"]}" to one open role.{hint}'}
        role_row = m["match"]
    if not role_row:
        open_roles = ", ".join(describe(x) for x in roles if (x.get("status") or "").lower() == "open")
        return {"action": "refuse",
                "message": f"No role for this hang. Reply `yes <role or client>`. Open roles: {open_roles}"}
    sl.set_status(doc_id, "drafting", {"role_row": role_row})
    return {"action": "draft", "role_row": role_row}
```

- [ ] **Step 5: Add the CLI commands to `state.py`**

In `interview-desk/scripts/state.py`, add imports after `import statelib as sl`:

```python
import replies
import roles
```

In `build_parser()`, before `return p`:

```python
    ar = sub.add_parser("apply-reply")
    ar.add_argument("key")
    ar.add_argument("--text", required=True)
    ar.add_argument("--user", required=True)
    ar.add_argument("--ts")
    sr = sub.add_parser("save-roles")
    sr.add_argument("--data", required=True)
```

In `main()`, before the `except` line, add branches:

```python
        elif args.cmd == "apply-reply":
            slack = json.loads((sl.root() / "config" / "slack.json").read_text())
            print(json.dumps(replies.apply_reply(args.key, args.text, args.user, args.ts,
                                                 roles.load_roles(), slack.get("sam_user_id", ""))))
        elif args.cmd == "save-roles":
            roles.save_roles(json.loads(args.data))
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd interview-desk && uv run pytest -q`
Expected: PASS (whole suite)

- [ ] **Step 7: Commit**

```bash
git add interview-desk
git commit -m "feat(interview-desk): open-role matching and Slack reply handling"
```

---

### Task 8: PreToolUse guard + project settings

**Files:**
- Create: `interview-desk/.claude/hooks/guard.py`, `interview-desk/.claude/settings.json`
- Test: `interview-desk/tests/test_guard.py`

**Interfaces:**
- Consumes: `statelib.root/load`, `roles.load_roles/is_open`, `config/slack.json`, `config/notion.json`.
- Produces:
  - `guard.notion_id(value) -> str | None` (last 32-hex id in a URL or dashed id)
  - `guard.decide(payload) -> str | None` (block reason, or None to allow)
  - Hook contract: reads `{"tool_name", "tool_input"}` JSON on stdin; exit 2 + stderr reason blocks; exit 0 allows.
  - Rules: `*slack_send_message` only to `dm_channel_id`; `*notion-create-pages` only with a `parent` whose ids are all Open-role `submissions_page` ids or the Candidates DB / data source; `*notion-update-page` only on `notion_row` / `submission_page` ids recorded in state. Plan C's skill must record a new page id with `state.py upsert <id> --data '{"submission_page": "<id>"}'` before updating it.

- [ ] **Step 1: Write the failing tests**

`interview-desk/tests/test_guard.py`:

```python
import importlib.util
import json
import subprocess
import sys

import pytest

import statelib as sl
from helpers import PROJECT

GUARD = PROJECT / ".claude" / "hooks" / "guard.py"
SUBS = "3d0d44192fa08015b033da933d44a689"
CAND = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
PAGE = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
SLACK = "mcp__c571a83e-d6be-4875-8c0f-00bfed9b68fd__slack_send_message"
CREATE = "mcp__e15988d3-3d1a-4fb0-927a-1a558d10e036__notion-create-pages"
UPDATE = "mcp__e15988d3-3d1a-4fb0-927a-1a558d10e036__notion-update-page"


@pytest.fixture
def guarded(desk):
    (desk / "config" / "slack.json").write_text(json.dumps({"sam_user_id": "U1", "dm_channel_id": "D123"}))
    (desk / "config" / "notion.json").write_text(json.dumps(
        {"open_roles_db": "", "candidates_db": CAND, "candidates_data_source": ""}))
    (desk / "state").mkdir(exist_ok=True)
    (desk / "state" / "open_roles.json").write_text(json.dumps([
        {"id": "r1", "role": "Chief Engineer", "client": "EQL", "status": "Open",
         "submissions_page": f"https://www.notion.so/Chief-Engineer-Submissions-{SUBS}"},
        {"id": "r2", "role": "Old", "client": "X", "status": "Closed",
         "submissions_page": "cccccccccccccccccccccccccccccccc"},
    ]))
    sl.upsert("doc1", {"submission_page": PAGE})
    spec = importlib.util.spec_from_file_location("guard", GUARD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_notion_id_from_url_and_dashes(guarded):
    assert guarded.notion_id(f"https://weare8.notion.site/Tom-Day-{SUBS}") == SUBS
    assert guarded.notion_id(f"https://www.notion.so/Face-Cafe-{SUBS}?pvs=4") == SUBS
    assert guarded.notion_id("3d0d4419-2fa0-8015-b033-da933d44a689") == SUBS


def test_slack_only_to_dm(guarded):
    assert guarded.decide({"tool_name": SLACK, "tool_input": {"channel_id": "D123", "text": "hi"}}) is None
    assert guarded.decide({"tool_name": SLACK, "tool_input": {"channel_id": "C999", "text": "hi"}})
    assert guarded.decide({"tool_name": SLACK, "tool_input": {}})


def test_create_under_open_role_submissions_page(guarded):
    ok = {"tool_name": CREATE, "tool_input": {"parent": {"page_id": SUBS}, "pages": [{}]}}
    assert guarded.decide(ok) is None


def test_create_in_candidates_db(guarded):
    ok = {"tool_name": CREATE, "tool_input": {"parent": {"database_id": CAND}}}
    assert guarded.decide(ok) is None


@pytest.mark.parametrize("parent", [
    {"page_id": "dddddddddddddddddddddddddddddddd"},
    {"page_id": "cccccccccccccccccccccccccccccccc"},  # closed role
    None,
])
def test_create_elsewhere_blocked(guarded, parent):
    inp = {"pages": [{}]} if parent is None else {"parent": parent, "pages": [{}]}
    assert guarded.decide({"tool_name": CREATE, "tool_input": inp})


def test_update_only_recorded_pages(guarded):
    assert guarded.decide({"tool_name": UPDATE, "tool_input": {"page_id": PAGE}}) is None
    assert guarded.decide({"tool_name": UPDATE, "tool_input": {"data": {"page_id": PAGE}}}) is None
    assert guarded.decide({"tool_name": UPDATE, "tool_input": {"page_id": SUBS}})


def test_other_tools_pass(guarded):
    assert guarded.decide({"tool_name": "Read", "tool_input": {"file_path": "x"}}) is None


def test_hook_exit_codes(guarded):
    bad = json.dumps({"tool_name": SLACK, "tool_input": {"channel_id": "C999"}})
    r = subprocess.run([sys.executable, str(GUARD)], input=bad, capture_output=True, text=True)
    assert r.returncode == 2 and "only allowed" in r.stderr
    r = subprocess.run([sys.executable, str(GUARD)], input="not json", capture_output=True, text=True)
    assert r.returncode == 2


def test_settings_wire_the_guard_and_denies():
    s = json.loads((PROJECT / ".claude" / "settings.json").read_text())
    hook = s["hooks"]["PreToolUse"][0]
    assert "guard.py" in hook["hooks"][0]["command"]
    for rule in ("Edit(./scripts/**)", "Edit(./state/debriefs.json)", "Edit(./state/open_roles.json)",
                 "mcp__e15988d3-3d1a-4fb0-927a-1a558d10e036__notion-move-pages"):
        assert rule in s["permissions"]["deny"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd interview-desk && uv run pytest tests/test_guard.py -q`
Expected: FAIL (guard.py and settings.json missing)

- [ ] **Step 3: Implement `guard.py`**

`interview-desk/.claude/hooks/guard.py`:

```python
#!/usr/bin/env python3
"""PreToolUse guard: Slack posts only to Sam's DM; Notion writes only where Interview Desk may write."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import roles  # noqa: E402
import statelib as sl  # noqa: E402

UUID = re.compile(r"([0-9a-f]{8})-([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{12})")
HEX = re.compile(r"(?<![0-9a-f])[0-9a-f]{32}(?![0-9a-f])")
PARENT_KEYS = {"page_id", "database_id", "data_source_id"}


def notion_id(value) -> str | None:
    """Last Notion id in a URL, dashed UUID or bare id. Slug letters never bleed into the id."""
    s = UUID.sub(r"\1\2\3\4\5", str(value or "").lower())
    found = HEX.findall(s)
    return found[-1] if found else None


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


def allowed() -> tuple[str | None, set[str], set[str]]:
    notion = _config("notion.json")
    parents = {notion_id(r.get("submissions_page")) for r in roles.load_roles() if roles.is_open(r)}
    parents |= {notion_id(notion.get(k)) for k in ("candidates_db", "candidates_data_source")}
    pages = {notion_id(i.get(k)) for i in sl.load()["items"].values() for k in ("notion_row", "submission_page")}
    return _config("slack.json").get("dm_channel_id") or None, parents - {None}, pages - {None}


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
            return "Notion pages may only be created under an open role's Submissions page or the Candidates DB."
        return None
    ids = [notion_id(v) for v in collect(inp, {"page_id"})]
    if not ids or any(i not in pages for i in ids):
        return "Notion updates are only allowed on pages Interview Desk created and recorded in state."
    return None


def main() -> int:
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
```

- [ ] **Step 4: Write `settings.json`**

`interview-desk/.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Read(./**)",
      "Edit(./state/**)",
      "Bash(.venv/bin/python scripts/*)",
      "mcp__c571a83e-d6be-4875-8c0f-00bfed9b68fd__slack_send_message",
      "mcp__c571a83e-d6be-4875-8c0f-00bfed9b68fd__slack_read_thread",
      "mcp__e15988d3-3d1a-4fb0-927a-1a558d10e036__notion-fetch",
      "mcp__e15988d3-3d1a-4fb0-927a-1a558d10e036__notion-search",
      "mcp__e15988d3-3d1a-4fb0-927a-1a558d10e036__notion-query-data-sources",
      "mcp__e15988d3-3d1a-4fb0-927a-1a558d10e036__notion-create-pages",
      "mcp__e15988d3-3d1a-4fb0-927a-1a558d10e036__notion-update-page",
      "mcp__e15988d3-3d1a-4fb0-927a-1a558d10e036__notion-create-file-upload"
    ],
    "deny": [
      "Edit(./scripts/**)",
      "Edit(./config/**)",
      "Edit(./.claude/**)",
      "Edit(./state/debriefs.json)",
      "Edit(./state/open_roles.json)",
      "Edit(./state/log.jsonl)",
      "mcp__e15988d3-3d1a-4fb0-927a-1a558d10e036__notion-move-pages",
      "mcp__e15988d3-3d1a-4fb0-927a-1a558d10e036__notion-duplicate-page",
      "mcp__c571a83e-d6be-4875-8c0f-00bfed9b68fd__slack_schedule_message",
      "mcp__c571a83e-d6be-4875-8c0f-00bfed9b68fd__slack_create_conversation",
      "Bash(curl *)",
      "Bash(wget *)"
    ]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__.*__(slack_send_message|notion-create-pages|notion-update-page)",
        "hooks": [{ "type": "command", "command": ".venv/bin/python .claude/hooks/guard.py" }]
      }
    ]
  }
}
```

- [ ] **Step 5: Run the full suite and the repo check**

Run: `cd interview-desk && uv run pytest -q && cd .. && sh scripts/check.sh`
Expected: all tests PASS, then `ok`

- [ ] **Step 6: Commit**

```bash
git add interview-desk
git commit -m "feat(interview-desk): PreToolUse guard and project permissions"
```

---

## After this plan

- **Plan B: Google discovery.** OAuth client setup (use the `wizard` skill for Sam's console steps), `watch_new_notes.py`: Drive query, title parse, Calendar resolve, Docs `includeTabsContent` export of the Transcript tab to text → `transcript.parse_transcript` → `inbox/<id>.json` (segment list), domain classify, settle (`complete` + 15 min idle), `upsert`/`set_status`. Re-export `inbox/` for open items whose file was pruned.
- **Plan C: agent and connectors.** Build step 0 spike (needs Sam's go-ahead: posts to his Slack DM, creates a private test page), create the Open Roles and Candidates databases (needs go-ahead), fill `config/slack.json` and `config/notion.json`, pin the three skills as `ids-*`, write `CLAUDE.md` and `post-hang-debrief/SKILL.md`, submission page builder, DOCX→PDF (neither `soffice` nor `pdftotext` is installed; decide Word `docx2pdf` vs `brew install libreoffice`), hourly Desktop scheduled task.

## Deviations from the spec (for the reviewer)

- `pending_transcript` is briefable once its transcript is complete (the spec's rules line said only `new`/`failed`; its status table already allowed `pending_transcript → awaiting_decision`).
- `cv_cache.json` dropped: text is cached by content hash under `state/cv_text/cache/`, which also survives renames.
- `allowlist.json` dropped: the guard reads `open_roles.json`, config and state directly, so it can't go stale. Direct edits to those files are denied; they change only via `state.py`.
- `pdftotext` replaced by `pypdf` (no system dependency).
