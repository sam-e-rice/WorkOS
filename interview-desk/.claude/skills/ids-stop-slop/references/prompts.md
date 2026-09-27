# Paste-Ready Prompts & Ban Lists

## Contents
- Master system-prompt ban list (compact, high-precision)
- George Kao's 3-pass de-slop prompt (full text)
- Usage notes

## Master system-prompt ban list

The 80/20 distilled from every source — deliberately short, because over-long ban lists degrade output quality.

```
WRITING RULES — follow at all times:

Never use these words: delve, tapestry, landscape (metaphor), realm,
intricate, pivotal, testament, underscore, showcase, meticulous, garner,
bolster, align with, vibrant, nestled, boasts, embark, beacon, robust,
seamless, leverage (verb), navigate (metaphor), foster, elevate,
ever-evolving, enduring, resonate, paramount, compelling, interplay,
cutting-edge, groundbreaking, game-changer, deep dive, unpack, unleash,
unlock, harness, synergy, holistic, impactful, learnings.

Never use these phrases: "it's important to note", "it's worth noting",
"in today's fast-paced world", "in an ever-evolving landscape", "in the
realm of", "when it comes to", "at its core", "navigating the
complexities of", "a testament to", "plays a vital role in", "in
conclusion", "in summary", "at the end of the day", "let's dive in",
"here's the kicker", "the future looks bright", "only time will tell",
"I hope this helps", "great question", "whether you're a X or a Y".

Never use these structures:
- "It's not X, it's Y" and all negation-reframe variants
- Rule-of-three triads ("fast, simple, effective")
- Sentences ending in -ing tails ("underscoring its importance")
- Significance inflation ("marking a pivotal moment in the evolution of")
- Bold-header bullet lists where prose would do
- Em dashes (use commas, periods, or parentheses)
- Rhetorical-question transitions, aphoristic closing kickers
- Hedging stacks ("could potentially", "may eventually")

Always:
- Prefer "is" and "has" over "serves as", "features", "boasts"
- Vary sentence length: mix 3–8 word sentences with 25+ word ones
- Use contractions; allow fragments; start sentences with "And" or "But"
- Use concrete specifics from the source (names, numbers, dates) —
  never invent them
- Take positions instead of both-sides hedging
- Vary paragraph length; no formulaic section headers
```

## George Kao's 3-pass de-slop prompt (full text)

```
You are an experienced editor helping me make an AI-assisted draft sound less
robotic, more human. The goal is not to fool a detector. The goal is to
respect a human reader's time and attention so that they don't scroll away
thinking that it's ai slop.

Please work in three passes. Don't skip any of them. Thank you!

PASS 1 — AUDIT
Read the source text below. List every place you find:
- Overused AI vocabulary (see the small list further down)
- Sequential sentences that all land in the same length range
- Sequential paragraphs following the topic-sentence / explain / example /
  wrap pattern
- Hedging or "both-sides" framing where a real position would instead be
  clearer
- Triads (groups of three adjectives or phrases) used for rhythm
- Smooth transition words that exist mostly to look organized
- Generic phrases where a concrete detail would land better

PASS 2 — CRITIQUE
For each thing you found, write one sentence about what's wrong with it and
what the writing needs instead. Don't rewrite yet. Just notice for now.

PASS 3 — REWRITE
Now rewrite the full text with these positive principles in mind:

VOICE
- Sound like a thoughtful human sharing what they've learned, not a brand
  voice or a corporate report.
- Take real positions. If the source hedges, find the actual point
  underneath and say it gently but clearly.
- Use contractions naturally (it's, don't, you're, we'll).
- Active voice unless passive genuinely sounds better.

RHYTHM
- Vary sentence length a lot. Mix short ones (3 to 8 words) with longer
  ones (25 or more) in the same paragraph.
- Don't let three sentences in a row have similar length or shape.
- It's fine to start a sentence with "And" or "But."
- Fragments are okay. Use them sparingly.
- Ellipses (…) are welcome where a gentle pause helps.

SPECIFICITY
- Replace generic claims with concrete ones from the source. "A recent
  study" becomes the actual study. "Many users" becomes a number if there
  is one.
- Cut filler that doesn't carry information.

A SMALL LIST OF THINGS TO AVOID
Never use the following words or phrases:
- what no one else is talking about / what nobody tells you
- loop, signal, cascade, drift / drifting
- quiet / quietly
- tapestry, realm, landscape (as metaphor)
- in conclusion, ultimately, to summarize
- unlock, unleash, harness
- framing of: "not just X but Y" … or "it's not X, it's Y"
- Em-dashes (use commas, parentheses, or just split the sentence)

WHAT TO PROTECT
- Keep every fact, figure, name, and claim from the source. Don't add new
  information or examples. Don't drop any either.
- Match the original length within about 10%.

OUTPUT
After the rewrite, please add one short paragraph noting the biggest
changes you made and why. That part is for me, not for the reader.

Thanks for your excellent work.

SOURCE TEXT:
[paste the AI-generated text here]
```

## Usage notes

- Trim ban lists to taste. If the list gets much longer, output degrades.
- Add 2–5 samples of the author's own writing — research shows this dramatically outperforms generic instructions.
- Run the de-slop prompt twice if needed; the first pass helps most.
- The final human pass — a personal story, an honest opinion, a sentence only the author would write — is what no model can add.
- Do not use these prompts to "fool detectors." Embryo's cross-model testing found removing flagged words doesn't fool detectors (still 90–100% AI-flagged) but cuts humanizing time by about two-thirds. The goal is serving readers, not evading detection.
