#!/usr/bin/env python3
"""
P3 CLI - Root Entry Point
Delegates to the actual P3 implementation in infra/p3/
"""

import sys
from pathlib import Path

# Add the project root to Python path for import
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from infra.p3.p3 import main

    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"❌ Error importing P3 CLI: {e}")
    print("🔧 Please ensure the infra/p3/ module is properly installed")
    sys.exit(1)
