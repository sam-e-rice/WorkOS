import json
import re

from helpers import PROJECT

SKILLS = PROJECT / ".claude" / "skills"
RUN = SKILLS / "post-hang-debrief" / "SKILL.md"
SPIKE_PAGE = "3e6d44192fa081298593e3cb6f3cd2ff"


def test_pinned_skills_present_and_renamed():
    for name in ("ids-recruitment-submissions", "ids-sam-rice-voice", "ids-stop-slop"):
        text = (SKILLS / name / "SKILL.md").read_text()
        assert re.search(rf"^name: {name}$", text, re.M), name
    assert (SKILLS / "ids-recruitment-submissions" / "references" / "structure-and-rules.md").exists()
    assert (SKILLS / "ids-sam-rice-voice" / "references" / "client-facing.md").exists()


def test_run_skill_commands_match_the_allow_rule():
    text = RUN.read_text()
    commands = re.findall(r"`(\.venv/bin/python [^`]+)`", text)
    assert commands, "run skill lists no commands"
    for c in commands:
        assert c.startswith(".venv/bin/python scripts/"), c
        assert "&&" not in c and "|" not in c and "cd " not in c, c
    assert "/Users/" not in text


def test_run_skill_and_claude_md_carry_the_marker():
    assert "🤖 Interview Desk · " in RUN.read_text()
    assert "🤖 Interview Desk · " in (PROJECT / "CLAUDE.md").read_text()


def test_config_is_not_pointing_at_the_spike_page():
    assert SPIKE_PAGE not in (PROJECT / "config" / "notion.json").read_text()


def test_spike_files_removed():
    assert not (PROJECT / "scripts" / "spike.py").exists()
    assert not (PROJECT / "docs" / "spike-task-prompt.md").exists()
