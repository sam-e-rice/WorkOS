# Submission Structure and Writing Rules

## Structure

The section order is fixed. **Which sections appear is not.** Match the candidate, not a template. In the calibration examples, Chris has no Highest Impact Work section at all, bullet counts run 2 to 4, and Current Situation runs 1 to 3 labels. A padded section is worse than an absent one.

**Horizontal rules.** Place a `---` immediately after every section heading (Overview, Why They Fit, Highest Impact Work, Current Situation). This is a visual separator, not optional formatting.

### Header Block

**This is a Notion callout block, not a plain paragraph.** The `<aside>...</aside>` wrapper is Notion's markdown representation of a callout; when the destination is a Notion page, this section must render as an actual callout block (grey background, left icon), not styled text sitting inside `<aside>` tags for show.

Labels use backtick-bold formatting (`` **`Label`:** ``). Separated by pipes.

```
<aside>

**`Current`:** [Title] @ [Company] | **`Skills`**: [4-8 items, specific tools and capabilities]

**`Location`**: [City] | **`Seeking`:** $[Amount]k + [Super/ESOP/equity structure as applicable] | **`Available`:** [Immediately / N weeks' notice]

</aside>
```

When output is plain markdown (chat, doc, email), the `<aside>` tags are the closest plain-text signal of a callout and should be kept as-is. When output goes to Notion (via the Notion API/MCP), create this block as a genuine `callout` block type rather than a paragraph or a quote, with the same content inside it.

Use the compensation structure the candidate actually named: `+ Super`, `+ ESOP`, `+ Super + ESOP`, or a range. Do not default to `+ Super` when the candidate said something different.

Availability lives here, which is why there is no Timeline paragraph later.

### Overview

Heading: `### 🔍 Overview:` followed by `---` on the next line.

Three paragraphs, or two where there is genuinely nothing personal worth saying. Never pad to reach three.

**Paragraph 1, opening impact.** Trajectory, scale, the achievement arc. Specific numbers required. Sam's own read of the candidate belongs here where he has one: "genuinely blew me away when we met last week."

**Paragraph 2, current work.** What they are doing right now, in detail. Specific technologies, systems built, migrations led, numbers. The highlight reel, not a job description. Usually the longest paragraph.

**Paragraph 3, the person.** Working style, judgement, motivations, what they chose and refused. Grounded in real observation. This is where Sam's endorsement lands: "comfortably one of the top engineers I've met in Melbourne, and they're only working with me (for now)." Omit if the material is thin; do not invent personality.

### Why They Fit

Heading: `### 🧩 Why [First Name] Fits At [Company]:` followed by `---` on the next line.

Three subsections. Each: `####` heading with unique emoji + candidate-specific header + **2 to 4 bullets**.

Bullets may use a bold lead-in label (`**SQL-Mode Harness:**`) or run as plain sentences. Both appear in the calibration examples. Pick one per submission and hold it.

**Strong headers, specific and candidate-unique:**
- `#### 🤖 Has Already Built the Agentic Future Stile Is Hiring For`
- `#### 🐍 Same Stack, Same Scale Problems, Already Solved`
- `#### 🔥 Frustrated By Bureaucracy`

**Never:** Technical Skills / Cultural Fit / Why They're a Good Match.

### Highest Impact Work

Heading: `### 🏆 Highest Impact Work:` followed by `---` on the next line.

**Optional.** Include where one or two projects deserve depth the Why They Fit bullets could not carry. Omit where the Overview already covered it. Chris's profile omits it entirely and is stronger for it.

Each project gets its own `####` subheading and a `**Company, dates**` line underneath, then **2 to 4 bullets** covering problem, build, and outcome. Numbers throughout.

```
#### Project Name

**Company, YYYY to now**

Brief context sentence setting up the problem or opportunity.

- **Bullet with bold lead-in** plus detail, metrics, outcome.
- **Another bullet** with specifics.
```

