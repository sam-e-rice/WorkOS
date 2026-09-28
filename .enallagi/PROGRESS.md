# PROGRESS

The loop's own record, one entry per iteration, newest last. Required by the `one-row` rail: write
it at the end of every iteration; re-read its **tail** — with SPEC.md and `git log --oneline -20` —
at the start of the next.

.enallagi/TASKS.md holds the task's record in its `notes:`. This file holds the run's: what a fresh process
needs in order not to repeat the last one.

**Keep entries short and keep the newest `next:` true.** This file grows without bound and the
loop reads only its tail; anything a future iteration must not lose belongs in .enallagi/LEARNINGS.md or in
the task's own `notes:`, not buried here.

## Entry format

```
## <date> — <task id> — <landed | BLOCKED | rejected>
rows: <the exit-criteria rows this iteration turned green, or none>
check: <the exact command and its result>
what happened: <two or three sentences>
friction: <one thing that cost time and a rule or check could prevent, or none>
next: <what the following iteration inherits>
```

`BLOCKED` carries a written reason and stops the loop. That is a success, not a failure
(`blocked-is-allowed`). A row is never recorded green without the exact command and its pasted
output.

`friction:` is the harness loop's only intake. The first occurrence of something is evidence and
stays here. The **second** occurrence of the same thing becomes a line in .enallagi/LEARNINGS.md.

---

## 2026-09-24 — T-001 — landed
rows: none — harness
check: `sh scripts/check.sh` → `ok` (exit 0)
what happened: implemented T-001 test-first — added the `readme_lists_skill` case to scripts/check.sh and watched it print 37 `FAIL readme_lists_skill:<name>` lines with no README.md present, then wrote README.md (one line per `.agents/skills/*` directory, paired with the raw `description:` from its SKILL.md frontmatter) and confirmed `ok`. Re-verified the case's teeth by deleting and restoring the `ask-matt` line. Committed README.md and scripts/check.sh only (`git commit e384099`); set task status to `review`.
friction: none
next: T-001 is in `review`, awaiting the verifier. No other `ready` task is queued in .enallagi/TASKS.md.

## 2026-09-24 — T-001 — landed
rows: none — harness
check: `sh scripts/check.sh` → `ok` (exit 0)
what happened: picked up T-001 after verifier REJECTED it for `readme_lists_skill`'s unanchored substring grep (3 demonstrated false negatives: `pr`, `handoff`, `triage`). Reproduced the exact rejection first (`ok` when `pr`'s bullet was deleted), then replaced the check with a line-anchored, backtick-delimited extraction of bullet names and an exact-match test against it. Re-ran the verifier's 3 named repros plus 4 more (`tdd`, `teach`, `retro`, `wizard`): all 7 now `FAIL readme_lists_skill:<name>` on deletion. `git diff --stat` since e384099 → `scripts/check.sh` only, README.md untouched. Committed at 9be0eab; set task status to `review`.
friction: none
next: T-001 is in `review` again, awaiting the verifier's re-check of the anchored-grep fix. No other `ready` task is queued in .enallagi/TASKS.md.
