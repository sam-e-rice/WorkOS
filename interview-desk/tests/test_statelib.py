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
