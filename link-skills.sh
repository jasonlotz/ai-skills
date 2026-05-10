#!/bin/bash
set -e

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"
HOOKS_DIR="$REPO_ROOT/hooks"
BIN_DIR="$REPO_ROOT/bin"
OPENCODE_SKILLS="$HOME/.config/opencode/skills"
CLAUDE_SKILLS="$HOME/.claude/skills"

mkdir -p "$OPENCODE_SKILLS"
mkdir -p "$CLAUDE_SKILLS"

for skill_dir in "$SKILLS_DIR"/*/; do
  skill_name=$(basename "$skill_dir")

  ln -sfn "$skill_dir" "$OPENCODE_SKILLS/$skill_name"
  echo "Linked $OPENCODE_SKILLS/$skill_name -> $skill_dir"

  ln -sfn "$skill_dir" "$CLAUDE_SKILLS/$skill_name"
  echo "Linked $CLAUDE_SKILLS/$skill_name -> $skill_dir"
done

if [ -d "$HOOKS_DIR" ]; then
  for hook in "$HOOKS_DIR"/*.sh; do
    [ -f "$hook" ] || continue
    chmod +x "$hook"
    echo "Made executable: $hook"
  done

  cat <<EOF

Hooks are checked in but not auto-wired. To enable worktree-setup, add to
~/.claude/settings.json:

{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          { "type": "command", "command": "bash $HOOKS_DIR/worktree-setup.sh" }
        ]
      }
    ]
  }
}
EOF
fi

if [ -d "$BIN_DIR" ]; then
  for script in "$BIN_DIR"/*.sh; do
    [ -f "$script" ] || continue
    chmod +x "$script"
    echo "Made executable: $script"
  done

  echo ""
  echo "Bin scripts made executable. They are typically invoked by their"
  echo "paired skill (e.g. /worktree-janitor) — no PATH or alias needed."
fi
