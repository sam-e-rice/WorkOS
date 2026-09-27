# Structural, Rhetorical & Tonal Patterns

The durable core of AI-slop detection — these survive vocabulary bans. Structure is the #1 detection signal: fix every banned word and leave the rhythm untouched, and the text still reads as AI.

## Contents
- Structural & syntactic (4.1–4.20)
- Rhetorical & tonal (5.1–5.14)

---

## Structural & syntactic

### 1. Negative parallelism — "It's not X, it's Y"
The single most diagnostic rhetorical move. Variants:
- Classic: "It's not just about efficiency — it's about transformation."
- Not-only: "not only a failure of policy but a failure of imagination"
- Countdown: "It's not the price. It's not the features. It's the trust."
- Split-sentence: "The headline isn't the speed. The real story is the cost." (each half looks innocent alone)
- Tailing negation: "The options come from the selected item, no guessing."
- Rather-than inversion: "prioritizing empirical consolidation rather than ideological purity" (Grok hallmark)
- Not-X-not-Y-just-Z: "Not a bug. Not a feature. A fundamental design flaw."
- Causal surprise: "not because X, but because Y"

**Fix:** State the point directly. One negated contrast per piece can work; ten is an insult to the reader.

### 2. Tricolon / rule of three
"Fast. Simple. Effective." / "innovation, inspiration, and insights." Three parallel phrases, equal length, identical punctuation.
**Fix:** Two items, four items, or a full sentence. Vary groupings.

### 3. Uniform sentence length (low burstiness)
Human prose bursts: short declaratives punctuated by long clausal sentences. LLM prose sits at a metronomic 14–22-word median. Same for paragraphs (every one 3–5 sentences).
**Fix:** Mix 3–8 word sentences with 25+ word sentences in the same paragraph. Never three consecutive sentences of similar length/shape. Fragments and one-sentence paragraphs are fine.

### 4. Copula avoidance
LLMs replace "is/are/has" with *serves as, stands as, functions as, represents, boasts, features, offers, maintains*. Academic writing showed a >10% drop in "is"/"are" in 2023 with no prior trend.
**Fix:** Default to "is"/"has" unless a more specific verb genuinely adds meaning.

### 5. Participial tail ("-ing" pseudo-analysis)
"The initiative represented a significant shift, **marking a pivotal moment in**…" Trigger words: *highlighting, underscoring, emphasizing, ensuring, reflecting, symbolizing, contributing to, cultivating, fostering, encompassing, enhancing*. Also the declarative form: "this represents a broader shift," "it speaks to a larger trend."
**Fix:** Delete the tail. If the sentence still works, it was never content.

### 6. Bad subject & orphaned demonstratives
The grammatical subject isn't the actual topic; "This highlights…" with no clear antecedent.
**Fix:** Make the subject the real topic. Give every this/that/these a referent.

### 7. Hypotactic smoothness
No fragments, no comma splices, no misbehavior — every sentence resolves. Clarkesworld's Neil Clarke: AI submissions are "boring… flat, no subtext or layers."
**Fix:** Let sentences misbehave a little. Start with "And"/"But." Don't sand away personality — over-polishing pushes prose *toward* AI statistical profiles.

### 8. Synonym cycling (elegant variation)
"the protagonist… the main character… the central figure… our hero" — the repetition penalty at work.
**Fix:** Repeat the clearest word.

### 9. False ranges
"From the Big Bang to dark matter." Manufactured breadth between unrelated extremes.
**Fix:** List the actual topics or pick the one that matters.

### 10. Inline-header bullet lists
`- **Performance:** Performance improved by 40%...` — bold stem repeats the gloss. Subtler variant: list-label periods (`- **Intros.** Years of…`) where a human writes a colon.
**Fix:** If list items need headers, write paragraphs. Fix label periods to colons.

### 11. Numbered-list inflation
"Three key takeaways." "Five things to know." Numbered lists are structurally safe, so AI defaults to them.
**Fix:** Use only when content genuinely has that many discrete parallel items.

### 12. Paragraph-reshuffle immunity (structure test)
Can you swap two body paragraphs without breaking the piece? If order doesn't matter, it's a list of points, not an argument.
**Fix:** Build a through-line; add bridge sentences.

### 13. Treadmill effect (low information density)
Ask of each paragraph "what's actually new here?" AI restates the premise in fresh words. Tell: cut 40–60% and lose nothing.
**Fix:** Name each paragraph's one fact/claim/turn. Lead with it; cut throat-clearing.

### 14. Excessive structure
3+ headings in under 300 words; 8+ bullets in under 200 words; formulaic headers ("Overview," "Key Points"); fragmented headers (heading followed by a one-line warm-up restating it); the five-paragraph-essay shape scaled to any length.
**Fix:** Merge sections; make headers specific; cut the warm-up line under a heading.

### 15. Diff-anchored writing
"This function was added to replace the previous approach…" — narrating the change instead of the thing.
**Fix:** Describe current behavior and why. History goes in the changelog.

