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

# Claude Desktop keeps its own skill store under a UUID path. It is NOT auto-populated
# here: we only re-point skills Desktop ALREADY has, so Desktop's skill set stays as you
# curated it and Code-only skills are not pushed into it. Re-run this after a Desktop
# update if a shared skill reverts to a private copy.
DESKTOP_STORE=$(find "$HOME/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin" \
  -maxdepth 3 -type d -name skills 2>/dev/null | head -1)

if [ -n "$DESKTOP_STORE" ] && [ -w "$DESKTOP_STORE" ]; then
  for skill_dir in "$SKILLS_DIR"/*/; do
    skill_name=$(basename "$skill_dir")
    target="$DESKTOP_STORE/$skill_name"

    [ -e "$target" ] || [ -L "$target" ] || continue          # only skills Desktop already has
    [ -L "$target" ] && [ "$(readlink "$target")" = "${skill_dir%/}" ] && continue  # already linked

    if [ ! -L "$target" ]; then
      backup="$REPO_ROOT/dist/desktop-backup-$skill_name-$(date +%Y%m%d%H%M%S)"
      mkdir -p "$REPO_ROOT/dist"
      mv "$target" "$backup"
      echo "Backed up Desktop's copy of $skill_name -> $backup"
    else
      rm -f "$target"
    fi

    ln -s "${skill_dir%/}" "$target"
    echo "Linked $target -> ${skill_dir%/}  (Claude Desktop)"
  done
else
  echo "Claude Desktop skill store not found or not writable; skipping."
fi

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
