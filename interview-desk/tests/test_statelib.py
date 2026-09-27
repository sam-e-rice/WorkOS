import json

import pytest

import statelib as sl


APPROVAL = {"approved_by": "U_SAM", "approved_ts": "101.0", "approved_parent": "p1"}


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
    sl.set_status("d1", "drafting", approval=APPROVAL)
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
    sl.set_status("d1", "drafting", approval=APPROVAL)
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


def test_drafting_from_a_decision_requires_approval(desk):
    sl.upsert("d1", {})
    sl.set_status("d1", "awaiting_decision")
    with pytest.raises(sl.StateError, match="approval"):
        sl.set_status("d1", "drafting")
    _, item = sl.set_status("d1", "drafting", approval=APPROVAL)
    assert item["approved_by"] == "U_SAM"
    assert item["approved_parent"] == "p1"


def test_approval_fields_cannot_be_set_directly(desk):
    sl.upsert("d1", {"approved_parent": "evil"})
    _, item = sl.set_status("d1", "pending_transcript", {"approved_by": "U_EVIL"})
    assert item["approved_parent"] is None
    assert item["approved_by"] is None


def test_page_ids_are_write_once(desk):
    sl.upsert("d1", {"submission_page": "aaa"})
    sl.upsert("d1", {"submission_page": "aaa"})
    with pytest.raises(sl.StateError, match="write-once"):
        sl.upsert("d1", {"submission_page": "bbb"})


def test_terminal_items_are_frozen(desk):
    sl.upsert("d1", {})
    for _ in range(3):
        sl.set_status("d1", "failed")
    with pytest.raises(sl.StateError, match="abandoned"):
        sl.set_status("d1", "abandoned", {"error": "x"})
    with pytest.raises(sl.StateError, match="abandoned"):
        sl.upsert("d1", {"submission_page": "zzz"})


def test_cv_path_cannot_be_set_through_fields(desk):
    item = sl.upsert("d1", {"cv_path": "/Users/samrice/.ssh/id_rsa"})
    assert item["cv_path"] is None


def test_record_cv_only_inside_the_cv_folder(desk, monkeypatch):
    cvdir = desk / "CVs"
    cvdir.mkdir()
    (cvdir / "Jane.pdf").write_bytes(b"x")
    (desk / "key.pdf").write_bytes(b"x")
    monkeypatch.setenv("DESK_CV_DIR", str(cvdir))
    sl.upsert("d1", {})
    assert sl.record_cv("d1", str(cvdir / "Jane.pdf"))["cv_path"] == str((cvdir / "Jane.pdf").resolve())
    with pytest.raises(sl.StateError, match="CV folder"):
        sl.record_cv("d1", str(desk / "key.pdf"))
    with pytest.raises(sl.StateError, match="CV folder"):
        sl.record_cv("d1", str(cvdir / ".." / "key.pdf"))
    (cvdir / "notes.txt").write_text("x")
    with pytest.raises(sl.StateError, match="pdf or .docx"):
        sl.record_cv("d1", str(cvdir / "notes.txt"))
