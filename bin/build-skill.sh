#!/bin/bash
# Build a .skill archive for importing a skill into Claude Desktop.
#
# Claude Desktop keeps its own read-only skill store and does not follow the
# symlinks that link-skills.sh creates for Claude Code and OpenCode. The only
# install path is importing a .skill archive (a plain zip) via the Save button.
#
# Usage: bash bin/build-skill.sh <skill-name> [output-dir]
set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_NAME="$1"
OUT_DIR="${2:-$REPO_ROOT/dist}"

if [ -z "$SKILL_NAME" ]; then
  echo "Usage: bash bin/build-skill.sh <skill-name> [output-dir]" >&2
  echo "Available:" >&2
  ls -1 "$REPO_ROOT/skills" | sed 's/^/  /' >&2
  exit 1
fi

SKILL_DIR="$REPO_ROOT/skills/$SKILL_NAME"
if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
  echo "No SKILL.md at $SKILL_DIR" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"
ARCHIVE="$OUT_DIR/$SKILL_NAME.skill"
rm -f "$ARCHIVE"

# SKILL.md must sit at the archive root, so zip from inside the skill directory.
( cd "$SKILL_DIR" && zip -q -r "$ARCHIVE" . \
    -x '*__pycache__*' -x '*.DS_Store' -x '*.pyc' )

echo "Built $ARCHIVE"
echo
unzip -Z1 "$ARCHIVE" | grep -v '/$' | sed 's/^/  /'
echo
echo "To install in Claude Desktop: open the app, import this file, and click"
echo "Save skill. Claude Code and OpenCode already track the repo via symlink."
