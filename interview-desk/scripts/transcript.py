#!/usr/bin/env python3
"""Parse Gemini hang titles and Transcript-tab text into segments."""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import statelib as sl
from textnorm import same_person

AUCKLAND = ZoneInfo("Pacific/Auckland")
TS_RE = re.compile(r"^\s*(?:#{1,6}\s*)?(?:\*\*)?(\d{1,2}:\d{2}:\d{2})(?:\*\*)?\s*$")
SPK_RE = re.compile(r"^\s*(?:\*\*)?([A-Z0-9][^:*\n]{0,79}?):(?:\*\*)?\s+(\S.*)$")
LABEL_ONLY_RE = re.compile(r"^\s*(?:\*\*)?([A-Z0-9][^:*\n]{0,79}?):(?:\*\*)?\s*$")
END_RE = re.compile(r"Transcription ended after (\d{1,2}:\d{2}:\d{2})")


def patterns() -> dict:
    return json.loads((sl.root() / "config" / "patterns.json").read_text())


def parse_title(title: str, regex: str | None = None) -> dict | None:
    m = re.match(regex or patterns()["title_regex"], title.strip())
    if not m:
        return None
    local = datetime.strptime(m["when"], "%Y/%m/%d %H:%M").replace(tzinfo=AUCKLAND)
    return {"name": m["name"].strip(), "meeting_at": sl.iso(local)}


def _speaker_counts(lines: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for line in lines:
        m = SPK_RE.match(line) or LABEL_ONLY_RE.match(line)
        if m and not TS_RE.match(line):
            label = m[1].strip()
            counts[label] = counts.get(label, 0) + 1
    return counts


def parse_transcript(text: str, known: list[str] | tuple = ()) -> dict:
    lines = text.splitlines()
    # A label is a speaker if it recurs or names a known attendee; other one-off
    # "Word: text" lines are continuations.
    counts = _speaker_counts(lines)
    speakers = {s for s, c in counts.items() if c >= 2 or any(same_person(s, k) for k in known)}
    segs: list[dict] = []
    start, ended = "00:00:00", None
    for line in lines:
        e = END_RE.search(line)
        if e:
            ended = e[1].zfill(8)
            break
        if not line.strip():
            continue
        t = TS_RE.match(line)
        if t:
            start = t[1].zfill(8)
            continue
        m = SPK_RE.match(line)
        label_only = LABEL_ONLY_RE.match(line)
        if m and m[1].strip() in speakers:
            segs.append({"speaker": m[1].strip(), "start": start, "text": m[2].strip()})
        elif label_only and label_only[1].strip() in speakers:
            segs.append({"speaker": label_only[1].strip(), "start": start, "text": ""})
        elif segs:
            segs[-1]["text"] = (segs[-1]["text"] + " " + line.strip().strip("*").strip()).strip()
    # No segments means the tab isn't a transcript we can read; never treat it as ready.
    return {"segments": segs, "complete": ended is not None and bool(segs), "ended_after": ended}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="transcript.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("title")
    t.add_argument("title")
    s = sub.add_parser("segments")
    s.add_argument("file")
    s.add_argument("--speaker", action="append", default=[])
    args = p.parse_args(argv)
    if args.cmd == "title":
        print(json.dumps(parse_title(args.title)))
    else:
        print(json.dumps(parse_transcript(Path(args.file).read_text(), args.speaker), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
