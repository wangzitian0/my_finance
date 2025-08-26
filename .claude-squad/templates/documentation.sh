#!/bin/bash
# Claude Squad Documentation Session Template
# Optimized for documentation and README updates

set -e

echo "📚 Starting documentation session..."

# Ensure we're in the project root
cd /Users/SP14016/zitian/my_finance

# Activate pixi environment
echo "📦 Activating pixi environment..."
export PATH="$HOME/.local/bin:$PATH"
eval "$(pixi shell-hook)"

echo "✅ Documentation session ready!"
echo ""
echo "Documentation files:"
echo "  README.md           - Main project documentation"
echo "  CLAUDE.md           - Claude Code instructions"
echo "  docs/               - Detailed documentation"
echo ""
echo "Key documentation areas:"
echo "  - Architecture overview"
echo "  - API documentation"
echo "  - Setup instructions"
echo "  - Workflow guidelines"
echo "  - Multi-window development"
echo ""
echo "Useful commands:"
echo "  p3 build-status     - Check build status"
echo "  p3 cache-status     - Check cache status"
echo "  find . -name '*.md' - Find all markdown files"
echo ""