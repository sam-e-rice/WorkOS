# Calibration Examples

Six submissions Sam has confirmed as good. **Read these before writing. They outrank any abstract rule in this skill.** If the structure guidance and these examples disagree, follow the examples and flag the discrepancy.

**The canonical formatting reference is Example 6 (Ben Gordijn).** This is the most recent submission and represents Sam's preferred style going forward. Every new submission must match its formatting exactly: `<aside>` header block with backtick-bold labels, `---` after every section heading, `####` subheadings in Highest Impact Work, paragraph-style Current Situation, and the `🚩 Potential Flag(s)` section when flags exist. Examples 1 to 5 are older and use a slightly different format (plain bullet headers, inline project entries); read them for voice, evidence quality, and Sam's presence in the writing, but follow Example 6 for structure and formatting.

**Normalisation note:** three prose em dashes and one banned buzzword were corrected from examples 1 to 5 so this file does not teach patterns the house style bans. Number ranges keep their en dashes (`$260k–$270k`), which is correct typography. Everything else is verbatim.

**What to notice, in order of importance:**

1. **Sam is present in the writing.** Lines like *genuinely blew me away when we met last week* and *comfortably one of the top engineers I've met in Melbourne, and they're only working with me (for now)* are Sam's own read of the candidate. A submission is a personal recommendation from a named recruiter, not a neutral dossier. Note these are Sam's words, not the candidate's; his voice is welcome, theirs is paraphrased.
2. **Ignore every quote in examples 1 to 5.** They predate the no-quote rule and are superseded by it. Those profiles contain fourteen candidate quotes; none of them should be copied, and no new submission may contain any. Paraphrase what the candidate said. Read these examples for structure, specificity, and Sam's presence in the writing, not for quotation. See "No Candidate Quotes" in `structure-and-rules.md`.
3. **Relevance is shown by selection, not stated.** No italicised asides telling the hiring manager what to conclude.
4. **Specificity carries the weight.** 60 trillion rows, 800K to 25 million, 97% bandwidth reduction, 133-tool-call blowout. Numbers do the persuading.
5. **Structure flexes.** Chris has no Highest Impact Work section. Bullet counts run 2 to 4. Current Situation runs 1 to 3 labels. Match the candidate, not a template.
6. **Example 6 is the formatting gold standard.** When in doubt about any structural choice, match Ben Gordijn's submission.

---

# Candidate Profiles Batch

---

## 1. Chris Lawrence
* **Current:** Lead Engineer @ Amp (Lifetimely)
* **Skills:** TypeScript, NestJS, React, ClickHouse, Claude Code / agentic AI, Ruby, Python, Genuinely AI First
* **Location:** Melbourne
* **Seeking:** $260k–$270k + Super
* **Availability:** Immediately

### 🔍 Overview
Chris Lawrence is an experienced, product-obsessed builder who genuinely blew me away when we met last week. They’ve just finished up at AMP, where they’ve been leading AI adoption since January 2025, eighteen months before CC was even in the broader conversation. While most engineering teams were still “exploring” ChatGPT, Chris had already migrated Amp's entire org onto Claude Code Enterprise. More importantly, they didn't just help AMP adopt AI in a passive way; they re-engineered the “factory that builds the software”: rebuilding Amp's CI and tooling to run at agent speed and redefining the whole SDLC around AI-first skills and harnesses (ESLint to Oxlint cut CI lint times from over 5 minutes to under 20 seconds). Plenty of people talk about it; Chris is one of the few who’s actually built it.

Currently, they’re the Head of Engineering for Amp's Lifetimely product, where they architected the customer-facing analyst agent running daily in production: a SQL-mode harness that collapses 150+ proprietary data tables (one with 60 trillion rows) into five agent-readable tables, wrapped in an eval harness, LLM-as-judge loops, and tool-call grounding that ties every quoted number to a real query to eliminate hallucinations. They re-platformed Lifetimely's data ingest from a Ruby monolith to an AWS-native NestJS pipeline, cutting first-install times for large Shopify stores from ~3 days to ~4 hours, with a direct impact on trial-to-paid conversion.

