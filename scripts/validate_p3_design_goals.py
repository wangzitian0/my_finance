#!/usr/bin/env python3
"""
P3 System Design Goals Validation Script
Validates that all design goals are achieved after the P3 system audit
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple


class P3DesignGoalsValidator:
    """Validates P3 system design goals completion."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.valid_commands = {
            "ready", "check", "test", "ship", 
            "debug", "reset", "build", "version"
        }
        self.deprecated_commands = {
            "env-status", "e2e", "create-pr", "format", "lint", 
            "pytest", "validate", "setup", "fix-env", "build-dataset",
            "version-info", "version-increment"
        }
    
    def validate_all_goals(self) -> Dict[str, Dict]:
        """Validate all design goals and return detailed results."""
        results = {}
        
        print("🎯 VALIDATING P3 SYSTEM DESIGN GOALS")
        print("=" * 50)
        
        # Goal 1: Command Reduction (49+ → 8 commands)
        results["command_reduction"] = self._validate_command_reduction()
        
        # Goal 2: Code Simplification (600+ → ~153 lines)
        results["code_simplification"] = self._validate_code_simplification()
        
        # Goal 3: Workflow-Oriented Commands
        results["workflow_oriented"] = self._validate_workflow_orientation()
        
        # Goal 4: Worktree Isolation
        results["worktree_isolation"] = self._validate_worktree_isolation()
        
        # Goal 5: English-Only Standard
        results["english_only"] = self._validate_english_only()
        
        # Goal 6: Documentation Consistency
        results["documentation_consistency"] = self._validate_documentation_consistency()
        
        return results
    
    def _validate_command_reduction(self) -> Dict:
        """Validate command reduction from 49+ to 8 commands."""
        print("\n📊 Goal 1: Command Reduction (49+ → 8 commands)")
        
        p3_file = self.project_root / "p3.py"
        if not p3_file.exists():
            return {"passed": False, "reason": "p3.py not found"}
        
        # Check p3.py for command definitions
        with open(p3_file, 'r') as f:
            content = f.read()
        
        # Extract commands from the commands dictionary
        commands_match = re.search(r'self\.commands = \{([^}]+)\}', content, re.DOTALL)
        if not commands_match:
            return {"passed": False, "reason": "Commands dictionary not found"}
        
        commands_block = commands_match.group(1)
        defined_commands = re.findall(r'"([^"]+)":', commands_block)
        
        passed = len(defined_commands) == 8 and set(defined_commands) == self.valid_commands
        
        print(f"   Commands defined: {len(defined_commands)}")
        print(f"   Expected: 8")
        print(f"   Commands: {', '.join(sorted(defined_commands))}")
        print(f"   Status: {'✅ PASSED' if passed else '❌ FAILED'}")
        
        return {
            "passed": passed,
            "commands_count": len(defined_commands),
            "commands": defined_commands,
            "expected": 8
        }
    
    def _validate_code_simplification(self) -> Dict:
        """Validate code simplification (600+ lines → ~153 lines)."""
        print("\n💻 Goal 2: Code Simplification (600+ → ~153 lines)")
        
        p3_file = self.project_root / "p3.py"
        if not p3_file.exists():
            return {"passed": False, "reason": "p3.py not found"}
        
        with open(p3_file, 'r') as f:
            lines = len(f.readlines())
        
        # Target is around 153 lines, allow some flexibility (up to 200)
        passed = lines <= 200
        
        print(f"   Current lines: {lines}")
        print(f"   Target: ≤200 lines (ideal ~153)")
        print(f"   Status: {'✅ PASSED' if passed else '❌ FAILED'}")
        
        return {
            "passed": passed,
            "current_lines": lines,
            "target_lines": 200,
            "ideal_lines": 153
        }
    
    def _validate_workflow_orientation(self) -> Dict:
        """Validate workflow-oriented design."""
        print("\n🚀 Goal 3: Workflow-Oriented Commands")
        
        # Check help text for workflow descriptions
        p3_file = self.project_root / "p3.py"
        if not p3_file.exists():
            return {"passed": False, "reason": "p3.py not found"}
        
        with open(p3_file, 'r') as f:
            content = f.read()
        
        # Check for workflow sections in help
        workflow_sections = [
            "DAILY WORKFLOW",
            "TROUBLESHOOTING", 
            "DATA & VERSION"
        ]
        
        sections_found = sum(1 for section in workflow_sections if section in content)
        passed = sections_found == len(workflow_sections)
        
        print(f"   Workflow sections found: {sections_found}/3")
        print(f"   Sections: {', '.join(workflow_sections)}")
        print(f"   Status: {'✅ PASSED' if passed else '❌ FAILED'}")
        
        return {
            "passed": passed,
            "sections_found": sections_found,
            "expected_sections": len(workflow_sections)
        }
    
    def _validate_worktree_isolation(self) -> Dict:
        """Validate worktree isolation functionality."""
        print("\n🔄 Goal 4: Worktree Isolation")
        
        # Check for worktree isolation import in p3.py
        p3_file = self.project_root / "p3.py"
        if not p3_file.exists():
            return {"passed": False, "reason": "p3.py not found"}
        
        with open(p3_file, 'r') as f:
            content = f.read()
        
        isolation_features = [
            "WorktreeIsolationManager",
            "auto_switch_python",
            "worktree" in content.lower()
        ]
        
        features_found = sum(1 for feature in isolation_features if 
                           (isinstance(feature, str) and feature in content) or
                           (isinstance(feature, bool) and feature))
        
        passed = features_found >= 2  # At least 2 of 3 features
        
        print(f"   Isolation features found: {features_found}/3")
        print(f"   Status: {'✅ PASSED' if passed else '❌ FAILED'}")
        
        return {
            "passed": passed,
            "features_found": features_found,
            "expected_features": 3
        }
    
    def _validate_english_only(self) -> Dict:
        """Validate English-only standard compliance."""
        print("\n🌐 Goal 5: English-Only Standard")
        
        # Check key files for non-English content
        non_english_patterns = [
            r'[\u4e00-\u9fff]+',  # Chinese characters
            r'[а-яё]+',  # Cyrillic  
            r'[α-ωάέήίόύώ]+'  # Greek
        ]
        
        violations = []
        key_files = [
            self.project_root / "p3.py",
            self.project_root / "README.md", 
            self.project_root / "CLAUDE.md"
        ]
        
        for file_path in key_files:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in non_english_patterns:
                        if re.search(pattern, content):
                            violations.append(str(file_path))
                            break
        
        passed = len(violations) == 0
        
        print(f"   Files checked: {len(key_files)}")
        print(f"   Violations found: {len(violations)}")
        if violations:
            print(f"   Files with non-English content: {', '.join(violations)}")
        print(f"   Status: {'✅ PASSED' if passed else '❌ FAILED'}")
        
        return {
            "passed": passed,
            "violations": violations,
            "files_checked": len(key_files)
        }
    
    def _validate_documentation_consistency(self) -> Dict:
        """Validate documentation consistency across files."""
        print("\n📚 Goal 6: Documentation Consistency")
        
        # Check that deprecated commands are not referenced in docs
        doc_files = [
            self.project_root / "README.md",
            self.project_root / "CLAUDE.md"
        ]
        
        deprecated_found = []
        total_checked = 0
        
        for file_path in doc_files:
            if file_path.exists():
                total_checked += 1
                with open(file_path, 'r') as f:
                    content = f.read()
                    for cmd in self.deprecated_commands:
                        if f"p3 {cmd}" in content:
                            deprecated_found.append(f"{file_path.name}: p3 {cmd}")
        
        passed = len(deprecated_found) == 0
        
        print(f"   Documentation files checked: {total_checked}")
        print(f"   Deprecated command references: {len(deprecated_found)}")
        if deprecated_found:
            for ref in deprecated_found:
                print(f"     • {ref}")
        print(f"   Status: {'✅ PASSED' if passed else '❌ FAILED'}")
        
        return {
            "passed": passed,
            "deprecated_references": deprecated_found,
            "files_checked": total_checked
        }
    
    def generate_validation_report(self) -> str:
        """Generate comprehensive validation report."""
        results = self.validate_all_goals()
        
        report = []
        report.append("=" * 80)
        report.append("🎯 P3 SYSTEM DESIGN GOALS VALIDATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Overall summary
        total_goals = len(results)
        passed_goals = sum(1 for result in results.values() if result["passed"])
        
        report.append("📊 OVERALL SUMMARY")
        report.append(f"• Total design goals: {total_goals}")
        report.append(f"• Goals achieved: {passed_goals}")
        report.append(f"• Success rate: {passed_goals/total_goals*100:.1f}%")
        report.append("")
        
        # Detailed results
        for goal, result in results.items():
            status = "✅ ACHIEVED" if result["passed"] else "❌ FAILED"
            report.append(f"{status} {goal.replace('_', ' ').title()}")
            
            # Add specific details for failed goals
            if not result["passed"] and "reason" in result:
                report.append(f"   Reason: {result['reason']}")
        
        report.append("")
        report.append("🚀 NEXT STEPS")
        if passed_goals == total_goals:
            report.append("✅ All design goals achieved! P3 system is ready.")
            report.append("• Run final validation tests")
            report.append("• Create PR with changes")
        else:
            report.append("❌ Some design goals need attention:")
            for goal, result in results.items():
                if not result["passed"]:
                    report.append(f"• Fix {goal.replace('_', ' ')}")
        
        return "\n".join(report)


def main():
    """Main execution function."""
    project_root = Path(__file__).parent.parent
    validator = P3DesignGoalsValidator(project_root)
    
    # Generate and display validation report
    report = validator.generate_validation_report()
    print(report)
    
    # Save report
    report_file = project_root / "build_data" / "logs" / "p3_design_goals_validation.txt"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n📊 Validation report saved to: {report_file}")
    
    # Return exit code based on success
    results = validator.validate_all_goals()
    all_passed = all(result["passed"] for result in results.values())
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())