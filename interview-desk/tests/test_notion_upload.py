import json

import pytest

import notion_upload as nu
import statelib as sl
from helpers import run_script

URL = "https://api.notion.com/v1/mcp/file_uploads/abc/send"
APPROVAL = {"approved_by": "U1", "approved_ts": "1.0", "approved_parent": "p1"}


class FakeResponse:
    status = 200

    def __init__(self, body):
        self.body = body

    def read(self):
        return json.dumps(self.body).encode()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def approved_item(desk, cv_name="Jane O'Brien CV.pdf", candidate="Jane O'Brien"):
    cv = desk / cv_name
    cv.write_bytes(b"%PDF-1.4 fake")
    sl.upsert("doc1", {"candidate": candidate, "cv_path": str(cv)})
    sl.set_status("doc1", "awaiting_decision")
    sl.set_status("doc1", "drafting", approval=APPROVAL)
    return cv


def test_upload_sends_the_items_cv(desk):
    approved_item(desk)
    seen = {}

    def opener(req, timeout):
        seen["url"], seen["body"], seen["headers"] = req.full_url, req.data, dict(req.header_items())
        return FakeResponse({"file_upload_id": "f1", "markdown_source": "file-upload://f1",
                             "suggested_markdown": '<pdf src="file-upload://f1"></pdf>'})

    out = nu.upload("doc1", URL, {"Authorization": "Bearer t"}, opener=opener)
    assert out["suggested_markdown"] == '<pdf src="file-upload://f1"></pdf>'
    assert out["filename"] == "Jane O'Brien CV.pdf"
    assert b"%PDF-1.4 fake" in seen["body"]
    assert seen["headers"]["Authorization"] == "Bearer t"


def test_docx_cv_keeps_its_type(desk):
    approved_item(desk, cv_name="Resume.docx", candidate="Jane Doe")
    out = nu.upload("doc1", URL, {}, opener=lambda req, timeout: FakeResponse({"suggested_markdown": "x"}))
    assert out["filename"] == "Jane Doe CV.docx"
    assert out["content_type"].endswith("wordprocessingml.document")


def test_non_notion_url_refused(desk):
    approved_item(desk)
    with pytest.raises(sl.StateError, match="Notion"):
        nu.upload("doc1", "https://evil.example/upload", {}, opener=None)


def test_unapproved_item_refused(desk):
    sl.upsert("doc1", {"cv_path": "/tmp/x.pdf"})
    sl.set_status("doc1", "awaiting_decision")
    with pytest.raises(sl.StateError, match="approved"):
        nu.upload("doc1", URL, {}, opener=None)


def test_cli_refusal_exits_2(desk):
    approved_item(desk)
    r = run_script("notion_upload.py", "doc1", "--url", "https://evil.example/x")
    assert r.returncode == 2
