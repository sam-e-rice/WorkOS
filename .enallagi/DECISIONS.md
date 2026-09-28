# DECISIONS

Earned rules first, then rejected findings, then archived blocks.

`## Earned rules` is every rule this loop paid for, one dated line each, written by the adjudicator.
Read it with `sed -n '/^## Earned rules/,/^## Rejected findings/p' .enallagi/DECISIONS.md` at the
start of every task. A line carries the `enallagi eval --gate <name>` run that admitted it or the
command that showed what it cost, and names a file, a command or a hook.

`## Rejected findings` is every proposal the adjudicator killed, one line each, with the command
that refutes it. Read it with `sed -n '/^## Rejected findings/,/^## \[T-/p' .enallagi/DECISIONS.md` and
never read past that range.

Below it, completed task blocks, verbatim, moved out of .enallagi/TASKS.md once `done` by
`enallagi run`. Each block is the implementer's and the verifier's own words, never summarised on
the way in.

## Earned rules

<!-- - [YYYY-MM-DD] <what went wrong> → <the rule instead> (`<the --gate run or the command>`) -->

## Rejected findings

<!-- - [YYYY-MM-DD] <the claim in one sentence> — refuted by `<command>`: <the output that refutes it> -->

## [T-001] the repository has no README naming the skills it carries
scope: README.md, scripts/check.sh
blockedBy: none
status: done
rows: none — harness
criteria:
  - `README.md` exists at the repository root and names every directory under `.agents/skills/` exactly once, each beside the `description:` line from its `SKILL.md` frontmatter
  - `scripts/check.sh` gains a case opened by a `# test: readme_lists_skill` line that prints `FAIL readme_lists_skill:<name>` for any `.agents/skills/<name>` missing from `README.md`
  - `sh scripts/check.sh` exits 0 and prints `ok`
