#!/usr/bin/env python3
"""
Setup tab completion for P3 commands.
Creates bash completion script that provides command hints and descriptions.
"""

import os
from pathlib import Path

# P3 command definitions with descriptions and examples
P3_COMMANDS = {
    # Core Development
    'build': {
        'desc': 'Fast F2 build (development default)',
        'example': 'p3 build  # Quick 2-company build'
    },
    'build-f2': {
        'desc': 'Fast 2-company build',
        'example': 'p3 build-f2  # MSFT, NVDA analysis'
    },
    'build-m7': {
        'desc': 'Full Magnificent 7 analysis',
        'example': 'p3 build-m7  # All 7 companies with DCF'
    },
    'build-n100': {
        'desc': 'NASDAQ-100 build',
        'example': 'p3 build-n100  # 100 companies'
    },
    'build-v3k': {
        'desc': 'VTI 3500 build (comprehensive)',
        'example': 'p3 build-v3k  # Full market analysis'
    },
    
    # Testing & Quality
    'test': {
        'desc': 'Run full test suite with coverage',
        'example': 'p3 test  # pytest + coverage reports'
    },
    'lint': {
        'desc': 'Format code (black + isort)',
        'example': 'p3 lint  # Auto-format all Python files'
    },
    'clean': {
        'desc': 'Clean all build artifacts',
        'example': 'p3 clean  # Remove old build directories'
    },
    
    # Status & Development
    'status': {
        'desc': 'Check environment status',
        'example': 'p3 status  # Pixi, Podman, Neo4j status'
    },
    'dev': {
        'desc': 'Development environment check',
        'example': 'p3 dev  # Quick dev readiness check'
    },
    
    # DCF Analysis
    'dcf': {
        'desc': 'Quick DCF analysis',
        'example': 'p3 dcf  # Interactive DCF analysis'
    },
    'dcf-f2': {
        'desc': 'Fast 2-company DCF test',
        'example': 'p3 dcf-f2  # Quick validation'
    },
    'dcf-m7': {
        'desc': 'Full Magnificent 7 DCF analysis',
        'example': 'p3 dcf-m7  # Complete M7 analysis'
    },
    
    # Environment Management
    'env-start': {
        'desc': 'Start all services (Podman + Neo4j)',
        'example': 'p3 env-start  # Boot up environment'
    },
    'env-stop': {
        'desc': 'Stop all services',
        'example': 'p3 env-stop  # Clean shutdown'
    },
    'env-status': {
        'desc': 'Detailed environment status',
        'example': 'p3 env-status  # Full system check'
    },
    'env-reset': {
        'desc': 'Reset environment (destructive)',
        'example': 'p3 env-reset  # Nuclear option'
    },
    'env-setup': {
        'desc': 'Initial environment setup',
        'example': 'p3 env-setup  # First-time setup'
    },
    
    # Release & PR
    'release': {
        'desc': 'Interactive build selection & release',
        'example': 'p3 release  # Select & promote build'
    },
    'pr': {
        'desc': 'Create pull request with testing',
        'example': 'p3 pr  # Test + create/update PR'
    },
}