Do not collapse projects into inline bullet entries (`* **Project | Company:**`). The subheading format gives each project the visual weight it earns.

### Current Situation

Heading: `### 📍 Current Situation:` followed by `---` on the next line.

One to three labelled paragraphs (not bullet points):

**At [Current Company]:** Why they are looking. Honest and specific. Sometimes omitted where the Why is self-evident.

**Why [Client]?** What actually pulled them. The genuine motivation, not a restatement of the job spec. Use the question mark in the label.

Then, if a real flag or caveat exists, set it apart visually:

```
 🚩 **Potential Flag(s) To Explore:** 🚩

Paragraph explaining the risk, caveat, salary mismatch, title gap, or anything else the hiring manager should know upfront. Frame it honestly but constructively, not as a deal-breaker dump.
```

Include the flag section when there is something real to disclose. A submission that hides the catch stops being useful. Do not invent flags to fill the section.

### CV

Heading: `## **\`CV DOWNLOAD + VIEWER\`**`

Include when a CV file is available. Format:

```
## **`CV DOWNLOAD + VIEWER`**

[Filename].pdf

👈 **Download here**

**View here** 👇

[Filename].pdf
```

Omit the section entirely when no CV is available.

---

## Evidence Hierarchy

Prioritise in order:
1. Specific outcomes with numbers (scaled X to Y, reduced latency Z%, saved $N)
2. Concrete decisions and behaviours (what they chose, what they refused, what they rebuilt and why)
3. Relevant technical depth (specific tools matching the role's stack)
4. Pattern matching (built multi-region architecture with data sovereignty requirements)

| Weak | Strong |
|---|---|
| "Strong React experience" | "Built component library in React + TypeScript used by **15 engineers**, reducing duplicate code **40%**" |
| "Good cultural fit" | "Chose to move back to IC after doing the management job well, because their strongest work happens building" |
| "Experienced with scaling" | "Scaled infrastructure from **3M to 70M users** whilst maintaining **99.99% uptime**" |

---

## No Candidate Quotes

**Do not quote the candidate. Ever.** Not with framing, not integrated, not a single phrase. Paraphrase everything they said.

Quotes rarely land and usually dilute the profile. The recruiter's read of what the candidate meant is worth more to a hiring manager than a transcript fragment.

**Banned in every form:**
- `Her own words:` · `In his own words:` · `She said:` · `As he put it:` · `When asked about X, she told me:`
- A quoted phrase inside a sentence: `he called it "almost my catchphrase"`
- A quote appended to a bullet
- Block quotes, italicised quotes, parenthetical quotes

| Never | Instead |
|---|---|
| Her own words: "is validated? And a lot of it hasn't." | She went to the customer research team herself, confirmed the gap, and rebuilt the delivery sequence rather than inherit a roadmap nobody had tested. |
| He called the ship-fast philosophy "almost my catchphrase". | The ship-fast philosophy is one he has been pushing at Culture Amp for years. |
| Excels in ambiguous environments ("I'm best when it's really murky out there"). | Excels in ambiguous, pre-PMF environments, and says so plainly: murk is where he does his best work. |
| Believes that *"if you set the bounds of your system really strictly and let people run within it, they're going to have far better outcomes."* | Treats strict TypeScript config and linting as deliberate guard rails, on the view that tight bounds produce better outcomes than loose ones. |

**Quotation marks are still correct for:** product and project names (`"Coach"`, `"Ivy"`), team or framework names (`"Backend familia"`, `"simple, lovable, complete"`), and established terms of art. Those are labels, not speech. The ban is on quoting what the candidate said.

## Relevance Without Tie-Backs

The hiring manager knows their own brief. **Never explain the connection back to them.** This is the single most obvious tell that a machine wrote the submission.

**Never write anything shaped like:**
- *Brad named "look at me" AI hoarding as a red flag unprompted; sharing the model instead of sitting on it is the opposite instinct.*
- *exactly the kind of compliance-checked delivery Birchal's rebuild will need.*
- *precisely what the role calls for.*
- *this maps directly to the challenge you described.*

The pattern to kill: a candidate fact, then an italicised editorial aside joining the dots to something the client said. Cut every one on sight.

**Relevance is established by selection, not by commentary.** Choosing the right evidence *is* the argument. Trust the reader to arrive.

Where a link genuinely needs stating, it is a short clause inside the bullet, never a separate sentence and never italicised. From the calibration examples: `Argues pipelines should let agents run checks during execution rather than afterwards in CI, the exact rethink Stile's AI Labs is chewing on.` One clause, no italics, no quoting the client back to themselves.

**Never quote or paraphrase the hiring manager to the hiring manager.**

---

## Banned Phrases

Never use: "experience reads like [Company]'s roadmap", "scaling mission-critical systems", "perfect fit for", "hit the ground running", "team player", "passionate about", "innovative", "thought leader", "synergy", "leverage", "seamlessly"

**Buzzword sense only.** "Dynamic" as a technical term (`dynamic generative UI`, `dynamically adjusting`) is correct and stays. "Dynamic" describing a person or a team does not.

---

## Formatting Rules

- **Bold:** numbers and metrics, key technologies, major achievements
- **Brackets:** candidate-specific technical details only (stack, metrics, tools, timeframes). Never bracket reminders about the client's own business.
- Output as markdown. When creating Notion pages, use Notion-flavoured markdown throughout, and the header block must be an actual Notion callout block (see Header Block above), not a styled paragraph.

---

## Section Header Examples

Create unique headers per candidate. Never reuse patterns.

**Technical:** Done the Exact Migration, Multiple Times, Under Real Pressure / Built Infrastructure That Survived 20x Growth / Production-Grade Multi-Region Scaling / Pragmatic Builder Who Productionises Without Over-Engineering

**Cultural/Human:** Accessibility as Conviction, Not Compliance Checkbox / Force Multiplier Who Ships the Invisible Work / Chose IC Work Over the CTO Path for the Right Reasons / High Agency Builder Who Ships Without Bureaucracy

---

## Quality Checklist

Structural gate. Run alongside the `shared-house-style` gate; both must pass.

**Structure**
- [ ] Header block in `<aside>` callout with backtick-bold labels and pipes
- [ ] Header block is a genuine Notion callout block when output goes to Notion, not a styled paragraph
- [ ] Compensation matches what the candidate said (Super, ESOP, or both)
- [ ] `---` horizontal rule after every section heading
- [ ] Overview: 3 paragraphs, or 2 with nothing padded
- [ ] Why They Fit: 3 subsections with `####` headings, 2 to 4 bullets each, consistent bullet style
- [ ] Highest Impact Work uses `####` subheading per project with company/dates line, not inline bullets
- [ ] Current Situation: labelled paragraphs (not bullets), flag section included if a real caveat exists
- [ ] No section padded to satisfy a template

**The two tells**
- [ ] Zero candidate quotes, in any form, framed or integrated
- [ ] Everything the candidate said is paraphrased
- [ ] Quotation marks appear only around product, project, team, or framework names
- [ ] Zero tie-back asides joining candidate facts to the client's brief
- [ ] Hiring manager never quoted or paraphrased back to themselves

**Content**
- [ ] Every bullet carries a metric, a concrete scale, or a specific decision
- [ ] Sam is present: a real first-person read, not a neutral dossier
- [ ] Why [Client] reflects genuine stated motivation, not the job spec restated
- [ ] Caveats disclosed rather than buried

**Language**
- [ ] No repeated phrases or headers from earlier submissions in this conversation
- [ ] All section headers unique and candidate-specific
- [ ] No banned phrases
- [ ] Numbers bolded

**Gut check**
- [ ] Would this make the hiring manager want to interview them immediately?
- [ ] Does it say something the CV alone could not?
- [ ] Read beside the calibration examples, does it sit at the same level?
