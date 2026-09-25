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


def test_cli_cannot_approve_a_draft(desk):
    run_script("state.py", "upsert", "d1", "--data", "{}")
    run_script("state.py", "set", "d1", "awaiting_decision")
    r = run_script("state.py", "set", "d1", "drafting", "--data", '{"approved_by": "U_SAM"}')
    assert r.returncode == 2
    assert "approval" in r.stderr