What makes Chris rare is not the tooling, but the judgment underneath it. They talk about "encoding taste" into linters and skills files because agents have no opinion on what good looks like, and someone has to give them one. They stepped up to Head of Engineering because Amp needed it, did it well, then was honest enough to say their strongest work happens building, not managing, and is deliberately moving back to IC. Chris is low-ego, gives great feedback unprompted, and wants their next move to genuinely matter: they named Stile as the kind of mission they’d wake up for. Chris is comfortably one of the top engineers I've met in Melbourne, and they’re only working with me (for now).

### 🧩 Why Chris Fits At Stile
#### 🤖 Has Already Built the Agentic Future Stile Is Hiring For
* **Customer-facing Analyst Agent:** Shipped to production, not a chatbot or RAG demo. It builds a merchant profile by scraping their storefront, tunes recommendations based on whether the logged-in user is a CEO or head of finance, then produces fully formatted markdown reports with integrated charts.
* **SQL-Mode Harness:** Solved the context problem by reducing 150+ tables of proprietary data into five purpose-built tables an agent can safely query (with a security model around it), after prototyping a Cloudflare-style code-mode approach first.
* **Eval & Trust Layer:** Built what most teams hand-wave: dataset generators producing known-outcome data, A/B/C grading of agent output, LLM-as-judge loops, plus a deliberate "flag bad data" UI signal distinct from a generic thumbs-down because the product is an analyst and bad data matters specifically.

#### 🏗️ Treats Tooling and Harness Work as the Real Multiplier
* **Redefined Amp's SDLC:** AI-first approach encoding `CLAUDE.md`, then commands, then per-repo skills for error handling, scaffolding, and package use, with a GitHub code-review agent that runs the error-handling skill against every PR.
* **Strict Boundaries:** Strict TypeScript config and linting as deliberate guard rails, believing that *"if you set the bounds of your system really strictly and let people run within it, they're going to have far better outcomes."*
* **Drove Adoption Beyond Engineering:** By the time they left, designers, ops, and finance were all using Claude, onboarded through workshops Chris wrote and ran themselves. Chris has the muscle to scale AI through an org, not just use it.

#### 🎯 Product-Minded IC Who Starts From the Customer Problem
* **Data Ingest Re-platforming:** Fixed slow sync because it was directly losing sales seen in trial conversion and retention metrics (reduced 3 days down to ~4 hours, rather than rewriting for its own sake).
* **Co-founded & Ran Resync Digital:** 4 years, scaling to 25 engineers and shipping 30+ MVPs while owning sales, early-stage product design, and the build. Chris has done the full idea-to-customer-to-production loop solo and at team scale.
* **Deliberately Moving Back to IC:** Can identify the product gap, write the PR, get buy-in, and ship it. AI now lets them own that whole loop without being throttled by typing speed.

### 📍 Current Situation
* **Why Stile:** Chris named Stile unprompted as their perfect example of mission-driven work worth doing: *"If AMP vanished, some B2B customers would find another analytics tool, but if Stile’s product went away, that's going to have a really big impact on schools, on children and on education at large."* They also flagged the fit with Stile's gender diversity programme as a real pull: as a trans engineer, inclusion-focused companies are a priority for them.

---

## 2. Jakub Riedl
* **Current:** Principal Engineer @ Culture Amp
* **Skills:** Production Agents, TypeScript, Production Evals
* **Location:** Melbourne
* **Seeking:** $280k–$300k + Super
* **Availability:** Immediately

### 🔍 Overview
Jakub Riedl is a principal engineer who took iflix from 800,000 to 25 million users across Southeast Asia, the Middle East, and Africa in three years (including live World Cup streaming), then led the skeleton engineering crew through Tencent's acquisition and the merge into WeTV.

