# The Science, Human Counter-Signals & Ethics

Load this file before making any claim that a specific text "is AI" — and to keep audits honest.

## Contents
- The research base
- Model fingerprints ("aidiolects")
- Signs of human writing
- Ineffective indicators (do NOT use)
- Detector unreliability — the numbers
- Ethics of accusation
- What rewriters must never do

## The research base

**Kobak et al., Science Advances 2025** ("Delving into LLM-assisted writing in biomedical publications through excess vocabulary") — 15M+ PubMed abstracts:
- 900 "excess words" spiked abruptly after Nov 2022, almost entirely stylistic
- Strongest: delves (r=28.0; monthly peak 39.5x mid-2024, ~8x by 2025), underscores (13.8x), showcasing (10.7x); also pivotal, intricate, meticulously, realm, aligns, underpins, garnered, bolstering, notably
- ≥13.5% of 2024 biomedical abstracts LLM-processed; up to 40% in some subcorpora
- Full list + code: github.com/berenslab/llm-excess-vocab

**The 21 focal words** (arXiv 2412.11385, "Why does ChatGPT delve so much?"): delve, intricate, commendable, meticulous, surpass, elevate, foster, tapestry, realm, navigate, landscape, pivotal, resonate, testament, underscore, showcasing, compelling, paramount, crucial, unwavering, alignment

**GPTZero AI Vocabulary** (3.3M texts, Oct 2024): "objective study aimed" 269x, "research needed to understand" 235x, "despite facing" 209x, "play significant role shaping" 182x, "crucial role in shaping" 155x, "notable works include" 120x+, "today's fast-paced world" 107x, "aims to explore" 50x+, "showcasing" 20x, "aligns" 16x, "surpassing" 12x, "impacting" 11x, "shed light" 11x.

**The two foundational signals:**
- **Perplexity** — how surprising each next word is. AI text: low and uniform. Human text: spikes.
- **Burstiness** — variation in perplexity/sentence length across a document. Humans burst; LLMs flatline.
Related: n-gram uniformity (LLMs deviate from Zipf's law), type-token ratio (human prose ~0.50–0.65 at 200+ words; AI drifts under 0.40), author-comparison baselines (most defensible forensic method).

## Model fingerprints ("aidiolects")

- **ChatGPT (GPT-4o/5):** heaviest em-dash use (pre-5.1), intro+triplet+recap structure, "Certainly!"/"Absolutely!" openers, aggressive boldface, strongest negated-contrast habit, uninvited markdown
- **Claude:** longer multi-clause sentences, mid-sentence dashes, heavy hedging ("It's worth noting," "While this may vary"), first-person self-reference, fewer tricolons, steadier long-document voice
- **Gemini:** verbose, flatter rhythm, low em-dash frequency, list/heading preference, errors cluster around bulkiness
- **Grok:** pseudo-scientific vocabulary (*causal, empirical, correlate*), "rather than" inversions, still overuses *underscore* as of 2026
- **Copilot/DeepSeek:** ChatGPT-adjacent (DeepSeek appears partly trained on GPT output)
- **Perplexity:** inline citations by default (a paradoxical non-tell)

**Critical caveat:** fingerprints drift. Delve itself peaked and declined. Any catalog is partially outdated on publication — structural patterns outlast word lists.

## Signs of human writing (Wikipedia's counter-list)

Empirically *more* common in human text:
- Simple is/has phrases ("there is a," "it has a")
- Plain words over stiff synonyms: *wrote* (not "authored"), *moved* (not "relocated"), *used* (not "utilized"), *tried* (not "attempted"), *died* (not "passed away")
- Superlative/definitive statements: "one of the best," "is the only," "was the first"
- Hedging qualifiers and intensifiers: *very, perhaps, tends to*
- Isolated wordy constructions: *as a result of, in order to, all of the, the fact that*
- Text older than Nov 30, 2022 — AI use safely ruled out
- Ability to explain one's own editorial choices
- Consistent personal style over time

## Ineffective indicators (do NOT use)

- Perfect grammar — skilled humans exist
- Formal/"fancy"/academic prose — the correlation is with *specific words*, not register
- Mixed casual+formal registers — often technical professionals, youth, or neurodivergence
- "Bland" prose — AI output skews positive and verbose, not flat
- Transition words in isolation — humans use them too
- Unsourced content — predates LLMs; modern AI text is often well-(mis)cited
- The em dash alone — distribution matters, not presence

## Detector unreliability — the numbers

- Stanford/Liang et al. (2023): seven major detectors misclassified **61.3% of TOEFL essays** as AI (near-perfect on U.S. 8th-grade essays). Structural bias against non-native writers, who naturally produce lower-perplexity text.
- OpenAI retired its own classifier July 2023: 26% accuracy on AI text, 9% false-positive rate.
- Washington Post test of Turnitin: 50% false positives on a small sample.
- Humans: ~53–70% accuracy (Penn State: 53%, barely above chance; German medical-essay study: 70% for experts). Exception: heavy daily LLM users ~90%.
- Humanizer tools and prompt tweaks ("write cheeky") defeat detectors 80–90% of the time.
- Independent test of 16 "humanizer" tools: only 2 worked; the rest mangled meaning and dropped up to 20% of content. Google's spam policy explicitly names automated synonymizing/paraphrasing as a violation.
- Neurodivergent writers and heavy Grammarly users trip detectors at elevated rates. One UC Davis investigation: 15 of 17 flagged students were false positives.

## Ethics of accusation

Never use detector scores or style tells as sole evidence in high-stakes contexts (academic integrity, hiring, publication). The evidence base: disproportionate flagging of ESL and neurodivergent writers, high false-positive rates, inability to distinguish "generated" from "polished/translated with assistance," and the impossibility of disproving an accusation. Writing-process evidence (draft history, oral discussion) is more defensible. False accusations carry real social cost — a deaf writer who must write precisely reports a dozen chatbot accusations in five months.

Second-order effect: writers now insert deliberate typos to signal humanity; some avoid their own metaphors because "ChatGPT excels at" them. The goal is better writing, not paranoia.

## What rewriters must never do

The failure mode of de-slopping itself (from the avoid-ai-writing "Never inject" rules):
- No fake first person the author never had
- No manufactured stakes ("now more than ever," "the stakes have never been higher")
- No forced contrarianism (inventing a foil is inventing a claim)
- No performed candor ("real talk," "let's be honest")
- No added em dashes during a rewrite
- No staccato conversion (vary sentences; don't chop them into fragments)
- No invented specifics — a fabricated number is worse than the vague phrasing it replaced. Flag the gap; never fill it.

**The test:** did the information in the rewrite come from the source? Subtraction and sharpening are allowed; addition of stance, personality, or fact is not.
