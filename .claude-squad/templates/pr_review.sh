#!/bin/bash
# Claude Squad PR Review Session Template
# Optimized for PR creation and review workflow

set -e

echo "🔀 Starting PR review session..."

# Ensure we're in the project root
cd /Users/SP14016/zitian/my_finance

# Activate pixi environment
echo "📦 Activating pixi environment..."
export PATH="$HOME/.local/bin:$PATH"
eval "$(pixi shell-hook)"

# Check git status
echo "📋 Git Status:"
git status --short

# Show recent branches
echo "🌿 Recent branches:"
git branch --sort=-committerdate | head -10

echo "✅ PR review session ready!"
echo ""
echo "PR workflow commands:"
echo "  p3 e2e                      - Run M7 tests (required before PR)"
echo "  p3 create-pr <desc> <issue> - Create PR with test validation"
echo "  p3 cleanup-branches         - Clean up merged branches"
echo ""
echo "Git commands:"
echo "  git status                  - Check current status"
echo "  git log --oneline -10       - Recent commits"
echo "  git diff                    - Show changes"
echo "  gh pr list                  - List PRs"
echo "  gh pr view <number>         - View specific PR"
echo ""
echo "Issue tracking:"
echo "  gh issue list               - List open issues"
echo "  gh issue view <number>      - View specific issue"
echo ""
echo "⚠️  Remember: Always run 'p3 e2e' before creating PRs!"
echo ""