He is now the principal engineer behind “Coach”, Culture Amp's flagship AI assistant for people leaders. In that role, Jakub owns the architecture and is actively building the AI practice (Software Factory, Shared Skills, etc.) that surrounds it. He’s also built a layered eval approach combining synthetic scenarios, anonymised production traffic, and thumbs up/down user signals. He introduced proof-of-work verification in CI (checking that an agent actually produced a change-set rather than re-running the task) precisely because he believes most teams are bolting agents onto pipelines built for humans. Alongside this, he co-founded `ctx|` (context pipe) in March this year to build AI context tooling on the side, and previously co-founded and ran Appear API (an API documentation and analytics startup) for over two years.

Jakub describes himself as an engineer at heart who "engineers everything imaginable" outside work, from mechanical to electrical projects. He moved to Melbourne from Prague eight years ago and was refreshingly direct about wanting to work somewhere smaller again with people he actually wants to hang out with. His career spans platform, product, and AI leadership, meaning he could add value across platform, product, or AI Labs teams. He has visited the Stile office multiple times, comes highly recommended by Don B, and knows Ben from MelJS meetups. 

### 🧩 Why Jakub Fits At Stile
#### 🧠 Already Doing a “Labs” Type Role at Culture Amp
* Built Coach's eval framework from synthetic scenarios, anonymised production data, and real user feedback.
* Solved the "agent-in-CI" problem with proof-of-work change-set checks rather than re-running tasks.
* Building and releasing production agents in the wild.
* Argues pipelines should let agents run checks during execution rather than afterwards in CI, the exact rethink Stile's AI Labs is chewing on.

#### 🚀 Proven at 10x-Plus Scale, More Than Once
* Scaled iflix from 800K to 25 million users (31x) across three continents in three years, then led the post-acquisition skeleton crew merging into WeTV.
* Rebuilt Culture Amp's front-end practice from an unconfigured template into a standardised Next.js stack with typed API generation and Storybook-driven testing, later adopted company-wide.

#### 🔥 Frustrated By Bureaucracy
* On hearing Stile's "no one's going to die" ship-fast philosophy, he noted it "resonates very strongly," calling his own version of it "almost my catchphrase" at Culture Amp.
* Explicitly stated Culture Amp is "the upper limit" he wants in company size and named Stile as the kind of team he wants to hang out with.

### 🏆 Highest Impact Work
* **Agentic Engineering & Evals on Coach (Culture Amp):** Owns the architecture and emerging practice of running agentic systems reliably in production. Combined synthetic prompts, anonymised production traffic, and thumbs up/down signals into a layered eval approach to close the gap between "the eval passed" and "the person actually got what they needed." Introduced proof-of-work verification via generated change-sets so CI can confirm execution without re-running the whole task.
* **31x Growth & Tencent Acquisition (iflix):** Rebuilt image handling and API layers; promoted to Head of Engineering through acquisition. Scaled platform to 25M MAU across SEA, Middle East, and Africa. Led post-acquisition team (5 direct, ~20 indirect reports) merging into Tencent's WeTV. Built and led an internal cross-region backend community ("Backend familia") across five global development centres.

### 📍 Current Situation
* **At Culture Amp:** Proud of what he’s built, but honest that the pace has slowed under new CFO-led leadership toward quarterly planning and bureaucracy.
* **Why Stile:** Drawn to the mission of improving education with AI, plus the team/culture fit (friends with Don, knows Ben via MelJS and AI conferences).

---

## 3. Brad Mommers
* **Current:** Senior Engineer @ QSIC
* **Skills:** Python (Django, SQLAlchemy), GraphQL, AWS (ECS, Lambda, Aurora, CDK, Greengrass), PostgreSQL, IoT/Embedded
* **Location:** Brisbane (remote)
* **Seeking:** $175k–$180k + Super
* **Availability:** 4 weeks

### 🔍 Overview
Brad Mommers is a Senior Backend Engineer with solid production Python skills, a Master's in computational quantum physics, and a knack for explaining complex technical topics clearly. He spent 3 years at Deloitte building the Python/SQLAlchemy/GraphQL backend for the Victorian Department of Transport's digital twin (eventually leading 9 backend engineers), and the last 2 years at QSIC owning core pieces of their Django monolith and IoT fleet platform.

