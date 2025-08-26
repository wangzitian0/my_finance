#!/bin/bash
# Claude Squad Research Session Template
# Optimized for code exploration and research

set -e

echo "🔍 Starting research session..."

# Ensure we're in the project root
cd /Users/SP14016/zitian/my_finance

# Activate pixi environment
echo "📦 Activating pixi environment..."
export PATH="$HOME/.local/bin:$PATH"
eval "$(pixi shell-hook)"

echo "✅ Research session ready!"
echo ""
echo "Project structure:"
echo "  ETL/                - Extract, Transform, Load pipeline"
echo "  dcf_engine/         - DCF calculation engine" 
echo "  graph_rag/          - Graph RAG Q&A system"
echo "  common/             - Shared utilities and configurations"
echo "  spider/             - Data collection spiders"
echo "  evaluation/         - Performance evaluation"
echo ""
echo "Research commands:"
echo "  find . -name '*.py' | head -20  - List Python files"
echo "  find . -name 'README.md'        - Find README files"
echo "  tree -L 3                       - Show directory structure"
echo "  p3 etl-status                   - ETL pipeline status"
echo "  p3 verify-sec-data              - Check SEC data"
echo ""
echo "Code exploration:"
echo "  grep -r 'class.*Engine'         - Find engine classes"
echo "  grep -r 'def.*process'          - Find processing functions"
echo "  find . -name '*test*.py'        - Find test files"
echo ""