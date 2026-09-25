import json
from pathlib import Path

import transcript as tr
import verify_facts as vf
from helpers import run_script

FIX = Path(__file__).parent / "fixtures"
CV = "Jane Doe. Staff Engineer, Canva (2021-present). Super 12% salary sacrifice."
DRAFT = """**Current:** Staff Engineer at Canva | **Location:** Sydney
**Salary:** $180k base + 12% super | **Notice:** 4 weeks

At Canva: Jane led the payments rebuild and cut checkout latency by **40%**.
Why EQL? She wants a smaller team.
"""


def sources():
    segs = tr.parse_transcript((FIX / "transcript_md.txt").read_text())["segments"]
    return " ".join(s["text"] for s in segs) + "\n" + CV


def test_supported_draft_passes():
    assert vf.check(DRAFT, sources(), allow=["EQL"]) == []


def test_unsupported_salary_flagged():
    out = vf.check(DRAFT.replace("$180k", "$200k"), sources(), allow=["EQL"])
    assert {"kind": "money", "value": 200000} in out


def test_spoken_range_supports_written_range():
    draft = DRAFT.replace("$180k base", "$170–190k base")
    assert vf.check(draft, sources(), allow=["EQL"]) == []


def test_unsupported_notice_flagged():
    out = vf.check(DRAFT.replace("4 weeks", "8 weeks"), sources(), allow=["EQL"])
    assert {"kind": "notice", "value": "8 week"} in out


def test_unsupported_employer_flagged():
    out = vf.check(DRAFT.replace("at Canva |", "at Atlassian |"), sources(), allow=["EQL"])
    assert {"kind": "employer", "value": "Atlassian"} in out


def test_unsupported_percent_flagged():
    out = vf.check(DRAFT.replace("40%", "60%"), sources(), allow=["EQL"])
    assert {"kind": "percent", "value": 60.0} in out


def test_bare_salary_number_flagged():
    out = vf.check(DRAFT.replace("$180k base", "NZD 210000 base"), sources(), allow=["EQL"])
    assert {"kind": "money", "value": 210000} in out


def test_employer_label_and_works_for_flagged():
    draft = DRAFT + "Current employer: Fonterra\nShe works for Fonterra.\n"
    out = vf.check(draft, sources(), allow=["EQL"])
    assert {"kind": "employer", "value": "Fonterra"} in out


def test_word_notice_flagged():
    out = vf.check(DRAFT.replace("4 weeks", "seven weeks"), sources(), allow=["EQL"])
    assert {"kind": "notice", "value": "7 week"} in out


def test_money_parsing():
    assert vf.money("$180,000 or 1.5m or 95k") == {180000, 1500000, 95000}
    assert vf.money("40% of 2019") == set()
    assert vf.money("about 180,000", loose=True) == {180000}


def test_cli(desk, tmp_path):
    segs = tr.parse_transcript((FIX / "transcript_md.txt").read_text())["segments"]
    (tmp_path / "s.json").write_text(json.dumps(segs))
    (tmp_path / "cv.txt").write_text(CV)
    (tmp_path / "d.md").write_text(DRAFT.replace("$180k", "$250k"))
    r = run_script("verify_facts.py", str(tmp_path / "d.md"), "--segments", str(tmp_path / "s.json"),
                   "--cv", str(tmp_path / "cv.txt"), "--allow", "EQL")
    assert r.returncode == 1
    assert {"kind": "money", "value": 250000} in json.loads(r.stdout)["unsupported"]
