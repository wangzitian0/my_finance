#!/usr/bin/env python3
"""
Simple build data management for multiple work trees.
Only handles essential build directory isolation per branch.
"""

import os
import subprocess
import argparse
from pathlib import Path
from datetime import datetime


def get_current_branch():
    """Get current git branch."""
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def get_branch_build_dir(branch_name=None):
    """Get branch-specific build directory."""
    if branch_name is None:
        branch_name = get_current_branch()
    
    data_dir = Path("data")
    
    # Use new stage_99_build directory per issue #58
    return data_dir / "stage_99_build"


def create_build_dir():
    """Create timestamped build directory."""
    build_base = get_branch_build_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    build_dir = build_base / f"build_{timestamp}"
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Update latest symlink
    latest_link = Path("latest")
    if latest_link.exists() or latest_link.is_symlink():
        latest_link.unlink()
    latest_link.symlink_to(build_dir)
    
    print(f"Created: {build_dir}")
    return build_dir


def promote_to_release():
    """Select and promote a build to release directory."""
    build_base = get_branch_build_dir()
    
    # Find all available builds
    builds = list(build_base.glob("build_*"))
    if not builds:
        print("No builds found in stage_99_build")
        return
    
    # Sort builds by timestamp (newest first)
    builds.sort(reverse=True)
    
    print("\nAvailable builds:")
    for i, build in enumerate(builds, 1):
        # Get basic info about the build
        build_time = build.name.replace("build_", "").replace("_", ":")
        dcf_reports = list(build.glob("*DCF_Report*.txt"))
        report_count = len(dcf_reports)
        
        print(f"  {i}. {build.name} (Time: {build_time[:8]} {build_time[8:]}, Reports: {report_count})")
        
        # Show first few lines of any DCF report for preview
        if dcf_reports:
            try:
                with open(dcf_reports[0], 'r') as f:
                    preview = f.readline().strip()
                    if preview:
                        print(f"     Preview: {preview[:60]}...")
            except:
                pass
    
    print(f"  0. Cancel")
    
    # Get user selection
    while True:
        try:
            choice = input(f"\nSelect build to release (1-{len(builds)} or 0 to cancel): ").strip()
            if choice == "0":
                print("Cancelled")
                return
            
            build_idx = int(choice) - 1
            if 0 <= build_idx < len(builds):
                selected_build = builds[build_idx]
                break
            else:
                print(f"Please enter a number between 0 and {len(builds)}")
        except ValueError:
            print("Please enter a valid number")
    
    # Create release
    release_dir = Path("data/release")
    release_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    release_name = f"release_{timestamp}_{selected_build.name}"
    release_path = release_dir / release_name
    
    print(f"\nPromoting {selected_build.name} to release...")
    print(f"Release name: {release_name}")
    response = input("Continue? [y/N]: ").strip().lower()
    
    if response in ['y', 'yes']:
        import shutil
        shutil.copytree(selected_build, release_path)
        
        # Create release notes
        create_release_notes(release_path, selected_build)
        
        print(f"✅ Released to: {release_path}")
    else:
        print("Cancelled")


def create_release_notes(release_path, build_dir):
    """Create release notes for the promoted build."""
    # Analyze the build to gather information
    dcf_reports = list(build_dir.glob("*DCF_Report*.txt"))
    m7_reports = list(build_dir.glob("*M7*DCF*.txt"))
    
    # Extract build timestamp
    build_time = build_dir.name.replace("build_", "")
    
    # Count companies analyzed
    companies_analyzed = 0
    analysis_method = "Unknown"
    
    if dcf_reports:
        try:
            with open(dcf_reports[0], 'r') as f:
                content = f.read()
                if "Pure LLM" in content:
                    analysis_method = "Pure LLM (Ollama gpt-oss:20b)"
                elif "Traditional DCF" in content:
                    analysis_method = "Traditional DCF"
                
                # Count analyzed companies (look for "## " headers)
                companies_analyzed = content.count("## ") - content.count("## Analysis")
        except:
            pass 
    
    release_notes = f"""# M7 LLM DCF Analysis Release

**Release Date**: {datetime.now().strftime('%Y-%m-%d')}  
**Build ID**: {build_time}  
**Analysis Method**: {analysis_method}

## 📊 Analysis Results

### Companies Analyzed: {companies_analyzed}
### Reports Generated: {len(dcf_reports)} DCF reports, {len(m7_reports)} M7 reports

### Performance Metrics
- **Build Time**: {build_time[:8]} {build_time[8:]}
- **Analysis Engine**: {analysis_method}
- **Success Rate**: Based on generated reports

## 📁 Release Contents

```
{release_path.name}/
├── DCF_Report_*.txt           # Main DCF analysis report
├── M7_LLM_DCF_Report_*.txt   # M7-specific report (if available)
├── artifacts/                 # Build artifacts
└── stage_logs/               # Build stage logs
```

## 🚀 Key Features

- **Pure LLM Analysis**: AI-powered DCF valuation using local Ollama model
- **Magnificent 7 Focus**: Analysis of major tech companies
- **Comprehensive Reports**: Detailed valuation analysis with recommendations

---

**Generated automatically by release management system**
**Release timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    # Write release notes
    notes_path = release_path / "RELEASE_NOTES.md"
    with open(notes_path, 'w') as f:
        f.write(release_notes)
    
    print(f"📝 Release notes created: {notes_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["create", "release"], 
                       help="create: new build dir, release: promote to release")
    
    args = parser.parse_args()
    
    if args.command == "create":
        create_build_dir()
    elif args.command == "release":
        promote_to_release()


if __name__ == "__main__":
    main()