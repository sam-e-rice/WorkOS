# Resource Directory

## Canonical references
- **Wikipedia: Signs of AI writing** (WikiProject AI Cleanup) — the most comprehensive forensic catalog in existence, built from thousands of flagged submissions. https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
- **WikiProject AI Cleanup: Guide and resources** — companion guide, tools, research. https://en.wikipedia.org/wiki/Wikipedia:WikiProject_AI_Cleanup
- **Matthew Vollmer, "A Field Guide to AI Tells"** (Substack) — full taxonomy: lexical, syntactic, rhetorical, tonal, formatting, domain- and model-specific tells, detection science, ethics. matthewvollmer.substack.com

## Research & data
- **Kobak et al., Science Advances 2025** — excess-vocabulary study. Paper: science.org/doi/full/10.1126/sciadv.adt3813. Code + all 900 annotated excess words: https://github.com/berenslab/llm-excess-vocab
- **"Why does ChatGPT delve so much?"** (arXiv 2412.11385) — the 21 focal words. https://arxiv.org/abs/2412.11385
- **Walsh, AI poetry study** (arXiv 2410.15299). https://arxiv.org/abs/2410.15299
- **Dhillon et al., MFA vs. LLM fiction study** (arXiv 2510.13939). https://arxiv.org/abs/2510.13939
- **Liang et al., Stanford 2023** — detector bias against non-native writers (61.3% false positives on TOEFL essays).
- **GPTZero AI Vocabulary** — continuously updated word/phrase skew rankings. https://gptzero.me/news/most-common-ai-vocabulary/
- **Sean Trott's Substack** — ongoing empirical studies of LLM signatures. seantrott.substack.com

## Tools & repos
- **blader/humanizer** — 33-pattern detection + rewrite skill, no-fabrication rule, voice calibration. https://github.com/blader/humanizer
- **conorbronsdon/avoid-ai-writing** — 50+ patterns, tiered vocabulary, P0/P1/P2 severity triage, context/voice profiles, never-inject rules. https://github.com/conorbronsdon/avoid-ai-writing
- **tropes.fyi** — directory of 32 named tropes with downloadable system-prompt file, "Deslopify" diff tool, "AI Vetter" link checker. https://tropes.fyi/
- **sam-paech/slop-score** — weighted slop metric (60% slop words, 25% not-X-but-Y, 15% slop trigrams). https://github.com/sam-paech/slop-score (+ eqbench.com/slop-score)
- **vale-ai-tells** — Vale prose-linter package for CI-style enforcement (search GitHub).
- **GitHub topic `prose-linter`** — 18 repos incl. a curated awesome-list of anti-slop tools, research, wordlists. https://github.com/topics/prose-linter

## Articles & essays
- **George Kao, "How To Write Without Sounding Like AI"** (Medium) — the 3-pass prompt; frames the goal as serving readers, not fooling detectors.
- **Blake Stockton, "Don't Write Like AI" series** (blakestockton.com) — negation as the most prominent tell; warns over-restrictive prompts produce stiff output.
- **Embryo, "A list of words that AI over-uses"** — ~300-item cross-model list validated against GPTZero. https://embryo.com/blog/list-words-ai-overuses/
- **Ted Chiang** — "ChatGPT Is a Blurry JPEG of the Web" (New Yorker, 2023); "Why A.I. Isn't Going to Make Art" (2024).
- **Vauhini Vara** — "Ghosts" (Believer), "Confessions of a Viral AI Writer" (Wired), *Searches* (2025); source of "polite, predictable, inoffensive, upbeat."
- **Laura Preston** — "HUMAN_FALLBACK" and "An Age of Hyperabundance" (n+1); "collapse of context."
- **Shreya Shankar** — sh-reya.com/blog/ai-writing; the bad-subject problem.
- **Charlie Guo, Artificial Ignorance** — em-dash Reddit analysis; "surface polish with nothing underneath."
- **Slate (Aug 2025)** — the paranoia spiral: humans inserting typos to signal humanity.
- **r/ChatGPTPro crowdsourced tell lists** — community-maintained phrase inventories.

## Critical vocabulary

- **AI slop** — low-effort AI output; "surface polish with nothing underneath" (Guo)
- **AI-ese** — the characteristic register: formal, helpful, perfectly structured, peculiar vocabulary
- **Aidiolect** — a model's individual dialect fingerprint
- **Delve-speak** — Reinhart/Kobak-inflected academese
- **Cyborg writing** — Originality.AI's term for heavy mixed tool-use text (Grammarly + autocorrect + LLM polish)
- **Lossy compression** — Chiang's metaphor for LLM knowledge
- **Regression to the mean** — Wikipedia's diagnosis of significance inflation
- **Collapse of context** — Preston's term for retrieving the phrase-proximate regardless of fit
- **Burstiness / perplexity** — the two foundational statistical signals