### 16. Manufactured punchlines & staccato drama
"It had no preference for symmetry. No aesthetic prior. No nostalgia. The old rules were gone."
**Fix:** Keep the one fragment that earns its emphasis; fold the rest into ordinary sentences.

### 17. Aphorism formulas
"X is the language of Y," "the architecture of trust," "X is not a tool but a mirror." Slot-fill profundity manufacturing a general law from a specific observation.
**Fix:** Replace the formula with the concrete claim.

### 18. The "serves as" dodge
"The building serves as a reminder of the city's heritage."
**Fix:** "The building recalls the city's heritage" — or better, show how.

### 19. Invented concept labels & contrast-pair mirroring
Pseudo-analytical terms coined mid-sentence and never defined ("the supervision paradox"). Related: one half of a contrast pair is a real term of art, the other fabricated for symmetry ("false precision rather than genuine accuracy").
**Fix:** Define on first use or describe the mechanism. For contrasts, find a real opposite or drop the structure.

### 20. Moral-adjective category errors
"An honest shape," "faithful accuracy," "flagged honestly" — moral adjectives on non-agentic nouns. Related: "the assumption stops being true" (assumptions degrade; they don't flip) and gratuitous universals ("taught in *every* first-year course").
**Fix:** State the concrete property: "a more realistic curve," "a clearer picture."

---

## Rhetorical & tonal

### 21. Significance inflation (regression to the mean)
The deepest tell: specific facts replaced by generic importance. Wikipedia: "like shouting louder and louder that a portrait shows a uniquely important person, while the portrait itself is fading into a blurry, generic sketch." Triggers: *stands/serves as, is a testament/reminder, a crucial/pivotal/vital role, marks a shift, key turning point, indelible mark, deeply rooted, setting the stage for, reflects broader*.
**Fix:** State what happened; let the reader judge. If the sentence works with the inflation clause deleted, delete it.

### 22. Promotional register on mundane subjects
"rich cultural heritage," "breathtaking landscapes," "vibrant community," "nestled within," "in the heart of," "boasts a diverse array."
**Fix:** "Alamata is a town in the Gonder region." If you wouldn't say it in conversation, cut it.

### 23. Vague attribution & weasel wording
"Experts argue," "Industry reports," "studies consistently show," "independent testing confirms" — faceless authority + unfalsifiable superlative.
**Fix:** Name the expert, study, test, result — or cut. One specific reference beats four name-drops.

### 24. Canned notability emphasis
"featured in Vogue, Wired, Toronto Star…" / "maintains an active social media presence."
**Fix:** Use sources with context ("In a 2024 Wired interview, she argued…").

### 25. Formulaic "challenges" section
"Despite its [promotional words], [subject] faces several challenges…" + vaguely positive outlook / "Future Prospects" section.
**Fix:** Name the actual challenge and response, or cut.

### 26. False concession / both-sides hedge
"While critics argue X, supporters maintain Y. The truth lies somewhere in between." Nuance theater saying nothing.
**Fix:** Make the concession specific or pick a side and argue it.

### 27. Hedge-stacking
"While this may vary, generally speaking, in most cases, it's worth noting that…" / "could potentially create," "may eventually unlock."
**Fix:** One hedge maximum, or state the claim with its actual scope.

### 28. Aphoristic closure / false profundity
Pseudo-profound closing kickers ("the real question isn't what AI can do — it's what we will do with it") and universal truisms ("Change is the only constant") — the lowest-perplexity tokens available.
**Fix:** End on the specific claim, the concrete next step, or nothing.

### 29. Sycophancy & cheap warmth
"Great question!", "You're absolutely right", "Hope this helps!" OpenAI conceded GPT-4o had become "overly flattering" and rolled back the April 2025 update.
**Fix:** Delete. Respond directly.

### 30. Emotional flatline & flat affect
Claiming emotions without conveying them ("What surprised me most…") and holding one temperature for the entire piece. Humans drift registers mid-essay; LLMs pick a temperature and hold it.
**Fix:** Earn claimed emotions in the surrounding writing; let the register move.

### 31. The missing concrete particular
No Tuesday. No laundromat. Generic nouns, hypothetical examples, no last names. Laura Preston (n+1): "collapse of context."
**Fix:** The Specificity Rewrite — replace every general noun with a specific one from the source ("my grandmother," "the layoffs of March 2020").

### 32. Confidence-calibration & persuasive-authority tropes
"Interestingly," "Importantly," "Undoubtedly," "the real question is," "make no mistake," "the truth is." One "notably" per 2,000 words is fine; three in 500 is emphasis stacking. Related: self-labeling significance ("That last move is the contrarian one").
**Fix:** Cut the cue; let the content carry its own weight.

### 33. Rhetorical-question openers & acknowledgment loops
"But what does this mean for developers?" / "You're asking about X. To answer your question…"
**Fix:** If you know the answer, say it. The reader knows what they asked.

### 34. Reasoning-chain artifacts
"Let me think step by step," "Step 1:," "Here's my thought process" — chain-of-thought scaffolding in published prose.
**Fix:** Conclusion first, then evidence. Hide the scaffolding.
