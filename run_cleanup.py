#!/usr/bin/env python3
"""Execute the directory cleanup script"""

import subprocess
import sys
from pathlib import Path

# Make sure we can import the cleanup script
cleanup_script = Path(__file__).parent / "cleanup_root_directory.py"

if __name__ == "__main__":
    try:
        result = subprocess.run(
            [sys.executable, str(cleanup_script)], capture_output=True, text=True, timeout=300
        )

        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)

        print(f"\nExit code: {result.returncode}")

    except subprocess.TimeoutExpired:
        print("Cleanup script timed out after 5 minutes")
    except Exception as e:
        print(f"Error running cleanup script: {e}")
