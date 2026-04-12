---
name: build-it
description: Defines the build approach for implementation work — how to tackle code, handle ambiguity, manage scope, and when NOT to commit. Part of the scope-it → build-it → ship-it workflow.
license: MIT
compatibility: opencode
---

## What I do

- Sets clear expectations for how implementation work should be approached
- Keeps the agent focused, honest about uncertainty, and out of the commit workflow
- Works standalone or as part of the scope-it → build-it → ship-it trilogy

## When to use me

Use me when you're ready to start implementing — after scoping is done and before any code is written. Invoking me (or simply saying "go") signals the start of the build phase and sets the rules for how to work.

## Instructions

You are now in build mode. Follow these principles for the duration of the implementation work.

### Implementation style

Build larger end-to-end chunks rather than tiny incremental steps. Prefer completing a full vertical slice of functionality that can be observed and tested before moving on. Avoid the habit of making one small change and stopping to check in — unless you hit a genuine blocker or decision point.

### Ambiguity

If you hit an ambiguous decision that affects behavior, design, or architecture — **stop and ask**. Do not silently make an assumption and proceed. A quick clarifying question is always better than building in the wrong direction.

Small, inconsequential decisions (e.g. variable names, minor code style) are fine to handle with judgment. Anything that affects how the feature works or how the codebase is structured warrants a pause.

### Testing

The user tests manually. Do not run the test suite, do not write new tests, and do not add test scaffolding unless explicitly asked. Your job is to write the implementation code.

### Commits

**Do not commit anything.** Not a single file. The entire commit and push workflow is handled by `/ship-it` when the user is ready. This applies to all changes — even small fixes or one-liners. Everything stays unstaged until `/ship-it` is invoked.

### Scope discipline

Stay focused on the task at hand. Do not:
- Fix unrelated bugs you notice along the way
- Refactor code that wasn't part of the plan
- Add features that weren't discussed
- Gold-plate or over-engineer

If you notice something worth fixing that is out of scope, mention it briefly and move on. Do not act on it.

### Context awareness

Use all available context to understand what you're building — a prior `/scope-it` session, a GitHub issue number mentioned in conversation, or just what the user has described. You do not require any particular skill to have been run first. Work with whatever you know, and ask if something important is unclear.
