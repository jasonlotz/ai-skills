---
name: review-it
description: Conducts a thorough, conversational code review focused on best practices, DRY principles, maintainability, and code quality — works on a specific feature, file, PR, or the full codebase (defaults to recent changes if no context is provided)
license: MIT
compatibility: opencode
---

## What I do

- Reviews code thoroughly for best practices, DRY violations, maintainability issues, naming clarity, separation of concerns, error handling, and security/performance concerns
- Works conversationally — asks clarifying questions as needed rather than dumping a wall of findings
- Accepts a specific scope (file path, PR number, git diff) or defaults to recent changes when none is provided
- Explains each finding clearly: what the issue is, why it matters, and a concrete suggestion for fixing it
- Closes with a summary of overall code health and the top priorities to address

## When to use me

Use me after writing code — whether you've just finished a feature, want a checkpoint mid-build, or want a broad review of an entire codebase or app. Common scenarios:

- You've just built a feature and want a quality check before shipping
- You want an architectural review of an existing codebase
- You're unsure if your approach is idiomatic or maintainable
- You want a second opinion on a specific file or module

Invoke me with: `/review-it [context]`

Examples:
- `/review-it` — review recent changes (git diff HEAD)
- `/review-it src/auth/login.ts` — review a specific file
- `/review-it 42` — review a PR by number
- `/review-it src/` — review an entire directory

## Instructions

### Step 1: Determine scope

Detect what to review based on how the skill was invoked:

**Context provided by the user** (file path, directory, PR number, or description):
- File or directory path → read those files directly
- PR number → run `gh pr diff <n>` to get the diff, and `gh pr view <n>` for context
- Description or feature name → use context from the current conversation plus `git diff HEAD`

**No context provided:**
- Default to recent changes: run `git diff HEAD` and `git status`
- If the working tree is clean, run `git log --oneline -10` and review the most recent commit: `git diff HEAD~1 HEAD`

Before reviewing, briefly tell the user what scope you're working with (e.g. "Reviewing changes in `src/auth/` based on your recent git diff.").

---

### Step 2: Explore the code thoroughly

Do not skim. Read the full content of every relevant file before forming opinions. For each file or diff:

- Understand the purpose and responsibility of the code
- Identify how it fits into the broader codebase (imports, dependencies, callers)
- Look for patterns — both good ones to reinforce and problematic ones to flag

If you need more context to make a confident judgment (e.g. a type definition, a related module, a shared utility), go find it. Do not guess.

---

### Step 3: Conduct the review conversationally

Do **not** dump all findings at once. Work through the review in logical chunks — by file, by concern area, or by severity. After each chunk, pause and ask if the user wants to dig deeper, has context that changes your read, or is ready to move on.

Lead with the most important findings. If there are 10 minor style nits and 2 architectural concerns, surface the architectural concerns first.

For each finding, be specific and actionable:

```
**[Area]** Short description of the issue

Why it matters: <1-2 sentences on the impact>

Suggestion: <concrete fix or alternative approach, with code if helpful>
```

---

### Step 4: Review criteria

Apply all of the following lenses. Skip any that are genuinely not applicable to the scope being reviewed.

**Best practices**
- Is the code idiomatic for the language and framework in use?
- Are established patterns followed consistently?
- Are there anti-patterns that will cause pain later?

**DRY (Don't Repeat Yourself)**
- Is logic duplicated across files, functions, or modules?
- Are there opportunities to extract shared utilities, hooks, or abstractions — without over-engineering?
- Is duplication intentional (e.g. for clarity or independence) or accidental?

**Maintainability**
- Will a developer unfamiliar with this code be able to understand and modify it safely?
- Are functions and modules focused on a single responsibility?
- Is complexity justified, or is there a simpler approach that achieves the same result?

**Naming and clarity**
- Are variables, functions, and types named precisely and consistently?
- Do names reveal intent, or do they require mental mapping?

**Separation of concerns**
- Are UI, business logic, data access, and side effects cleanly separated?
- Are there components or modules doing too many things?

**Error handling**
- Are errors caught and handled at the right level?
- Are error messages useful for debugging?
- Are edge cases (null, empty, unexpected input) accounted for?

**Security**
- Is user input validated and sanitized?
- Are secrets, tokens, or sensitive data handled safely?
- Are there obvious injection, auth, or data exposure risks?

**Performance**
- Are there obvious inefficiencies (unnecessary re-renders, N+1 queries, redundant computation)?
- Only flag if genuinely impactful — do not nitpick micro-optimizations.

---

### Step 5: Closing summary

After working through the findings conversationally, close with a brief summary:

```
## Overall assessment

**Strengths:** <what's working well>

**Top priorities:**
1. <most important thing to fix>
2. <second most important>
3. <third, if applicable>

**Overall quality:** <one honest sentence on where this code stands>
```

Keep it direct and honest. A senior engineer is reading this — they want the truth, not reassurance.
