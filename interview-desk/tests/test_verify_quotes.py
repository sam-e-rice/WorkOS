import json
from pathlib import Path

import transcript as tr
import verify_quotes as vq
from helpers import run_script

FIX = Path(__file__).parent / "fixtures"
SAM = "Sam Rice | We Are Eight"


def segs():
    return tr.parse_transcript((FIX / "transcript_md.txt").read_text())["segments"]


def test_exact_quote_passes():
    md = '> "we cut checkout latency by 40%" (Jane Doe, 00:00:45)\n'
    assert vq.check(md, segs(), "Jane Doe", SAM) == []


def test_quote_spanning_continuation_passes():
    md = '> "by 40%. So basically: it was a two year project" (Jane Doe, 00:00:45)\n'
    assert vq.check(md, segs(), "Jane Doe", SAM) == []


def test_paraphrase_fails():
    md = '> "we halved checkout latency" (Jane Doe, 00:00:45)\n'
    [f] = vq.check(md, segs(), "Jane Doe", SAM)
    assert f["reason"] == "not found in the candidate's words"


def test_sams_words_attributed_to_candidate_fail():
    md = '> "Thanks for jumping on" (Jane Doe, 00:00:00)\n'
    assert len(vq.check(md, segs(), "Jane Doe", SAM)) == 1


def test_quote_attributed_to_sam_fails():
    md = '> "Thanks for jumping on" (Sam Rice, 00:00:00)\n'
    [f] = vq.check(md, segs(), "Jane Doe", SAM)
    assert f["reason"].startswith("attributed to Sam Rice")


def test_first_name_speaker_label_still_verifies():
    s = [{"speaker": "Jane", "start": "00:01:00", "text": "I want a smaller team."}]
    md = '> "I want a smaller team" (Jane Doe, 00:01:00)\n'
    assert vq.check(md, s, "Jane Doe", SAM) == []


def test_partial_word_does_not_match():
    md = '> "ut checkout" (Jane Doe, 00:00:45)\n'
    assert len(vq.check(md, segs(), "Jane Doe", SAM)) == 1


def test_malformed_quote_line_fails():
    md = '> "we cut checkout latency by 40%" - Jane Doe\n'
    [f] = vq.check(md, segs(), "Jane Doe", SAM)
    assert f["reason"] == "not in quote format"


def test_one_word_quote_fails():
    md = '> "worries" (Jane Doe, 00:00:00)\n'
    [f] = vq.check(md, segs(), "Jane Doe", SAM)
    assert f["reason"] == "too short to verify"


def test_wrong_timestamp_fails():
    md = '> "we cut checkout latency by 40%" (Jane Doe, 00:09:00)\n'
    assert len(vq.check(md, segs(), "Jane Doe", SAM)) == 1


def test_drop_removes_only_failing_lines():
    md = ('Fit: strong.\n'
          '> "we cut checkout latency by 40%" (Jane Doe, 00:00:45)\n'
          '> "we halved checkout latency" (Jane Doe, 00:00:45)\n')
    out = vq.drop(md, vq.check(md, segs(), "Jane Doe", SAM))
    assert "halved" not in out
    assert "40%" in out and "Fit: strong." in out


def test_cli_exit_codes_and_drop(desk, tmp_path):
    seg_file = tmp_path / "segs.json"
    seg_file.write_text(json.dumps(segs()))
    md = tmp_path / "brief.md"
    md.write_text('> "we halved checkout latency" (Jane Doe, 00:00:45)\n')
    r = run_script("verify_quotes.py", str(md), str(seg_file), "--speaker", "Jane Doe")
    assert r.returncode == 1
    assert json.loads(r.stdout)["failures"][0]["quote"] == "we halved checkout latency"
    r = run_script("verify_quotes.py", str(md), str(seg_file), "--speaker", "Jane Doe", "--drop")
    assert r.returncode == 0
    assert "halved" not in md.read_text()
