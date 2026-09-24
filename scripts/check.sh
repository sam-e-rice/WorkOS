#!/bin/sh
# The repository's one green check. Each case opens with `# test: <name>`; each failing case prints `FAIL <name>`; exit is non-zero if any fail.
cd "$(dirname "$0")/.." || exit 1
fails=0
fail() { echo "FAIL $1"; fails=$((fails + 1)); }

# test: skills_lock_is_json — skills-lock.json parses as JSON.
python3 -m json.tool skills-lock.json >/dev/null 2>&1 || fail skills_lock_is_json

# test: claude_skill_resolves — every .claude/skills entry resolves to a directory holding a SKILL.md.
for link in .claude/skills/*; do
  [ -f "$link/SKILL.md" ] || fail "claude_skill_resolves:$(basename "$link")"
done

# test: agent_skill_has_skill_md — every .agents/skills directory has a SKILL.md.
for dir in .agents/skills/*/; do
  [ -f "$dir/SKILL.md" ] || fail "agent_skill_has_skill_md:$(basename "$dir")"
done

# test: readme_lists_skill — every .agents/skills directory has its own bullet in README.md.
readme_bullet_names=$(grep -oE '^- `[^`]+`' README.md 2>/dev/null | sed -E 's/^- `//; s/`$//')
for dir in .agents/skills/*/; do
  name=$(basename "$dir")
  printf '%s\n' "$readme_bullet_names" | grep -qxF -- "$name" || fail "readme_lists_skill:$name"
done

[ "$fails" -eq 0 ] && echo "ok" || exit 1
