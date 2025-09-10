#!/usr/bin/env python3
"""
I/O Compliance Validation - Python wrapper for the shell script
Provides easy access to I/O compliance validation
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Run I/O compliance validation"""
    script_path = Path(__file__).parent / "validate_io_compliance.sh"
    
    if not script_path.exists():
        print("❌ I/O compliance validation script not found")
        sys.exit(1)
    
    try:
        result = subprocess.run(["bash", str(script_path)], check=False)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"❌ Failed to run I/O compliance validation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()