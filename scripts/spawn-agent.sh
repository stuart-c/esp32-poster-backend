#!/bin/bash
# spawn-agent.sh (Optimized for .trees/ directory)

TASK_NAME=$1
# Replace spaces with hyphens for clean folder naming
CLEAN_NAME=$(echo "$TASK_NAME" | tr ' ' '-')
WORKTREE_PATH=".trees/$CLEAN_NAME"

# Ensure the .trees directory is ignored by Git
if ! grep -qs "^.trees/" .gitignore; then
  echo ".trees/" >> .gitignore
  echo "📁 Added .trees/ to .gitignore"
fi

echo "🚀 Spawning Agent Worktree: $WORKTREE_PATH"
git worktree add -b "feat/$CLEAN_NAME" "$WORKTREE_PATH" main

# Hand off to Antigravity
antigravity open "$WORKTREE_PATH" --rules ".antigravity/rules.md" --task "$TASK_NAME"
