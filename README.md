# ai-skills

A collection of reusable AI agent skills for use with OpenCode and Claude.

## Structure

```
skills/
  <skill-name>/
    SKILL.md     — skill definition (frontmatter + instructions)
hooks/
  <hook>.sh      — Claude Code harness hooks (e.g. SessionStart)
bin/
  <script>.sh    — standalone CLI scripts (typically invoked by a paired skill)
```

Each skill is a directory containing a single `SKILL.md` file with YAML frontmatter (`name`, `description`) followed by markdown instructions.

Hooks are shell scripts invoked by the Claude Code harness — see [Hooks](#hooks) below. Standalone scripts live under `bin/` — see [Bin Scripts](#bin-scripts).

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

Follow these steps:

1. Create a new directory under `skills/` matching the skill name
2. Add a `SKILL.md` with valid frontmatter (`name` must match the directory name)
3. Run `bash link-skills.sh`

## Hooks

Shell scripts under `hooks/` are referenced by absolute path from
`~/.claude/settings.json`. Running `link-skills.sh` makes them executable and
prints the settings snippet to wire them up.

Current hooks:

- `worktree-setup.sh` — `SessionStart` hook. When a session opens in a git
  worktree of a Next.js project, symlinks `.env` / `.env.local` from the main
  checkout and runs `npm ci` if `node_modules` is missing. No-op outside
  worktrees and on non-Next.js projects.

## Bin Scripts

Standalone scripts under `bin/` hold logic that's easier to test and version
as shell. They're typically invoked by a paired skill (so the user calls
`/skill-name`, the skill runs the script). `link-skills.sh` makes them
executable; `bin/` is not added to `PATH`.

Current scripts:

- `worktree-janitor.sh` — paired with the `worktree-janitor` skill. Sweeps
  Claude Code worktree leftovers in two passes: orphan
  `.claude/worktrees/<name>/` directory stubs that git no longer tracks, and
  merged local `claude/*` branches with no active worktree. Unmerged
  `claude/*` branches are listed for review but never deleted. Flags: `-y`
  skips the prompt, `--dry-run` lists without deleting. Defaults to the
  current repo; pass paths to scan multiple (e.g.
  `worktree-janitor.sh ~/Workspaces/fleet/*`).

## AI agent context

See [AGENTS.md](AGENTS.md) for conventions, rules, and project context used by AI coding agents (Codex, Gemini, etc.). Claude Code reads [CLAUDE.md](CLAUDE.md), which points there as well.
