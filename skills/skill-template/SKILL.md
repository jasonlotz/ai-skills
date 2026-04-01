---
name: skill-template
description: Reference implementation that outputs a guide for creating new skills in this repo
license: MIT
compatibility: claude
---

## What I do

Output a complete reference guide explaining the skill system and how to create a new skill from scratch.

## When to use me

Use this skill when you want a reminder of the skill file format, naming rules, required sections, and how to register a new skill.

## Instructions

Respond with the following guide exactly:

---

# How to Create a New Skill

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
./stow-skills.sh
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
- [ ] `./stow-skills.sh` run to deploy symlinks
