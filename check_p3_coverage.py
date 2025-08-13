#!/usr/bin/env python3
"""
Check P3 command coverage against documentation.
Ensures README.md and CLAUDE.md have 100% P3 coverage.
"""

import re
from pathlib import Path
from typing import Set, Dict, List

def extract_commands_from_docs() -> Dict[str, Set[str]]:
    """Extract all commands from documentation files."""
    
    commands = {}
    
    # Files to check
    doc_files = {
        'README.md': Path('README.md'),
        'CLAUDE.md': Path('CLAUDE.md'),
    }
    
    for doc_name, doc_path in doc_files.items():
        if not doc_path.exists():
            print(f"⚠️  {doc_name} not found")
            continue
            
        with open(doc_path, 'r') as f:
            content = f.read()
        
        # Extract all commands from code blocks
        cmd_pattern = r'```bash\n(.*?)```'
        code_blocks = re.findall(cmd_pattern, content, re.DOTALL)
        
        doc_commands = set()
        for block in code_blocks:
            lines = block.strip().split('\n')
            for line in lines:
                line = line.strip()
                # Skip comments and empty lines
                if line.startswith('#') or not line:
                    continue
                
                # Extract command (first word/phrase)
                if line.startswith('p3 '):
                    cmd = line.split()[1] if len(line.split()) > 1 else ''
                    if cmd:
                        doc_commands.add(cmd)
                elif line.startswith('pixi run '):
                    # This should be replaced with p3
                    cmd = line.replace('pixi run ', '').split()[0]
                    print(f"❌ Found unreplaced pixi run command in {doc_name}: {line}")
        
        commands[doc_name] = doc_commands
    
    return commands

def extract_p3_commands_from_pixi() -> Set[str]:
    """Extract all P3 commands from pixi.toml."""
    
    pixi_file = Path('pixi.toml')
    if not pixi_file.exists():
        print("❌ pixi.toml not found")
        return set()
    
    with open(pixi_file, 'r') as f:
        content = f.read()
    
    # Extract tasks section
    tasks_match = re.search(r'\[tasks\](.*?)(?=\n\[|\Z)', content, re.DOTALL)
    if not tasks_match:
        print("❌ No [tasks] section found in pixi.toml")
        return set()
    
    tasks_content = tasks_match.group(1)
    
    # Extract all task names (commands)
    task_pattern = r'^([a-zA-Z0-9_-]+)\s*='
    task_matches = re.findall(task_pattern, tasks_content, re.MULTILINE)
    
    # Filter for P3-style commands (exclude long legacy names)
    p3_commands = set()
    for cmd in task_matches:
        # Include short commands and commands with hyphens
        if len(cmd) <= 25 and not cmd.startswith('p3'):  # Exclude p3 and p3-help
            p3_commands.add(cmd)
        # Include specific patterns
        elif cmd.startswith(('build-', 'dcf-', 'env-', 'test-', 'neo4j-', 'cleanup-', 'commit-', 'update-', 'validate-', 'generate-', 'podman-')):
            p3_commands.add(cmd)
    
    return p3_commands

def check_coverage():
    """Check P3 command coverage."""
    
    print("🔍 Checking P3 Command Coverage")
    print("=" * 50)
    
    # Extract commands from documentation
    doc_commands = extract_commands_from_docs()
    
    # Extract P3 commands from pixi.toml
    pixi_commands = extract_p3_commands_from_pixi()
    
    print(f"📖 Commands found in documentation:")
    for doc_name, commands in doc_commands.items():
        print(f"   {doc_name}: {len(commands)} commands")
        for cmd in sorted(commands):
            print(f"     - {cmd}")
    
    print(f"\n⚙️  P3 commands available in pixi.toml: {len(pixi_commands)}")
    for cmd in sorted(pixi_commands):
        print(f"     - {cmd}")
    
    # Check coverage for each document
    print("\n📊 Coverage Analysis:")
    
    overall_missing = set()
    
    for doc_name, commands in doc_commands.items():
        missing = commands - pixi_commands
        coverage = (len(commands) - len(missing)) / len(commands) * 100 if commands else 100
        
        print(f"\n📄 {doc_name}:")
        print(f"   Coverage: {coverage:.1f}% ({len(commands) - len(missing)}/{len(commands)})")
        
        if missing:
            print(f"   ❌ Missing P3 commands:")
            for cmd in sorted(missing):
                print(f"     - {cmd}")
                overall_missing.add(cmd)
        else:
            print(f"   ✅ 100% coverage!")
    
    # Summary
    print("\n" + "=" * 50)
    if overall_missing:
        print(f"❌ COVERAGE INCOMPLETE")
        print(f"Missing P3 commands: {sorted(overall_missing)}")
        print(f"\n💡 Action needed:")
        print(f"   1. Add missing commands to pixi.toml [tasks] section")
        print(f"   2. Update documentation to use existing P3 commands")
        return False
    else:
        print("✅ 100% P3 COVERAGE ACHIEVED!")
        print("All commands in README.md and CLAUDE.md have P3 equivalents")
        return True

def suggest_missing_commands():
    """Suggest pixi.toml entries for missing commands."""
    
    doc_commands = extract_commands_from_docs()
    pixi_commands = extract_p3_commands_from_pixi()
    
    all_doc_commands = set()
    for commands in doc_commands.values():
        all_doc_commands.update(commands)
    
    missing = all_doc_commands - pixi_commands
    
    if missing:
        print(f"\n💡 Suggested pixi.toml entries for missing commands:")
        print("# Add these to the [tasks] section:")
        
        for cmd in sorted(missing):
            # Suggest appropriate command mappings
            if 'update' in cmd and 'stock' in cmd:
                print(f'{cmd} = "python ETL/fetch_ticker_lists.py"')
            elif 'commit' in cmd and 'data' in cmd:
                print(f'{cmd} = "python infra/commit_data_changes.py"')
            elif 'cleanup' in cmd and 'branch' in cmd:
                print(f'{cmd} = "python infra/cleanup_merged_branches.py"')
            elif 'run-job' in cmd:
                print(f'{cmd} = "python ETL/run_job.py"')
            elif 'create-build' in cmd:
                print(f'{cmd} = "python scripts/manage_build_data.py create"')
            else:
                print(f'{cmd} = "echo \'Command {cmd} not yet implemented\'"')

if __name__ == "__main__":
    success = check_coverage()
    if not success:
        suggest_missing_commands()
    print("")
