# Formatting, Punctuation & Markup Tells

## Contents
- Em dash guidance
- Formatting overkill
- Typography leaks
- Markup fingerprints (near-definitive)
- Placeholders & templates
- Citation tells

## Em dash (—)

Most famous, most contested tell. Facts:
- LLM training data overrepresents long-form journalism (NYT, Atlantic, New Yorker), so models default to dashes.
- Em-dash usage in tech/startup subreddits roughly tripled in 2023–2024 (Reddit API analysis, Charlie Guo).
- Model variance: Plagiarism Today's six-model test — ChatGPT/Copilot/DeepSeek heavy, Claude two, Gemini/Meta.ai none. OpenAI suppressed them in GPT-5.1. A July 2026 study found only Claude still exceeds professional writers.
- Dissent: The Ringer's Brian Phillips called em-dash shaming "dumb" — "the most human punctuation mark there is."

**Diagnostic fine-grain:** distribution, not presence. Humans use dashes for sharp asides/interruptions; LLMs use them additively (attaching qualifiers — breath-cycle clauses), usually space-padded.

**Fix:** Target zero in professional copy; hard max one per 1,000 words. Replace with commas, periods, colons, parentheses. Exception: the dash separating a bold list lead from its gloss is typography, not a splice. Never *add* dashes during a rewrite.

## Formatting overkill

- **Boldface abuse** — every instance of a term bolded, "key takeaways" style. Fix: one bolded phrase per major section, max.
- **Emoji as structure** — 🚀🔑💡✅ in headings/bullets. RLHF residue from marketing blogs. Fix: remove (max 1–2 end-of-line on social).
- **Title Case headings in surprising places.** Fix: sentence case.
- **Unusual tables** — small tables that should be prose.
- **Skipped heading levels / thematic breaks before headings** — markdown habits leaking elsewhere.
- **Unicode flair** — 𝗯𝗼𝗹𝗱 as math Unicode, → arrows in non-technical prose, • raw bullet characters.

## Typography leaks (weak, corroborating signals)

- **Curly vs. straight quotes** — typographic quotes in straight-quote contexts (code, Reddit, plain email). Weak alone: Word/macOS/iOS auto-curl too.
- **Immaculate typography in casual registers** — flawless punctuation at Slack speed. Inverse rule: when editing a human's casual text, *preserve* typos and quirks — smoothing erases their fingerprint.
- **Near-perfect grammar, zero contractions, Oxford-comma uniformity** — machine cleanliness.
- **Hyphenated modifier stacking** — "a high-quality, well-architected, future-proof, cross-functional solution." Individual hyphens may be correct; density is the tell.

## Markup fingerprints (near-definitive paste evidence)

| Tool | Leaked artifact |
|---|---|
| ChatGPT | `citeturn0search0`, `contentReference[oaicite:0]{index=0}`, `oai_citation`, `utm_source=chatgpt.com`, `+1` citation artifacts, `attributableIndex` JSON |
| Gemini | `[cite: 1]`, `[span_1](start_span)` / `(end_span)` |
| Grok | `grok_card`, `grok_render_citation_card_json`, `referrer=grok.com` |
| DeepSeek | lenticular brackets + daggers: `【85†L261-269】` |
| Perplexity | `[attached_file:1]`, `[web:1]`, `ppl-ai-file-upload` S3 links |
| Copilot | `utm_source=copilot.com` |

**Fix:** Strip tokens and tracking parameters mechanically. Replace meaningful citations with real references. Delete markup — never "humanize" it.

## Placeholders & templates

Unfilled Mad-Libs slots: "Hi {client_name},", "[Describe the specific section…]", "Best regards, [Your Name]", "2025-XX-XX", `<!-- Add if available -->`. Near-definitive unedited paste.
**Fix:** Fill or delete. A shipped placeholder is a publishing bug.

## Citation tells

- Hallucinated references: real journals with wrong volumes/pages, shuffled authors, valid-looking DOIs resolving to unrelated articles, ISBNs failing checksum.
- Book citations without page numbers or URLs.
- Named references declared but never used inline.
- Broken external links that never existed (absent even from archives).
- Outdated access dates relative to the edit date.
