---
name: post-hang-debrief
description: Interview Desk run. Brief new hangs to Sam in Slack, read his replies, build private Notion submission pages on yes. Never publish.
---

# Interview Desk run

Run every command exactly in the form shown, from this folder: `.venv/bin/python scripts/...`.
No absolute paths, `cd`, pipes or `&&`. In single-quoted arguments write an apostrophe as
`'\''` (e.g. `--name 'Jane O'\''Brien'`).

Config: `config/slack.json` (`sam_user_id`, `dm_channel_id` to post to, `dm_im_channel` to read),
`config/notion.json` (`open_roles_db`, `candidates_data_source`).
Every Slack message you post starts with `🤖 Interview Desk · `.
If a tool call is blocked by the guard, do not retry or work around it: record the error on
the item (`state.py set <key> failed|draft_failed --error '...'`) and move on.

## 0. Start
1. `.venv/bin/python scripts/state.py lock`. Exit 3: another run is going, stop quietly.
   Exit 4: wrong folder, stop and say so. Any other non-zero: stop.
2. `.venv/bin/python scripts/state.py recover`

## 1. Roles
Query the Open Roles data source (`open_roles_db`) for every row. Build a JSON list of
`{"id", "role", "client", "aliases": [...], "brief", "submissions_page", "status"}`
(aliases split on commas) and run `.venv/bin/python scripts/state.py save-roles --data '<json>'`.

## 2. Items
If `scripts/watch_new_notes.py` exists run `.venv/bin/python scripts/watch_new_notes.py`.
Then `.venv/bin/python scripts/state.py list --open`.

## 3. Replies
1. For each open item with a `slack_ts`: read the thread (`dm_im_channel`, `slack_ts`). For each
   reply newer than `last_reply_ts`, oldest first:
   `.venv/bin/python scripts/state.py apply-reply <key> --text '<text>' --user <user> --ts <ts>`
2. Read top-level messages in `dm_im_channel` since the oldest waiting `slack_ts`. For each, oldest first:
   `.venv/bin/python scripts/state.py dm-reply --text '<text>' --user <user> --ts <ts>`
3. Act on the returned `action`:
   - `draft` / `resume`: do step 5 for that item this run.
   - `parked`: set the item's Candidates row Outcome to Parked and Park reason to `reason`.
   - `refuse`: reply in the item's thread: `🤖 Interview Desk · <message>`.
   - `ask`: post top-level in the DM: `🤖 Interview Desk · <message>`.
   - `ignore`: nothing.

## 4. Brief
For each item with status `new`, `pending_transcript` or `failed` whose `inbox/<doc_id>.json` exists:
1. `.venv/bin/python scripts/match_cv.py --name '<candidate>' --email '<email>' --meeting-at <meeting_at> --doc-id <doc_id>`
   On a single match it records the item's `cv_path` itself (only CVs inside the CV folder).
2. If `role_row` is empty: `.venv/bin/python scripts/roles.py match --text '<role_text or title>'`;
   on a match `.venv/bin/python scripts/state.py upsert <doc_id> --data '{"role_row": "<id>"}'`.
3. Read `inbox/<doc_id>.json`, `state/cv_text/<doc_id>.txt` (if any) and the role's Brief page.
4. Write `state/briefs/<doc_id>.md` with: person; role and client (or "Role: none found" plus hints);
   fit (3 bullets); risks (up to 3); 2–4 candidate quotes as `> "..." (Name, HH:MM:SS)`;
   CV vs call gaps; missing facts (salary, notice, location, right to work); questions for Sam.
5. `.venv/bin/python scripts/verify_quotes.py state/briefs/<doc_id>.md inbox/<doc_id>.json --speaker '<candidate>'`
   Exit 1: fix the listed quotes once from the transcript and rerun. Still 1: rerun with `--drop`.
6. Post top-level to `dm_channel_id`:
   `🤖 Interview Desk · <Name> · <Role (Client) | Role: none found (maybe: X?)> · <fit in one line> · Risk: <top risk> · CV: <file name | none | ambiguous>`
   then on a new line: ``Reply in this thread: `yes`, `yes <role>`, or `no <reason>`.``
   Then reply in its thread: `🤖 Interview Desk · Brief` followed by the brief.
7. Create the Candidates row in `candidates_data_source`: Name, Hang date, Outcome `Needs decision`,
   Gemini doc, Doc id, CV file name; page content = the brief.
   `.venv/bin/python scripts/state.py upsert <doc_id> --data '{"notion_row": "<row id>"}'`
8. `.venv/bin/python scripts/state.py set <doc_id> awaiting_decision --data '{"slack_ts": "<top-level ts>"}'`
On any error: `.venv/bin/python scripts/state.py set <doc_id> failed --error '<short message>'`.

## 5. Draft
For each item with status `drafting` (and `draft_failed`, first set back with
`.venv/bin/python scripts/state.py set <doc_id> drafting`):
1. Look up its role in `state/open_roles.json` by `role_row`; fetch the Brief page. Read the
   transcript, CV text, the brief, and `answer` if Sam answered a question.
2. Use the ids-recruitment-submissions skill to write `state/drafts/<doc_id>.md`
   (callout lines first, then `## 🔍 Overview`, `## 🧩 Why <Name> Fits At <Client>`, `## 📍 Current Situation`).
   If it needs a decision from Sam: reply in the thread `🤖 Interview Desk · <question>`, then
   `.venv/bin/python scripts/state.py set <doc_id> needs_input --data '{"question": "<question>"}'`, next item.
3. ids-sam-rice-voice (client-facing): tone only. 4. ids-stop-slop: remove only, never add facts.
5. `.venv/bin/python scripts/verify_facts.py state/drafts/<doc_id>.md --segments inbox/<doc_id>.json --cv state/cv_text/<doc_id>.txt --allow '<client>' --allow 'We Are Eight'`
   Exit 1: fix once and rerun. Still 1: ask Sam about each unsupported fact as in 2.
6. CV (if the item has no `cv_path`, skip this step and leave `--cv-markdown` out of step 7):
   notion-create-file-upload with filename `<Name> CV.pdf` (or `.docx`), then
   `.venv/bin/python scripts/notion_upload.py <doc_id> --url '<upload_url>' --headers '<upload_headers json>'`
7. `.venv/bin/python scripts/build_page.py --draft state/drafts/<doc_id>.md --candidate '<Name>' --role '<Role title>' --cv-markdown '<suggested_markdown>'`
8. Fetch the item's `approved_parent` page. If it already lists a child titled `<Name> | <Role title>`,
   use that page. Otherwise notion-create-pages under `approved_parent` (page_id) with the built
   title and content, `allow_async: false`.
9. `.venv/bin/python scripts/state.py upsert <doc_id> --data '{"submission_page": "<page id>"}'`
   Update the Candidates row: Outcome `Submitted`, Submission page = the page URL.
   Reply in the thread: `🤖 Interview Desk · Draft ready (private): <url>. Review it, then Publish when you're happy.`
   Only then: `.venv/bin/python scripts/state.py set <doc_id> submitted`
On any error: `.venv/bin/python scripts/state.py set <doc_id> draft_failed --error '<short message>'`.

## 6. Finish
1. `.venv/bin/python scripts/state.py prune`
2. `.venv/bin/python scripts/state.py unlock --advance-watermark`
3. If you posted anything: `.venv/bin/python scripts/state.py notify '<n> briefed, <m> drafted'`
4. End with one line per item you touched: name · status · what happened.
