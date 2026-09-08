---
name: test-it
description: Builds a focused smoke-test checklist from recent changes, then drives it in the in-app browser together with the user. Works standalone or as part of the scope-it → build-it → review-it → test-it → ship-it workflow.
license: MIT
compatibility: opencode
---

## What I do

- Inspects recent changes to understand what was built or modified
- Reads the relevant changed files to understand intent, not just surface-level diffs
- Outputs a concise numbered smoke test checklist — 3 to 8 items — covering the critical paths worth verifying
- Each checklist item includes a one-line rationale explaining what could break
- Then launches the in-app browser against the running app and drives the checklist together with the user, sharing screenshots and results
- Works standalone or as part of the scope-it → build-it → review-it → test-it → ship-it workflow

## When to use me

Use me any time you want to know: *"what should we verify right now, and let's check it together?"* Common scenarios:

- You've just finished a build session and want to smoke test before shipping
- A `review-it` session flagged changes and you want to verify the fixes
- You've made a focused change and want a quick sanity check before committing
- You want a second opinion on what's risky in a set of changes

No prior skill in the chain is required. Invoke me at any point.

Invoke me with: `/test-it [optional context]`

Examples:
- `/test-it` — derive scope from git diff and current conversation
- `/test-it src/auth/login.ts` — focus on a specific file or directory
- `/test-it 42` — inspect a PR by number

## Instructions

### Step 1: Determine scope

Detect what to test based on how the skill was invoked:

**Context provided by the user** (file path, directory, PR number, or description):
- File or directory path → read those files and run `git diff HEAD -- <path>`
- PR number → run `gh pr diff <n>` to get the diff, and `gh pr view <n>` for context
- Description or feature name → use context from the current conversation plus `git diff HEAD`

**No context provided:**
- Default to recent changes: run `git diff HEAD` and `git status`
- If the working tree is clean, run `git log --oneline -10` and inspect the most recent commit: `git diff HEAD~1 HEAD`

Before outputting the checklist, briefly tell the user what scope you're working with (e.g. "Basing this on changes in `src/auth/` from your current git diff.").

---

### Step 2: Read the changed files

Do not rely on the diff alone. Read the full content of each changed file to understand:

- What the code is supposed to do
- What user-facing behavior or system behavior it affects
- What adjacent code, flows, or integrations it touches

If a changed file references another module, API, or component that's relevant to understanding the risk, go read it. Do not guess at intent.

---

### Step 3: Build the smoke test checklist

Output a numbered checklist of 3 to 8 items. Target the critical paths — the things most likely to break or regress if something went wrong.

Format each item as:

```
1. <Imperative action to take> — <one-line rationale: what could break or go wrong>
```

Examples of well-formed items:
```
1. Submit the login form with an invalid email — confirm the error message appears and the form does not submit
2. Log in with valid credentials — confirm redirect to dashboard and session is established
3. Refresh the page after login — confirm the session persists and the user is not logged out
```

Guidelines:
- Write items as user-level actions where possible, not implementation details
- Group by area with a short heading if changes span multiple distinct concerns
- Keep each item to one sentence — no multi-step items
- Do not exceed 8 items; if changes are large, prioritize the highest-risk paths
- Do not write automated test code, test scaffolding, or test file stubs
- Do not comment on code quality — that is `review-it`'s job

---

### Step 4: Verify in the browser together

Don't stop at the checklist — bring the running app up and walk the critical paths with the user.

1. Launch the in-app Browser pane: `preview_start` with the project's `.claude/launch.json` config name, or point it at an already-running dev server (`preview_start` with the `url`). Never start a dev server with a raw shell command — use the Browser/preview tooling.
2. The Browser pane is a fresh, isolated session and does not share the user's login. If you hit a login page, pause and ask the user to log in ("I'll log in if necessary"), then continue. **An auth wall is never a reason to skip verification** — you are not entering credentials, just stopping at the login page so the user can sign in. Ask and wait.
3. Drive each checklist item yourself where you can — navigate, click, `read_page`, screenshot, check the console/network, measure. For anything only the user can judge (visual taste, feel), show a screenshot and ask.
4. Share proof as you go (screenshots, measurements, log lines) and note any item that fails so it can be fixed before shipping.

If the change isn't observable in the browser (pure tooling, types, non-UI logic), say so and rely on the checklist plus build/lint instead of forcing a browser session.

Do not write automated test code or test scaffolding, and do not comment on code quality — that is `review-it`'s job.
