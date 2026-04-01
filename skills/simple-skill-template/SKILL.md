---
name: simple-skill-template
description: Reference guide for the minimal skill format — directory structure, required frontmatter fields, required sections, and how to register a new skill
license: MIT
compatibility: claude
---

## What I do

Output a concise reference guide for creating a basic skill with just a `SKILL.md`.

## When to use me

Use this skill when you want a quick reminder of the minimal skill file format, naming rules, required sections, and how to register a new skill. For advanced patterns (supporting directories, full frontmatter fields), use `/advanced-skill-template` instead.

## Instructions

Respond with the following guide exactly:

---

# How to Create a New Skill (Simple)

## Directory structure

```
skills/
  <skill-name>/
    SKILL.md
```

- The directory name must exactly match the `name` field in `SKILL.md`
- `SKILL.md` must be spelled in all caps

## SKILL.md format

```markdown
---
name: your-skill-name
description: What this skill does (1–1024 chars, specific enough for an agent to decide whether to load it)
license: MIT
compatibility: claude
---

## What I do

- Bullet points describing what the skill does

## When to use me

When to invoke this skill.

## Instructions

What Claude should actually do when this skill is triggered.
```

## Naming rules

- `name` must be **lowercase alphanumeric with single hyphens** — e.g. `my-skill`, not `MySkill` or `my_skill`
- Directory name must match `name` exactly
- `compatibility` should be `opencode` for tool-agnostic skills, or `claude` for Claude-specific ones

## Required sections

Every skill should have:
1. **What I do** — describes the skill's purpose
2. **When to use me** — helps the agent decide when to invoke it
3. **Instructions** — the actual behavior Claude executes

## Registering the skill

After creating `skills/<skill-name>/SKILL.md`, run from the repo root:

```sh
./link-skills.sh
```

This creates symlinks at:
- `~/.claude/skills/<skill-name>` → repo skill directory
- `~/.config/opencode/skills/<skill-name>` → repo skill directory

## Quick checklist

- [ ] Directory created at `skills/<skill-name>/`
- [ ] `SKILL.md` (all caps) created inside it
- [ ] `name` in frontmatter matches directory name exactly
- [ ] `description` is specific and under 1024 chars
- [ ] Three required sections present (What I do, When to use me, Instructions)
- [ ] `./link-skills.sh` run to deploy symlinks
