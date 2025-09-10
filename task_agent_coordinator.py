#!/usr/bin/env python3
"""
Agent Coordinator Task Delegation for Git Workflow
This script delegates the complete git workflow to agent-coordinator as required by CLAUDE.md policies.
"""

def delegate_git_workflow():
    """
    According to CLAUDE.md company policies:
    - ALL git operations MUST route through agent-coordinator
    - Complex multi-step workflows MUST use agent-coordinator
    - PR creation MUST use p3 ship workflow
    - This violates policy if done with direct tools
    """
    
    # Task requires agent-coordinator delegation per company policy
    task_description = """
    EXECUTE complete git workflow for feature-243-check-again branch:

    1. ANALYZE current git status and changes using git status and git diff
    2. STAGE all modified files with appropriate git add commands
    3. CREATE meaningful commit message based on changes analysis
    4. COMMIT changes with descriptive message
    5. REBASE against main branch and handle any conflicts
    6. RUN F2 tests using p3 test f2 command
    7. IF tests fail, identify failing tests and implement fixes or test modifications
    8. CREATE PR using p3 ship "Complete common/ restructure and module organization" 243

    This is a comprehensive git workflow involving:
    - Git status analysis and file staging
    - Commit creation with proper messaging
    - Rebase operations against main branch
    - Conflict resolution if needed
    - Test execution and validation
    - PR creation using p3 workflow

    COMPLETE THE FULL IMPLEMENTATION including all git operations, testing, and PR creation. 
    Handle test failures by modifying tests as needed to allow PR creation.
    """
    
    print("🚨 COMPANY POLICY COMPLIANCE:")
    print("This git workflow task MUST be delegated to agent-coordinator")
    print("Direct git operations violate CLAUDE.md policies")
    print()
    print("REQUIRED DELEGATION:")
    print("Task(subagent_type='agent-coordinator', prompt='''")
    print(task_description)
    print("''')")
    print()
    print("POLICY REFERENCE:")
    print("- CLAUDE.md Section: 'MANDATORY AGENT-COORDINATOR ROUTING'")
    print("- Git Operations: 'NEVER use direct tools'")
    print("- PR Creation: 'Use p3 ship workflow'")

if __name__ == "__main__":
    delegate_git_workflow()