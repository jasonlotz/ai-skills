---
name: app-comparator
description: Deeply compares 2 or more applications given their relative paths. Analyzes and diffs dependencies, library versions, tooling, coding patterns, reusable components, and best practices — then produces a structured markdown report with prioritized recommendations to align the apps.
license: MIT
compatibility: opencode
---

## What I do

- Accepts 2 or more relative paths to application directories as input
- Detects each app's language, framework, and runtime from its manifests
- Diffs dependencies and library versions across all apps, flagging mismatches and missing packages
- Compares tooling and configuration (linters, formatters, test runners, build tools, CI, type configs)
- Analyzes coding patterns across source directories (component structure, state management, API layer, error handling, naming conventions)
- Identifies reusable code — logic or components duplicated across apps or present in one but useful to others
- Produces a structured markdown report with a prioritized action item list

## When to use me

Use me when you have 2 or more applications that should share standards, libraries, or coding patterns and you want a clear picture of where they diverge and how to align them. Common scenarios:

- Auditing a monorepo where multiple apps have drifted from each other
- Evaluating whether two separate repos can share a common library or component system
- Standardizing a team's apps before a migration or major refactor
- Reviewing an older app against a newer one to identify modernization opportunities

Invoke me with: `/app-comparator <path-to-app-1> <path-to-app-2> [<path-to-app-3> ...]`

## Instructions

### 0. Parse inputs

Extract the list of app paths from the invocation arguments. All paths are relative to the current working directory. Resolve and confirm each directory exists before proceeding. If a path does not exist, report it and stop.

### 1. Detect each app's stack

For each app, read its manifest files to determine language, runtime, framework, and package manager. Look for:

| Ecosystem    | Files to check                                          |
|--------------|---------------------------------------------------------|
| JavaScript   | `package.json`, `.nvmrc`, `.node-version`              |
| TypeScript   | `tsconfig.json`, `tsconfig.*.json`                     |
| Python       | `pyproject.toml`, `setup.py`, `requirements*.txt`, `Pipfile` |
| Go           | `go.mod`, `go.sum`                                     |
| Rust         | `Cargo.toml`, `Cargo.lock`                             |
| Ruby         | `Gemfile`, `.ruby-version`                             |
| Java/Kotlin  | `pom.xml`, `build.gradle`, `build.gradle.kts`          |
| .NET         | `*.csproj`, `*.sln`, `global.json`                     |
| Docker       | `Dockerfile`, `docker-compose.yml`                     |

Record: language, runtime version (if pinned), primary framework, package manager.

### 2. Inventory dependencies

For each app, collect all declared dependencies and their versions from the relevant manifest. Then:

- Build a unified dependency matrix: rows = package names, columns = apps, cells = version (or "missing")
- Flag **version mismatches** — same package at different versions across apps
- Flag **missing dependencies** — package present in one app but absent in another (note whether absence is intentional or an oversight)
- Flag **functional equivalents** — different package names that serve the same purpose (e.g. `axios` vs `node-fetch`, `pytest` vs `unittest`)
- Note packages that are significantly outdated relative to their latest stable release (use available context; do not make network calls unless the user requests it)

### 3. Inventory tooling and configuration

Compare the presence and configuration of:

- **Linters** (ESLint, Ruff, golangci-lint, RuboCop, etc.)
- **Formatters** (Prettier, Black, gofmt, rustfmt, etc.)
- **Test frameworks and runners** (Jest, Vitest, Pytest, Go test, etc.)
- **Build tools** (Webpack, Vite, esbuild, tsc, etc.)
- **CI/CD configs** (`.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, etc.)
- **Type checking configs** (`tsconfig.json`, `mypy.ini`, etc.)
- **Environment variable handling** (`.env.example`, dotenv libraries, secret managers)
- **Git hooks** (`.husky/`, `.pre-commit-config.yaml`, etc.)

For each category: note which apps have it, which don't, and where configs differ meaningfully.

### 4. Analyze coding patterns

Explore the source directories of each app. Focus on:

- **Directory/module structure** — how code is organized (feature-based, layer-based, flat, etc.)
- **Component or class patterns** — how UI components, services, or domain objects are structured
- **State management** — approach used (local state, context, Redux, Zustand, Pinia, signals, etc.)
- **API/data-fetching layer** — how external calls are made and abstracted
- **Error handling** — patterns for catching, logging, and surfacing errors
- **Testing patterns** — unit vs integration vs e2e coverage, test file co-location vs separate dirs
- **Naming conventions** — file names, function names, variable names (camelCase, snake_case, etc.)
- **Code comments and documentation** — JSDoc, docstrings, inline comments presence/style

Note patterns present in one app but absent or inconsistent in another.

### 5. Identify reusable code opportunities

Look for:

- **Duplicated utilities** — functions or helpers that do the same thing in both apps (string formatting, date handling, validation, etc.)
- **Parallel components** — UI components or service classes with the same purpose implemented differently
- **Shared constants or config** — magic strings, environment variable names, feature flags that are repeated
- **Extractable modules** — coherent pieces of logic in one app that the other app would benefit from having

For each candidate: name it, describe what it does, and note which app(s) it currently lives in.

### 6. Produce the report

Output a structured markdown report with the following sections. Be specific and concrete — cite file paths and line numbers where helpful.

---

#### App Overview

A summary table:

| Property         | App 1 | App 2 | ... |
|------------------|-------|-------|-----|
| Path             |       |       |     |
| Language         |       |       |     |
| Framework        |       |       |     |
| Runtime version  |       |       |     |
| Package manager  |       |       |     |

---

#### Dependencies

- Version mismatch table (package, app1 version, app2 version, recommendation)
- Missing packages per app with recommendation (add, remove, or intentional)
- Functional equivalents with recommendation (standardize on one)

---

#### Tooling & Configuration

Per category (linting, formatting, testing, build, CI, etc.):
- Which apps have it
- Key config differences
- Recommendation

---

#### Coding Patterns

Per pattern category (structure, state, API layer, error handling, etc.):
- How each app approaches it
- Which approach is preferred or more consistent with best practices
- Recommendation to align

---

#### Reusable Code Opportunities

Per candidate:
- Name / description
- Where it currently lives
- How to extract or share it (e.g., move to shared lib, publish as internal package, copy-with-attribution)

---

#### Prioritized Action Items

A numbered list ordered by impact (high to low). Each item should include:
- What to do
- Which app(s) it affects
- Why it matters

Example format:
```
1. [HIGH] Align on Node.js version — app-a uses 18, app-b uses 20. Standardize on 20 LTS.
2. [HIGH] Add ESLint to app-b — app-a has a full ESLint config; app-b has none.
3. [MED]  Extract date formatting utils — duplicated in app-a/src/utils/date.ts and app-b/lib/helpers.js.
4. [LOW]  Rename snake_case files in app-b to match camelCase convention used in app-a.
```

---

### 7. Offer next steps

After presenting the report, ask the user which action items they want to tackle first, and offer to begin implementing the highest-priority changes immediately.
