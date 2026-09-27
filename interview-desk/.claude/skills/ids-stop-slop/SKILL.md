---
name: ids-stop-slop
description: Detect, remove, and prevent "AI slop" in writing: the statistically overrepresented words, phrases, structures, and tonal habits that make text read as machine-generated (delve, tapestry, "it's not X, it's Y", rule of three, em-dash stacking, significance inflation, bold-stem bullet lists, chatbot residue). Use whenever asked to "de-AI this", "remove AI-isms", "humanize this text", "make this sound less like ChatGPT/AI", "stop the slop", "audit this for AI tells", "clean up this AI draft", or when drafting new text that must not read as AI-generated. Also use to build ban lists for system prompts, triage a document by severity, or answer questions about AI-writing detection research. Covers detection, rewriting, and prevention. Do NOT use for general copyediting with no AI-slop concern, or for high-stakes authorship accusations (see references/science-and-ethics.md for why).
---

# Stop Slop

Compiled from Wikipedia's *Signs of AI Writing* (WikiProject AI Cleanup), Kobak et al. 2025 (*Science Advances*), GPTZero's AI Vocabulary data, tropes.fyi, and the open-source humanizer / avoid-ai-writing skill repos.

## Core principle

No single tell proves AI authorship. The signal is **clustering and density**: three or more tells within a few hundred words. Structure (rhythm, argument shape) is a stronger and more durable signal than vocabulary. Models adapt their words faster than their sentence shapes. All patterns are descriptive observations, not verdicts.

## Modes

Pick one based on the request:

1. **Audit (detect only).** Flag AI-isms, quote the offending spans, group by severity (P0/P1/P2 below). Do not rewrite. Use when the user wants to decide fixes themselves, or the text must not be altered.
2. **Rewrite (default).** Audit, then produce a clean version, then list what changed and why.
3. **Prevent.** Draft new text (or a system-prompt ban list) that avoids the patterns from the start. Use `references/prompts.md`.

## Audit procedure

1. Run the 60-second cluster check: focal AI word in casual context; "it's not X, it's Y"; rule of three; additive em dashes; "-ing" participial tails ("underscoring its importance"); significance inflation ("marking a pivotal moment"); promotional register on mundane subjects; vague attribution ("experts believe"); copula avoidance ("serves as" for "is"); bold-stem bullet lists; uniform sentence length; chatbot residue ("I hope this helps!"); orphaned demonstratives; aphoristic closing kicker; zero concrete particulars (no names, numbers, dates, places).
2. Check for fingerprints (near-definitive, search mechanically): `citeturn0search0`, `oai_citation`, `utm_source=chatgpt.com`, `[cite: N]`, `【..†L..】`, `grok_card`, `[attached_file:1]`, unfilled placeholders (`[Your Name]`, `2025-XX-XX`).
3. Classify each hit by severity:
   - **P0 (credibility killers, fix immediately):** cutoff disclaimers, chatbot artifacts, leaked markup/tracking parameters, unfilled placeholders, vague attributions without sources, significance inflation on routine events, hashtag stuffing.
   - **P1 (obvious AI smell, fix before publishing):** Tier-1 vocabulary, template/slot-fill phrases, negative parallelism, synonym cycling, formulaic openings, bold overuse, em-dash rate above 1 per 1,000 words, generic future-narrative closers, hedge-stacked predictions ("could potentially").
   - **P2 (stylistic polish):** generic conclusions, compulsive rule of three, uniform paragraph length, copula avoidance, transition scaffolding ("Moreover/Furthermore"), unnecessary hyphenation.
4. If the text has 5+ vocabulary hits AND 3+ pattern categories AND uniform rhythm, patching won't save it. Advise a full rewrite: state the core point in one sentence and rebuild.

## Rewrite rules (non-negotiable)

- **No fabrication.** Never add facts, numbers, names, dates, or citations not in the source. If a concrete detail is missing, flag the gap. Never fill it.
- **Never inject:** fake first person the author didn't have; manufactured stakes ("now more than ever"); forced contrarianism; performed candor ("real talk"); added em dashes; staccato fragment-chopping. Subtraction and sharpening only, no added stance, personality, or fact.
- **Preserve what's human.** Leave clean passages, quoted material, code, and tables untouched. Preserve the author's typos and quirks in casual registers, because smoothing erases their fingerprint.
- **Don't over-polish.** Removing every irregularity pushes text toward the AI statistical profile. Keep natural disfluency, varied rhythm, and a stated position where the genre allows.
- Always run a **second audit pass** on your own rewrite ("what still reads as AI?") and fix what survived.

## Positive rewrite targets

Vary sentence length (3–8 word sentences mixed with 25+ word ones); use contractions; allow fragments; start sentences with "And"/"But"; prefer "is"/"has" over "serves as"/"features"; replace generic nouns with concrete specifics *from the source*; take a position instead of both-sides hedging; cut smoothing transitions; end on the specific claim, not a bow-tying kicker.

## Reference files

Load as needed. Do not load all upfront:

- **references/vocabulary.md**: Tier 1/2/3 word lists with measured frequency ratios, replacement tables, phrase catalogs (openers, transitions, closers, chatbot residue, social-media slop). Load for any audit or rewrite.
- **references/patterns.md**: Structural, rhetorical, and tonal pattern catalog with before/after fixes (negative parallelism variants, tricolons, burstiness, copula avoidance, participial tails, significance inflation, false concessions, aphorism formulas, and 20+ more). Load for any audit or rewrite.
- **references/formatting.md**: Em-dash guidance, boldface/emoji/title-case rules, typography leaks, per-model markup fingerprint table, placeholder and citation tells. Load when checking pasted AI output.
- **references/domain-tells.md**: Poetry, fiction, student, academic, journalism, and email/business tells. Load when the text is one of those genres.
- **references/prompts.md**: Paste-ready assets: the master system-prompt ban list and George Kao's 3-pass de-slop prompt. Load for Prevention mode or when the user wants reusable prompts.
- **references/science-and-ethics.md**: The research base (Kobak et al., GPTZero, detector accuracy), signs of *human* writing, ineffective indicators, false-positive rates, and ethics of accusation. Load before making any claim that a specific text "is AI", and to keep audits honest.
- **references/resources.md**: Full source directory with links for further reading and list refreshes.

## Word lists decay

Model vocabulary drifts (delve peaked at 39.5x in mid-2024, fell to ~8x by 2025). Treat vocabulary tiers as a snapshot; structural patterns in `references/patterns.md` are the durable core. If the user has web access needs, refresh against GPTZero's AI Vocabulary tool and Wikipedia's living guide.
