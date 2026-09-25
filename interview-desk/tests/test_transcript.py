import json
from pathlib import Path

import pytest

import transcript as tr
from helpers import run_script
from textnorm import norm, tokens

FIX = Path(__file__).parent / "fixtures"


def test_norm_folds_accents_punctuation_and_underscores():
    assert norm("José O’Brien_CV!") == "jose o brien cv"
    assert tokens("Sam Rice | We Are Eight") == ["sam", "rice", "we", "are", "eight"]


def test_title_nzst(desk):
    t = "Hang Out With Sam Rice (Jane Doe) – 2026/09/20 14:00 NZST – Notes by Gemini"
    assert tr.parse_title(t) == {"name": "Jane Doe", "meeting_at": "2026-09-20T02:00:00Z"}


def test_title_nzdt_after_dst_switch(desk):
    t = "Hang Out With Sam Rice (Jane Doe) – 2026/09/28 10:00 NZDT – Notes by Gemini"
    assert tr.parse_title(t)["meeting_at"] == "2026-09-27T21:00:00Z"


def test_title_with_hyphens_is_rejected(desk):
    assert tr.parse_title("Hang Out With Sam Rice (Jane Doe) - 2026/09/20 14:00 NZST - Notes by Gemini") is None


def test_title_other_meeting_is_rejected(desk):
    assert tr.parse_title("Time with Danny (Jane Doe) – 2026/09/20 14:00 AEST – Notes by Gemini") is None


@pytest.mark.parametrize("name", ["transcript_md.txt", "transcript_plain.txt"])
def test_segments_both_formats(name):
    out = tr.parse_transcript((FIX / name).read_text())
    segs = out["segments"]
    assert [s["speaker"] for s in segs] == [
        "Sam Rice | We Are Eight", "Jane Doe", "Jane Doe", "Sam Rice | We Are Eight", "Jane Doe"]
    assert segs[2]["start"] == "00:00:45"
    assert out["complete"] is True
    assert out["ended_after"] == "00:12:31"


def test_continuation_line_that_looks_like_a_speaker_stays_attached():
    segs = tr.parse_transcript((FIX / "transcript_md.txt").read_text())["segments"]
    assert segs[2]["text"].endswith("So basically: it was a two year project.")
    assert "So basically" not in {s["speaker"] for s in segs}


def test_disclaimer_after_end_marker_is_ignored():
    segs = tr.parse_transcript((FIX / "transcript_md.txt").read_text())["segments"]
    assert "computer generated" not in segs[-1]["text"]


def test_incomplete_transcript():
    text = (FIX / "transcript_md.txt").read_text().split("Transcription ended")[0]
    assert tr.parse_transcript(text)["complete"] is False


def test_cli_segments(desk):
    r = run_script("transcript.py", "segments", str(FIX / "transcript_plain.txt"))
    assert json.loads(r.stdout)["complete"] is True


def test_candidate_who_speaks_once_is_kept_when_known():
    text = ("Sam Rice | We Are Eight: Hi there.\n"
            "Jane Doe: I built the payments platform.\n"
            "Sam Rice | We Are Eight: Great, thanks.\n"
            "Transcription ended after 00:05:00\n")
    segs = tr.parse_transcript(text, known=["Jane Doe"])["segments"]
    assert [s["speaker"] for s in segs] == ["Sam Rice | We Are Eight", "Jane Doe", "Sam Rice | We Are Eight"]


def test_label_on_its_own_line():
    text = ("**Sam Rice | We Are Eight:**\nHi there.\n**Jane Doe:**\nHappy to chat.\n"
            "**Sam Rice | We Are Eight:**\nGreat.\n**Jane Doe:**\nThanks.\n"
            "Transcription ended after 00:05:00\n")
    segs = tr.parse_transcript(text)["segments"]
    assert [(s["speaker"], s["text"]) for s in segs][:2] == [
        ("Sam Rice | We Are Eight", "Hi there."), ("Jane Doe", "Happy to chat.")]


def test_no_segments_is_not_complete():
    out = tr.parse_transcript("just notes\nTranscription ended after 00:01:00\n")
    assert out["segments"] == []
    assert out["complete"] is False
