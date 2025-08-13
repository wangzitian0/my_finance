#!/usr/bin/env python3
"""
Setup tab completion for pixi commands
Generates bash and zsh completion scripts for pixi run commands
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


def get_pixi_tasks() -> List[str]:
    """Get list of available pixi tasks"""
    try:
        result = subprocess.run(
            ["pixi", "task", "list"], capture_output=True, text=True, check=True
        )

        # Parse the output to extract task names
        tasks = []
        lines = result.stdout.strip().split("\n")

        for line in lines:
            if line.startswith("Tasks that can run on this machine:"):
                continue
            if line.startswith("---"):
                continue
            if line.startswith("Task"):
                continue
            if line.strip() and not line.startswith(" "):
                # Task names are comma-separated
                task_line = line.strip()
                if task_line:
                    tasks.extend([task.strip() for task in task_line.split(", ")])

        return sorted(set(tasks))

    except subprocess.CalledProcessError as e:
        print(f"Error getting pixi tasks: {e}", file=sys.stderr)
        return []


def generate_bash_completion(tasks: List[str]) -> str:
    """Generate bash completion script"""
    tasks_str = " ".join(tasks)

    return f"""#!/bin/bash
# Pixi tab completion for bash
# Source this file or add to ~/.bashrc

_pixi_run_completion() {{
    local cur prev words cword
    _init_completion || return

    if [[ $COMP_CWORD -eq 2 && "${{words[1]}}" == "run" ]]; then
        # Complete pixi run commands
        local tasks="{tasks_str}"
        COMPREPLY=($(compgen -W "$tasks" -- "$cur"))
    fi
}}

# Register completion for pixi
complete -F _pixi_run_completion pixi

# Also handle 'pixi run' directly
_pixi_run_direct_completion() {{
    local cur prev words cword
    _init_completion || return
    
    local tasks="{tasks_str}"
    COMPREPLY=($(compgen -W "$tasks" -- "$cur"))
}}

complete -F _pixi_run_direct_completion pixi-run

# Create alias for convenience
alias pr='pixi run'
complete -F _pixi_run_direct_completion pr
"""


def generate_zsh_completion(tasks: List[str]) -> str:
    """Generate zsh completion script"""
    task_completions = []
    for task in tasks:
        task_completions.append(f'    "{task}:Run {task} task"')

    completions_str = "\n".join(task_completions)

    return f"""#compdef pixi

# Pixi tab completion for zsh
# Add to ~/.zshrc or save as _pixi in your fpath

_pixi() {{
    local context state line
    typeset -A opt_args

    _arguments -C \\
        '1:command:->command' \\
        '*::arg:->args'

    case $state in
        command)
            _values 'pixi commands' \\
                'run[Run a task]' \\
                'add[Add dependencies]' \\
                'install[Install dependencies]' \\
                'shell[Start shell in environment]' \\
                'task[Manage tasks]'
            ;;
        args)
            case $words[1] in
                run)
                    _values 'available tasks' \\
{completions_str}
                    ;;
            esac
            ;;
    esac
}}

_pixi "$@"

# Create alias for convenience
alias pr='pixi run'

# Completion for the alias
_pr() {{
    _values 'available tasks' \\
{completions_str}
}}

compdef _pr pr
"""


def generate_fish_completion(tasks: List[str]) -> str:
    """Generate fish completion script"""
    completions = []
    for task in tasks:
        completions.append(
            f"complete -c pixi -n '__fish_seen_subcommand_from run' -a '{task}' -d 'Run {task} task'"
        )

    completions_str = "\n".join(completions)

    return f"""# Pixi tab completion for fish
# Save as ~/.config/fish/completions/pixi.fish

# Basic pixi commands
complete -c pixi -n "not __fish_seen_subcommand_from run add install shell task" -a "run" -d "Run a task"
complete -c pixi -n "not __fish_seen_subcommand_from run add install shell task" -a "add" -d "Add dependencies"
complete -c pixi -n "not __fish_seen_subcommand_from run add install shell task" -a "install" -d "Install dependencies"
complete -c pixi -n "not __fish_seen_subcommand_from run add install shell task" -a "shell" -d "Start shell in environment"
complete -c pixi -n "not __fish_seen_subcommand_from run add install shell task" -a "task" -d "Manage tasks"

# Task completions for 'pixi run'
{completions_str}

# Create alias for convenience
alias pr='pixi run'

# Completion for the alias
{completions_str.replace('pixi', 'pr')}
"""


def setup_completions():
    """Setup tab completion for the current user"""
    tasks = get_pixi_tasks()
    if not tasks:
        print("No pixi tasks found. Make sure pixi is installed and configured.")
        return False

    print(f"Found {len(tasks)} pixi tasks: {', '.join(tasks[:5])}{'...' if len(tasks) > 5 else ''}")

    # Create completion scripts directory
    completion_dir = Path.home() / ".config" / "my_finance" / "completions"
    completion_dir.mkdir(parents=True, exist_ok=True)

    # Generate completion scripts
    scripts = {
        "pixi_completion.bash": generate_bash_completion(tasks),
        "pixi_completion.zsh": generate_zsh_completion(tasks),
        "pixi_completion.fish": generate_fish_completion(tasks),
    }

    for filename, content in scripts.items():
        script_path = completion_dir / filename
        with open(script_path, "w") as f:
            f.write(content)
        script_path.chmod(0o755)
        print(f"✅ Generated: {script_path}")

    # Generate installation instructions
    instructions_path = completion_dir / "INSTALL_INSTRUCTIONS.md"
    instructions = f"""# Tab Completion Installation Instructions

Your pixi tab completion scripts have been generated in: `{completion_dir}`

## For Bash Users

Add this line to your ~/.bashrc:
```bash
source {completion_dir}/pixi_completion.bash
```

## For Zsh Users

Add this line to your ~/.zshrc:
```zsh
source {completion_dir}/pixi_completion.zsh
```

## For Fish Users

Copy the fish completion script:
```bash
mkdir -p ~/.config/fish/completions
cp {completion_dir}/pixi_completion.fish ~/.config/fish/completions/pixi.fish
```

## Usage

After sourcing the appropriate script and restarting your shell:

- `pixi run <TAB>` - Complete task names
- `pr <TAB>` - Complete task names (alias for pixi run)

## Available Tasks ({len(tasks)} total)

{chr(10).join(f'- {task}' for task in tasks)}

## Updating Completions

Run this script again to regenerate completions when new tasks are added:
```bash
python scripts/setup_tab_completion.py
```
"""

    with open(instructions_path, "w") as f:
        f.write(instructions)

    print(f"✅ Instructions: {instructions_path}")
    print("\n🎉 Tab completion setup complete!")
    print(f"📖 See {instructions_path} for installation instructions")

    return True


if __name__ == "__main__":
    success = setup_completions()
    sys.exit(0 if success else 1)
