#!/usr/bin/env python3
"""
Directory consolidation script for Issue #256
Implements the DRY principle by merging related functionality
"""
import os
import shutil
from pathlib import Path


def consolidate_directories():
    """Execute the directory consolidation plan"""
    root = Path(".")

    print("PHASE 1: Merge Small Modules into Existing Larger Ones")
    print("=" * 60)

    # Check current state
    existing_dirs = [d for d in root.iterdir() if d.is_dir() and not d.name.startswith(".")]
    print(f"Current directories: {[d.name for d in existing_dirs]}")

    # 1. Move graph_rag/ → ETL/graph_rag/ (both are data processing)
    if (root / "graph_rag").exists():
        target = root / "ETL" / "graph_rag"
        target.parent.mkdir(exist_ok=True)
        print(f"Moving graph_rag/ → ETL/graph_rag/")
        if not target.exists():
            shutil.move(str(root / "graph_rag"), str(target))
            # Add __init__.py if not exists
            init_file = target / "__init__.py"
            if not init_file.exists():
                init_file.write_text('"""Graph RAG data processing module"""\n')
        else:
            print(f"  WARNING: {target} already exists, skipping")

    # 2. Move evaluation/ → dcf_engine/evaluation/ (both are analysis)
    if (root / "evaluation").exists():
        target = root / "dcf_engine" / "evaluation"
        target.parent.mkdir(exist_ok=True)
        print(f"Moving evaluation/ → dcf_engine/evaluation/")
        if not target.exists():
            shutil.move(str(root / "evaluation"), str(target))
            # Add __init__.py if not exists
            init_file = target / "__init__.py"
            if not init_file.exists():
                init_file.write_text('"""Evaluation and backtesting module"""\n')
        else:
            print(f"  WARNING: {target} already exists, skipping")

    # 3. Move dts/ → common/types/ (type definitions belong in common)
    if (root / "dts").exists():
        target = root / "common" / "types"
        target.parent.mkdir(exist_ok=True)
        print(f"Moving dts/ → common/types/")
        if not target.exists():
            shutil.move(str(root / "dts"), str(target))
            # Add __init__.py if not exists
            init_file = target / "__init__.py"
            if not init_file.exists():
                init_file.write_text('"""Type definitions and schemas"""\n')
        else:
            print(f"  WARNING: {target} already exists, skipping")

    # 4. Move templates/ → common/templates/ (shared resources)
    if (root / "templates").exists():
        target = root / "common" / "templates"
        target.parent.mkdir(exist_ok=True)
        print(f"Moving templates/ → common/templates/")
        if not target.exists():
            shutil.move(str(root / "templates"), str(target))
            # Add __init__.py if not exists
            init_file = target / "__init__.py"
            if not init_file.exists():
                init_file.write_text('"""Template resources and configurations"""\n')
        else:
            print(f"  WARNING: {target} already exists, skipping")

    # 5. Check if agents/ needs to be moved to common/agents/ (if not already there)
    if (root / "agents").exists() and not (root / "common" / "agents").exists():
        target = root / "common" / "agents"
        target.parent.mkdir(exist_ok=True)
        print(f"Moving agents/ → common/agents/")
        shutil.move(str(root / "agents"), str(target))
        # Add __init__.py if not exists
        init_file = target / "__init__.py"
        if not init_file.exists():
            init_file.write_text('"""Agent definitions and configurations"""\n')

    print("\nPHASE 2: Consolidate Scripts and Tools")
    print("=" * 60)

    # 1. Move scripts/ → infra/scripts/ (infrastructure tools)
    if (root / "scripts").exists():
        target = root / "infra" / "scripts"
        target.parent.mkdir(exist_ok=True)
        print(f"Moving scripts/ → infra/scripts/")
        if not target.exists():
            shutil.move(str(root / "scripts"), str(target))
            # Add __init__.py if not exists
            init_file = target / "__init__.py"
            if not init_file.exists():
                init_file.write_text('"""Infrastructure scripts and utilities"""\n')
        else:
            print(f"  WARNING: {target} already exists, skipping")

    # 2. Consolidate docs/ and releases/ → docs/ (single documentation location)
    if (root / "releases").exists():
        docs_dir = root / "docs"
        docs_dir.mkdir(exist_ok=True)
        releases_target = docs_dir / "releases"
        print(f"Moving releases/ → docs/releases/")
        if not releases_target.exists():
            shutil.move(str(root / "releases"), str(releases_target))
        else:
            print(f"  WARNING: {releases_target} already exists, skipping")

    print("\nPHASE 3: Rename for Clarity")
    print("=" * 60)

    # 1. Rename dcf_engine/ → analysis/ (more general, contains dcf + evaluation)
    if (root / "dcf_engine").exists() and not (root / "analysis").exists():
        print(f"Renaming dcf_engine/ → analysis/")
        shutil.move(str(root / "dcf_engine"), str(root / "analysis"))
        # Update __init__.py
        init_file = root / "analysis" / "__init__.py"
        if init_file.exists():
            content = init_file.read_text()
            updated_content = content.replace("DCF Engine", "Analysis Engine")
            updated_content = updated_content.replace("dcf_engine", "analysis")
            init_file.write_text(updated_content)

    print("\nPHASE 4: Ensure All Directories are Python Modules")
    print("=" * 60)

    # Add __init__.py to all directories that need to be modules
    module_dirs = [
        "ETL",
        "analysis",
        "common",
        "infra",
        "tests",
        "ETL/embedding_generator",
        "ETL/sec_filing_processor",
        "analysis/components",
        "common/config",
        "common/monitoring",
        "common/tools",
    ]

    for module_dir in module_dirs:
        dir_path = root / module_dir
        if dir_path.exists() and dir_path.is_dir():
            init_file = dir_path / "__init__.py"
            if not init_file.exists():
                print(f"Adding __init__.py to {module_dir}")
                # Create appropriate docstring based on directory name
                if "ETL" in module_dir:
                    docstring = f'"""ETL data processing module: {module_dir}"""'
                elif "analysis" in module_dir:
                    docstring = f'"""Analysis and evaluation module: {module_dir}"""'
                elif "common" in module_dir:
                    docstring = f'"""Common utilities module: {module_dir}"""'
                elif "infra" in module_dir:
                    docstring = f'"""Infrastructure module: {module_dir}"""'
                else:
                    docstring = f'"""Module: {module_dir}"""'

                init_file.write_text(docstring + "\n")

    print("\nCONSOLIDATION COMPLETE!")
    print("=" * 60)

    # Show final structure
    final_dirs = [d for d in root.iterdir() if d.is_dir() and not d.name.startswith(".")]
    print(f"Final L1 directories: {[d.name for d in sorted(final_dirs, key=lambda x: x.name)]}")
    print(f"Total directories reduced to: {len(final_dirs)}")


if __name__ == "__main__":
    consolidate_directories()
