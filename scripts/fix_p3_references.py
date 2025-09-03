#!/usr/bin/env python3
"""
P3 References Fix Script
Systematically fixes all outdated P3 command references in the codebase
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple


class P3ReferencesFixer:
    """Fixes outdated P3 command references throughout the codebase."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.fixes_applied = 0
        
        # Command mapping: old -> new
        self.command_mapping = {
            "env-status": "debug",
            "e2e": "test", 
            "create-pr": "ship",
            "format": "check",
            "lint": "check",
            "pytest": "check",
            "validate": "test",
            "setup": "ready",
            "fix-env": "reset",
            "build-dataset": "build",
            "version-info": "version",
            "version-increment": "version"
        }
        
        # Files to fix (order matters for dependencies)
        self.target_files = [
            "README.md",
            "CLAUDE.md", 
            "pixi.toml",
            "p3.py",
            "common/README.md"
        ]
    
    def fix_all_references(self) -> int:
        """Fix all P3 references in target files."""
        print("🔧 FIXING P3 COMMAND REFERENCES")
        print("=" * 40)
        
        for file_name in self.target_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                fixes = self._fix_file_references(file_path)
                if fixes > 0:
                    print(f"✅ Fixed {fixes} references in {file_name}")
                else:
                    print(f"✅ No fixes needed in {file_name}")
            else:
                print(f"⚠️  File not found: {file_name}")
        
        print(f"\n🎉 Total fixes applied: {self.fixes_applied}")
        return self.fixes_applied
    
    def _fix_file_references(self, file_path: Path) -> int:
        """Fix P3 references in a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            fixes_in_file = 0
            
            # Apply each command mapping
            for old_cmd, new_cmd in self.command_mapping.items():
                # Pattern to match p3 commands with various quote styles
                patterns = [
                    rf'`p3\s+{re.escape(old_cmd)}([`\s])',  # `p3 old-cmd` or `p3 old-cmd `
                    rf'"p3\s+{re.escape(old_cmd)}"',       # "p3 old-cmd"
                    rf'p3\s+{re.escape(old_cmd)}(\s|$)',   # p3 old-cmd followed by space or end
                ]
                
                for pattern in patterns:
                    matches = list(re.finditer(pattern, content))
                    if matches:
                        for match in matches:
                            if pattern.startswith('`'):
                                # Markdown code style
                                replacement = f'`p3 {new_cmd}{match.group(1)}'
                            elif pattern.startswith('"'):
                                # Quoted style
                                replacement = f'"p3 {new_cmd}"'
                            else:
                                # Plain style
                                replacement = f'p3 {new_cmd}{match.group(1)}'
                            
                            content = content[:match.start()] + replacement + content[match.end():]
                            fixes_in_file += 1
            
            # Write back only if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes_applied += fixes_in_file
            
            return fixes_in_file
            
        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")
            return 0
    
    def validate_fixes(self) -> List[str]:
        """Validate that no deprecated commands remain."""
        remaining_issues = []
        
        for file_name in self.target_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for any remaining deprecated commands
                for old_cmd in self.command_mapping.keys():
                    if re.search(rf'p3\s+{re.escape(old_cmd)}\b', content):
                        remaining_issues.append(f"{file_name}: p3 {old_cmd}")
        
        return remaining_issues


def main():
    """Main execution function."""
    project_root = Path(__file__).parent.parent
    fixer = P3ReferencesFixer(project_root)
    
    print("🚀 P3 REFERENCES SYSTEMATIC FIX")
    print("=" * 50)
    
    # Apply fixes
    total_fixes = fixer.fix_all_references()
    
    print("\n🔍 VALIDATION")
    print("-" * 20)
    
    # Validate fixes
    remaining_issues = fixer.validate_fixes()
    
    if remaining_issues:
        print("❌ Some deprecated references still remain:")
        for issue in remaining_issues:
            print(f"   • {issue}")
        return 1
    else:
        print("✅ All deprecated P3 references have been fixed!")
        return 0


if __name__ == "__main__":
    exit(main())