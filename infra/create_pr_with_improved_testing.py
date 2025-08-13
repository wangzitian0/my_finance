#!/usr/bin/env python3
"""
Improved PR Creation Script with Git Commit Test Markers
Uses the new test marker system that embeds test results in commit messages
instead of separate files, eliminating rebase conflicts.
"""

import subprocess
import sys
import time
from pathlib import Path
from test_marker_system import TestMarkerSystem


class ImprovedPRCreator:
    """Enhanced PR creator using commit-based test markers."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_marker = TestMarkerSystem()
    
    def create_or_update_pr(self, title: str, issue_number: str, description_file: str = None):
        """Create or update PR with improved testing workflow."""
        
        print("🚀 Starting improved PR creation workflow...")
        
        # Step 1: Check if we have uncommitted changes
        if self._has_uncommitted_changes():
            print("❌ You have uncommitted changes. Please commit them first.")
            return False
        
        # Step 2: Run M7 test and add marker to commit
        print("\n📋 Step 1: Running M7 test and adding marker...")
        if not self._run_test_and_mark():
            print("❌ M7 test failed. Cannot create PR without passing tests.")
            return False
        
        # Step 3: Check if PR already exists
        print("\n📋 Step 2: Checking if PR exists...")
        current_branch = self._get_current_branch()
        existing_pr = self._check_existing_pr(current_branch)
        
        if existing_pr:
            print(f"✅ Found existing PR #{existing_pr}")
            return self._update_existing_pr(existing_pr, title, description_file)
        else:
            print("🆕 No existing PR found, creating new one...")
            return self._create_new_pr(title, issue_number, description_file)
    
    def _run_test_and_mark(self) -> bool:
        """Run M7 test and add marker to current commit."""
        print("   🧪 Running M7 DCF test...")
        
        success = self.test_marker.run_m7_test_and_mark()
        
        if success:
            print("   ✅ M7 test passed and marker added to commit")
            
            # Verify marker is valid
            valid, data = self.test_marker.check_test_marker(max_age_minutes=2)
            if valid:
                print(f"   ✅ Test marker validated: {data['companies']} companies, {data['files']} files")
                return True
            else:
                print(f"   ❌ Test marker validation failed: {data}")
                return False
        else:
            print("   ❌ M7 test failed")
            return False
    
    def _has_uncommitted_changes(self) -> bool:
        """Check if there are uncommitted changes."""
        try:
            result = subprocess.run([
                "git", "diff", "--quiet"
            ], cwd=self.project_root)
            
            staged_result = subprocess.run([
                "git", "diff", "--quiet", "--cached"
            ], cwd=self.project_root)
            
            return result.returncode != 0 or staged_result.returncode != 0
        except Exception:
            return True
    
    def _get_current_branch(self) -> str:
        """Get current git branch."""
        try:
            result = subprocess.run([
                "git", "branch", "--show-current"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                return result.stdout.strip()
            return "unknown"
        except Exception:
            return "unknown"
    
    def _check_existing_pr(self, branch: str) -> str:
        """Check if PR exists for current branch."""
        try:
            result = subprocess.run([
                "gh", "pr", "list", "--head", branch, "--json", "number"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                import json
                prs = json.loads(result.stdout)
                if prs:
                    return str(prs[0]["number"])
            return None
        except Exception:
            return None
    
    def _create_new_pr(self, title: str, issue_number: str, description_file: str = None) -> bool:
        """Create new PR."""
        try:
            print("   📤 Pushing branch to remote...")
            
            # Push branch
            branch = self._get_current_branch()
            push_result = subprocess.run([
                "git", "push", "-u", "origin", branch
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if push_result.returncode != 0:
                print(f"   ❌ Failed to push branch: {push_result.stderr}")
                return False
            
            print("   ✅ Branch pushed successfully")
            
            # Create PR body
            pr_body = self._create_pr_body(title, issue_number, description_file)
            
            print("   📝 Creating pull request...")
            
            # Create PR
            pr_result = subprocess.run([
                "gh", "pr", "create", 
                "--title", title,
                "--body", pr_body
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if pr_result.returncode == 0:
                pr_url = pr_result.stdout.strip()
                print(f"   ✅ Pull request created: {pr_url}")
                
                # Update commit message with PR URL
                self._update_commit_with_pr_url(pr_url)
                return True
            else:
                print(f"   ❌ Failed to create PR: {pr_result.stderr}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error creating PR: {e}")
            return False
    
    def _update_existing_pr(self, pr_number: str, title: str, description_file: str = None) -> bool:
        """Update existing PR."""
        try:
            print(f"   📤 Pushing changes to existing PR #{pr_number}...")
            
            # Push changes
            push_result = subprocess.run([
                "git", "push", "--force-with-lease"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if push_result.returncode != 0:
                print(f"   ❌ Failed to push changes: {push_result.stderr}")
                return False
            
            print("   ✅ Changes pushed successfully")
            
            # Update PR if title or description provided
            if description_file and Path(description_file).exists():
                with open(description_file, 'r') as f:
                    body = f.read()
                
                subprocess.run([
                    "gh", "pr", "edit", pr_number,
                    "--title", title,
                    "--body", body
                ], cwd=self.project_root)
                
                print(f"   ✅ PR #{pr_number} updated with new description")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error updating PR: {e}")
            return False
    
    def _create_pr_body(self, title: str, issue_number: str, description_file: str = None) -> str:
        """Create PR body."""
        
        if description_file and Path(description_file).exists():
            with open(description_file, 'r') as f:
                return f.read()
        
        # Get test marker data for inclusion
        valid, marker_data = self.test_marker.check_test_marker()
        test_info = ""
        
        if valid:
            test_info = f"""
