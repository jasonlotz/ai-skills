#!/bin/bash
set -e

SKILLS_DIR="$(cd "$(dirname "$0")" && pwd)/skills"

# Detect OS and set paths
case "$(uname -s)" in
  Darwin)  # macOS
    OPENCODE_SKILLS="$HOME/.config/opencode/skills"
    CLAUDE_SKILLS="$HOME/.claude/skills"
    ;;
  MINGW*|MSYS*|CYGWIN*)  # Windows (Git Bash, MSYS2, Cygwin)
    OPENCODE_SKILLS="${APPDATA}/opencode/skills"
    CLAUDE_SKILLS="${USERPROFILE}/.claude/skills"
    # Enable native Windows symlinks in Git Bash/MSYS2
    export MSYS=winsymlinks:nativestrict
    ;;
  Linux)
    OPENCODE_SKILLS="$HOME/.config/opencode/skills"
    CLAUDE_SKILLS="$HOME/.claude/skills"
    ;;
  *)
    echo "Unsupported OS: $(uname -s)"
    exit 1
    ;;
esac

mkdir -p "$OPENCODE_SKILLS"
mkdir -p "$CLAUDE_SKILLS"

# Track if any symlink fails (for Windows warning)
SYMLINK_FAILED=false

for skill_dir in "$SKILLS_DIR"/*/; do
  skill_name=$(basename "$skill_dir")

  # Remove existing target (directory or symlink) before creating symlink
  rm -rf "$OPENCODE_SKILLS/$skill_name" 2>/dev/null || true
  if ln -sfn "$skill_dir" "$OPENCODE_SKILLS/$skill_name" 2>/dev/null; then
    echo "Linked $OPENCODE_SKILLS/$skill_name -> $skill_dir"
  else
    echo "Failed to link $OPENCODE_SKILLS/$skill_name"
    SYMLINK_FAILED=true
  fi

  # Remove existing target (directory or symlink) before creating symlink
  rm -rf "$CLAUDE_SKILLS/$skill_name" 2>/dev/null || true
  if ln -sfn "$skill_dir" "$CLAUDE_SKILLS/$skill_name" 2>/dev/null; then
    echo "Linked $CLAUDE_SKILLS/$skill_name -> $skill_dir"
  else
    echo "Failed to link $CLAUDE_SKILLS/$skill_name"
    SYMLINK_FAILED=true
  fi
done

# Warn Windows users about symlink issues
if [ "$SYMLINK_FAILED" = true ]; then
  echo ""
  echo "WARNING: Some symlinks failed to create."
  case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*)
      echo "On Windows, symlinks require Developer Mode to be enabled."
      echo "To enable: Settings > Update & Security > For developers > Developer Mode"
      echo "Alternatively, run Git Bash as Administrator."
      ;;
  esac
fi
