#!/usr/bin/env bash
# Claude Code SessionStart hook.
#
# When a session starts in a git worktree (not the main checkout) of a
# Next.js project, symlink gitignored env files from the main checkout and
# materialize node_modules so the worktree is immediately runnable.
#
# Idempotent: re-running is a no-op once setup is complete.

set -euo pipefail

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

git_dir="$(cd "$(git rev-parse --git-dir)" && pwd)"
git_common_dir="$(cd "$(git rev-parse --git-common-dir)" && pwd)"

# Same dir means main checkout, not a worktree — nothing to do.
[ "$git_dir" = "$git_common_dir" ] && exit 0

main_checkout="$(git worktree list --porcelain | awk '/^worktree / {print $2; exit}')"
[ -n "$main_checkout" ] && [ "$main_checkout" != "$PWD" ] || exit 0

# Only act on Next.js projects.
[ -f package.json ] && grep -q '"next"' package.json || exit 0

actions=()

for f in .env .env.local; do
  if [ ! -e "$f" ] && [ -e "$main_checkout/$f" ]; then
    ln -s "$main_checkout/$f" "$f"
    actions+=("symlinked $f from main checkout")
  fi
done

if [ ! -d node_modules ] && [ -f package-lock.json ]; then
  npm ci --silent
  actions+=("ran npm ci")
fi

if [ ${#actions[@]} -gt 0 ]; then
  printf 'Worktree setup: %s\n' "$(IFS='; '; echo "${actions[*]}")"
fi