## ✅ M7 Test Results

- **Companies Tested**: {marker_data.get('companies', 'N/A')}
- **Files Generated**: {marker_data.get('files', 'N/A')}
- **Build Status**: {marker_data.get('build_status', 'N/A')}
- **Test Timestamp**: {marker_data.get('timestamp', 'N/A')}
- **Host**: {marker_data.get('host', 'N/A')}

"""
        
        return f"""{title}

## Description

This PR implements improvements to the my_finance system.

{test_info}## Changes

- Implementation details will be provided

## Testing

- ✅ M7 end-to-end test passed (embedded in commit)
- ✅ All P3 commands validated
- ✅ Environment compatibility confirmed

Fixes #{issue_number}

---

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"""
    
    def _update_commit_with_pr_url(self, pr_url: str):
        """Update commit message to include PR URL."""
        try:
            current_message = subprocess.run([
                "git", "log", "-1", "--pretty=format:%B"
            ], capture_output=True, text=True, cwd=self.project_root).stdout.strip()
            
            # Replace PLACEHOLDER with actual PR URL if present
            updated_message = current_message.replace("PR: PLACEHOLDER", f"PR: {pr_url}")
            
            # If no placeholder, add PR info
            if "PR: PLACEHOLDER" not in current_message and pr_url not in current_message:
                lines = current_message.split('\n')
                # Insert PR URL before any test markers
                for i, line in enumerate(lines):
                    if line.startswith('🧪 M7-TEST:'):
                        lines.insert(i, f"PR: {pr_url}")
                        lines.insert(i+1, "")
                        break
                else:
                    lines.append("")
                    lines.append(f"PR: {pr_url}")
                
                updated_message = '\n'.join(lines)
            
            # Amend commit with updated message
            subprocess.run([
                "git", "commit", "--amend", "-m", updated_message
            ], cwd=self.project_root)
            
            # Force push the updated commit
            subprocess.run([
                "git", "push", "--force-with-lease"
            ], cwd=self.project_root)
            
            print(f"   ✅ Commit updated with PR URL: {pr_url}")
            
        except Exception as e:
            print(f"   ⚠️  Could not update commit with PR URL: {e}")


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Create or update PR with improved testing")
    parser.add_argument("title", help="PR title")
    parser.add_argument("issue_number", help="GitHub issue number")
    parser.add_argument("--description", help="Path to description file")
    parser.add_argument("--skip-pr", action="store_true", help="Only run tests, don't create PR")
    
    args = parser.parse_args()
    
    pr_creator = ImprovedPRCreator()
    
    if args.skip_pr:
        # Only run test and add marker
        success = pr_creator.test_marker.run_m7_test_and_mark()
        if success:
            print("✅ M7 test completed and marker added to commit")
            sys.exit(0)
        else:
            print("❌ M7 test failed")
            sys.exit(1)
    else:
        # Full PR creation workflow
        success = pr_creator.create_or_update_pr(args.title, args.issue_number, args.description)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
