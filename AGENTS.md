# AGENTS.md — Project Context for AI Coding Agents

## Goal

A collection of reusable AI agent skills for use with OpenCode and Claude. Skills are stored in a tool-agnostic directory structure and deployed to each tool's expected location via `link-skills.sh`.

---

## Critical Rules

- **Never run `git commit` or `git push` without explicit user permission**
- **Skill directory names must exactly match the `name` field** in the corresponding `SKILL.md` frontmatter
- **`SKILL.md` must be spelled in all caps**
- **`name` must be lowercase alphanumeric with single hyphens** — e.g. `hello-world`, not `Hello_World`

---

## Code Style & Conventions

### Skill Frontmatter

- Required fields: `name`, `description`
- Optional fields: `license`, `compatibility`, `metadata`
- `description` should be specific enough for an agent to decide whether to load the skill (1–1024 chars)
- `compatibility`: use `opencode` for tool-agnostic skills, `claude` for Claude-specific ones

### Skill Content

- Write instructions in plain markdown after the frontmatter
- Include a "What I do" section, a "When to use me" section, and an "Instructions" section
- Keep skills focused on a single responsibility

---

## Structure

```
skills/
  <skill-name>/
    SKILL.md
hooks/
  <hook-name>.sh   — Claude Code harness hooks, referenced by absolute path from settings.json
link-skills.sh    — symlinks skills into OpenCode/Claude dirs and prepares hooks
README.md
AGENTS.md         — project context for AI coding agents (Codex, Gemini, etc.)
CLAUDE.md         — Claude Code entry point; references AGENTS.md
```

---

## Adding a Skill

1. Create `skills/<skill-name>/SKILL.md`
2. Ensure `name` in frontmatter matches the directory name exactly
3. Run `./link-skills.sh` from the repo root to deploy

---

## Adding a Hook

Hooks are shell scripts invoked by the Claude Code harness (`SessionStart`,
`PreToolUse`, etc.). Unlike skills they are not auto-loaded — they must be
referenced by absolute path from `~/.claude/settings.json`.

1. Create `hooks/<hook-name>.sh` with a shebang
2. Run `./link-skills.sh` to make it executable; the script prints the
   `settings.json` snippet to copy in
3. Keep hooks fast and idempotent — they may run on every session start
