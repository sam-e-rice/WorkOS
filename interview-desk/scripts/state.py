#!/usr/bin/env python3
"""CLI over statelib. The only way the agent changes Interview Desk state."""
import argparse
import json
import os
import subprocess
import sys

import replies
import roles
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
    ar = sub.add_parser("apply-reply")
    ar.add_argument("key")
    ar.add_argument("--text", required=True)
    ar.add_argument("--user", required=True)
    ar.add_argument("--ts")
    dm = sub.add_parser("dm-reply")
    dm.add_argument("--text", required=True)
    dm.add_argument("--user", required=True)
    dm.add_argument("--ts", required=True)
    sr = sub.add_parser("save-roles")
    sr.add_argument("--data", required=True)
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
        elif args.cmd == "apply-reply":
            slack = json.loads((sl.root() / "config" / "slack.json").read_text())
            print(json.dumps(replies.apply_reply(args.key, args.text, args.user, args.ts,
                                                 roles.load_roles(), slack.get("sam_user_id", ""))))
        elif args.cmd == "dm-reply":
            slack = json.loads((sl.root() / "config" / "slack.json").read_text())
            print(json.dumps(replies.route_dm(args.text, args.user, args.ts,
                                              roles.load_roles(), slack.get("sam_user_id", ""))))
        elif args.cmd == "save-roles":
            roles.save_roles(json.loads(args.data))
    except sl.StateError as e:
        print(str(e), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
