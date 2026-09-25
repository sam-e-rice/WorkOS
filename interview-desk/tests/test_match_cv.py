import json
import os

import docx
import pytest

import match_cv
from helpers import run_script

MEETING = "2026-09-20T02:00:00Z"
MEETING_TS = 1789869600  # 2026-09-20T02:00:00Z


@pytest.fixture
def cvs(tmp_path, monkeypatch):
    d = tmp_path / "CVs"
    d.mkdir()
    texts = {}

    def add(name, text, content=None, days_off=0):
        p = d / name
        p.write_bytes((content or name).encode())
        os.utime(p, (MEETING_TS + days_off * 86400,) * 2)
        texts[name] = text
        return p

    monkeypatch.setattr(match_cv, "extract_text", lambda p: texts[p.name])
    return d, add


def test_email_in_text_wins(desk, cvs):
    d, add = cvs
    add("Resume.pdf", "Contact: jane@example.com")
    add("Jane Doe CV.pdf", "Jane Doe engineer")
    out = match_cv.match(d, "Jane Doe", "jane@example.com", MEETING)
    assert out["match"].endswith("Resume.pdf")


def test_identical_duplicates_are_one_match(desk, cvs):
    d, add = cvs
    add("Jane Doe CV.pdf", "Jane Doe", content="same-bytes")
    add("Jane Doe CV (1).pdf", "Jane Doe", content="same-bytes", days_off=1)
    out = match_cv.match(d, "Jane Doe", None, MEETING)
    assert out["match"].endswith("Jane Doe CV (1).pdf")


def test_two_different_cvs_are_ambiguous(desk, cvs):
    d, add = cvs
    add("Jane Doe CV.pdf", "v1", content="a")
    add("Jane_Doe_Resume.pdf", "v2", content="b")
    out = match_cv.match(d, "Jane Doe", None, MEETING)
    assert len(out["ambiguous"]) == 2


def test_name_found_in_text_only(desk, cvs):
    d, add = cvs
    add("20260730 - Resume.pdf", "JANE DOE\nStaff Engineer")
    assert match_cv.match(d, "Jane Doe", None, MEETING)["match"].endswith("Resume.pdf")


def test_outside_window_is_ignored(desk, cvs):
    d, add = cvs
    add("Jane Doe CV.pdf", "Jane Doe", days_off=45)
    assert match_cv.match(d, "Jane Doe", None, MEETING) == {"none": True}


def test_first_name_only_does_not_match_by_filename(desk, cvs):
    d, add = cvs
    add("Jane CV.pdf", "nothing useful")
    assert match_cv.match(d, "Jane", None, MEETING) == {"none": True}


def test_cli_with_real_docx_copies_text(desk, tmp_path, monkeypatch):
    d = tmp_path / "real"
    d.mkdir()
    doc = docx.Document()
    doc.add_paragraph("Jane Doe - jane@example.com - Staff Engineer at Canva")
    p = d / "Resume.docx"
    doc.save(p)
    os.utime(p, (MEETING_TS,) * 2)
    r = run_script("match_cv.py", "--name", "Jane Doe", "--email", "jane@example.com",
                   "--meeting-at", MEETING, "--doc-id", "doc1", "--dir", str(d))
    out = json.loads(r.stdout)
    assert out["match"].endswith("Resume.docx")
    assert "Canva" in (desk / out["text"]).read_text()
