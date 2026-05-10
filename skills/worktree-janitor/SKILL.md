---
name: worktree-janitor
description: Sweeps up Claude Code worktree leftovers — orphan .claude/worktrees/<name>/ directory stubs and merged claude/* local branches that have no active worktree. Lists unmerged claude/* branches for review but never deletes them. Use when the user wants to clean up after worktree-isolated agent runs.
license: MIT
compatibility: claude
---

## What I do

- Remove orphan `.claude/worktrees/<name>/` directory stubs that git no longer tracks
- Delete merged local `claude/*` branches that have no active worktree
- List unmerged `claude/*` branches for the user's manual review (never delete them)

## When to use me

Invoke when the user wants to clean up worktree leftovers — phrasings like:
- "clean up worktrees"
- "tidy up after agent runs"
- "are there stale claude branches"
- "run the janitor"

## Instructions

### 1. Determine scope

Decide which paths to scan:

- If the user names a specific repo or directory, use that
- If the current working directory is inside `~/Workspaces/fleet/`, default to scanning the whole fleet: `~/Workspaces/fleet/*`
- Otherwise default to the current repo (no path argument)

### 2. Preview with --dry-run

Run the janitor in dry-run mode first to show the user what would be cleaned. The script lives at:

```
~/Workspaces/ai-skills/bin/worktree-janitor.sh
```

Invoke:

```sh
bash ~/Workspaces/ai-skills/bin/worktree-janitor.sh --dry-run <paths>
```

Show the output to the user. If nothing was found, report that and stop — no cleanup needed.

### 3. Confirm before deleting

If the dry-run found things to clean, ask the user to confirm before proceeding. Show:
- The orphan directories (with sizes)
- The merged branches (which will be deleted)
- Any unmerged branches (which will NOT be deleted, listed for awareness only)

Wait for explicit confirmation.

### 4. Run with -y to clean

Once confirmed, run again with `-y` to actually delete:

```sh
bash ~/Workspaces/ai-skills/bin/worktree-janitor.sh -y <paths>
```

### 5. Handle unmerged branches

If the dry-run listed unmerged `claude/*` branches under "Kept", the script will NOT touch them. After cleaning the safe ones, surface those to the user with the suggested fix:

```sh
git -C <repo> branch -D <branch>
```

Ask before running — unmerged means the work is only on that branch and nowhere else.

### 6. Report results

Summarize what was removed (count of dirs + count of branches) and what was kept (unmerged count). Keep it brief.
