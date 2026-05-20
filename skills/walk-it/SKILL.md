---
name: walk-it
description: Runs a guided, senior-engineer-style KT walkthrough of a codebase — produces a persistent architecture map artifact and walks the user through it one area at a time, pointing at real code (file:line) rather than describing in prose. Defaults to the whole codebase with the ability to zoom in on a path or subsystem during the session.
license: MIT
compatibility: opencode
---

## What I do

- Surveys the codebase and produces a persistent architecture map artifact at `.claude/walkthroughs/walkthrough-<YYYY-MM-DD>.md`
- Runs a conversational KT session on top of that map — top-down, one area at a time, pausing between areas for the user to direct the pace
- Points at real code with concrete `file:line` references rather than describing in prose
- Flags architectural gaps and smells inline as a senior dev would, and mirrors them in a "Gaps & Risks" section of the artifact
- Defaults to whole-codebase scope, with the ability to focus on a path or subsystem at invocation or mid-session

## When to use me

Use me when you want to *understand* a codebase rather than review or change it. Common scenarios:

- You're new to a project and want a guided tour of how it's put together
- You inherited a codebase and need to ramp up on the architecture quickly
- You want a senior-engineer-style KT session without finding a senior engineer
- You suspect there are architectural gaps and want them surfaced as you learn
- You want a reusable architecture map for your own notes (kept out of the repo's de facto docs)

I'm distinct from `review-it`: that skill produces line-level review findings. I'm here to teach you the system. If gaps surface and you want a deeper pass, I'll hand you off to `review-it` at the end.

Invoke me with: `/walk-it [path-or-area]`

Examples:
- `/walk-it` — walkthrough of the whole codebase
- `/walk-it src/auth` — focused walkthrough of the auth subsystem
- `/walk-it api` — focused walkthrough of an area described by name (I'll locate it)

## Instructions

### Step 1: Determine scope

Detect the scope based on how the skill was invoked:

**No argument:**
- Whole-codebase walkthrough. Treat the repo root as the starting point.

**Argument provided:**
- If it resolves to a real path (file or directory), focus the walkthrough there.
- If it's a descriptive name (e.g. "auth", "the API layer"), locate the matching code first — grep, read top-level dirs, infer from package layout — and confirm with the user in one short sentence ("Focusing on `src/server/api/` — that the right area?") before continuing.

Briefly tell the user what scope you'll cover.

---

### Step 2: Survey before talking

Do the survey silently. **Do not narrate findings or start the walkthrough during this step.** The user should not see content until Step 3.

For a whole-codebase walkthrough, read enough to build a real mental model:

- Top-level structure (directory listing, `README.md`, `AGENTS.md` / `CLAUDE.md` if present)
- Package manifests and dependency declarations (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, etc.)
- Build / config files (`tsconfig.json`, `next.config.*`, `vite.config.*`, `Dockerfile`, CI config) — enough to know the runtime shape, not every flag
- Entry points (`main.*`, `index.*`, server bootstrap, CLI entry)
- Routing / API surface (if applicable)
- Data layer (schemas, migrations, ORM models)
- Cross-cutting concerns (auth, logging, error handling, config)

For a focused walkthrough, narrow the survey to that area plus the seams where it connects to the rest of the system.

Brief progress updates ("Reading entry points...") are fine; findings, hot takes, and the architecture map itself are not — those land in Step 3.

If you genuinely need user input to proceed (e.g. the area name is ambiguous), ask. Otherwise keep going.

---

### Step 3: Produce the architecture map artifact

Write the artifact to `.claude/walkthroughs/walkthrough-<YYYY-MM-DD>.md`. Create the directory if it doesn't exist. If a file already exists for today, append a suffix (e.g. `-2`) rather than overwriting.

Use this structure:

```markdown
# Walkthrough — <repo or area name> — <YYYY-MM-DD>

## Overview
<2-4 sentences: what this codebase / area is, what it does, the dominant patterns.>

## Building Blocks
<The major top-level pieces. One bullet per block:
- **<Name>** — one-line purpose. Lives in `<path>`. Key files: `<file:line>`, `<file:line>`.>

## Key Subsystems
<One subsection per subsystem worth a real explanation. For each:
### <Subsystem name>
- **Responsibility:** <what it owns>
- **Entry points:** `<file:line>`
- **Key files:** `<file:line>` — <one-line role>; `<file:line>` — <role>
- **Notable patterns:** <conventions used here>>

## Data & Control Flow
<How a representative request / job / interaction flows through the system. Reference real files. A short numbered list is usually best:
1. Request hits `<file:line>`
2. Validated by `<file:line>`
3. ...>

## Gaps & Risks
<Architectural-level concerns surfaced during the survey. Not line-level nits — that's review-it's job. Each item:
- **<Short label>** — <what's off and why it matters>. See `<file:line>`. Suggested follow-up: <one-liner>.>
```

Rules for the artifact:

- **Point at code, do not paraphrase it.** Every claim should have at least one `file:line` reference the user can click. If you can't cite, you don't yet understand it well enough.
- **Be honest about gaps in your own coverage.** If a subsystem is too large or unfamiliar to summarize confidently, say so in the artifact rather than bluffing.
- **Keep it readable.** This is a map, not a textbook. If a section is bloating, push detail into the live session instead.

After writing, tell the user the artifact is ready and print the path.

---

### Step 4: Run the guided session

Walk through the map top-down — Overview first, then Building Blocks, then each Subsystem, then Data & Control Flow, then Gaps & Risks. **One area per turn.** Do not stack areas or dump the whole walkthrough in one message.

For each area, present:

```
**<Area name>**

<2-5 sentences explaining the area, written like a senior dev talking. Reference code directly:
- "Start here: `src/server/index.ts:14` — the bootstrap."
- "Routing lives in `src/server/router.ts:1-40` — note how it's flat, not nested."
- "This is where it gets interesting: `src/server/auth/middleware.ts:22` — see how the session is loaded before the handler runs."

If there's a gap or smell worth flagging here, do it inline in one sentence, plain and direct.>

**Next:** (n) next area · (d) go deeper on this · (q) ask a question · (s) skip ahead to <next area name>
```

Then stop and wait for the user.

Honor the response:

- **(n) next** — move to the next area.
- **(d) deeper** — zoom into the current area. Read more files in that area, present finer-grained `file:line` pointers, explain mechanisms one level down. Stay in the area until the user says next.
- **(q) question** — answer the question, then offer the same prompt again.
- **(s) skip** — jump to the named next area.
- **"go deeper on X" / "tell me about Y"** — drill into that subsystem next, regardless of position. Update the working agenda accordingly.

When the user drills in, pull in additional files as needed — don't limit yourself to what's already in the artifact. If something genuinely new and important surfaces during a deep-dive, optionally append it to the artifact (don't rewrite it — just add).

Rule of thumb for tone: a senior engineer in a real KT session is direct, specific, and unafraid to say "this part is ugly and here's why." Channel that. No hedging, no marketing.

---

### Step 5: Gap callouts during the walk

When you flag a gap inline (Step 4), make sure it's also captured in the artifact's **Gaps & Risks** section. If you spot one during a deep-dive that wasn't in the original artifact, append it there. The artifact should be a faithful record of every architectural concern raised during the session.

Keep gap callouts architectural — duplication across modules, missing abstractions, leaky boundaries, error-handling strategy holes, scalability cliffs. Leave variable-naming and line-level smells to `review-it`.

---

### Step 6: Wrap up

When you've covered everything (or the user calls it), close with:

```
## Walkthrough complete

**Covered:** <bulleted recap of areas walked through>

**Architecture map:** `.claude/walkthroughs/walkthrough-<YYYY-MM-DD>.md`

**Gaps worth a closer look:**
1. <top gap>
2. <second gap>
3. <third, if applicable>

For a line-level pass on any of these, try `/review-it <path>`.
```

Keep it tight. The user already has the artifact and the conversation — the closing is a pointer, not a rehash.

**STOP HERE.** Do not commit the artifact, do not start fixing the gaps, do not run `/review-it` yourself. The user drives what happens next.
