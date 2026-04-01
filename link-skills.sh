#!/bin/bash
set -e

SKILLS_DIR="$(cd "$(dirname "$0")" && pwd)/skills"
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
