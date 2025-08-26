#!/bin/bash
# Claude Squad Development Session Template
# Optimized for main development workflow

set -e

echo "🚀 Starting development session..."

# Ensure we're in the project root
cd /Users/SP14016/zitian/my_finance

# Check git status
echo "📋 Git Status:"
git status --short

# Start with latest main
echo "🔄 Syncing with main branch..."
git checkout main 2>/dev/null || echo "Already on main or branch doesn't exist"
git pull origin main 2>/dev/null || echo "No remote updates"

# Activate pixi environment
echo "📦 Activating pixi environment..."
export PATH="$HOME/.local/bin:$PATH"
eval "$(pixi shell-hook)"

# Check environment status
echo "🔍 Environment Status:"
./p3 env-status

# Ready for development
echo "✅ Development session ready!"
echo ""
echo "Available p3 commands:"
echo "  p3 build m7          - Build M7 dataset"
echo "  p3 e2e              - Run end-to-end tests" 
echo "  p3 format           - Format code"
echo "  p3 lint             - Lint code"
echo "  p3 test             - Run tests"
echo "  p3 create-pr <desc> <issue> - Create PR"
echo ""
echo "Multi-window workflow:"
echo "  - This window: Main development"
echo "  - Open testing window: p3 squad-testing"
echo "  - Open docs window: p3 squad-docs"
echo "  - Open research window: p3 squad-research"
echo ""