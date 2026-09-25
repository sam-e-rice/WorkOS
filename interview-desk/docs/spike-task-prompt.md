You are running the Interview Desk connector test (a spike). It checks what works in an unattended scheduled run. Do exactly the steps below, record every result, and do nothing else: no other Slack posts, no other Notion pages, never publish or share anything, never delete anything.

Paths (always use these absolute paths, whatever your working directory is):
- PY = /Users/samrice/Documents/Claude/Projects/WorkOS/interview-desk/.venv/bin/python
- SPIKE = /Users/samrice/Documents/Claude/Projects/WorkOS/interview-desk/scripts/spike.py
- Results file: /Users/samrice/Documents/Claude/Projects/WorkOS/interview-desk/state/spike.json
Record a result with: `PY SPIKE record <key> '<json>'` (single-quoted JSON, keep it short; strip any upload URL or auth header values before recording).

Constants:
- Slack connector: the Slack MCP tools (slack_send_message, slack_read_thread). Sam's self-DM channel_id = U08H0HD5PBM.
- Notion connector: the Notion MCP tools (notion-create-pages, notion-create-file-upload, notion-update-page).
- Test parent page id: 3e6d44192fa081298593e3cb6f3cd2ff (private page "Interview Desk - test run (delete me)").
- Marker every Slack message you post must start with: `🤖 Interview Desk · `

If any tool call is denied or blocked (by permissions or a hook), do not retry and do not work around it: record the exact denial/hook message under that step's key and continue with the next step.

First, read the results file if it exists. If it already has a "slack_post" key, this is RUN B: skip to RUN B below. Otherwise do RUN A.

RUN A
1. Run `PY SPIKE env` (records the environment). Also record key "session" with your current working directory as you see it and whether you can see a project `.claude/settings.json` in it.
2. Slack post: slack_send_message with channel_id U08H0HD5PBM and message: `🤖 Interview Desk · test run. Sam: please reply "yes test" in this thread.` Record key "slack_post" with {ok, ts, channel, any link}. The ts is required for run B.
3. Slack read: slack_read_thread (response_format detailed) on that channel and ts. Record key "slack_thread_a" with, for each message: user id, any bot_id / app_id / subtype / "sent via" or app attribution field you can see, and the first 60 characters of text.
4. Notion create: notion-create-pages with parent {"page_id": "3e6d44192fa081298593e3cb6f3cd2ff"}, allow_async false, one page titled "Test child - Interview Desk" with content "Created by the Interview Desk test run.". Record key "notion_create" with the new page id/url, or the error.
5. Guard check: notion-create-pages with parent {"page_id": "00000000000000000000000000000000"}, allow_async false, one page titled "Should be blocked". Record key "guard_check" with whether it was blocked by a hook (quote the hook message) or failed at Notion (quote the error), or succeeded.
6. File upload: notion-create-file-upload with filename "interview-desk-test.pdf". Record key "file_upload_prep" with which fields came back (names only, plus markdown_source/suggested_markdown values). Then run `PY SPIKE upload --url '<upload_url>' --headers '<upload_headers as JSON>'` (it records "upload" itself). Then notion-update-page on the child page from step 4 to append the suggested_markdown so the PDF is attached. Record key "notion_update" with success or the error/hook message.
7. Record key "run_a_done" true. Finish with a short summary of each step: worked / blocked / failed.

RUN B
1. Read "slack_post" from the results file for channel and ts. slack_read_thread (detailed) on it. Record key "slack_thread_b" with, for each message: user id, any bot_id / app_id / subtype / attribution fields, first 60 characters of text.
2. Record key "reply_found" with whether a message whose text starts with "yes test" exists, its user id, and every field that differs between that reply and the marker message posted in run A.
3. Record key "run_b_done" true. Finish with a short summary. Do not post anything to Slack in run B.