At QSIC, he worked across cloud and device stacks. On the cloud side, he maintained and performance-tuned the Django monolith and built an automated model export pipeline that propagates state from the monolith to a new Go-based device-management service via async worker queues, ECS, and S3 (with deterministic, auditable change ordering). On the device side, he overhauled the on-device stack, cutting bandwidth utilisation by 97% and operating costs by over 50% while maintaining legacy compatibility. He owns CI/CD end-to-end, drove a Buildkite to GitHub Actions migration, and writes Terraform as needed.

Brad brings deep problem-solving discipline from his quantum physics background (simulations for supercomputing clusters). He excels at breaking down complex performance bottlenecks and understands the nuances of ORM tradeoffs versus raw SQL. 

### 🧩 Why Brad Fits At ExoFlare
#### 🐍 Same Stack, Same Scale Problems, Already Solved
* **3 Years on Python/SQLAlchemy GraphQL API (Deloitte):** VicGov digital twin team lead (9 engineers). Established standards for code review, testing, and documentation; explicitly guarded against GraphQL N+1 query traps.
* **Django Monolith & Infrastructure (QSIC):** Handles ECS-hosted services, async worker queues, cascade-failure mitigation, and ORM migrations. Rolled a custom SQLite layer on-device to isolate device-level state.

#### ☁️ AWS-Native Builder Who Owns the Whole Pipe
* **Hands-on AWS:** ECS, Lambda, Aurora, CDK, Step Functions, S3, Greengrass, and Terraform. Built data pipelines from Django models through async workers to S3 with anti-cascade failure protections.
* **CI/CD & Automation:** Migrated QSIC from Buildkite to GitHub Actions. Views automation as a velocity multiplier: *"the core of development is figuring out how to solve the problem, then everything else is about consistency."*

#### 🧠 Pragmatic AI-Native Without the Hype
* Uses Claude Code daily for searching legacy codebases and navigating undocumented AWS SDK calls (reduced Greengrass research from days to hours).
* Keeps architectural and debugging judgment human-driven; understands that AI velocity requires strict production guardrails.

### 🏆 Highest Impact Work
* **Automated Model Export Pipeline | QSIC (2024–2025):** Designed/shipped an export module propagating model changes in Django to a new Go service via deterministic, auditable change logs. Used async worker queues and S3 landing zones to prevent request path blocking and avoid ECS cascade failures.
* **On-Device Stack Overhaul | QSIC:** Cut bandwidth utilisation by 97% and operating costs by over 50% while maintaining backward compatibility across the production fleet.
* **GraphQL Backend for VicGov Digital Twin | Deloitte (2021–2024):** Led a 9-engineer team powering a digital twin of Victoria's motorway network using Python and SQLAlchemy. Prototyped automated schematic motorway views for live traffic management and conducted research that helped secure a multimillion-dollar geospatial implementation project.

### 📍 Current Situation
* **At QSIC:** Well-respected, but QSIC has shifted new development primarily to Go. Brad prefers backend systems, data pipelines, and Python/GraphQL engineering.
* **Why ExoFlare:** Enthusiastic about the combination of Python, GraphQL, geospatial data, and IoT data ingestion, alongside ExoFlare's mission and graph-based relationship analysis.

---

## 4. Maxy Lotherington
* **Current:** Head of Product & Design @ InvestorHub
* **Skills:** Conversation design, LLM evals, tone-of-voice systems, product strategy, hands-on Claude Code, product design
* **Location:** Melbourne
* **Seeking:** $200k–$220k + Super
* **Availability:** 4 weeks

### 🔍 Overview
Maxy Lotherington is currently Head of Product & Design at InvestorHub. She took a versatile career path spanning marketing, graphic design, and UX design, moving into senior/lead product design roles at A Cloud Guru, Pearson, and Exo Digital before taking the head-of-function seat at InvestorHub in early 2023.

Recently, her focus has been on designing, evaluating, and shipping a production conversational agent ("Ivy") to revenue-generating customers. She developed Ivy's tone-of-voice guidelines iteratively with Claude, built the eval system from scratch (writing expected behaviors and model answers per tool, scoring multi-LLM outputs, and spot-checking edge cases), and managed a staggered closed beta with daily transcript reviews to catch inaccuracies and tool-call loops.

