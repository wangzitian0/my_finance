#!/usr/bin/env python3
"""
Comprehensive P3 System Audit Script
Final validation of all P3 system design goals and consistency
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any


class ComprehensiveP3Auditor:
    """Complete P3 system audit and validation."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.audit_results = {}
        
        # Expected P3 system configuration
        self.expected_commands = {
            "ready": "Start working (env + services)",
            "check": "Validate code (format + lint + test)", 
            "test": "Comprehensive testing",
            "ship": "Create PR",
            "debug": "Diagnose issues", 
            "reset": "Fix environment",
            "build": "Build dataset",
            "version": "Version management"
        }
        
        self.deprecated_commands = {
            "env-status", "e2e", "create-pr", "format", "lint", 
            "pytest", "validate", "setup", "fix-env", "build-dataset",
            "version-info", "version-increment"
        }
    
    def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Run complete audit of P3 system."""
        print("🚀 COMPREHENSIVE P3 SYSTEM AUDIT")
        print("=" * 60)
        
        # Phase 1: Core System Validation
        self.audit_results["core_system"] = self._audit_core_system()
        
        # Phase 2: Documentation Consistency  
        self.audit_results["documentation"] = self._audit_documentation()
        
        # Phase 3: Design Goals Validation
        self.audit_results["design_goals"] = self._audit_design_goals()
        
        # Phase 4: Code Quality Check
        self.audit_results["code_quality"] = self._audit_code_quality()
        
        # Generate summary
        self.audit_results["summary"] = self._generate_summary()
        
        return self.audit_results
    
    def _audit_core_system(self) -> Dict[str, Any]:
        """Audit core P3 system implementation."""
        print("\n📋 Phase 1: Core System Validation")
        print("-" * 40)
        
        results = {}
        
        # Check p3.py exists and has correct structure
        p3_file = self.project_root / "p3.py"
        if not p3_file.exists():
            results["p3_file"] = {"status": "FAILED", "reason": "p3.py not found"}
            return results
        
        with open(p3_file, 'r') as f:
            content = f.read()
        
        # Validate command count
        commands_match = re.search(r'def _load_commands.*?\{([^}]+)\}', content, re.DOTALL)
        if commands_match:
            commands_block = commands_match.group(1)
            defined_commands = re.findall(r'"([^"]+)":', commands_block)
            
            # Check exact command match
            commands_correct = set(defined_commands) == set(self.expected_commands.keys())
            count_correct = len(defined_commands) == 8
            
            results["commands"] = {
                "status": "PASSED" if commands_correct and count_correct else "FAILED",
                "count": len(defined_commands),
                "expected_count": 8,
                "defined": sorted(defined_commands),
                "expected": sorted(self.expected_commands.keys()),
                "missing": list(set(self.expected_commands.keys()) - set(defined_commands)),
                "extra": list(set(defined_commands) - set(self.expected_commands.keys()))
            }
            
            print(f"   Commands: {'✅' if commands_correct and count_correct else '❌'} {len(defined_commands)}/8 commands")
        else:
            results["commands"] = {"status": "FAILED", "reason": "Commands definition not found"}
            print("   Commands: ❌ Commands definition not found")
        
        # Check help system
        help_sections = ["DAILY WORKFLOW", "TROUBLESHOOTING", "DATA & VERSION"]
        help_correct = all(section in content for section in help_sections)
        results["help_system"] = {
            "status": "PASSED" if help_correct else "FAILED", 
            "sections": help_sections,
            "found": [s for s in help_sections if s in content]
        }
        print(f"   Help System: {'✅' if help_correct else '❌'} Workflow-oriented help")
        
        # Check code size (target ~153 lines, max 200)
        lines = len(content.splitlines())
        size_ok = lines <= 200
        results["code_size"] = {
            "status": "PASSED" if size_ok else "FAILED",
            "current_lines": lines,
            "target_max": 200,
            "ideal": 153
        }
        print(f"   Code Size: {'✅' if size_ok else '❌'} {lines} lines (target ≤200)")
        
        return results
    
    def _audit_documentation(self) -> Dict[str, Any]:
        """Audit documentation consistency."""
        print("\n📚 Phase 2: Documentation Consistency")
        print("-" * 40)
        
        results = {}
        doc_files = {
            "README.md": self.project_root / "README.md",
            "CLAUDE.md": self.project_root / "CLAUDE.md",
            "common/README.md": self.project_root / "common" / "README.md"
        }
        
        for doc_name, doc_path in doc_files.items():
            if not doc_path.exists():
                results[doc_name] = {"status": "FAILED", "reason": "File not found"}
                print(f"   {doc_name}: ❌ Not found")
                continue
            
            with open(doc_path, 'r') as f:
                content = f.read()
            
            # Check for deprecated command references
            deprecated_found = []
            for cmd in self.deprecated_commands:
                if re.search(rf'p3\s+{re.escape(cmd)}\b', content):
                    deprecated_found.append(cmd)
            
            # Check for valid command references
            valid_found = []
            for cmd in self.expected_commands.keys():
                if f'p3 {cmd}' in content:
                    valid_found.append(cmd)
            
            doc_status = "PASSED" if not deprecated_found else "FAILED"
            results[doc_name] = {
                "status": doc_status,
                "deprecated_commands": deprecated_found,
                "valid_commands": valid_found,
                "deprecated_count": len(deprecated_found)
            }
            
            status_icon = "✅" if doc_status == "PASSED" else "❌"
            print(f"   {doc_name}: {status_icon} {len(deprecated_found)} deprecated refs")
        
        return results
    
    def _audit_design_goals(self) -> Dict[str, Any]:
        """Audit design goals achievement."""
        print("\n🎯 Phase 3: Design Goals Validation")
        print("-" * 40)
        
        results = {}
        
        # Goal 1: Command Reduction (49+ → 8)
        core_results = self.audit_results.get("core_system", {})
        commands_info = core_results.get("commands", {})
        goal1_passed = commands_info.get("count", 0) == 8
        results["command_reduction"] = {
            "status": "PASSED" if goal1_passed else "FAILED",
            "from": "49+ commands",
            "to": "8 commands", 
            "actual": commands_info.get("count", 0)
        }
        print(f"   Command Reduction: {'✅' if goal1_passed else '❌'} 49+ → 8 commands")
        
        # Goal 2: Code Simplification (600+ → ~153)
        size_info = core_results.get("code_size", {})
        goal2_passed = size_info.get("current_lines", 0) <= 200
        results["code_simplification"] = {
            "status": "PASSED" if goal2_passed else "FAILED",
            "from": "600+ lines",
            "to": "~153 lines",
            "actual": size_info.get("current_lines", 0)
        }
        print(f"   Code Simplification: {'✅' if goal2_passed else '❌'} 600+ → {size_info.get('current_lines', 0)} lines")
        
        # Goal 3: Workflow-Oriented Design
        help_info = core_results.get("help_system", {})
        goal3_passed = help_info.get("status") == "PASSED"
        results["workflow_oriented"] = {
            "status": "PASSED" if goal3_passed else "FAILED",
            "sections": help_info.get("found", [])
        }
        print(f"   Workflow-Oriented: {'✅' if goal3_passed else '❌'} Developer intent focus")
        
        # Goal 4: Documentation Currency
        doc_results = self.audit_results.get("documentation", {})
        deprecated_total = sum(
            result.get("deprecated_count", 0) 
            for result in doc_results.values() 
            if isinstance(result, dict)
        )
        goal4_passed = deprecated_total == 0
        results["documentation_currency"] = {
            "status": "PASSED" if goal4_passed else "FAILED",
            "deprecated_references": deprecated_total
        }
        print(f"   Documentation Currency: {'✅' if goal4_passed else '❌'} {deprecated_total} deprecated refs")
        
        # Goal 5: English-Only Standard
        goal5_passed = self._check_english_only()
        results["english_only"] = {
            "status": "PASSED" if goal5_passed else "FAILED"
        }
        print(f"   English-Only Standard: {'✅' if goal5_passed else '❌'} Compliance check")
        
        return results
    
    def _audit_code_quality(self) -> Dict[str, Any]:
        """Audit code quality aspects."""
        print("\n🔍 Phase 4: Code Quality Check")
        print("-" * 40)
        
        results = {}
        
        p3_file = self.project_root / "p3.py"
        if not p3_file.exists():
            return {"status": "FAILED", "reason": "p3.py not found"}
        
        with open(p3_file, 'r') as f:
            content = f.read()
        
        # Check for proper imports
        required_imports = ["os", "sys", "subprocess", "pathlib", "typing"]
        imports_found = [imp for imp in required_imports if f"import {imp}" in content]
        imports_ok = len(imports_found) >= 4  # At least 4 of 5
        
        results["imports"] = {
            "status": "PASSED" if imports_ok else "FAILED",
            "found": imports_found,
            "required": required_imports
        }
        print(f"   Imports: {'✅' if imports_ok else '❌'} {len(imports_found)}/{len(required_imports)} required imports")
        
        # Check for proper error handling
        error_handling = "sys.exit" in content and "except" in content
        results["error_handling"] = {
            "status": "PASSED" if error_handling else "FAILED",
            "has_exit": "sys.exit" in content,
            "has_exceptions": "except" in content
        }
        print(f"   Error Handling: {'✅' if error_handling else '❌'} Proper error handling")
        
        # Check for docstrings
        docstring_count = content.count('"""')
        has_docstrings = docstring_count >= 4  # Class + methods
        results["documentation"] = {
            "status": "PASSED" if has_docstrings else "FAILED",
            "docstring_count": docstring_count // 2  # Each docstring has start/end
        }
        print(f"   Documentation: {'✅' if has_docstrings else '❌'} {docstring_count//2} docstrings")
        
        return results
    
    def _check_english_only(self) -> bool:
        """Check for English-only compliance."""
        # Quick check for common non-English patterns
        non_english_patterns = [
            r'[\u4e00-\u9fff]+',  # Chinese
            r'[а-яё]+',  # Cyrillic
            r'[α-ωάέήίόύώ]+'  # Greek
        ]
        
        key_files = [self.project_root / "p3.py", self.project_root / "README.md"]
        for file_path in key_files:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in non_english_patterns:
                        if re.search(pattern, content):
                            return False
        return True
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate audit summary."""
        summary = {
            "total_phases": 4,
            "phases_passed": 0,
            "critical_issues": [],
            "warnings": [],
            "overall_status": "UNKNOWN"
        }
        
        # Analyze results
        for phase_name, phase_results in self.audit_results.items():
            if phase_name == "summary":
                continue
                
            if isinstance(phase_results, dict):
                phase_passed = True
                for check_name, check_result in phase_results.items():
                    if isinstance(check_result, dict) and check_result.get("status") == "FAILED":
                        phase_passed = False
                        summary["critical_issues"].append(f"{phase_name}.{check_name}")
                    elif isinstance(check_result, dict) and check_result.get("status") == "PASSED":
                        # Check for warnings (partial success)
                        if check_name == "commands" and check_result.get("extra"):
                            summary["warnings"].append(f"Extra commands found: {check_result['extra']}")
                
                if phase_passed:
                    summary["phases_passed"] += 1
        
        # Determine overall status
        if summary["phases_passed"] == summary["total_phases"]:
            summary["overall_status"] = "PASSED"
        elif summary["phases_passed"] >= 2:
            summary["overall_status"] = "PARTIAL"
        else:
            summary["overall_status"] = "FAILED"
        
        return summary
    
    def generate_final_report(self) -> str:
        """Generate comprehensive final report."""
        self.run_comprehensive_audit()
        
        report = []
        report.append("=" * 80)
        report.append("🚀 COMPREHENSIVE P3 SYSTEM AUDIT - FINAL REPORT")
        report.append("=" * 80)
        report.append("")
        
        summary = self.audit_results["summary"]
        
        # Executive Summary
        report.append("📊 EXECUTIVE SUMMARY")
        status_icon = {"PASSED": "✅", "PARTIAL": "⚠️", "FAILED": "❌"}[summary["overall_status"]]
        report.append(f"Overall Status: {status_icon} {summary['overall_status']}")
        report.append(f"Phases Passed: {summary['phases_passed']}/{summary['total_phases']}")
        report.append(f"Critical Issues: {len(summary['critical_issues'])}")
        report.append(f"Warnings: {len(summary['warnings'])}")
        report.append("")
        
        # Design Goals Achievement
        report.append("🎯 DESIGN GOALS ACHIEVEMENT")
        if "design_goals" in self.audit_results:
            for goal, result in self.audit_results["design_goals"].items():
                status = result.get("status", "UNKNOWN")
                icon = "✅" if status == "PASSED" else "❌"
                report.append(f"{icon} {goal.replace('_', ' ').title()}")
        report.append("")
        
        # Critical Issues
        if summary["critical_issues"]:
            report.append("🚨 CRITICAL ISSUES REQUIRING ATTENTION")
            for issue in summary["critical_issues"]:
                report.append(f"❌ {issue}")
            report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS")
        if summary["overall_status"] == "PASSED":
            report.append("✅ P3 system audit completed successfully!")
            report.append("• All design goals achieved")
            report.append("• System ready for production use")
            report.append("• Consider running final validation tests")
        elif summary["overall_status"] == "PARTIAL":
            report.append("⚠️  P3 system mostly ready with minor issues:")
            for issue in summary["critical_issues"]:
                report.append(f"• Address {issue}")
        else:
            report.append("❌ P3 system requires significant fixes:")
            report.append("• Address all critical issues before proceeding")
            report.append("• Re-run audit after fixes")
        
        return "\n".join(report)


def main():
    """Main execution function."""
    project_root = Path(__file__).parent.parent
    auditor = ComprehensiveP3Auditor(project_root)
    
    # Run audit and generate report
    report = auditor.generate_final_report()
    print(report)
    
    # Save detailed results
    results_file = project_root / "build_data" / "logs" / "p3_comprehensive_audit.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)
    with open(results_file, 'w') as f:
        json.dump(auditor.audit_results, f, indent=2)
    
    # Save report
    report_file = project_root / "build_data" / "logs" / "p3_final_audit_report.txt"  
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n📊 Detailed results: {results_file}")
    print(f"📋 Final report: {report_file}")
    
    # Return exit code
    overall_status = auditor.audit_results["summary"]["overall_status"]
    return 0 if overall_status == "PASSED" else 1


if __name__ == "__main__":
    exit(main())