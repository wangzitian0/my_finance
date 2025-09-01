#!/usr/bin/env python3
"""
Directory Hygiene Analysis Tool for Issue #122
CRITICAL: Root Directory Hygiene Validation for Clean Repository Structure
"""

import os
import fnmatch
import json
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime

class DirectoryHygieneAnalyzer:
    """
    EXECUTE comprehensive root directory hygiene analysis
    Validates Clean Repository Structure against CLAUDE.md policies
    """
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self.violations = []
        self.recommendations = []
        
        # Define allowed files in root per CLAUDE.md policies
        self.allowed_root_files = {
            # Core configuration files
            "README.md", "CLAUDE.md", "CHANGELOG.md",
            ".gitignore", ".gitattributes", 
            "pixi.toml", "pixi.lock", "pyproject.toml",
            
            # P3 Command System (mandatory)
            "p3.py",
            
            # Validation scripts (allowed for CI/CD)
            "ci_language_check.py", "ci_m7_validation.py",
            "check_n100.py", "check_v3k.py",
            
            # Test files (should eventually be moved)
            "test_ci_validation.py", "test_dual_config_compatibility.py",
            "test_f2_sec.py", "test_orthogonal_config.py", "test_sec_config.py",
            
            # Debug files (should be moved)
            "debug_ollama_api.py"
        }
        
        # Define Five-Layer Data Architecture paths
        self.required_data_layers = {
            "build_data/stage_00_raw": "Layer 0: Raw immutable source data",
            "build_data/stage_01_daily_delta": "Layer 1: Daily incremental changes", 
            "build_data/stage_02_daily_index": "Layer 2: Vectors and entities",
            "build_data/stage_03_graph_rag": "Layer 3: Unified knowledge base",
            "build_data/stage_04_query_results": "Layer 4: Analysis results"
        }
        
        # Policy violations to detect
        self.prohibited_md_files = [
            "ARCHITECTURE_REVIEW.md", "IMPLEMENTATION_PLAN.md",
            "OPTIMIZATION_ROADMAP.md", "PROJECT_STATUS.md",
            "HRBP-SYSTEM-OVERVIEW.md"  # Should be in GitHub Issues
        ]

    def execute_hygiene_scan(self) -> Dict:
        """EXECUTE comprehensive directory hygiene scan"""
        print("🔍 EXECUTING Root Directory Hygiene Analysis for Issue #122")
        
        # 1. Validate root directory contents
        self._check_root_directory_violations()
        
        # 2. Validate Five-Layer Data Architecture
        self._validate_data_architecture()
        
        # 3. Detect misplaced files
        self._detect_misplaced_files()
        
        # 4. Check for build artifacts
        self._check_build_artifacts()
        
        # 5. Validate prohibited documentation files
        self._check_prohibited_documentation()
        
        # 6. Generate cleanup recommendations
        self._generate_cleanup_recommendations()
        
        return self._generate_report()
    
    def _check_root_directory_violations(self):
        """Check for unauthorized files in root directory"""
        print("📁 Checking root directory violations...")
        
        root_files = []
        for item in self.root_dir.iterdir():
            if item.is_file() and not item.name.startswith('.'):
                root_files.append(item.name)
        
        for file in root_files:
            if file not in self.allowed_root_files:
                self.violations.append({
                    "type": "UNAUTHORIZED_ROOT_FILE",
                    "file": file,
                    "severity": "HIGH",
                    "description": f"Unauthorized file in root: {file}",
                    "action": "MOVE_OR_DELETE"
                })
    
    def _validate_data_architecture(self):
        """Validate Five-Layer Data Architecture exists"""
        print("🏗️ Validating Five-Layer Data Architecture...")
        
        for layer_path, description in self.required_data_layers.items():
            full_path = self.root_dir / layer_path
            if not full_path.exists():
                self.violations.append({
                    "type": "MISSING_DATA_LAYER", 
                    "path": layer_path,
                    "severity": "CRITICAL",
                    "description": f"Missing required data layer: {description}",
                    "action": "CREATE_DIRECTORY"
                })
    
    def _detect_misplaced_files(self):
        """Detect files that should be in build_data structure"""
        print("📋 Detecting misplaced data files...")
        
        # Check for data files outside build_data
        for root, dirs, files in os.walk(self.root_dir):
            rel_root = Path(root).relative_to(self.root_dir)
            
            # Skip build_data directory itself
            if str(rel_root).startswith('build_data'):
                continue
                
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.root_dir)
                
                # Check for data file extensions
                data_extensions = {'.json', '.csv', '.pkl', '.parquet', '.db', '.sqlite'}
                if file_path.suffix in data_extensions:
                    # Allow some configuration files
                    if not any(part in str(rel_path) for part in ['config', 'template', 'schema']):
                        self.violations.append({
                            "type": "MISPLACED_DATA_FILE",
                            "file": str(rel_path),
                            "severity": "MEDIUM",
                            "description": f"Data file outside build_data: {rel_path}",
                            "action": "MOVE_TO_BUILD_DATA"
                        })
    
    def _check_build_artifacts(self):
        """Check for build artifacts that should be gitignored"""
        print("🛠️ Checking for build artifacts...")
        
        artifact_patterns = ['*.log', '*.tmp', '*.cache', '*.pid', '*.lock']
        
        for root, dirs, files in os.walk(self.root_dir):
            # Skip hidden directories and build_data
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'build_data']
            
            rel_root = Path(root).relative_to(self.root_dir)
            
            for file in files:
                for pattern in artifact_patterns:
                    if fnmatch.fnmatch(file, pattern) and file != 'pixi.lock':  # pixi.lock is allowed
                        file_path = rel_root / file
                        self.violations.append({
                            "type": "BUILD_ARTIFACT",
                            "file": str(file_path),
                            "severity": "LOW",
                            "description": f"Build artifact should be gitignored: {file}",
                            "action": "ADD_TO_GITIGNORE"
                        })
    
    def _check_prohibited_documentation(self):
        """Check for prohibited MD files per CLAUDE.md policy"""
        print("📝 Checking for prohibited documentation files...")
        
        for prohibited_file in self.prohibited_md_files:
            file_path = self.root_dir / prohibited_file
            if file_path.exists():
                self.violations.append({
                    "type": "PROHIBITED_DOCUMENTATION",
                    "file": prohibited_file,
                    "severity": "HIGH",
                    "description": f"Prohibited documentation file (use GitHub Issues): {prohibited_file}",
                    "action": "CONVERT_TO_GITHUB_ISSUE"
                })
        
        # Check for markdown files in releases directory (should be in build_data)
        releases_dir = self.root_dir / "releases"
        if releases_dir.exists():
            for root, dirs, files in os.walk(releases_dir):
                for file in files:
                    if file.endswith('.md') and file != 'README.md':
                        rel_path = Path(root).relative_to(self.root_dir) / file
                        self.violations.append({
                            "type": "MISPLACED_RELEASE_DATA",
                            "file": str(rel_path),
                            "severity": "MEDIUM", 
                            "description": f"Release data file should be in build_data: {rel_path}",
                            "action": "MOVE_TO_BUILD_DATA"
                        })
    
    def _generate_cleanup_recommendations(self):
        """Generate specific cleanup recommendations"""
        print("💡 Generating cleanup recommendations...")
        
        # Group violations by action type
        actions = {}
        for violation in self.violations:
            action = violation["action"]
            if action not in actions:
                actions[action] = []
            actions[action].append(violation)
        
        # Generate specific recommendations
        for action, violations in actions.items():
            if action == "MOVE_TO_BUILD_DATA":
                self.recommendations.append({
                    "action": action,
                    "description": "Move data files to appropriate build_data layers",
                    "files": [v["file"] for v in violations],
                    "script": self._generate_move_script(violations, "build_data/stage_00_raw/")
                })
            
            elif action == "CONVERT_TO_GITHUB_ISSUE":
                self.recommendations.append({
                    "action": action,
                    "description": "Convert prohibited MD files to GitHub Issues",
                    "files": [v["file"] for v in violations],
                    "script": "# Use GitHub web interface or gh CLI to create issues"
                })
            
            elif action == "ADD_TO_GITIGNORE":
                self.recommendations.append({
                    "action": action,
                    "description": "Add build artifacts to .gitignore",
                    "files": [v["file"] for v in violations],
                    "script": self._generate_gitignore_additions(violations)
                })
    
    def _generate_move_script(self, violations: List[Dict], target_dir: str) -> str:
        """Generate bash script to move files"""
        script_lines = ["#!/bin/bash", "set -e", ""]
        script_lines.append(f"mkdir -p {target_dir}")
        script_lines.append("")
        
        for violation in violations:
            src_file = violation["file"]
            target_file = f"{target_dir}{Path(src_file).name}"
            script_lines.append(f"mv '{src_file}' '{target_file}'")
        
        return "\n".join(script_lines)
    
    def _generate_gitignore_additions(self, violations: List[Dict]) -> str:
        """Generate .gitignore additions"""
        patterns = set()
        for violation in violations:
            file_path = Path(violation["file"])
            if file_path.suffix:
                patterns.add(f"*{file_path.suffix}")
            else:
                patterns.add(file_path.name)
        
        return "\n# Build artifacts\n" + "\n".join(sorted(patterns))
    
    def _generate_report(self) -> Dict:
        """Generate comprehensive hygiene report"""
        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "issue_number": 122,
            "total_violations": len(self.violations),
            "severity_breakdown": {
                "CRITICAL": len([v for v in self.violations if v["severity"] == "CRITICAL"]),
                "HIGH": len([v for v in self.violations if v["severity"] == "HIGH"]),
                "MEDIUM": len([v for v in self.violations if v["severity"] == "MEDIUM"]),
                "LOW": len([v for v in self.violations if v["severity"] == "LOW"])
            },
            "violations": self.violations,
            "recommendations": self.recommendations,
            "data_architecture_status": {
                "required_layers": len(self.required_data_layers),
                "existing_layers": len([p for p in self.required_data_layers.keys() 
                                      if (self.root_dir / p).exists()])
            }
        }
        
        return report

def main():
    """EXECUTE comprehensive directory hygiene analysis"""
    analyzer = DirectoryHygieneAnalyzer()
    report = analyzer.execute_hygiene_scan()
    
    # Save report
    report_file = Path("build_data/quality_reports/directory_hygiene_report.json")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 DIRECTORY HYGIENE ANALYSIS SUMMARY")
    print("="*60)
    print(f"Total Violations: {report['total_violations']}")
    print(f"Critical: {report['severity_breakdown']['CRITICAL']}")
    print(f"High: {report['severity_breakdown']['HIGH']}")
    print(f"Medium: {report['severity_breakdown']['MEDIUM']}")
    print(f"Low: {report['severity_breakdown']['LOW']}")
    print(f"Data Architecture: {report['data_architecture_status']['existing_layers']}/{report['data_architecture_status']['required_layers']} layers")
    
    print("\n🔧 TOP PRIORITY ACTIONS:")
    for rec in report['recommendations'][:3]:
        print(f"- {rec['action']}: {rec['description']}")
        print(f"  Affects {len(rec['files'])} files")
    
    print(f"\n📋 Full report saved to: {report_file}")
    
    return report

if __name__ == "__main__":
    main()