notes: hand-written trial task for the first enallagi run. Scrutinise that the new check case fails when a skill line is removed from README.md.
  IMPLEMENTER: added README.md listing all 37 `.agents/skills/*` directories, each as `- \`<name>\` — description: <raw description: line copied from its SKILL.md frontmatter>`. Added the `readme_lists_skill` case to scripts/check.sh (greps README.md for each skill dir's basename, prints `FAIL readme_lists_skill:<name>` on miss). Watched it fail red with README.md absent (37 FAILs), then green once README.md was added. Re-verified the case catches regressions by removing the `ask-matt` line and restoring it — see notes below for the pasted commands/output. Reviewer: the check is a plain substring grep, so it would false-positive if one skill's directory name were a substring of another's; none of the current 37 names collide this way.
  VERIFIER: REJECTED — criterion 2 fails for real inputs, demonstrated, not hypothetical. `git status --porcelain` clean, implementation committed at e384099 (BASE=b1e3998, the commit immediately before it; `enallagi base T-001` itself errors: "records no product sha"). `sh scripts/check.sh` → `ok`, exit 0. `git diff b1e3998 --name-only` → `README.md`, `scripts/check.sh` only, matching `scope:`. All 38 current `.agents/skills/*` directories (not 37 — implementer's count is stale, harmless) are listed with descriptions matching their `SKILL.md` frontmatter character for character, confirmed by diffing every entry.
    But the `readme_lists_skill` case (`grep -qF -- "$name" README.md`) matches `$name` as a substring anywhere in the file, not against a delimited bullet — exactly the failure mode the implementer's own note raised, except it isn't limited to one skill name being a substring of *another skill name*; it also fires when a skill's name is a substring of ordinary prose elsewhere in the README. Reproduced for 3 of 38 skills — the check stayed `ok` (exit 0, no FAIL line) after deleting that skill's own bullet line and nothing else:
    - `pr`: removing `- \`pr\` — description: "Use when writing a PR body."` still passes — `pr` survives as a substring of `improve` (line 19) and of `PR` in `code-review`'s own description (line 8).
    - `handoff`: removing `handoff`'s bullet still passes — substring of `claude-handoff` (a separate skill's name, present on its own line).
    - `triage`: removing `triage`'s bullet still passes — substring hit elsewhere in the file.
    Commands run (restored README.md after each): `grep -v '^- \`pr\`' README.md > /tmp/x && mv /tmp/x README.md && sh scripts/check.sh` → `ok`/exit 0 (expected: `FAIL readme_lists_skill:pr`, exit 1). Same for `handoff`, `triage`. `tdd`, `teach`, `retro`, `wizard` correctly fail when removed — the case only breaks for names that are substrings of other text in the file, but that is exactly the case criterion 2 says must be caught ("`FAIL ... for any .agents/skills/<name> missing from README.md`" — no exception for short or substring-prone names). Working tree confirmed clean (`git status --porcelain`) and check green again before writing this verdict.
    Fix needs the grep anchored to a delimited bullet (e.g. `grep -qE -- "^- \`$name\`" README.md`, or matching against extracted bullet names only) so a name's presence in prose elsewhere can't mask its own line being deleted. Not a scope violation to fix in the same task — scope already includes `scripts/check.sh`.
  IMPLEMENTER: addressed the rejection. Reproduced it first: `grep -v '^- \`pr\`' README.md > /tmp/x && mv /tmp/x README.md && sh scripts/check.sh` → `ok`/exit 0 (should have failed). Replaced the substring `grep -qF -- "$name" README.md` with extraction-then-exact-match: `readme_bullet_names=$(grep -oE '^- \`[^\`]+\`' README.md | sed -E 's/^- \`//; s/\`$//')` then `printf '%s\n' "$readme_bullet_names" | grep -qxF -- "$name"` — this pulls every bullet's name from a line-anchored, backtick-delimited capture and requires an exact line match, so a name's presence as a substring of prose or of another skill's name can no longer mask its own bullet being deleted. Re-ran the verifier's exact repro for all 3 named failures (`pr`, `handoff`, `triage`) plus `tdd`, `teach`, `retro`, `wizard`: all 7 now print `FAIL readme_lists_skill:<name>` (exit 1) when their bullet is removed, restored README.md after each, `git status --porcelain` clean. `sh scripts/check.sh` → `ok`, exit 0. `git diff --stat` → `scripts/check.sh` only (README.md untouched, matching scope). Reviewer: check the extraction regex still matches every current bullet's format (`^- \`name\` — description: ...`) — if a future bullet ever deviates from that exact `- \`name\`` opening, its name would silently drop out of `readme_bullet_names` and the case would false-fail for that one skill, which is the safe failure direction (visible FAIL, not a silent pass).
  VERIFIER: VERIFIED. `git status --porcelain` clean, implementation committed (BASE=b1e3998, immediately before e384099 — `enallagi base T-001` still errors "records no product sha", same as last round). `sh scripts/check.sh` → `ok`, exit 0, run fresh at the start and again at the end of this review. `.enallagi/.check-baseline` holds no test names (comment-only), so no inherited failures to reconcile. `git diff b1e3998 --name-only` → `README.md`, `scripts/check.sh` only, matching `scope:` exactly. No `test-hashes.json` in this repo (`git diff b1e3998 -- test-hashes.json` empty, file absent) — no re-cut-key fraud possible. `rows: none — harness` matches the task block, so the `harness-lane` check on a check.sh edit does not apply.
    Criterion 1: `diff <(ls .agents/skills | sort) <(grep -oE '^- `[^`]+`' README.md | sed -E 's/^- `//; s/`$//' | sort)` → empty, 38/38 directories listed, no dupes either side (`sort | uniq -d` empty both). Diffed all 38 descriptions individually (`grep -m1 '^description:' <dir>/SKILL.md` vs the README bullet) — every one matches character for character, including the quoted-with-escaped-quotes ones (`code-review`, `implement-spec`, `pr`, `resolving-merge-conflicts`, `retro`, `setup-matt-pocock-skills`, `to-spec`, `wait-what`, `writing-fragments`, `writing-shape`).
    Criterion 2 (the substring bug this task exists to fix): re-ran the prior verifier's exact repro plus the implementer's follow-up set — `pr`, `handoff`, `triage`, `tdd`, `teach`, `retro`, `wizard` — deleting each name's own bullet (`grep -v "^- \`$name\`" README.md`) and running `sh scripts/check.sh`. All 7 now print `FAIL readme_lists_skill:<name>` and exit 1 (previously `pr`/`handoff`/`triage` stayed `ok`/exit 0, the exact defect rejected last round). Restored README.md after each and confirmed `git status --porcelain` clean before the next.
    Criterion 3: `sh scripts/check.sh` → `ok`, exit 0, fresh run, matches.
    Commit register (`caveman-commit`): `9be0eab fix(check.sh): anchor readme_lists_skill to exact bullet name` (61 chars) — clean. `e384099 feat(README): T-001 list .agents/skills/* in README.md, gate on it in check.sh` is 78 chars, over the 72-char hard cap — noted, not a rejection: it's history now (rewriting it would be more disruptive than the nit itself), doesn't affect any file content or criterion, and isn't fluff — it's task detail crammed into one line. Not filing a proposed block since there's no fixable defect in the current tree, just a style miss on an already-landed commit.
    Ponytail: the fix itself is minimal — one regex extraction plus one exact-match test, no new abstraction, no dependency. `PROGRESS.md` has a `friction:` line on both entries (`none` both times, not a repeat) — no `friction-repeat` action needed.
    No litter in the tree, no invented strategy, no uncited claims, no live network calls (shell-only diff). `status: done`.
