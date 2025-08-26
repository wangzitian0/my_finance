#!/bin/bash
# Claude Squad Testing Session Template
# Optimized for testing and validation workflow

set -e

echo "🧪 Starting testing session..."

# Ensure we're in the project root
cd /Users/SP14016/zitian/my_finance

# Activate pixi environment
echo "📦 Activating pixi environment..."
export PATH="$HOME/.local/bin:$PATH"
eval "$(pixi shell-hook)"

# Run environment checks
echo "🔍 Environment Status:"
./p3 env-status

echo "✅ Testing session ready!"
echo ""
echo "Testing commands:"
echo "  p3 e2e              - Full end-to-end test (M7)"
echo "  p3 e2e f2           - Fast 2-company test"  
echo "  p3 test             - Unit tests"
echo "  p3 format           - Format code"
echo "  p3 lint             - Lint code"
echo "  p3 build m7         - Build M7 dataset"
echo ""
echo "Validation commands:"
echo "  p3 verify-env       - Verify environment"
echo "  p3 check-integrity  - Check data integrity"
echo "  p3 verify-sec-data  - Verify SEC data"
echo ""