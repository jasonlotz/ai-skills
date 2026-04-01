# ai-skills

A collection of reusable AI agent skills for use with OpenCode and Claude.

## Structure

```
skills/
  <skill-name>/
    SKILL.md    — skill definition (frontmatter + instructions)
```

Each skill is a directory containing a single `SKILL.md` file with YAML frontmatter (`name`, `description`) followed by markdown instructions.

## Setup

Run the install script from the repo root:

```bash
bash link-skills.sh
```

This symlinks each skill directory into the expected locations for each tool:

| Tool | Path |
| --- | --- |
| OpenCode | `~/.config/opencode/skills/<name>` |
| Claude | `~/.claude/skills/<name>` |

Re-run `link-skills.sh` whenever you add a new skill.

## Adding a skill

Use the `/simple-skill-template` or `/advanced-skill-template` skill for a reference guide, or follow these steps:

1. Create a new directory under `skills/` matching the skill name
2. Add a `SKILL.md` with valid frontmatter (`name` must match the directory name)
3. Run `bash link-skills.sh`

## AI agent context

See [AGENTS.md](AGENTS.md) for conventions, rules, and project context used by AI coding agents (Codex, Gemini, etc.). Claude Code reads [CLAUDE.md](CLAUDE.md), which points there as well.
