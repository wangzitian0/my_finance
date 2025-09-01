#!/bin/bash
# I/O Compliance Validation Script
# Enforces SSOT DirectoryManager usage across the codebase

set -e

echo "🔍 Checking I/O compliance..."
echo "========================================"

VIOLATIONS=0

# Function to check and report violations
check_violation() {
    local check_name="$1"
    local pattern="$2"
    local directories="$3"
    local severity="$4"
    
    echo -n "Checking $check_name... "
    
    if grep -r "$pattern" --include="*.py" $directories 2>/dev/null | grep -v "# ALLOWED\|# OK\|# EXEMPT" | head -5; then
        echo "❌ VIOLATION FOUND"
        echo "   Severity: $severity"
        echo "   Files with violations shown above"
        VIOLATIONS=$((VIOLATIONS + 1))
        echo
    else
        echo "✅ OK"
    fi
}

# Check 1: Hard-coded paths (Level 3 Violation)
check_violation \
    "hard-coded Path() constructions" \
    'Path\s*\(\s*["\'"'"'][^"]*build_data\|common/config\|data/["\'"'"']' \
    "ETL/ common/ dcf_engine/ graph_rag/" \
    "LEVEL 3 - BLOCKS PR"

# Check 2: Direct file operations with hard-coded paths (Level 3 Violation)
check_violation \
    "direct file operations with hard-coded paths" \
    'open\s*\(\s*["\'"'"'][^"]*\.\|/[^"]*["\'"'"']' \
    "ETL/ common/ dcf_engine/ graph_rag/" \
    "LEVEL 3 - BLOCKS PR"

# Check 3: Removed I/O libraries (Level 3 Violation) 
check_violation \
    "removed I/O libraries" \
    "from.*common\.io_utils\|from.*common\.storage_backends\|import.*io_utils\|import.*storage_backends" \
    ". --exclude-dir=.git --exclude-dir=__pycache__" \
    "LEVEL 3 - BLOCKS PR"

echo "========================================"

if [ $VIOLATIONS -eq 0 ]; then
    echo "🎉 I/O COMPLIANCE VALIDATION PASSED"
    echo "All I/O operations follow SSOT DirectoryManager patterns"
    exit 0
else
    echo "❌ I/O COMPLIANCE VALIDATION FAILED"
    echo "Found $VIOLATIONS violation types that need to be fixed"
    echo
    echo "📖 See detailed rules in: common/README.md"
    echo "🛠️  Migration guide available in: common/README.md"
    echo
    exit 1
fi