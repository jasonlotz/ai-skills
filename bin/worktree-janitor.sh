#!/usr/bin/env bash
# Sweep up Claude Code worktree leftovers.
#
# Two cleanup passes:
#   1. Orphan worktree directories under .claude/worktrees/<name>/ that
#      git no longer tracks
#   2. Stale local claude/* branches that have no active worktree and are
#      fully merged into the repo's default branch
#
# Unmerged claude/* branches are listed for review but never deleted.
#
# Usage:
#   worktree-janitor.sh [-y|--dry-run] [REPO ...]
#
# With no REPO args, scans the current directory's repo. Pass paths
# (e.g. ~/Workspaces/fleet/*) to scan multiple.
#
# Flags:
#   -y, --yes       Skip the confirmation prompt and clean immediately
#   --dry-run       List what would be cleaned, then exit (no prompt, no delete)

set -euo pipefail

CONFIRM=1
DRY_RUN=0
while [ $# -gt 0 ]; do
  case "$1" in
    -y|--yes) CONFIRM=0; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help)
      sed -n '2,/^[^#]/p' "$0" | sed 's/^# \?//;$d'
      exit 0
      ;;
    --) shift; break ;;
    -*) echo "unknown flag: $1" >&2; exit 2 ;;
    *) break ;;
  esac
done

repos=("$@")
[ ${#repos[@]} -eq 0 ] && repos=(".")

orphan_dirs=()
merged_branches=()
unmerged_branches=()

for repo in "${repos[@]}"; do
  [ -d "$repo" ] || continue
  git -C "$repo" rev-parse --git-dir >/dev/null 2>&1 || continue

  repo_path="$(cd "$repo" && pwd)"

  active_paths="$(git -C "$repo" worktree list --porcelain | awk '/^worktree / {print $2}')"
  active_branches="$(git -C "$repo" worktree list --porcelain \
    | awk '/^branch / {sub(/^refs\/heads\//, "", $2); print $2}')"

  wt_root="$repo_path/.claude/worktrees"
  if [ -d "$wt_root" ]; then
    for entry in "$wt_root"/*/; do
      [ -d "$entry" ] || continue
      entry_path="$(cd "$entry" && pwd)"
      if ! printf '%s\n' "$active_paths" | grep -Fxq "$entry_path"; then
        orphan_dirs+=("$entry_path")
      fi
    done
    git -C "$repo" worktree prune 2>/dev/null || true
  fi

  default_branch="$(git -C "$repo" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')"
  default_branch="${default_branch:-main}"
  current_branch="$(git -C "$repo" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")"

  while IFS= read -r br; do
    [ -z "$br" ] && continue
    [ "$br" = "$current_branch" ] && continue
    if printf '%s\n' "$active_branches" | grep -Fxq "$br"; then
      continue
    fi
    if git -C "$repo" merge-base --is-ancestor "$br" "$default_branch" 2>/dev/null; then
      behind="$(git -C "$repo" rev-list --count "$br..$default_branch" 2>/dev/null || echo "?")"
      merged_branches+=("$repo_path|$br|$behind|$default_branch")
    else
      ahead="$(git -C "$repo" rev-list --count "$default_branch..$br" 2>/dev/null || echo "?")"
      unmerged_branches+=("$repo_path|$br|$ahead|$default_branch")
    fi
  done < <(git -C "$repo" for-each-ref --format='%(refname:short)' 'refs/heads/claude/*' 2>/dev/null)
done

total_to_remove=$(( ${#orphan_dirs[@]} + ${#merged_branches[@]} ))

if [ $total_to_remove -eq 0 ] && [ ${#unmerged_branches[@]} -eq 0 ]; then
  echo "Nothing to clean — no orphan stubs or stale claude/* branches found."
  exit 0
fi

if [ ${#orphan_dirs[@]} -gt 0 ]; then
  echo "Found ${#orphan_dirs[@]} orphan worktree stub(s):"
  for p in "${orphan_dirs[@]}"; do
    size="$(du -sh "$p" 2>/dev/null | cut -f1)"
    printf '  %s  (%s)\n' "$p" "$size"
  done
  echo ""
fi

if [ ${#merged_branches[@]} -gt 0 ]; then
  echo "Found ${#merged_branches[@]} merged claude/* branch(es):"
  for entry in "${merged_branches[@]}"; do
    IFS='|' read -r rp br behind def <<< "$entry"
    printf '  %s: %s (%s commits behind %s)\n' "$(basename "$rp")" "$br" "$behind" "$def"
  done
  echo ""
fi

if [ ${#unmerged_branches[@]} -gt 0 ]; then
  echo "Kept (unmerged claude/* branches — review and 'git branch -D' if intentional):"
  for entry in "${unmerged_branches[@]}"; do
    IFS='|' read -r rp br ahead def <<< "$entry"
    printf '  %s: %s (%s commits ahead of %s)\n' "$(basename "$rp")" "$br" "$ahead" "$def"
  done
  echo ""
fi

if [ $total_to_remove -eq 0 ]; then
  exit 0
fi

if [ $DRY_RUN -eq 1 ]; then
  exit 0
fi

if [ $CONFIRM -eq 1 ]; then
  printf 'Remove all? [y/N] '
  read -r reply
  case "${reply:-}" in
    y|Y|yes|YES) ;;
    *) echo "Aborted."; exit 0 ;;
  esac
fi

if [ ${#orphan_dirs[@]} -gt 0 ]; then
  for p in "${orphan_dirs[@]}"; do
    rm -rf "$p"
    echo "Removed dir: $p"
  done
fi

if [ ${#merged_branches[@]} -gt 0 ]; then
  for entry in "${merged_branches[@]}"; do
    IFS='|' read -r rp br _ _ <<< "$entry"
    if git -C "$rp" branch -d "$br" >/dev/null 2>&1; then
      echo "Deleted branch: $(basename "$rp")/$br"
    else
      echo "FAILED to delete: $(basename "$rp")/$br (try 'git -C $rp branch -d $br' manually)" >&2
    fi
  done
fi
