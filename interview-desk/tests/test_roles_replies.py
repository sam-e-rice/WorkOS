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


# Connector posts carry Sam's own user id; only the marker/footer tells them apart.
DESK_POSTS = [
    "🤖 Interview Desk · Jane Doe - submit? yes / no",
    ":robot_face: Interview Desk · Base or package?",
    "yes\n*Sent using* <@U0BFYH9F2KW|Claude>",
]


@pytest.mark.parametrize("text", DESK_POSTS)
def test_desk_own_posts_never_approve(desk, text):
    awaiting(desk, "r1")
    assert replies.apply_reply("doc1", text, SAM, "101.0", ROLES, SAM)["action"] == "ignore"
    assert sl.load()["items"]["doc1"]["status"] == "awaiting_decision"


@pytest.mark.parametrize("text", DESK_POSTS)
def test_desk_own_posts_never_answer_needs_input(desk, text):
    awaiting(desk, "r1")
    replies.apply_reply("doc1", "yes", SAM, "100.5", ROLES, SAM)
    sl.set_status("doc1", "needs_input", {"question": "Base or package?"})
    assert replies.apply_reply("doc1", text, SAM, "101.0", ROLES, SAM)["action"] == "ignore"
    assert sl.load()["items"]["doc1"]["status"] == "needs_input"

def test_already_seen_reply_is_ignored(desk):
    awaiting(desk, "r1")
    sl.upsert("doc1", {"last_reply_ts": "105.0"})
    assert replies.apply_reply("doc1", "yes", SAM, "104.0", ROLES, SAM)["action"] == "ignore"


def test_answer_resumes_needs_input(desk):
    awaiting(desk, "r1")
    replies.apply_reply("doc1", "yes", SAM, "100.5", ROLES, SAM)
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


def test_yes_records_approval_and_frozen_parent(desk):
    awaiting(desk, "r1")
    replies.apply_reply("doc1", "yes", SAM, "101.0", ROLES, SAM)
    item = sl.load()["items"]["doc1"]
    assert (item["approved_by"], item["approved_ts"], item["approved_parent"]) == (SAM, "101.0", "p1")


def test_yes_for_a_closed_role_is_refused(desk):
    awaiting(desk, "r4")
    assert replies.apply_reply("doc1", "yes", SAM, "101.0", ROLES, SAM)["action"] == "refuse"
    assert sl.load()["items"]["doc1"]["status"] == "awaiting_decision"


# Replies Sam posts in the DM itself, not in a candidate's thread.
def waiting_item(doc_id, name, slack_ts="100.0"):
    sl.upsert(doc_id, {"candidate": name, "role_row": "r1"})
    sl.set_status(doc_id, "awaiting_decision", {"slack_ts": slack_ts})


def test_dm_reply_applies_to_the_only_waiting_item(desk):
    waiting_item("doc1", "Jane Doe")
    out = replies.route_dm("yes", SAM, "101.0", ROLES, SAM)
    assert (out["action"], out["key"]) == ("draft", "doc1")
    assert sl.load()["items"]["doc1"]["status"] == "drafting"


def test_dm_reply_with_several_waiting_asks_which(desk):
    waiting_item("doc1", "Jane Doe")
    waiting_item("doc2", "John Roe")
    out = replies.route_dm("yes", SAM, "101.0", ROLES, SAM)
    assert out["action"] == "ask"
    assert "Jane Doe" in out["message"] and "John Roe" in out["message"]
    assert {i["status"] for i in sl.load()["items"].values()} == {"awaiting_decision"}


def test_dm_reply_is_only_handled_once(desk):
    waiting_item("doc1", "Jane Doe")
    waiting_item("doc2", "John Roe")
    replies.route_dm("yes", SAM, "101.0", ROLES, SAM)
    assert replies.route_dm("yes", SAM, "101.0", ROLES, SAM)["action"] == "ignore"


def test_dm_reply_before_the_ask_is_ignored(desk):
    waiting_item("doc1", "Jane Doe", slack_ts="200.0")
    assert replies.route_dm("yes", SAM, "150.0", ROLES, SAM)["action"] == "ignore"
    assert sl.load()["items"]["doc1"]["status"] == "awaiting_decision"


def test_dm_reply_with_nothing_waiting_is_ignored(desk):
    assert replies.route_dm("yes", SAM, "101.0", ROLES, SAM)["action"] == "ignore"


@pytest.mark.parametrize("user,text", [("U_OTHER", "yes"), (SAM, DESK_POSTS[2])])
def test_dm_reply_ignores_others_and_desk_posts(desk, user, text):
    waiting_item("doc1", "Jane Doe")
    assert replies.route_dm(text, user, "101.0", ROLES, SAM)["action"] == "ignore"
    assert sl.load()["items"]["doc1"]["status"] == "awaiting_decision"


def test_cli_dm_reply(desk):
    waiting_item("doc1", "Jane Doe")
    (desk / "config" / "slack.json").write_text(json.dumps({"sam_user_id": SAM}))
    roles.save_roles(ROLES)
    r = run_script("state.py", "dm-reply", "--text", "yes", "--user", SAM, "--ts", "101.0")
    assert json.loads(r.stdout)["key"] == "doc1"


def test_cli_roles_match(desk):
    run_script("state.py", "save-roles", "--data", json.dumps(ROLES))
    r = run_script("roles.py", "match", "--text", "Chief Engineer chat")
    assert json.loads(r.stdout) == {"match": "r1"}
