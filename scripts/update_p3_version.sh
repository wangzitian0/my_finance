#!/bin/bash
# P3 Version Auto-Update Script
# 
# This script should be run after git pull to automatically update P3 version
# and can be integrated into git hooks for seamless version management.

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🔄 P3 Version Auto-Update"
echo "========================"

# Check if p3_version.py exists
if [ ! -f "p3_version.py" ]; then
    echo "❌ p3_version.py not found. Please ensure P3 version management is installed."
    exit 1
fi

# Show current version first
echo "📋 Current version:"
python3 p3_version.py info
echo ""

# Check if update is needed
echo "🔍 Checking for updates..."
if python3 p3_version.py check-updates | grep -q "Version update recommended"; then
    echo ""
    echo "⚠️  Version update recommended. Updating now..."
    
    # Update version based on git changes
    if python3 p3_version.py update-on-pull; then
        echo "✅ P3 version updated successfully"
        echo ""
        echo "📋 New version information:"
        python3 p3_version.py info
    else
        echo "ℹ️  No version update applied (no git hash changes detected)"
    fi
else
    echo "✅ Version is up to date"
fi

echo ""
echo "💡 Manual version management:"
echo "   p3 version                     - Show version info"
echo "   p3 version-check              - Check if update needed"  
echo "   p3 version-increment [level]  - Increment version manually"
echo "   p3 version-history            - Show version history"
echo "   p3 install-version-hooks      - Install git hooks for auto-updates"