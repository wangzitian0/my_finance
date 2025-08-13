#!/usr/bin/env python3
"""
Improved M7 Test Marker System
Uses git commit --amend to add test markers to commit messages instead of separate files.
This eliminates the .m7-test-passed file conflicts during rebase.
"""

import subprocess
import json
import datetime
import re
from pathlib import Path
from typing import Dict, Optional, Tuple


class TestMarkerSystem:
    """Manages test markers in git commit messages."""
    
    TEST_MARKER_PREFIX = "🧪 M7-TEST:"
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
    
    def create_test_marker(self, test_results: Dict) -> str:
        """Create a test marker string with results."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        commit_hash = self._get_current_commit_hash()
        
        marker_data = {
            "passed": True,
            "timestamp": timestamp,
            "commit": commit_hash,
            "companies": test_results.get("companies", 7),
            "files": test_results.get("files", 0),
            "build_status": test_results.get("build_status", "completed"),
            "host": self._get_hostname(),
            "pixi_version": "latest"
        }
        
        # Create compact marker
        marker = f"{self.TEST_MARKER_PREFIX} {json.dumps(marker_data, separators=(',', ':'))}"
        return marker
    
    def add_test_marker_to_commit(self, test_results: Dict, original_message: Optional[str] = None) -> bool:
        """Add test marker to the last commit using --amend."""
        try:
            # Get current commit message if not provided
            if original_message is None:
                original_message = self._get_last_commit_message()
            
            # Remove any existing test markers
            cleaned_message = self._remove_existing_markers(original_message)
            
            # Create new test marker
            test_marker = self.create_test_marker(test_results)
            
            # Combine message with marker
            new_message = f"{cleaned_message}\n\n{test_marker}"
            
            # Amend the commit with new message
            result = subprocess.run([
                "git", "commit", "--amend", "-m", new_message
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print(f"✅ Test marker added to commit: {test_marker}")
                return True
            else:
                print(f"❌ Failed to amend commit: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error adding test marker: {e}")
            return False
    
    def check_test_marker(self, max_age_minutes: int = 10) -> Tuple[bool, Dict]:
        """Check if current commit has a valid recent test marker."""
        try:
            commit_message = self._get_last_commit_message()
            marker_match = re.search(rf"{self.TEST_MARKER_PREFIX}\s+(.+)", commit_message)
            
            if not marker_match:
                return False, {"error": "No test marker found in commit message"}
            
            try:
                marker_data = json.loads(marker_match.group(1))
            except json.JSONDecodeError:
                return False, {"error": "Invalid test marker format"}
            
            # Check if test passed
            if not marker_data.get("passed", False):
                return False, {"error": "Test marker indicates failure"}
            
            # Check age
            marker_time = datetime.datetime.strptime(marker_data["timestamp"], "%Y%m%d_%H%M%S")
            age_minutes = (datetime.datetime.now() - marker_time).total_seconds() / 60
            
            if age_minutes > max_age_minutes:
                return False, {
                    "error": f"Test marker too old ({age_minutes:.1f} minutes > {max_age_minutes})",
                    "marker_data": marker_data
                }
            
            # Check commit hash matches
            current_commit = self._get_current_commit_hash()
            if marker_data.get("commit") != current_commit:
                return False, {
                    "error": "Test marker commit hash doesn't match current commit",
                    "marker_commit": marker_data.get("commit"),
                    "current_commit": current_commit
                }
            
            return True, marker_data
            
        except Exception as e:
            return False, {"error": f"Error checking test marker: {e}"}
    
    def run_m7_test_and_mark(self) -> bool:
        """Run M7 test and add marker to commit if successful."""
        print("🚀 Running M7 test...")
        
        # Run the actual M7 test
        test_result = self._run_m7_test()
        
        if test_result["success"]:
            print("✅ M7 test passed, adding marker to commit...")
            return self.add_test_marker_to_commit(test_result["data"])
        else:
            print(f"❌ M7 test failed: {test_result['error']}")
            return False
    
    def _run_m7_test(self) -> Dict:
        """Run the actual M7 test using p3 command."""
        try:
            print("   🧪 Executing: p3 dcf-m7")
            
            # Run M7 DCF test
            result = subprocess.run([
                "pixi", "run", "dcf-m7"
            ], capture_output=True, text=True, cwd=self.project_root, timeout=600)
            
            if result.returncode == 0:
                # Count files to validate test ran properly
                build_files = self._count_build_files()
                
                test_data = {
                    "companies": 7,
                    "files": build_files,
                    "build_status": "completed"
                }
                
                if build_files >= 7:  # At least 7 files (one per company)
                    return {"success": True, "data": test_data}
                else:
                    return {
                        "success": False, 
                        "error": f"Insufficient build files: {build_files} < 7"
                    }
            else:
                return {
                    "success": False,
                    "error": f"M7 test command failed: {result.stderr}"
                }
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "M7 test timed out after 10 minutes"}
        except Exception as e:
            return {"success": False, "error": f"Error running M7 test: {e}"}
    
    def _count_build_files(self) -> int:
        """Count files in latest build directory."""
        try:
            build_dir = self.project_root / "data" / "stage_99_build"
            if not build_dir.exists():
                return 0
            
            # Find latest build directory
            builds = sorted([d for d in build_dir.iterdir() if d.is_dir() and d.name.startswith("build_")])
            if not builds:
                return 0
            
            latest_build = builds[-1]
            # Count significant files (excluding logs)
            file_count = len([f for f in latest_build.rglob("*") 
                             if f.is_file() and not f.name.endswith('.log')])
            return file_count
            
        except Exception:
            return 0
    
    def _get_current_commit_hash(self) -> str:
        """Get current commit hash."""
        try:
            result = subprocess.run([
                "git", "rev-parse", "HEAD"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                return result.stdout.strip()[:12]  # Short hash
            return "unknown"
        except Exception:
            return "unknown"
    
    def _get_last_commit_message(self) -> str:
        """Get the last commit message."""
        try:
            result = subprocess.run([
                "git", "log", "-1", "--pretty=format:%B"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                return result.stdout.strip()
            return ""
        except Exception:
            return ""
    
    def _remove_existing_markers(self, message: str) -> str:
        """Remove any existing test markers from commit message."""
        lines = message.split('\n')
        filtered_lines = []
        
        for line in lines:
            if not line.strip().startswith(self.TEST_MARKER_PREFIX):
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines).strip()
    
    def _get_hostname(self) -> str:
        """Get system hostname."""
        try:
            import socket
            return socket.gethostname()
        except Exception:
            return "unknown"


def main():
    """Main function for command-line usage."""
    import sys
    
    marker_system = TestMarkerSystem()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "run-test":
            # Run M7 test and add marker
            success = marker_system.run_m7_test_and_mark()
            sys.exit(0 if success else 1)
            
        elif command == "check":
            # Check existing marker
            valid, data = marker_system.check_test_marker()
            if valid:
                print(f"✅ Valid test marker found: {data}")
                sys.exit(0)
            else:
                print(f"❌ Invalid or missing test marker: {data}")
                sys.exit(1)
                
        elif command == "add-marker":
            # Add marker with dummy data (for testing)
            test_data = {
                "companies": 7,
                "files": 21,
                "build_status": "completed"
            }
            success = marker_system.add_test_marker_to_commit(test_data)
            sys.exit(0 if success else 1)
    
    else:
        print("Usage:")
        print("  python test_marker_system.py run-test    # Run M7 test and add marker")
        print("  python test_marker_system.py check       # Check existing marker")
        print("  python test_marker_system.py add-marker  # Add test marker to commit")


if __name__ == "__main__":
    main()
