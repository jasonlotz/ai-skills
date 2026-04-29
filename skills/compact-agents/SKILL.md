---
name: compact-agents
description: Compacts and standardizes AGENTS.md files across a fleet of related projects. Enforces a canonical skeleton, extracts byte-identical shared blocks, trims to high-signal content only, and drops re-derivable noise like project-structure trees. Use when AGENTS.md files have grown bloated, drifted out of sync, or vary inconsistently across sibling projects.
license: MIT
compatibility: claude
---

## What I do

- Read every AGENTS.md across a fleet of related projects
- Rewrite each into a consistent skeleton with byte-identical shared blocks (so cross-project directives stay in sync and compress well in context)
- Trim aggressively: drop project-structure trees, collapse boilerplate, keep only what an AI needs that it couldn't derive from the code
- Preserve genuinely project-specific rules, conventions, and domain notes — but in their tightest possible form

## When to use me

- AGENTS.md files in a multi-project repo or workspace have grown long, bloated, or repetitive
- Cross-project directives have drifted out of sync (same rule worded differently in each file)
- A new project was added and its AGENTS.md should match fleet conventions
- Periodic maintenance — these files creep over time, and brevity matters since they're loaded into context for every AI request

Invoke with: `/compact-agents` (operates on the current workspace) or `/compact-agents <path>` (specific dir).

## Guiding principles

1. **Brevity is the goal.** AGENTS.md content is loaded into every AI request. Every line costs context. Default answer to "should this be in here?" is **no**.
2. **Don't restate what the code already shows.** If `ls` or `grep` would surface it, drop it. Project-structure trees are the worst offender.
3. **Shared blocks are byte-identical.** Cross-project directives (commit policy, lint policy, framework conventions) appear with the *exact same wording* in every file. This is non-negotiable — drift is the failure mode.
4. **Project-specific = anything that surprises a new AI.** Rules that override defaults, gotchas, invariants, single-source-of-truth files. If it's obvious from looking at the repo, leave it out.
5. **Domain rules stay in AGENTS.md, but ruthlessly trimmed.** Keep only the rules that affect future code generation — drop implementation details that already live in code/comments.

## Canonical skeleton

Every AGENTS.md in the fleet follows this exact section order:

```markdown
# <Name>

<one-sentence description of what the project is>

## Rules (shared)

<byte-identical across the fleet — fleet-wide directives>

## Rules (project)

<unique to this project — overrides, gotchas, project-only invariants>

## Stack

<5–10 bullets: framework, db, auth, styling, deployment, notable libs, domain>

## Conventions (shared)

<byte-identical across the fleet — universal coding/naming/import/error conventions>

## Conventions (project)

<deltas only — what differs from the shared block for this project>

## Domain

<business rules that affect future code; high-signal only>

## Notable files

<only files an AI couldn't discover by reading the repo: gitignored, generated, single-source-of-truth, surprising boundaries>
```

Sections may be omitted if a project genuinely has nothing to say in them. Order is fixed.

## Instructions

### Step 1: Survey the fleet

Find every AGENTS.md in the workspace:

```sh
find . -maxdepth 4 -name "AGENTS.md" -not -path "*/node_modules/*"
wc -l <each-file>
```

Read all of them. Note:
- What's truly shared across all (or most) — these become the shared blocks
- What's project-specific
- What's bloat (structure trees, restated framework docs, implementation details)

### Step 2: Define the shared blocks

Identify text that should be byte-identical across the fleet. Typical candidates:

- **Rules (shared):** commit/push policy, build/lint policy, conventional-commit format
- **Conventions (shared):** language/typing rules, naming, import conventions, form/dialog patterns, error handling, ORM/auth boilerplate that's the same in every project

If a rule appears in 4 of 5 files with slight wording variation, **standardize it into the shared block** rather than letting drift continue. The one outlier either accepts the shared rule (delete the variant) or moves the deviation to its `Rules (project)` / `Conventions (project)` section as an explicit override.

Write each shared block once. Copy verbatim into every file. Do not paraphrase per project.

