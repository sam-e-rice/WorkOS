#!/bin/sh
# The repository's one green check. Each failing case prints `FAIL <name>`; exit is non-zero if any fail.
cd "$(dirname "$0")/.." || exit 1
fails=0
fail() { echo "FAIL $1"; fails=$((fails + 1)); }

# skills-lock.json parses as JSON.
python3 -m json.tool skills-lock.json >/dev/null 2>&1 || fail skills_lock_is_json

# Every .claude/skills entry resolves to a directory holding a SKILL.md.
for link in .claude/skills/*; do
  [ -f "$link/SKILL.md" ] || fail "claude_skill_resolves:$(basename "$link")"
done

# Every .agents/skills directory has a SKILL.md.
for dir in .agents/skills/*/; do
  [ -f "$dir/SKILL.md" ] || fail "agent_skill_has_skill_md:$(basename "$dir")"
done

[ "$fails" -eq 0 ] && echo "ok" || exit 1
