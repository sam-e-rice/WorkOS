#!/usr/bin/env python3
"""Check brief quote blocks against the candidate's transcript segments."""
import argparse
import json
import re
import sys
from pathlib import Path

import transcript
from textnorm import norm, same_person

QUOTE_RE = re.compile(
    r'^>[ \t]*["“](?P<q>.+?)["”][ \t]*\((?P<who>[^,()]+),[ \t]*(?P<ts>\d{1,2}:\d{2}:\d{2})\)[ \t]*$',
    re.M,
)
QUOTE_LIKE_RE = re.compile(r'^>[ \t]*["“].*$', re.M)
MIN_TOKENS = 3
TS_SLACK = 60  # seconds either side of the run a quote's timestamp may fall


def _secs(ts: str) -> int:
    h, m, s = (int(x) for x in ts.split(":"))
    return h * 3600 + m * 60 + s


def candidate_runs(segments: list[dict], name: str, sam_label: str) -> list[tuple[str, int, int]]:
    """(normalised text, first start, last start) for each unbroken run of the candidate speaking."""
    runs, cur = [], []
    for s in segments + [{"speaker": sam_label, "start": "00:00:00", "text": ""}]:
        if norm(s["speaker"]) != norm(sam_label) and same_person(s["speaker"], name):
            cur.append(s)
        elif cur:
            runs.append((" ".join(norm(c["text"]) for c in cur), _secs(cur[0]["start"]), _secs(cur[-1]["start"])))
            cur = []
    return runs


def check(md: str, segments: list[dict], name: str, sam_label: str) -> list[dict]:
    runs = candidate_runs(segments, name, sam_label)
    fails = []
    matched = set()
    for m in QUOTE_RE.finditer(md):
        matched.add(m[0])
        q = norm(m["q"])
        who = m["who"].strip()
        ts = _secs(m["ts"])
        if norm(who) == norm(sam_label) or not same_person(who, name):
            fails.append({"quote": m["q"], "line": m[0], "reason": f"attributed to {who}, not the candidate"})
        elif len(q.split()) < MIN_TOKENS:
            fails.append({"quote": m["q"], "line": m[0], "reason": "too short to verify"})
        elif not any(f" {q} " in f" {text} " and first - TS_SLACK <= ts <= last + TS_SLACK
                     for text, first, last in runs):
            fails.append({"quote": m["q"], "line": m[0], "reason": "not found in the candidate's words"})
    for m in QUOTE_LIKE_RE.finditer(md):
        if m[0] not in matched:
            fails.append({"quote": m[0], "line": m[0], "reason": "not in quote format"})
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