Maxy combines strategic product vision with hands-on technical prototyping in Claude Code. She excels in ambiguous, pre-PMF environments ("I'm best when it's really murky out there").

### 🧩 Why Maxy Fits At Enrola
#### 🎙️ Has Built the Taste-and-Eval Loop
* Owns Ivy's end-to-end behavior in production: tone of voice, conversation design, eval suite, beta selection, and daily transcript feedback loops.
* Translated abstract goals ("make it feel premium") into explicit agent behavior through live prompt iteration and guardrail tuning.

#### 🔁 Ships Small, Measures, and Iterates
* Operates in two-week cycles using an SLC ("simple, lovable, complete") framework.
* Staggered the Ivy beta rollout from 3 to 10 power users, running cohort-based adjustments. Rebuilt measurement targets after observing actual user edge-case testing rather than relying on vanity metrics.

#### 🧵 Strategic Vision + Hands-on Execution
* Led three major features from initial pitch to core product offerings (website builder, webinars, workflow consolidation) by distilling SLT/sales context into actionable product direction.
* Prototypes directly in Claude Code against codebases to evaluate micro-interactions and flows independently.

### 🏆 Highest Impact Work
* **Ivy, InvestorHub's In-Product AI Agent (2026–Present):** Designed and deployed an in-product agent that executes workflows and queries data for listed-company executives via natural language chat. Created the evaluation framework, conducted multi-LLM benchmarking, managed user rollout, and caught critical edge cases (e.g., resolving a 133-tool-call single-turn blowout).
* **Feature Bets (InvestorHub, 2023–2025):** Pitched and delivered key product expansions against initial internal skepticism, including a website builder that became a core sales driver and a webinar upsell feature that grew into a primary revenue stream.

### 📍 Current Situation
* **At InvestorHub:** InvestorHub has reached PMF and moved into a maintain/defend phase. Maxy thrives in earlier, higher-ambiguity problem spaces and wants new customer challenges.
* **Why Enrola:** Attracted to the founding generalist scope, early-stage problem space, and the leadership team.
* **Note:** Seeking $210k + Super (slightly above standard range, though offset by overall team composition). Needs to partner with sales/go-to-market teams to align conversational design with sales playbooks.

---

## 5. James Davie
* **Current:** CEO & Co-Founder @ Miyagi
* **Skills:** Conversational AI, Evals & Observability, Product Discovery, Prompt Engineering
* **Location:** Sydney, NSW
* **Seeking:** $180k–$200k + Super
* **Availability:** Immediately

### 🔍 Overview
James Davie was the founding CEO of Miyagi, where he designed and deployed production AI that handled real-time phone interactions between patients and medical receptionists across 15 practices handling hundreds of daily calls ($5k–$20k contract values). 

His background includes 9 years across NLP research and product management: NLP Data Scientist at Max Kelsen (2017), Product Manager at Otso AI (onboarded 188 government agencies in 3 months), Product Manager at Ignition (grew self-serve revenue to 15% of ARR), and product leadership at Softr (800K users) before founding Miyagi.

At Miyagi, James managed the behavioral orchestration layer: streaming call audio, extracting intent via LLM passes, pre-fetching information to reduce latency, and dynamically adjusting user interface elements via generative UI. He built evaluation pipelines using 10–12 real call categories, screenshot regression testing, and reproduction/replay tools for debugging.

### 🧩 Why James Fits At Enrola
#### 🧪 Closes the Loop From Live Failure Back Into Evals
* Built regression test coverage directly from live production failures (e.g., catching prompt wording changes that prevented confirmation UI rendering).
* Employs pragmatic, iteration-focused testing: built lightweight screenshot and scenario checks early to ensure fast shipping while maintaining production reliability.

#### 🎧 Deep User-Centric Behavioral Research
* Conducted shadow sessions with clinic staff to eliminate UI friction, transitioning from intrusive overlays to dynamic generative UI.
* Understands prompt sensitivity in conversational flows and how subtle phrase changes alter model execution paths.

