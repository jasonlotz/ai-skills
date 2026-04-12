---
name: scope-it
description: Scopes a feature before you start building — looks up or creates a GitHub issue, works through a plan conversationally, and updates the issue with an agreed task checklist so you're ready to code. Pairs with ship-it.
license: MIT
compatibility: opencode
---

## What I do

- Accepts an optional GitHub issue number as input
- If an issue is provided, fetches its current title, body, labels, and assignees from GitHub
- Asks focused questions one at a time to understand the feature, constraints, and context
- Proposes a concrete task breakdown and iterates until the user confirms the plan
- Creates or updates the GitHub issue with a structured body: background summary and a GitHub task list checklist
- Signals clearly when the scope is agreed and the issue is ready — so you can start building with confidence

## When to use me

Use me at the start of any non-trivial piece of work, before writing a single line of code. Common scenarios:

- You have a GitHub issue that needs fleshing out before you start
- You have an idea in your head but no issue yet — I'll help you shape and capture it
- You want a clear task checklist to work from so nothing falls through the cracks

Invoke me with: `/scope-it [issue-number]`

Examples:
- `/scope-it 42` — scope and refine an existing issue
- `/scope-it` — start from scratch, create a new issue

## Instructions

### Step 1: Detect input

Check whether an issue number was passed as an argument.

**If an issue number was provided:**

Run:
```sh
gh issue view <n>
```

Display the issue title, body, labels, and assignees to the user. Use this as the starting context for the conversation — you do not need to ask "what are you building?" since the issue already answers that. Instead, move directly to targeted follow-up questions to fill gaps.

**If no issue number was provided:**

Start the conversation cold from step 2.

---

### Step 2: Understand the feature (conversational)

Ask questions **one at a time** — do not present a list of questions all at once. Wait for the user's answer before asking the next question. The goal is to build a shared understanding of the work before proposing a plan.

Key things to uncover (not a script — adapt based on what you already know from the issue or prior answers):

- What problem does this solve, or what is the user trying to build?
- Who is affected or benefits from this?
- Are there any known constraints, dependencies on other work, or things that are explicitly out of scope?
- Are there existing patterns, components, or conventions in the codebase this should follow?
- Are there any open questions or risks that should be noted?

If an issue was fetched in step 1, use its content to skip questions that are already clearly answered. Only ask about genuine gaps.

Keep the conversation tight — 2 to 4 questions is usually enough. Stop asking when you have enough to write a solid plan.

---

### Step 3: Propose a task breakdown

Once you have enough context, propose a concrete task list. Format it clearly:

```
Here's how I'd break this down:

1. <task one>
2. <task two>
3. <task three>
...

Does this cover everything, or is there anything missing, wrong, or that should be reordered?
```

Be specific — tasks should be actionable, not vague. "Add validation to the form submit handler" is better than "handle validation".

---

### Step 4: Iterate until agreed

Refine the plan based on the user's feedback. Add, remove, reorder, or reword tasks as needed. Keep iterating until the user explicitly confirms the plan is good to go.

Do not proceed to step 5 until you have clear confirmation.

---

### Step 5: Write the GitHub issue

Format the issue body as follows:

```markdown
## Background
<1-2 sentences summarizing the problem or goal>

## Tasks
- [ ] task one
- [ ] task two
- [ ] task three
```

Keep the background concise and factual. The task list should exactly reflect the agreed plan from step 4 — do not add or remove tasks at this stage.

**If an issue number was provided:**

Update the issue using:
```sh
gh issue edit <n> --body "<content>"
```

If the existing issue title is vague or inaccurate given the refined plan, also update it:
```sh
gh issue edit <n> --title "<new title>"
```

**If no issue number was provided:**

Create a new issue. Propose a title to the user before creating — confirm or adjust it if they want. Then:
```sh
gh issue create --title "<title>" --body "$(cat <<'EOF'
## Background
<summary>

## Tasks
- [ ] task one
- [ ] task two
EOF
)"
```

Report the new issue number and URL after creation.

---

### Step 6: Signal ready

Confirm that the issue has been created or updated, print the issue URL, and tell the user they're scoped and ready to build.

Example closing message:
```
Issue #42 is updated: <url>

Scope is locked. Ready to build whenever you are.
```

**STOP HERE.**

Do not enter plan mode, start coding, create files, run commands, or take any implementation action. Your job is complete. The user will explicitly tell you when to proceed with the work.
