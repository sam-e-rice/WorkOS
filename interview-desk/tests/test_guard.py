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
