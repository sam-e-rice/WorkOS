"""Turn Sam's Slack thread replies into state transitions."""
import statelib as sl
from roles import describe, is_open, match_role, page_allowed

YES = {"yes", "y", "yep", "yeah", "submit"}
NO = {"no", "n", "nah", "nope", "park"}
NOT_A_NO = ("no worries", "no problem", "no rush", "no stress", "no dramas")
# The Slack connector posts as Sam's own user id, so the desk's messages are only
# distinguishable by the marker prefix or the "Sent using Claude" footer.
DESK_PREFIXES = ("🤖 Interview Desk ·", ":robot_face: Interview Desk ·")
SENT_USING = "*Sent using*"


def is_desk_post(text: str) -> bool:
    return text.lstrip().startswith(DESK_PREFIXES) or SENT_USING in text


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
    if item["status"] in sl.TERMINAL:
        return {"action": "ignore", "reason": f"status {item['status']}"}
    last = item.get("last_reply_ts")
    if ts and last and float(ts) <= float(last):
        return {"action": "ignore", "reason": "already seen"}
    if ts:
        sl.upsert(doc_id, {"last_reply_ts": ts})
    if not sam_user_id or user != sam_user_id:
        return {"action": "ignore", "reason": "not from Sam"}
    if is_desk_post(text):
        return {"action": "ignore", "reason": "desk's own post"}
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
    role = next((x for x in roles if x["id"] == role_row and is_open(x)), None)
    if not role:
        open_roles = ", ".join(describe(x) for x in roles if is_open(x))
        return {"action": "refuse",
                "message": f"No open role for this hang. Reply `yes <role or client>`. Open roles: {open_roles}"}
    if not page_allowed(role["submissions_page"]):
        return {"action": "refuse",
                "message": f"The Submissions page for {describe(role)} isn't in config/notion.json "
                           "submission_pages yet. Add it, then reply yes again."}
    # The approval freezes the Submissions page the guard will allow for this item.
    approval = {"approved_by": user, "approved_ts": ts or sl.iso(sl.utcnow()),
                "approved_parent": role["submissions_page"]}
    sl.set_status(doc_id, "drafting", {"role_row": role_row}, approval=approval)
    return {"action": "draft", "role_row": role_row}


WAITING = {"awaiting_decision", "parked", "needs_input"}


def route_dm(text: str, user: str, ts: str, roles: list[dict], sam_user_id: str) -> dict:
    """Handle a top-level DM message: apply it only when exactly one item is waiting."""
    if not sam_user_id or user != sam_user_id or is_desk_post(text):
        return {"action": "ignore", "reason": "not from Sam"}
    data = sl.load()
    last = data.get("dm_last_ts")
    if last and float(ts) <= float(last):
        return {"action": "ignore", "reason": "already seen"}
    data["dm_last_ts"] = ts
    sl.save(data)
    # Only items the desk had already asked about when Sam wrote this.
    waiting = [(d, i) for d, i in data["items"].items()
               if i["status"] in WAITING and i.get("slack_ts") and float(i["slack_ts"]) < float(ts)]
    if not waiting:
        return {"action": "ignore", "reason": "nothing waiting"}
    if len(waiting) > 1:
        names = ", ".join(i.get("candidate") or d for d, i in waiting)
        return {"action": "ask",
                "message": f"Several candidates are waiting ({names}). Reply in the candidate's thread so I know who you mean."}
    doc_id = waiting[0][0]
    return {"key": doc_id, **apply_reply(doc_id, text, user, ts, roles, sam_user_id)}