#### 🎯 Data-Backed Performance Commitments
* Measured pre-deployment metrics (e.g., two-week baseline call duration) to prove post-deployment ROI at 3 and 6 months.
* Built API validation layers to verify that agent-reported completions matched backend state changes before confirming actions.

### 🏆 Highest Impact Work
* **Relay + Generative UI Layer | Miyagi (2024–2026):** Built an AI agent layer interfacing telephony (3CX) and practice management systems (Best Practice Premier). Handled emergency escalation, auditability, and dynamic interface rendering. Built proactive pre-fetching to display doctor availability within seconds during live calls. Managed founder-led sales and IT partner distribution across three states.
* **Self-Serve Conversion | Ignition (2019–2022):** Transitioned onboarding from high-touch sales to self-serve workflows, growing self-serve ARR to 15% ($7M–$10M volume) and shifting CSMs to expansion/account management roles.

### 📍 Current Situation
* **At Miyagi:** Winding down operations following a funding attempt against heavily capitalized incumbent clinical software. Clear-eyed experience in high-compliance deployments.
* **Why Enrola:** Excited by conversational agent orchestration, evaluation design, and building non-frustrating user-facing AI systems.
* **Note:** Primary conversational AI experience centers on inbound service/support and dynamic UI orchestration rather than outbound sales/persuasion workflows. Learning curve expected on pure sales conversion playbooks.

---

## 6. Ben Gordijn (CANONICAL FORMATTING REFERENCE)

**This is the gold standard for structure and formatting. Every new submission must match this layout.**

<aside>

**`Current`:** Product Manager @ Karbon | **`Skills`**: Agentic AI platforms, Databricks and dbt, SQL, Python, Claude Code and Figma, Regulated data governance, Release management

**`Location`**: Sydney | **`Seeking`:** $150k + ESOP | **`Available`:** 2 weeks' notice

</aside>

### 🔍 Overview:

---

**Ben Gordijn** ran the RFP that picked Karbon as BlueRock's practice management system, then crossed to the other side of the screen and joined Karbon as a PM, where he took his first product surface from **$900k to $2.2m ARR** in just over a year. Then he wrote the manifesto for what Karbon's AI product should be, won the work, and spent the last year as the founding PM for the agentic AI team: running **two squads** and managing **22 software engineers,** including **5 data engineer**s and a project to migrate the customer-facing intelligence platform.

At Karbon, he currently owns the **Agent Management System:** the surface where accounting firms configure agents, manage capabilities, and work through chat, task assignment and @mentions, with each mode wired to a different platform capability underneath. He designed the three-part model that separates a **Karbon-owned agent and skill catalogue** from **firm-governed workflows and permissions** and a **firm-visible memory service**, which is (roughly) the same authorisation problem Birchal has to solve across issuers, investors and internal users.

When it comes to product craft: Ben is the one owning it all. nothing reaches him scoped and right now he works an opportunity from research through design, writes the requirements and acceptance criteria himself, cuts them into tickets with Claude, then runs all the rituals that get them shipped: **three** standups a day, **three** refinements a week, **three** retros fortnightly. Let's just say he can write given-whens till the cows come home 🐄

Ben is super talented, smart and incredibly driven. I've not met many (if any) product folk at his level that speak so fluently about what good PMing is (and isn't) and in that way he's years ahead of most of his peers for me. Yes, he's currently in a PM role right now not a PO role. But to put it simply, Karbon are spreading him thinnnn (too many teams, 16 hour days) and not being recognising him for all the hard work he's put in. He knows Birchal well, and he's VERY excited to explore the opportunity with you.

### 🧩 Why Ben Fits At Birchal:

---

#### 🧾 Regulated Delivery Is Work He Has Already Done

- **He owned governance end to end** on BlueRock's enterprise data platform: ingestion, transformation, lineage, retention and client confidentiality, consolidating **11 source systems** into one governed source of truth for a **$40m** accounting and advisory business. Compliance shaped that build rather than turning up as a review gate at the end.
- **He shipped CoPilots firm-wide** for BAS and tax return workflows, built on discovery across BAS, returns, bookkeeping and FBT, and ran roughly **30 client engagements** solo as the key contact across regulated industries. He has also sat on the buying side of a regulated platform decision, running the selection for a **200+ person** practice with audit, compliance and workflow implications.

