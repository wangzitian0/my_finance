#!/usr/bin/env python3
"""
Script to replace pixi run commands with p3 equivalents in documentation files.
"""

import re
from pathlib import Path

def replace_pixi_run_commands(content: str) -> str:
    """Replace pixi run commands with p3 equivalents."""
    
    # Define mapping of pixi run commands to p3 commands
    replacements = {
        # Core development commands
        'pixi run build': 'p3 build',
        'pixi run build-f2': 'p3 build-f2',
        'pixi run build-m7': 'p3 build-m7',
        'pixi run build-n100': 'p3 build-n100',
        'pixi run build-v3k': 'p3 build-v3k',
        'pixi run test': 'p3 test',
        'pixi run lint': 'p3 lint',
        'pixi run clean': 'p3 clean',
        'pixi run status': 'p3 status',
        'pixi run dev': 'p3 dev',
        
        # DCF commands
        'pixi run dcf': 'p3 dcf',
        'pixi run dcf-f2': 'p3 dcf-f2',
        'pixi run dcf-m7': 'p3 dcf-m7',
        'pixi run e2e-f2': 'p3 dcf-f2',
        'pixi run e2e': 'p3 dcf-m7',
        'pixi run e2e-m7': 'p3 dcf-m7',
        'pixi run e2e-n100': 'p3 build-n100',
        'pixi run e2e-v3k': 'p3 build-v3k',
        
        # Environment commands
        'pixi run env-start': 'p3 env-start',
        'pixi run env-stop': 'p3 env-stop',
        'pixi run env-status': 'p3 env-status',
        'pixi run env-reset': 'p3 env-reset',
        'pixi run env-setup': 'p3 env-setup',
        'pixi run setup-env': 'p3 env-setup',
        
        # Release & PR commands
        'pixi run release': 'p3 release',
        'pixi run release-build': 'p3 release',
        'pixi run create-build': 'p3 create-build',
        'pixi run pr': 'p3 pr',
        'pixi run gen-pr': 'p3 pr',
        'pixi run create-pr': 'p3 pr',
        
        # Legacy commands with p3 equivalents
        'pixi run generate-report': 'p3 generate-report',
        'pixi run validate-strategy': 'p3 validate-strategy',
        'pixi run format': 'p3 lint',
        'pixi run run-job': 'p3 run-job',
        'pixi run update-stock-lists': 'p3 update-stock-lists',
        'pixi run commit-data-changes': 'p3 commit-data-changes',
        'pixi run shutdown-all': 'p3 env-stop',
        'pixi run test-e2e': 'p3 pr --skip-pr',
        'pixi run cleanup-branches': 'p3 cleanup-branches',
        'pixi run cleanup-branches-dry-run': 'p3 cleanup-branches-dry-run',
        'pixi run cleanup-branches-auto': 'p3 cleanup-branches-auto',
        
        # Container management
        'pixi run podman-status': 'p3 podman-status',
        'pixi run neo4j-logs': 'p3 neo4j-logs',
        'pixi run neo4j-connect': 'p3 neo4j-connect',
        'pixi run neo4j-restart': 'p3 neo4j-restart',
        'pixi run neo4j-stop': 'p3 neo4j-stop',
        'pixi run neo4j-start': 'p3 neo4j-start',
        
        # Additional tools
        'pixi run ollama-status': 'p3 ollama-status',
        'pixi run build-status': 'p3 build-status',
        'pixi run build-size': 'p3 build-size',
    }
    
    # Apply all replacements
    for old_cmd, new_cmd in replacements.items():
        content = content.replace(old_cmd, new_cmd)
    
    return content

def process_file(file_path: Path):
    """Process a single file for pixi run replacements."""
    print(f"Processing {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        content = replace_pixi_run_commands(content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Updated {file_path}")
        else:
            print(f"  ⏭️  No changes needed for {file_path}")
            
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")

def main():
    """Main function to process all documentation files."""
    
    # Files to process
    files_to_process = [
        Path("CLAUDE.md"),
        Path("README.md"),
        Path("ARCHITECTURE.md"),
        Path("tests/README.md"),
        Path("ETL/README.md"),
        Path("dcf_engine/README.md"),
        Path("infra/README.md"),
    ]
    
    print("🚀 Starting pixi run -> p3 command replacement")
    print("="*50)
    
    for file_path in files_to_process:
        if file_path.exists():
            process_file(file_path)
        else:
            print(f"  ⚠️  File not found: {file_path}")
    
    print("="*50)
    print("✅ Replacement complete!")

if __name__ == "__main__":
    main()
