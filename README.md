# README

Skills carried by this repository under `.agents/skills/`, one line each: the directory name,
and the `description:` from its `SKILL.md` frontmatter.

- `ask-matt` — description: Ask which skill or flow fits your situation. A router over the skills in this repo.
- `claude-handoff` — description: Hand the current conversation off to a fresh background agent that picks up the work immediately.
- `code-review` — description: "Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes: Standards (does the code follow this repo's documented coding standards?) and Spec (does the code match what the originating issue/spec asked for?). Runs both reviews in parallel sub-agents and reports them side by side. Use when the user wants to review a branch, a PR, work-in-progress changes, or asks to \"review since X\"."
- `codebase-design` — description: Shared vocabulary for designing deep modules. Use when the user wants to design or improve a module's interface, find deepening opportunities, decide where a seam goes, make code more testable or AI-navigable, or when another skill needs the deep-module vocabulary.
- `diagnosing-bugs` — description: Diagnosis loop for hard bugs and performance regressions. Use when the user says "diagnose"/"debug this", or reports something broken/throwing/failing/slow.
- `domain-modeling` — description: Build and sharpen a project's domain model. Use when discussing codebase terminology, writing or editing a CONTEXT.md, or recording or editing an ADR.
- `git-guardrails-claude-code` — description: Set up Claude Code hooks to block dangerous git commands (push, reset --hard, clean, branch -D, etc.) before they execute. Use when user wants to prevent destructive git operations, add git safety hooks, or block git push/reset in Claude Code.
- `grill-me` — description: A relentless interview to sharpen a plan or design.
- `grill-with-docs` — description: A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go.
- `grilling` — description: Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
- `handoff` — description: Compact the current conversation into a handoff document for another agent to pick up.
- `implement-spec` — description: "Implement a specification in code."
- `implement` — description: "Implement a piece of work based on a spec or set of tickets."
- `improve-codebase-architecture` — description: Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick.
- `loop-me` — description: Grill me about specs for the workflows I want to build, within this workspace.
- `migrate-to-shoehorn` — description: Migrate test files from `as` type assertions to @total-typescript/shoehorn. Use when user mentions shoehorn, wants to replace `as` in tests, or needs partial test data.
- `pr` — description: "Use when writing a PR body."
- `prototype` — description: Build a throwaway prototype to answer a design question. Use when the user wants to sanity-check whether a state model or logic feels right, or explore what a UI should look like.
- `research` — description: Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent.
- `resolving-merge-conflicts` — description: "Use when you need to resolve an in-progress git merge/rebase conflict."
- `retro` — description: "Conduct a retrospective on a coding session."
- `scaffold-exercises` — description: Create exercise directory structures with sections, problems, solutions, and explainers that pass linting. Use when user wants to scaffold exercises, create exercise stubs, or set up a new course section.
- `setup-matt-pocock-skills` — description: "Configure this repo for the engineering skills: set up its issue tracker, triage label vocabulary, and domain doc layout. Run once before first use of the other engineering skills."
- `setup-pre-commit` — description: Set up Husky pre-commit hooks with lint-staged (Prettier), type checking, and tests in the current repo. Use when user wants to add pre-commit hooks, set up Husky, configure lint-staged, or add commit-time formatting/typechecking/testing.
- `setup-ts-deep-modules` — description: Wire dependency-cruiser into a TypeScript repo so each package is a deep module, with implementation hidden in subfolders and reachable only through its entry-point files. User-invoked.
- `tdd` — description: Test-driven development. Use when the user wants to build features or fix bugs test-first, mentions "red-green-refactor", or wants integration tests.
- `teach` — description: Teach the user a new skill or concept, within this workspace.
- `to-questionnaire` — description: Turn a decision you can't fully answer into a questionnaire for someone else to fill in.
- `to-spec` — description: "Turn the current conversation into a spec and publish it to the project issue tracker: no interview, just synthesis of what you've already discussed."
- `to-tickets` — description: Break a plan, spec, or the current conversation into a set of tracer-bullet tickets, each declaring its blocking edges, published to the configured tracker (edges as text in one file per ticket locally, or native blocking links on a real tracker).
- `triage` — description: Move issues and external PRs through a state machine of triage roles, categorise, verify, grill if needed, and write agent-ready briefs.
- `wait-what` — description: "Stop. That last message did not land: re-pitch it."
- `wayfinder` — description: Plan a huge chunk of work (more than one agent session can hold) as a shared map of decision tickets on your issue tracker, and resolve them one at a time until the way to the destination is clear.
- `wizard` — description: Generate an interactive bash wizard that walks a human through steps only they can perform. Use when provisioning infrastructure, setting up credentials or CI secrets, walking an unfamiliar third-party dashboard, or running a one-off migration or cutover. Don't invoke this for steps the agent can perform itself.
- `writing-beats` — description: Writing, exploit; assemble raw material into a journey of beats, grounding each term before a beat leans on it.
- `writing-for-agents` — description: Writing documents for agents. Use when creating or editing skills, or modifying AGENTS.md or CLAUDE.md.
- `writing-fragments` — description: "Writing, explore: mine raw fragments, no structure yet."
- `writing-shape` — description: "Writing, exploit: shape raw material into an article, paragraph by paragraph."
