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
