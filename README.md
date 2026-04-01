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
chmod +x stow-skills.sh
./stow-skills.sh
```

This symlinks each skill directory into the expected locations for each tool:

| Tool | Path |
| --- | --- |
| OpenCode | `~/.config/opencode/skills/<name>` |
| Claude | `~/.claude/skills/<name>` |

Re-run `stow-skills.sh` whenever you add a new skill.

## Adding a skill

1. Create a new directory under `skills/` matching the skill name
2. Add a `SKILL.md` with valid frontmatter (`name` must match the directory name)
3. Run `./stow-skills.sh`
