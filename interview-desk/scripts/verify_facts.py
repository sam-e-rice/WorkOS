#!/usr/bin/env python3
"""Check a submission draft's money, percentages, notice period and employers against transcript + CV."""
import argparse
import json
import re
import sys
from pathlib import Path

from textnorm import norm

MULT = {"k": 1_000, "grand": 1_000, "thousand": 1_000, "m": 1_000_000, "million": 1_000_000}
SUFFIX = r"(k|m|grand|thousand|million)\b"
RANGE_RE = re.compile(
    r"\$?(\d+(?:\.\d+)?)\s*(?:to|and|-|–)\s*\$?(\d+(?:\.\d+)?)\s?" + SUFFIX, re.I)
MONEY_RE = re.compile(r"(?<![\w.,])(\$)?\s?(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s?(?:" + SUFFIX + ")?", re.I)
PCT_RE = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)\s?(?:%|percent\b)", re.I)
WORDNUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
           "eight": 8, "ten": 10, "twelve": 12}
NOTICE_RE = re.compile(r"\b(\d+|" + "|".join(WORDNUM) + r")[\s-]+(week|month)s?\b", re.I)
NAME = r"([A-Z][\w&.'-]*(?:\s+[A-Z][\w&.'-]*){0,3})"
AT_LABEL_RE = re.compile(r"\bAt " + NAME + ":")
AT_INLINE_RE = re.compile(r"\bat " + NAME)


def money(text: str, loose: bool = False) -> set[int]:
    vals = set()
    for m in RANGE_RE.finditer(text):
        mult = MULT[m[3].lower()]
        vals |= {round(float(m[1]) * mult), round(float(m[2]) * mult)}
    for m in MONEY_RE.finditer(RANGE_RE.sub(" ", text)):
        dollar, num, suf = m[1], m[2], m[3]
        if not (dollar or suf or (loose and "," in num)):
            continue
        vals.add(round(float(num.replace(",", "")) * (MULT[suf.lower()] if suf else 1)))
    return vals


def percents(text: str) -> set[float]:
    return {float(m[1]) for m in PCT_RE.finditer(text)}


def notices(text: str) -> set[tuple[int, str]]:
    out = set()
    for m in NOTICE_RE.finditer(text):
        n = m[1].lower()
        out.add((int(n) if n.isdigit() else WORDNUM[n], m[2].lower()))
    return out


def employers(draft: str) -> list[str]:
    found = [m[1] for m in AT_LABEL_RE.finditer(draft)]
    for line in draft.splitlines():
        if "current" in line.lower():
            found += [m[1] for m in AT_INLINE_RE.finditer(line)]
    return list(dict.fromkeys(e.strip(" .") for e in found))


def check(draft: str, sources: str, allow=()) -> list[dict]:
    out = []
    src_money = money(sources, loose=True)
    out += [{"kind": "money", "value": v} for v in sorted(money(draft) - src_money)]
    out += [{"kind": "percent", "value": v} for v in sorted(percents(draft) - percents(sources))]
    notice_lines = "\n".join(l for l in draft.splitlines() if "notice" in l.lower())
    out += [{"kind": "notice", "value": f"{n} {u}"}
            for n, u in sorted(notices(notice_lines) - notices(sources))]
    src_norm = f" {norm(sources)} "
    allowed = {norm(a) for a in allow}
    for e in employers(draft):
        ne = norm(e)
        if ne not in allowed and f" {ne} " not in src_norm:
            out.append({"kind": "employer", "value": e})
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="verify_facts.py")
    p.add_argument("draft")
    p.add_argument("--segments", required=True)
    p.add_argument("--cv")
    p.add_argument("--allow", action="append", default=[])
    args = p.parse_args(argv)
    segs = json.loads(Path(args.segments).read_text())
    sources = " ".join(s["text"] for s in segs)
    if args.cv and Path(args.cv).exists():
        sources += "\n" + Path(args.cv).read_text()
    out = check(Path(args.draft).read_text(), sources, args.allow)
    if out:
        print(json.dumps({"unsupported": out}))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
