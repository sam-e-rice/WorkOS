---
name: ids-recruitment-submissions
description: "Creates evidence-based candidate submissions from transcripts and CVs that make hiring managers want to interview immediately. Use whenever the user says 'submit candidate', 'write a submission', 'write up', 'candidate submission', provides a candidate transcript and CV for a role, or references writing a candidate presentation for a client. Always writes in Sam Rice's voice regardless of who runs it, calibrates against six confirmed-good example submissions (with Example 6, Ben Gordijn, as the canonical formatting reference for all new submissions), and blocks two recurring failure patterns: quoting the candidate at all (every candidate quote is paraphrased) and tie-back asides that explain a candidate's relevance back to the client brief. Runs shared-house-style and stop-slop as blocking gates before any output. Works standalone or coordinated by the phase-2-client-brain orchestrator."
---

# Recruitment Submissions

Creates uniquely crafted, evidence-based candidate submissions from interview transcripts and CVs.

## How to Use

1. **Load `shared-house-style`.** Hard rules and the delivery gate. Load it by skill, not by file path; paths break silently, a missing skill does not.
2. **Load `sam-rice-voice`. Always.** Submissions go out under the We Are Eight name as a personal recommendation from Sam, so they carry Sam's voice regardless of who is running this skill. This overrides the author routing table in `shared-house-style`, which governs personal content such as LinkedIn posts, not client deliverables.
3. **Read `references/examples.md`.** Six confirmed-good submissions. **Example 6 (Ben Gordijn) is the canonical formatting reference; every new submission must match its layout exactly.** Examples 1 to 5 are older and use a slightly different format; read them for voice and evidence quality, but follow Example 6 for structure. **One exception: the quotes in examples 1 to 5 are superseded by the no-quote rule and must not be copied.**
4. Read `references/structure-and-rules.md` for format, the two failure patterns, and the structural checklist
5. Complete the silent analysis (Stage 0 and Stage 1)
6. Write the submission (Stage 2)
7. **Pass all three gates before delivery (Stage 3).** A submission that fails any gate is not delivered.

## The Two Failure Patterns

Both are covered in full in `references/structure-and-rules.md`. Named here because they recur:

**Candidate quotes.** Do not quote the candidate at all, in any form. No framing devices, no integrated fragments, no single quoted phrases. Paraphrase everything they said. Quotation marks stay only around product, project, team, and framework names.

**Tie-back asides.** Never join a candidate fact to the client's brief with an editorial aside, italicised or otherwise. The hiring manager knows their own brief. Relevance comes from choosing the right evidence, not from explaining the choice.

## Inputs

**Mandatory:** Candidate interview transcript, candidate CV/resume, role context (Brain file, JD, or project brief).

**Optional:** Additional context from the user, previous submissions in this conversation (for language freshness).

## Process

### Stage 0: Context Loading (Silent)

Load the role spec from whatever source is available (Brain file from Phase 2, uploaded JD, project files). Extract must-haves, deal-breakers, nice-to-haves, company challenges. Think like the hiring manager: what keeps them up at night?

### Stage 1: Deep Analysis (Silent, Never Output)

**Evidence extraction:** Identify what the candidate actually said about each must-have, then paraphrase it. Never carry their wording through to the draft. Identify concrete projects with measurable impact. Flag red flags against deal-breakers. Note cultural fit signals.

**Gap analysis:** What is missing vs requirements? Can gaps be overcome? Compensating strengths?

**Competitive positioning:** What makes this candidate uniquely valuable for this company specifically? What is their unfair advantage?

**Objection handling:** Anticipate hiring manager concerns. Prepare evidence-based responses from transcript.

**Language freshness:** Review previous submissions in this conversation. Actively avoid reusing phrases, headers, sentence patterns.

### Stage 2: Write the Submission

Follow the structure in `references/structure-and-rules.md` exactly. Output as markdown only.

### Stage 3: Gates (Blocking)

Three gates, all mandatory, run in this order. None is advisory.

**Gate A, house style.** Run the blocking gate in `shared-house-style`. Spelling, em dashes, arrow glyph, banned phrases, invented facts, bolded numbers.

**Gate B, structure and tells.** Run the quality checklist in `references/structure-and-rules.md`. Section shape, plus the two failure patterns: candidate quotes and tie-back asides.

**Gate C, `stop-slop`.** Run the full skill over the finished draft before it reaches anyone. Score it. Below 35/50 means revise, not deliver. Protected patterns named in `sam-rice-voice` survive this pass.

Do not restate any of these checklists here. Run them from source, so a fix made once is inherited everywhere.

**If any gate fails, revise and re-run. Do not deliver with a caveat attached; a caveat is not a fix.** Delivering flawed prose alongside an apology still counts as failing.

**Any edit re-opens all three gates.** A draft revised in a follow-up turn is new prose and gets checked again. This is the most common way slop reaches the client.

**Do not report gate mechanics in the output.** Sam wants the submission, not a compliance log. Gates run silently unless something fails and needs his decision.
