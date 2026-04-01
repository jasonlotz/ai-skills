---
name: advanced-skill-template
description: Reference guide for the full skill format — all frontmatter fields, supporting directories (templates, scripts, examples, references), and advanced patterns
license: MIT
compatibility: claude
---

## What I do

Output a comprehensive reference guide covering the complete skill format, every frontmatter field, and how to use supporting directories to build richer skills.

## When to use me

Use this skill when building a skill that needs more than just a `SKILL.md` — e.g. scaffold templates, validation scripts, reference docs, or advanced frontmatter options. For a minimal quick-start, use `/simple-skill-template` instead.

## Instructions

Respond with the following guide exactly:

---

# How to Create a New Skill (Advanced)

## Full directory structure

```
skills/
  <skill-name>/
    SKILL.md              # required: skill definition
    templates/            # optional: scaffold files (YAML, JSON, code, etc.)
    scripts/              # optional: executable helper scripts (.sh, .py, etc.)
    examples/             # optional: reference implementation files
    references/           # optional: detailed technical documentation (.md)
```

The entire skill directory is symlinked to `~/.claude/skills/<name>` and `~/.config/opencode/skills/<name>`, so all files are accessible from instructions via relative paths.

---

## Complete frontmatter field reference

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Lowercase alphanumeric + hyphens, e.g. `my-skill` |
| `description` | Yes | 1–1024 chars; specific enough for an agent to decide whether to load the skill |
| `license` | No | e.g. `MIT` |
| `compatibility` | No | `opencode` for tool-agnostic, `claude` for Claude-specific |
| `version` | No | Semantic version, e.g. `1.0.0` |
| `argument-hint` | No | Usage hint shown to user for slash command args, e.g. `<filename>` |
| `user-invocable` | No | Set `false` to hide from slash-command list (Claude-invoked only) |
| `disable-model-invocation` | No | Set `true` for user-facing output only (no Claude processing) |
| `tools` | No | Comma-separated list of tools the skill is allowed to use |
| `context` | No | Set `fork` to run the skill in an isolated subagent |
| `agent` | No | Agent type to use when `context: fork` is set |

---

## Supporting directories

### templates/
Scaffold files for generated output — any format (YAML, JSON, TypeScript, HTML, etc.). Reference them from `Instructions` via relative paths:

```
In instructions: "Use the template at templates/component.tsx.template as the basis for..."
```

### scripts/
Executable scripts for validation, parsing, or transformation. Make them executable and invoke from instructions:

```sh
bash scripts/validate.sh
```

### examples/
Reference implementations showing expected patterns or code style. Link from instructions to help users understand the expected output:

```
See examples/unit-test.ts for the expected test structure.
```

### references/
Deep-dive markdown documentation injected as context. Link from instructions when the skill needs to reason over detailed specs or patterns:

```
Consult references/auth.md for the authentication flow this skill implements.
```

---

## Registering the skill

After creating the skill directory, run from the repo root:

```sh
./link-skills.sh
```

This creates symlinks at:
- `~/.claude/skills/<skill-name>` → repo skill directory
- `~/.config/opencode/skills/<skill-name>` → repo skill directory

---

## Full checklist

- [ ] Directory created at `skills/<skill-name>/`
- [ ] `SKILL.md` (all caps) created inside it
- [ ] `name` in frontmatter matches directory name exactly
- [ ] `description` is specific and under 1024 chars
- [ ] Three required sections present (What I do, When to use me, Instructions)
- [ ] Supporting directories added as needed (`templates/`, `scripts/`, `examples/`, `references/`)
- [ ] Any scripts made executable (`chmod +x scripts/*.sh`)
- [ ] `./link-skills.sh` run to deploy symlinks