#### 🧪 Prototypes First, Writes the Requirements Second

- **Claude writes his tickets, and he prototypes in Claude Code, Cursor and Figma** alongside his own SQL and Python to test an idea before it reaches a sprint. That is the loop you want: push a real interface around against the design system, then write the requirements off what you learn, with no hi-fi mockup handoff in the middle.
- **He gives the technique away instead of sitting on it.** His manifesto became Karbon's AI strategy, the platform framework he built is what other Karbon product teams put their agentic features on top of, and he is coaching a senior PM (a career changer out of support and success) plus other PMs through the AI space while not holding the senior title himself.

### 🏆 Highest Impact Work:

---

#### Agent Management System and Agentic Platform

**Karbon, 2025 to now**

Karbon needed an agentic product without handing accounting firms an unbounded automation loose on client data. Ben defined the strategy from zero with the Senior Director and built both the customer surface and the framework underneath it.

- **Designed a three-part platform model that separates concerns**: a Karbon-owned agent and skill catalogue, firm-governed workflows and permissions, and a firm-visible memory service that lets Karbon learn end-customer and use-case patterns. This is the closest analogue I have seen to the access and authorisation reasoning BirchalNext needs across issuers, investors and internal users.
- **Built and owns the AMS itself**, the web surface for configuring agents and managing capabilities, with three interaction patterns (chat, task assignment, @mention in comments) each mapping to a different capability underneath. He partners with engineering on the architecture calls across A2A, A2UI, agentic RAG, knowledge graphs and MCP rather than lobbing requirements over a wall.
- **Runs tiered releases with real trade-off judgement**, including tightly held betas of **5 to 100 firms**, everything behind feature flags, and a go or no-go call he makes himself on what enters each monthly release. He pulled the cadence back from weekly when go-to-market could not carry the training and enablement load.

#### Enterprise Data Platform and CoPilots

**BlueRock, 2021 to 2024**

He identified and scoped BlueRock's innovation programme as an analyst, then owned it as PM. Nobody handed him the brief.

- **Consolidated 11 source systems** into a governed source of truth for the accounting and advisory business, and owned the integration surface into downstream AI, propensity modelling and the 360° Client View, which shipped to partners firm-wide.
- **CoPilots went out firm-wide** across BAS and tax return workflows with high adoption and a projected lift of up to **50%** in accountant task productivity. The internal LLM chatbot he built was productised by BlueRock after he left and now runs in other accounting and advisory firms.

### 📍 Current Situation:

---

**At Karbon:** Fortunately for Karbon, Ben's AI Manifesto has been a roaring success and they're benefitting massively. Unfortunately for Ben though, his workload has quadrupled but he's had zero support by way of additional product resource, or additional recognition. He's asked several times for a progression plan and the business simply blew him off. So he's looking for something better where he can be valued and also progress quickly.

**Why Birchal?** Ben know's Birchal really well. BlueRock clients and subsidiaries have raised on the platform, and one of the directors he worked with (at BlueRock) is close to the business. When I told him about the journey and rebuild, he got it instantly and was excited by the idea of helping, saying that he wants to work in a smaller, close-knit team where he can have a big impact on the work and progress into a HO Product role in time.

 🚩 **Potential Flag(s) To Explore:** 🚩

Not so much a flag, but more something for you to make sure you feel comfortable with, but obviously Ben is not a Product Owner and is already doing a fully fledged PM role. We spoke openly about the Birchal PO role and the fact that you need him to help execute in the first instance and he was more than okay with that.

My vote would be to bring him in as a PM, let him get up to speed co-owning the roadmap, proving himself and then he'll naturally step into the PM role and have all the context etc needed. One to meet 100% IMO

## **`CV DOWNLOAD + VIEWER`**

20260730 - Resume.pdf

👈 **Download here**

**View here** 👇

20260730 - Resume.pdf