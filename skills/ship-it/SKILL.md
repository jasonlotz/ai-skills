---
name: ship-it
description: Prepares code for commit and push — runs build and lint, updates AGENTS.md and README.md if needed, then commits and pushes with a conventional commit message (feat:/fix:/etc.).
license: MIT
compatibility: claude
---

## What I do

- Runs any available build and lint commands to catch errors before committing
- Reviews recent changes and updates AGENTS.md and README.md if those docs are stale or incomplete
- Stages all relevant changes, writes a conventional commit message, and pushes to the current branch

## When to use me

Use me when you're ready to commit and push your work. I'll handle the final quality checks and documentation updates so you don't have to.

## Instructions

Follow these steps in order:

### 1. Understand what changed

Run `git diff HEAD` and `git status` to get a clear picture of all staged and unstaged changes.

### 2. Build and lint

**This step is mandatory — do not skip it.**

Look for build/lint scripts in the project (e.g. `package.json` scripts, `Makefile`, `pyproject.toml`, etc.) and run them:
- If a build step exists, **run it now**. Do not proceed until it passes.
- If a lint step exists (e.g. `eslint`, `ruff`, `golangci-lint`), **run it now**. Do not proceed until it passes.
- Fix any errors before moving on — never commit with a failing build or lint.
- Only skip this step if you have confirmed that no build or lint commands exist in the project.

### 3. Update docs if needed

Read `AGENTS.md` and `README.md`. Compare them against the changes from step 1. Update either file if:
- A new skill, feature, or tool was added that isn't documented
- Existing instructions are now inaccurate or incomplete
- The structure section is out of date

Only make changes that are accurate and necessary — do not pad or invent content.

### 4. Stage changes

Stage all modified and new files relevant to the work. Avoid staging unrelated files or secrets (`.env`, credentials, etc.).

### 5. Write the commit message

Use the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>: <short imperative summary>
```

Common types:
- `feat:` — new feature or skill
- `fix:` — bug fix
- `docs:` — documentation-only changes
- `refactor:` — code change that isn't a fix or feature
- `chore:` — maintenance (deps, config, tooling)

Rules:
- Summary must be lowercase and imperative (e.g. `feat: add ship-it skill`)
- No period at the end
- Keep it under 72 characters

### 6. Commit and push

```sh
git commit -m "<your message>"
git push
```

If the branch has no upstream, use `git push -u origin <branch>`.

After pushing, confirm success and report the commit hash and message to the user.
