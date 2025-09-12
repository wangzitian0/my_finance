#!/usr/bin/env python3
"""Execute the directory cleanup directly"""

import os
import sys

# Set up the path
sys.path.insert(0, "/Users/SP14016/zitian/my_finance/.git/worktree/feature-256-dir-adjust")

# Import and run the cleanup
try:
    print("Importing cleanup module...")
    from execute_cleanup import main

    print("Starting directory cleanup execution...")
    success = main()

    if success:
        print("\n🎉 Directory cleanup completed successfully!")
    else:
        print("\n⚠️  Directory cleanup completed with warnings")

except ImportError as e:
    print(f"Import error: {e}")
    print("Trying to run with direct path manipulation...")

    # Try to run the script directly
    import subprocess

    script_path = (
        "/Users/SP14016/zitian/my_finance/.git/worktree/feature-256-dir-adjust/execute_cleanup.py"
    )

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            cwd="/Users/SP14016/zitian/my_finance/.git/worktree/feature-256-dir-adjust",
            capture_output=True,
            text=True,
            timeout=300,
        )

        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)

        print(f"\nProcess exit code: {result.returncode}")
        success = result.returncode == 0

    except subprocess.TimeoutExpired:
        print("Cleanup script timed out")
        success = False
    except Exception as e:
        print(f"Error running cleanup script: {e}")
        success = False

except Exception as e:
    print(f"Unexpected error: {e}")
    success = False

# Exit with appropriate code
sys.exit(0 if success else 1)