def create_bash_completion():
    """Create bash completion script for P3 commands."""
    
    # Generate command list for completion
    commands = list(P3_COMMANDS.keys())
    commands_str = ' '.join(commands)
    
    # Create the completion script
    completion_script = f'''#!/bin/bash
# P3 Command Completion Script
# Usage: source this file or add to ~/.bashrc

_p3_completion() {{
    local cur prev commands
    COMPREPLY=()
    cur="${{COMP_WORDS[COMP_CWORD]}}"
    prev="${{COMP_WORDS[COMP_CWORD-1]}}"
    
    # Available P3 commands
    commands="{commands_str}"
    
    # Generate completions
    if [[ ${{COMP_CWORD}} == 1 ]]; then
        COMPREPLY=($(compgen -W "${{commands}}" -- "${{cur}}"))
        
        # Show help for partial matches
        if [[ ${{#COMPREPLY[@]}} == 1 ]] && [[ "${{cur}}" != "${{COMPREPLY[0]}}" ]]; then
            local cmd="${{COMPREPLY[0]}}"
            case "$cmd" in
'''
    
    # Add case statements for each command
    for cmd, info in P3_COMMANDS.items():
        completion_script += f'''                {cmd})
                    echo "  → {info['desc']}"
                    echo "    {info['example']}"
                    ;;
'''
    
    completion_script += '''            esac
        fi
    fi
    
    return 0
}

# Register completion function
complete -F _p3_completion p3

# P3 Help Function - shows all commands with descriptions
p3_help() {
    echo "🚀 P3 Command System - Available Commands:"
    echo ""
    echo "📖 Core Development:"
'''

    # Add core development commands
    for cmd in ['build', 'build-f2', 'build-m7', 'test', 'lint', 'clean', 'status', 'dev']:
        if cmd in P3_COMMANDS:
            info = P3_COMMANDS[cmd]
            completion_script += f'    echo "   p3 {cmd:<12} - {info["desc"]}"\n'
    
    completion_script += '''
    echo ""
    echo "🧬 DCF Analysis:"
'''
    
    # Add DCF commands
    for cmd in ['dcf', 'dcf-f2', 'dcf-m7']:
        if cmd in P3_COMMANDS:
            info = P3_COMMANDS[cmd]
            completion_script += f'    echo "   p3 {cmd:<12} - {info["desc"]}"\n'
    
    completion_script += '''
    echo ""
    echo "🔧 Environment:"
'''
    
    # Add environment commands
    for cmd in ['env-start', 'env-stop', 'env-status', 'env-reset', 'env-setup']:
        if cmd in P3_COMMANDS:
            info = P3_COMMANDS[cmd]
            completion_script += f'    echo "   p3 {cmd:<12} - {info["desc"]}"\n'
    
    completion_script += '''
    echo ""
    echo "📦 Release & PR:"
'''
    
    # Add release commands
    for cmd in ['release', 'pr']:
        if cmd in P3_COMMANDS:
            info = P3_COMMANDS[cmd]
            completion_script += f'    echo "   p3 {cmd:<12} - {info["desc"]}"\n'
    
    completion_script += '''
    echo ""
    echo "💡 Usage: p3 <command> or p3 <TAB> for completion"
    echo "💡 Help:  p3_help (this message) or p3 (quick help)"
}

# Create alias for quick help
alias p3h=p3_help

echo "✅ P3 completion loaded! Try: p3 <TAB>"
echo "💡 For full help: p3_help or p3h"
'''
    
    return completion_script

def setup_completion():
    """Setup P3 tab completion system."""
    
    print("🚀 Setting up P3 tab completion...")
    
    # Create completion script
    completion_content = create_bash_completion()
    
    # Write to completion file
    completion_file = Path.home() / ".p3_completion"
    with open(completion_file, 'w') as f:
        f.write(completion_content)
    
    print(f"✅ Created completion script: {completion_file}")
    
    # Instructions for user
    print("""
📖 To enable P3 tab completion:

1. Add to your shell profile (~/.bashrc, ~/.zshrc, etc.):
   echo 'source ~/.p3_completion' >> ~/.bashrc

2. Or source it now:
   source ~/.p3_completion

3. Test it:
   p3 <TAB>         # Shows all commands
   p3 bu<TAB>       # Completes to 'build'
   p3_help          # Shows full command reference

💡 The completion system will show command descriptions and examples!
""")
    
    # Try to auto-add to bashrc if it exists
    bashrc = Path.home() / ".bashrc"
    if bashrc.exists():
        with open(bashrc, 'r') as f:
            content = f.read()
        
        source_line = "source ~/.p3_completion"
        if source_line not in content:
            with open(bashrc, 'a') as f:
                f.write(f"\n# P3 Command Completion\n{source_line}\n")
            print(f"✅ Auto-added to {bashrc}")
    
    # Check for zsh
    zshrc = Path.home() / ".zshrc" 
    if zshrc.exists():
        with open(zshrc, 'r') as f:
            content = f.read()
        
        source_line = "source ~/.p3_completion"
        if source_line not in content:
            with open(zshrc, 'a') as f:
                f.write(f"\n# P3 Command Completion\n{source_line}\n")
            print(f"✅ Auto-added to {zshrc}")
    
    return completion_file

if __name__ == "__main__":
    setup_completion()
