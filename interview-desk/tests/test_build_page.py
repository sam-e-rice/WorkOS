import json

import pytest

import build_page as bp
from helpers import run_script

DRAFT = """# Jane Doe | Chief Engineer
**Current:** Staff Engineer at Canva | **Location:** Sydney
**Salary:** $180k base | **Notice:** 4 weeks

## 🔍 Overview
Jane led the payments rebuild.

## 🧩 Why Jane Fits At EQL
- **Scale:** ran a 12-person team.

## 📍 Current Situation
At Canva: steady.
"""
PDF = '<pdf src="file-upload://f1"></pdf>'


def test_header_becomes_callout_and_title_line_dropped():
    out = bp.build(DRAFT, "Jane Doe", "Chief Engineer", PDF)
    assert out["title"] == "Jane Doe | Chief Engineer"
    assert out["content"].startswith('<callout icon="📌" color="gray_bg">\n\t**Current:**')
    assert "# Jane Doe | Chief Engineer" not in out["content"]
    assert out["content"].rstrip().endswith("## 📎 CV\n\n" + PDF)


def test_existing_callout_is_not_wrapped_twice():
    draft = DRAFT.replace("**Current:** Staff Engineer at Canva | **Location:** Sydney\n**Salary:** $180k base | **Notice:** 4 weeks",
                          '<callout icon="📌" color="gray_bg">\n\t**Current:** Staff Engineer\n</callout>')
    out = bp.build(draft, "Jane Doe", "Chief Engineer")
    assert out["content"].count("<callout") == 1


def test_docx_cv_as_file_block():
    out = bp.build(DRAFT, "Jane Doe", "Chief Engineer", '<file src="file-upload://f2"></file>')
    assert '<file src="file-upload://f2"></file>' in out["content"]


def test_missing_section_raises():
    with pytest.raises(bp.BuildError, match="Current Situation"):
        bp.build(DRAFT.split("## 📍")[0], "Jane Doe", "Chief Engineer")


@pytest.mark.parametrize("bad", ['<page url="x">HOMEBASE</page>', '<database url="y">DB</database>'])
def test_forbidden_tags_raise(bad):
    with pytest.raises(bp.BuildError, match="move"):
        bp.build(DRAFT + bad, "Jane Doe", "Chief Engineer")
    with pytest.raises(bp.BuildError, match="move"):
        bp.build(DRAFT, "Jane Doe", "Chief Engineer", bad)


def test_cli(desk, tmp_path):
    d = tmp_path / "draft.md"
    d.write_text(DRAFT)
    r = run_script("build_page.py", "--draft", str(d), "--candidate", "Jane Doe", "--role", "Chief Engineer",
                   "--cv-markdown", PDF)
    assert json.loads(r.stdout)["title"] == "Jane Doe | Chief Engineer"
    d.write_text("no sections")
    assert run_script("build_page.py", "--draft", str(d), "--candidate", "J", "--role", "R").returncode == 2
