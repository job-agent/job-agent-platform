#!/bin/bash
set -e

REPO_NAME="job-agent-platform"

if [ -z "$1" ]; then
    echo "Usage: $0 <worktree-name>"
    echo "Example: $0 task1"
    exit 1
fi

WORKTREE_NAME="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MONOREPO_ROOT="$(cd "$REPO_ROOT/.." && pwd)"
WORKTREE_PATH="$MONOREPO_ROOT/worktrees/$REPO_NAME/$WORKTREE_NAME"

cd "$REPO_ROOT"

# Remove worktree locally
if [ -d "$WORKTREE_PATH" ]; then
    git worktree remove "$WORKTREE_PATH" --force
    echo "Removed local worktree: $WORKTREE_PATH"
else
    echo "Worktree not found locally: $WORKTREE_PATH"
fi

# Delete branch from GitHub
if git ls-remote --exit-code --heads origin "$WORKTREE_NAME" > /dev/null 2>&1; then
    git push origin --delete "$WORKTREE_NAME"
    echo "Deleted remote branch: $WORKTREE_NAME"
else
    echo "Remote branch not found: $WORKTREE_NAME"
fi

# Delete local branch if it exists
if git show-ref --verify --quiet "refs/heads/$WORKTREE_NAME"; then
    git branch -D "$WORKTREE_NAME"
    echo "Deleted local branch: $WORKTREE_NAME"
fi

echo "Worktree cleanup complete"
