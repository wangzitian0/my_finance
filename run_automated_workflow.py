#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Execute Fully Automated Workflow for Issue #214

This script executes the enhanced agent-coordinator with full automation:
1. Rebase feature/check-CC-hooks-214 onto main (handle conflicts automatically)
2. Validate GitHub issue #214 completion status
3. Run p3 e2e m7 tests and report results

All sub-tasks execute automatically without requiring manual intervention.
"""

import sys
from pathlib import Path

# Add the current directory to Python path to import common module
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from common import execute_automated_workflow, get_agent_coordinator

    def main():
        print("=" * 60)
        print("🚀 STARTING FULLY AUTOMATED WORKFLOW - ISSUE #214")
        print("=" * 60)
        print()

        # Set working directory to current directory
        working_dir = str(current_dir)
        print(f"Working Directory: {working_dir}")
        print()

        # Execute the full automated workflow
        print("🤖 Initializing Agent Coordinator with Enhanced Automation...")
        coordinator = get_agent_coordinator(working_dir)

        print("📋 Executing Workflow Tasks:")
        print("  1. Git rebase feature/check-CC-hooks-214 onto main")
        print("  2. Validate GitHub issue #214 completion status")
        print("  3. Run p3 e2e m7 tests and report results")
        print()

        # Run the automated workflow
        result = execute_automated_workflow()

        print("=" * 60)
        print("📊 WORKFLOW EXECUTION SUMMARY")
        print("=" * 60)
        print(f"✅ Overall Success: {result['workflow_success']}")
        print(f"⏱️ Total Execution Time: {result['execution_time']:.2f} seconds")
        print(f"📈 Tasks Completed: {result['tasks_successful']}/{result['tasks_executed']}")
        print()

        if result["failed_tasks"]:
            print("❌ FAILED TASKS:")
            for task_num, description, error in result["failed_tasks"]:
                print(f"  Task {task_num}: {description}")
                print(f"    Error: {error}")
            print()

        # Detailed task results
        print("📋 DETAILED TASK RESULTS:")
        for task_name, task_result in result["detailed_results"].items():
            status = "✅ SUCCESS" if task_result.success else "❌ FAILED"
            print(f"  {task_name.replace('_', ' ').title()}: {status}")
            print(f"    Execution Time: {task_result.execution_time:.2f}s")
            print(f"    Retry Count: {task_result.retry_count}")

            if task_result.output:
                # Truncate long outputs
                output = str(task_result.output)
                if len(output) > 200:
                    output = output[:200] + "... (truncated)"
                print(f"    Output: {output}")

            if task_result.error:
                print(f"    Error: {task_result.error}")
            print()

        print("=" * 60)
        if result["workflow_success"]:
            print("🎉 AUTOMATED WORKFLOW COMPLETED SUCCESSFULLY!")
        else:
            print("⚠️ WORKFLOW COMPLETED WITH SOME FAILURES")
        print("=" * 60)

        return 0 if result["workflow_success"] else 1

except ImportError as e:
    print(f"❌ Error importing agent coordinator: {e}")
    print("Make sure you're running this from the project root directory")
    return 1
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback

    traceback.print_exc()
    return 1

if __name__ == "__main__":
    sys.exit(main())
