#!/usr/bin/env python3
"""
P3 System Comprehensive Audit and Correction Script
Ensures consistency with the new 8-command P3 system
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class P3Reference:
    """Represents a P3 command reference found in code."""
    file_path: str
    line_number: int
    line_content: str
    command: str
    context: str
    needs_update: bool = False
    suggested_fix: str = ""


class P3SystemAuditor:
    """Comprehensive P3 system auditor and corrector."""
    
    # New 8-command P3 system
    VALID_P3_COMMANDS = {
        "ready": "Start working (env + services)",
        "check": "Validate code (format + lint + test)", 
        "test": "Comprehensive testing",
        "ship": "Create PR",
        "debug": "Diagnose issues", 
        "reset": "Fix environment",
        "build": "Build dataset",
        "version": "Version management"
    }
    
    # Old commands that should be replaced
    DEPRECATED_COMMANDS = {
        # Old command mappings to new commands
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
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.findings: List[P3Reference] = []
        self.corrections_made = 0
        
    def audit_all_files(self) -> Dict[str, List[P3Reference]]:
        """Audit all files for P3 references."""
        print("🔍 Starting comprehensive P3 system audit...")
        
        # File patterns to search
        patterns = ["*.py", "*.md", "*.sh", "*.yml", "*.yaml", "*.toml", "*.txt"]
        
        all_findings = {}
        
        for pattern in patterns:
            findings = self._search_files_pattern(pattern)
            if findings:
                all_findings[pattern] = findings
                
        return all_findings
    
    def _search_files_pattern(self, pattern: str) -> List[P3Reference]:
        """Search files matching pattern for P3 references."""
        findings = []
        
        # Use glob to find files
        for file_path in self.project_root.glob(f"**/{pattern}"):
            if self._should_skip_file(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        p3_refs = self._extract_p3_references(
                            str(file_path), line_num, line
                        )
                        findings.extend(p3_refs)
            except (UnicodeDecodeError, PermissionError):
                print(f"⚠️  Skipping {file_path} (encoding/permission issue)")
                continue
                
        return findings
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped in audit."""
        skip_patterns = [
            "/.git/",
            "/build_data/", 
            "/__pycache__/",
            "/.pytest_cache/",
            "/node_modules/",
            "/.pixi/",
            "/logs/"
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)
    
    def _extract_p3_references(
        self, file_path: str, line_num: int, line: str
    ) -> List[P3Reference]:
        """Extract P3 command references from a line."""
        references = []
        
        # Pattern to match p3 commands
        patterns = [
            r'p3\s+([a-zA-Z0-9_-]+)',  # p3 command
            r'`p3\s+([a-zA-Z0-9_-]+)',  # `p3 command` in markdown
            r'"p3\s+([a-zA-Z0-9_-]+)',  # "p3 command" in strings
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, line)
            for match in matches:
                command = match.group(1)
                ref = P3Reference(
                    file_path=file_path,
                    line_number=line_num,
                    line_content=line.strip(),
                    command=command,
                    context=self._get_context_type(file_path)
                )
                
                # Check if command needs updating
                if command in self.DEPRECATED_COMMANDS:
                    ref.needs_update = True
                    ref.suggested_fix = self.DEPRECATED_COMMANDS[command]
                elif command not in self.VALID_P3_COMMANDS:
                    ref.needs_update = True
                    ref.suggested_fix = "UNKNOWN - may need manual review"
                    
                references.append(ref)
        
        return references
    
    def _get_context_type(self, file_path: str) -> str:
        """Determine the context type of the file."""
        if file_path.endswith('.md'):
            return "documentation"
        elif file_path.endswith('.py'):
            return "code"
        elif file_path.endswith(('.sh', '.bash')):
            return "script"
        elif file_path.endswith(('.yml', '.yaml', '.toml')):
            return "config"
        else:
            return "other"
    
    def generate_audit_report(self) -> str:
        """Generate comprehensive audit report."""
        all_findings = self.audit_all_files()
        
        report = []
        report.append("=" * 80)
        report.append("🚀 P3 SYSTEM COMPREHENSIVE AUDIT REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        total_refs = sum(len(refs) for refs in all_findings.values())
        needs_update = sum(
            len([r for r in refs if r.needs_update]) 
            for refs in all_findings.values()
        )
        
        report.append("📊 SUMMARY")
        report.append(f"• Total P3 references found: {total_refs}")
        report.append(f"• References needing updates: {needs_update}")
        report.append(f"• Valid 8-command system references: {total_refs - needs_update}")
        report.append("")
        
        # Valid commands
        report.append("✅ VALID P3 COMMANDS (Current 8-Command System)")
        for cmd, desc in self.VALID_P3_COMMANDS.items():
            report.append(f"• p3 {cmd} - {desc}")
        report.append("")
        
        # Findings by file type
        for pattern, findings in all_findings.items():
            if not findings:
                continue
                
            report.append(f"📄 {pattern.upper()} FILES")
            report.append("-" * 40)
            
            for finding in findings:
                status = "❌ NEEDS UPDATE" if finding.needs_update else "✅ OK"
                report.append(f"{status} {finding.file_path}:{finding.line_number}")
                report.append(f"   Command: p3 {finding.command}")
                report.append(f"   Context: {finding.context}")
                if finding.needs_update:
                    report.append(f"   Fix: p3 {finding.suggested_fix}")
                report.append(f"   Line: {finding.line_content}")
                report.append("")
        
        return "\n".join(report)
    
    def apply_corrections(self) -> int:
        """Apply automatic corrections where possible."""
        print("🔧 Applying P3 command corrections...")
        
        all_findings = self.audit_all_files()
        corrections = 0
        
        for findings in all_findings.values():
            for finding in findings:
                if finding.needs_update and finding.suggested_fix != "UNKNOWN - may need manual review":
                    if self._apply_single_correction(finding):
                        corrections += 1
        
        print(f"✅ Applied {corrections} automatic corrections")
        return corrections
    
    def _apply_single_correction(self, finding: P3Reference) -> bool:
        """Apply a single correction to a file."""
        try:
            # Read the file
            with open(finding.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Update the specific line
            line_idx = finding.line_number - 1
            if line_idx < len(lines):
                old_line = lines[line_idx]
                # Replace the command
                new_line = re.sub(
                    rf'p3\s+{re.escape(finding.command)}',
                    f'p3 {finding.suggested_fix}',
                    old_line
                )
                lines[line_idx] = new_line
                
                # Write back
                with open(finding.file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                print(f"✅ Fixed {finding.file_path}:{finding.line_number}")
                print(f"   p3 {finding.command} → p3 {finding.suggested_fix}")
                return True
                
        except Exception as e:
            print(f"❌ Failed to fix {finding.file_path}: {e}")
            
        return False
    
    def validate_design_goals(self) -> Dict[str, bool]:
        """Validate that design goals are met."""
        print("🎯 Validating P3 system design goals...")
        
        goals = {}
        
        # Goal 1: Command reduction (8 commands only)
        all_findings = self.audit_all_files()
        used_commands = set()
        for findings in all_findings.values():
            for finding in findings:
                if finding.command in self.VALID_P3_COMMANDS:
                    used_commands.add(finding.command)
        
        goals["command_reduction"] = len(used_commands) <= 8
        
        # Goal 2: Code simplification (check p3.py size)
        p3_file = self.project_root / "p3.py"
        if p3_file.exists():
            with open(p3_file, 'r') as f:
                lines = len(f.readlines())
            goals["code_simplification"] = lines <= 200  # Target: ~153 lines
        else:
            goals["code_simplification"] = False
        
        # Goal 3: No deprecated commands in use
        deprecated_found = False
        for findings in all_findings.values():
            for finding in findings:
                if finding.command in self.DEPRECATED_COMMANDS:
                    deprecated_found = True
                    break
        goals["no_deprecated_commands"] = not deprecated_found
        
        # Goal 4: English-only (check for common non-English patterns)
        goals["english_only"] = self._validate_english_only()
        
        return goals
    
    def _validate_english_only(self) -> bool:
        """Validate English-only standard."""
        # Check for common non-English patterns in key files
        non_english_patterns = [
            r'[\u4e00-\u9fff]+',  # Chinese characters
            r'[а-яё]+',  # Cyrillic
            r'[α-ωάέήίόύώ]+',  # Greek
        ]
        
        for file_path in self.project_root.glob("**/*.py"):
            if self._should_skip_file(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in non_english_patterns:
                        if re.search(pattern, content):
                            print(f"⚠️  Non-English content found in {file_path}")
                            return False
            except (UnicodeDecodeError, PermissionError):
                continue
                
        return True


def main():
    """Main execution function."""
    project_root = Path(__file__).parent.parent
    auditor = P3SystemAuditor(project_root)
    
    print("🚀 P3 SYSTEM COMPREHENSIVE AUDIT AND CORRECTION")
    print("=" * 60)
    
    # Generate audit report
    report = auditor.generate_audit_report()
    
    # Save report
    report_file = project_root / "build_data" / "logs" / "p3_audit_report.txt"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"📊 Audit report saved to: {report_file}")
    print()
    
    # Print summary
    print(report.split("📄")[0])  # Print only summary section
    
    # Apply corrections
    corrections = auditor.apply_corrections()
    print()
    
    # Validate design goals
    goals = auditor.validate_design_goals()
    print("🎯 DESIGN GOAL VALIDATION")
    print("-" * 30)
    for goal, passed in goals.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} {goal.replace('_', ' ').title()}")
    
    print()
    print("🎉 P3 SYSTEM AUDIT COMPLETE")
    print(f"📊 Report: {report_file}")
    print(f"🔧 Corrections Applied: {corrections}")
    
    return 0 if all(goals.values()) else 1


if __name__ == "__main__":
    exit(main())