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
OTHER = "dddddddddddddddddddddddddddddddd"
SLACK = "mcp__c571a83e-d6be-4875-8c0f-00bfed9b68fd__slack_send_message"
CREATE = "mcp__e15988d3-3d1a-4fb0-927a-1a558d10e036__notion-create-pages"
UPDATE = "mcp__e15988d3-3d1a-4fb0-927a-1a558d10e036__notion-update-page"


def load_guard():
    spec = importlib.util.spec_from_file_location("guard", GUARD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def guarded(desk):
    (desk / "config" / "slack.json").write_text(json.dumps(
        {"sam_user_id": "U1", "dm_channel_id": "D123", "dm_im_channel": "D999"}))
    (desk / "config" / "notion.json").write_text(json.dumps(
        {"open_roles_db": "", "candidates_db": CAND, "candidates_data_source": ""}))
    sl.upsert("approved", {})
    sl.set_status("approved", "awaiting_decision")
    sl.set_status("approved", "drafting", approval={
        "approved_by": "U1", "approved_ts": "1.0",
        "approved_parent": f"https://www.notion.so/Chief-Engineer-Submissions-{SUBS}"})
    sl.upsert("waiting", {})
    sl.set_status("waiting", "awaiting_decision")
    (desk / "state" / "created_pages.json").write_text(json.dumps([PAGE]))
    return load_guard()


def test_notion_id_from_url_and_dashes(guarded):
    assert guarded.notion_id(f"https://weare8.notion.site/Tom-Day-{SUBS}") == SUBS
    assert guarded.notion_id(f"https://www.notion.so/Face-Cafe-{SUBS}?pvs=4") == SUBS
    assert guarded.notion_id("3d0d4419-2fa0-8015-b033-da933d44a689") == SUBS


def test_url_with_two_ids_is_rejected(guarded):
    assert guarded.notion_id(f"https://notion.so/Evil-{OTHER}?v={SUBS}") is None
    evil = {"tool_name": CREATE, "tool_input": {"parent": {"page_id": f"https://notion.so/Evil-{OTHER}?v={SUBS}"}}}
    assert guarded.decide(evil)


MARKED = "🤖 Interview Desk · Jane Doe · Chief Engineer (EQL)"


def test_slack_only_to_dm_with_marker(guarded):
    assert guarded.decide({"tool_name": SLACK, "tool_input": {"channel_id": "D123", "message": MARKED}}) is None
    assert guarded.decide({"tool_name": SLACK, "tool_input": {"channel_id": "D999", "message": MARKED,
                                                               "thread_ts": "1.0"}}) is None
    assert guarded.decide({"tool_name": SLACK, "tool_input": {"channel_id": "C999", "message": MARKED}})
    assert guarded.decide({"tool_name": SLACK, "tool_input": {"channel_id": "D123", "message": "yes"}})
    assert guarded.decide({"tool_name": SLACK, "tool_input": {}})


def test_marked_thread_reply_in_another_channel_blocked(guarded):
    inp = {"channel_id": "C999", "thread_ts": "1.0", "message": MARKED}
    assert guarded.decide({"tool_name": SLACK, "tool_input": inp})


@pytest.mark.parametrize("tag", ['<page url="https://notion.so/x">HOMEBASE</page>',
                                 '<database url="https://notion.so/y">DB</database>',
                                 '<folder url="z">F</folder>'])
def test_move_tags_blocked_in_create_and_update(guarded, tag):
    create = {"tool_name": CREATE, "tool_input": {"parent": {"page_id": SUBS},
                                                   "pages": [{"content": f"Hello\n{tag}"}]}}
    update = {"tool_name": UPDATE, "tool_input": {"page_id": PAGE, "command": "insert_content",
                                                   "content": tag}}
    assert "move" in guarded.decide(create)
    assert "move" in guarded.decide(update)


def test_create_under_an_approved_drafting_parent(guarded):
    ok = {"tool_name": CREATE, "tool_input": {"parent": {"page_id": SUBS}, "pages": [{}]}}
    assert guarded.decide(ok) is None


def test_create_under_parent_without_approval_blocked(guarded):
    sl.set_status("approved", "draft_failed")
    blocked = {"tool_name": CREATE, "tool_input": {"parent": {"page_id": SUBS}, "pages": [{}]}}
    assert guarded.decide(blocked)


def test_create_in_candidates_db(guarded):
    assert guarded.decide({"tool_name": CREATE, "tool_input": {"parent": {"database_id": CAND}}}) is None


@pytest.mark.parametrize("parent", [{"page_id": OTHER}, OTHER, None])
def test_create_elsewhere_blocked(guarded, parent):
    inp = {"pages": [{}]} if parent is None else {"parent": parent, "pages": [{}]}
    assert guarded.decide({"tool_name": CREATE, "tool_input": inp})


def test_update_only_pages_the_loop_created(guarded):
    assert guarded.decide({"tool_name": UPDATE, "tool_input": {"page_id": PAGE}}) is None
    assert guarded.decide({"tool_name": UPDATE, "tool_input": {"data": {"page_id": PAGE}}}) is None
    assert guarded.decide({"tool_name": UPDATE, "tool_input": {"page_id": SUBS}})


def test_agent_recorded_page_ids_do_not_unlock_updates(guarded):
    sl.upsert("waiting", {"submission_page": OTHER})
    assert guarded.decide({"tool_name": UPDATE, "tool_input": {"page_id": OTHER}})


def test_record_mode_adds_created_page_ids(guarded, desk):
    new = "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
    payload = {"tool_name": CREATE, "tool_input": {"parent": {"page_id": SUBS}},
               "tool_response": {"pages": [{"id": "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
                                            "parent": {"page_id": SUBS}}]}}
    guarded.record(payload)
    ids = json.loads((desk / "state" / "created_pages.json").read_text())
    assert new in ids and SUBS not in ids


def test_other_tools_pass(guarded):
    assert guarded.decide({"tool_name": "Read", "tool_input": {"file_path": "x"}}) is None


def test_hook_exit_codes(guarded):
    bad = json.dumps({"tool_name": SLACK, "tool_input": {"channel_id": "C999", "message": MARKED}})
    r = subprocess.run([sys.executable, str(GUARD)], input=bad, capture_output=True, text=True)
    assert r.returncode == 2 and "only allowed" in r.stderr
    r = subprocess.run([sys.executable, str(GUARD)], input="not json", capture_output=True, text=True)
    assert r.returncode == 2


def settings():
    return json.loads((PROJECT / ".claude" / "settings.json").read_text())


def test_pre_hook_fails_closed_when_python_is_missing(guarded, monkeypatch):
    cmd = settings()["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
    ok = json.dumps({"tool_name": SLACK, "tool_input": {"channel_id": "D123", "message": MARKED}})
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", "/nonexistent")
    assert subprocess.run(["sh", "-c", cmd], input=ok, text=True, capture_output=True).returncode == 2
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(PROJECT))
    assert subprocess.run(["sh", "-c", cmd], input=ok, text=True, capture_output=True).returncode == 0


def test_settings_wire_the_guard_and_denies():
    s = settings()
    assert "--record" in s["hooks"]["PostToolUse"][0]["hooks"][0]["command"]
    assert "mcp__c571a83e-d6be-4875-8c0f-00bfed9b68fd__slack_read_channel" in s["permissions"]["allow"]
    for rule in ("Edit(./scripts/**)", "Edit(./state/debriefs.json)", "Edit(./state/open_roles.json)",
                 "Edit(./state/created_pages.json)",
                 "mcp__e15988d3-3d1a-4fb0-927a-1a558d10e036__notion-move-pages"):
        assert rule in s["permissions"]["deny"]