### Step 3: Aggressive cuts

These get **deleted** in every file (do not move, do not preserve, just delete):

- **Project structure trees.** A directory listing is not high-signal — `ls` produces the same thing on demand. The only files worth naming are the few that are surprising (gitignored, generated, single-source-of-truth) — those go in "Notable files" as a short list.
- **Restated framework / library docs.** "Next.js 15 App Router" in Stack is enough. Don't explain how App Router works.
- **Restated naming/lint rules already in tsconfig/eslint.** Mention them once in shared conventions if non-obvious; otherwise drop.
- **Verbose multi-paragraph design-system descriptions.** Compress to one line + a pointer to `DESIGN.md` if one exists.
- **Implementation walkthroughs.** "It calls X which calls Y which then..." — if the reader needs that, they read the code.
- **TODO / changelog / decision-log fragments.** AGENTS.md is not a journal.

### Step 4: Trim domain rules

Domain rules **stay** in AGENTS.md (don't punt them to a separate doc — locality matters), but trim ruthlessly. For each rule, ask:

- **Will this affect what an AI generates?** If no → drop.
- **Is this a hidden invariant the AI couldn't infer from the schema?** If yes → keep, in one sentence.
- **Is this an implementation detail of one function?** If yes → drop. It belongs in a code comment, not here.

Aim for one bullet per rule. If you need a sub-list, the rule probably needs splitting or trimming.

### Step 5: Notable files (replaces structure tree)

After deleting the structure tree, replace it with a short "Notable files" list. **Only include files that meet at least one of:**

- Gitignored but referenced (e.g. `prisma/seed.ts` with real data, `generated/` Prisma client)
- Single source of truth for something fleet-wide (e.g. seed JSON that drives reference data)
- A surprising API boundary or transform (e.g. snake_case → camelCase fence)
- A shared primitive that isn't auto-discoverable (e.g. `<PageHeader>` if it's policy to use it)

If a file is in an obvious location with an obvious name, leave it out. Aim for 5–10 entries max.

### Step 6: Rewrite each file

For each AGENTS.md:

1. Start from the canonical skeleton
2. Paste the shared blocks verbatim
3. Fill in Stack from existing content (one bullet per item)
4. Move project-specific overrides into the `(project)` sections
5. Trim Domain to high-signal bullets
6. Replace structure tree with Notable files list

Write the file with `Write`, not multiple `Edit`s — the rewrite is structural.

### Step 7: Verify line counts dropped

Run `wc -l` again. Expect roughly **40–60% reduction** in total lines across the fleet for a typical first pass. If reduction is under 30%, you didn't cut hard enough — reread the "Aggressive cuts" list and try again.

### Step 8: Verify byte-identical shared blocks

```sh
# Extract shared blocks from each file and diff them
# (or visually scan: every "## Rules (shared)" section should be identical)
```

If the shared blocks differ even by whitespace, fix immediately. The whole point is that they stay in sync — start as you mean to go on.

### Step 9: Report back

Tell the user:
- Total lines before → after (and percent reduction)
- Which files changed the most
- Anything you trimmed that you weren't 100% sure about, so they can sanity-check

## Anti-patterns to refuse

- **Don't expand a section "to be helpful."** If the user asks "shouldn't we add X?" and X fails the high-signal test, say so. The skill exists because these files bloat over time — defending brevity is the job.
- **Don't preserve text "just in case."** If unsure whether to keep a line, drop it. The user can re-add specific items later. The default is delete.
- **Don't introduce per-project variations of shared rules.** If one project genuinely needs to deviate, name the deviation in `Rules (project)` / `Conventions (project)` as an explicit override — don't fork the shared block.
- **Don't move content to a separate doc unless the user asks.** Keep AGENTS.md self-contained; trim instead of relocating.

## Notes on `CLAUDE.md`

In this fleet, each project's `CLAUDE.md` is a one-line `@AGENTS.md` reference. Don't touch those — the rewrite of AGENTS.md is automatically picked up.
