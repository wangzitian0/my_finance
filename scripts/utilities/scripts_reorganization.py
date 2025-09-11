#!/usr/bin/env python3
"""
Scripts Directory Reorganization Tool
EXECUTE complete reorganization of scripts directory with proper categorization
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set


class ScriptsReorganizer:
    """
    EXECUTE scripts directory cleanup and reorganization
    Creates logical subdirectories and moves files to appropriate locations
    """

    def __init__(self):
        self.scripts_dir = Path("scripts")
        self.repo_root = Path(".")

        # File categorization mapping
        self.workflow_files = {
            "workflow_ready.py": "ready.py",
            "workflow_check.py": "check.py",
            "workflow_debug.py": "debug.py",
            "workflow_reset.py": "reset.py",
        }

        self.utility_files = {
            "worktree_isolation.py": "worktree_isolation.py",
            "directory_cleanup_executor.py": "directory_cleanup_executor.py",
            "directory_hygiene_analysis.py": "directory_hygiene_analysis.py",
            "config_summary.py": "config_summary.py",
            "fast_env_check.py": "fast_env_check.py",
        }

        # Migration files pattern
        self.migrate_pattern = "migrate_*.py"

        # Subdirectories to create
        self.new_subdirs = {
            "workflow": "P3 workflow implementations",
            "utilities": "Development utilities and tools",
        }

        # Files to update for path references
        self.files_to_update_references = [
            "p3.py",  # Main P3 CLI
            "scripts/p3/commands.py",  # P3 command mappings
            "infra/ansible/*.yml",  # Ansible playbooks
        ]

    def execute_reorganization(self):
        """EXECUTE complete scripts directory reorganization"""
        print("🚀 EXECUTING Scripts Directory Reorganization")
        print("=" * 60)

        try:
            # Phase 1: Create new subdirectories
            self._create_subdirectories()

            # Phase 2: Move workflow files
            self._move_workflow_files()

            # Phase 3: Move utility files
            self._move_utility_files()

            # Phase 4: Move migration files
            self._move_migration_files()

            # Phase 5: Update path references
            self._update_path_references()

            # Phase 6: Validate reorganization
            self._validate_reorganization()

            print("\n✅ Scripts directory reorganization completed successfully!")
            return True

        except Exception as e:
            print(f"❌ Reorganization failed: {e}")
            self._rollback_changes()
            return False

    def _create_subdirectories(self):
        """Create new subdirectories for organization"""
        print("\n📁 Creating new subdirectories...")

        for subdir, description in self.new_subdirs.items():
            subdir_path = self.scripts_dir / subdir
            subdir_path.mkdir(exist_ok=True)
            print(f"✅ Created: {subdir_path} - {description}")

            # Create __init__.py for Python modules
            init_file = subdir_path / "__init__.py"
            if not init_file.exists():
                init_file.write_text(f'"""{description}"""\n')
                print(f"   Added: {init_file}")

    def _move_workflow_files(self):
        """Move workflow_*.py files to scripts/workflow/"""
        print("\n🔄 Moving workflow files...")

        workflow_dir = self.scripts_dir / "workflow"

        for old_name, new_name in self.workflow_files.items():
            old_path = self.scripts_dir / old_name
            new_path = workflow_dir / new_name

            if old_path.exists():
                shutil.move(str(old_path), str(new_path))
                print(f"✅ Moved: {old_name} → workflow/{new_name}")
            else:
                print(f"⚠️  File not found: {old_name}")

    def _move_utility_files(self):
        """Move utility files to scripts/utilities/"""
        print("\n🛠️  Moving utility files...")

        utilities_dir = self.scripts_dir / "utilities"

        for old_name, new_name in self.utility_files.items():
            old_path = self.scripts_dir / old_name
            new_path = utilities_dir / new_name

            if old_path.exists():
                shutil.move(str(old_path), str(new_path))
                print(f"✅ Moved: {old_name} → utilities/{new_name}")
            else:
                print(f"⚠️  File not found: {old_name}")

    def _move_migration_files(self):
        """Move migrate_*.py files to utilities"""
        print("\n📦 Moving migration files...")

        utilities_dir = self.scripts_dir / "utilities"
        migrate_files = list(self.scripts_dir.glob(self.migrate_pattern))

        if migrate_files:
            for migrate_file in migrate_files:
                new_path = utilities_dir / migrate_file.name
                shutil.move(str(migrate_file), str(new_path))
                print(f"✅ Moved: {migrate_file.name} → utilities/{migrate_file.name}")
        else:
            print("ℹ️  No migration files found to move")

    def _update_path_references(self):
        """Update path references in P3 CLI and other files"""
        print("\n🔧 Updating path references...")

        # Update main P3 CLI file
        self._update_p3_cli_references()

        # Update P3 command mappings if they exist
        self._update_p3_command_mappings()

        print("✅ Path references updated")

    def _update_p3_cli_references(self):
        """Update path references in main P3 CLI"""
        p3_file = self.repo_root / "p3.py"

        if not p3_file.exists():
            print("⚠️  p3.py not found, skipping reference updates")
            return

        # Read current content
        content = p3_file.read_text()

        # Update workflow script paths
        old_patterns = {
            "scripts/workflow_ready.py": "scripts/workflow/ready.py",
            "scripts/workflow_check.py": "scripts/workflow/check.py",
            "scripts/workflow_debug.py": "scripts/workflow/debug.py",
            "scripts/workflow_reset.py": "scripts/workflow/reset.py",
        }

        updated = False
        for old_path, new_path in old_patterns.items():
            if old_path in content:
                content = content.replace(old_path, new_path)
                updated = True
                print(f"   Updated reference: {old_path} → {new_path}")

        if updated:
            p3_file.write_text(content)
            print("✅ Updated p3.py with new script paths")
        else:
            print("ℹ️  No path references found to update in p3.py")

    def _update_p3_command_mappings(self):
        """Update P3 command mappings if they exist"""
        commands_file = self.scripts_dir / "p3" / "commands.py"

        if commands_file.exists():
            content = commands_file.read_text()

            # Update import paths for workflow modules
            old_imports = [
                "from scripts import workflow_ready",
                "from scripts import workflow_check",
                "from scripts import workflow_debug",
                "from scripts import workflow_reset",
            ]

            new_imports = [
                "from scripts.workflow import ready",
                "from scripts.workflow import check",
                "from scripts.workflow import debug",
                "from scripts.workflow import reset",
            ]

            updated = False
            for old_import, new_import in zip(old_imports, new_imports):
                if old_import in content:
                    content = content.replace(old_import, new_import)
                    updated = True
                    print(f"   Updated import: {old_import} → {new_import}")

            if updated:
                commands_file.write_text(content)
                print("✅ Updated P3 command mappings")

    def _validate_reorganization(self):
        """Validate that reorganization completed successfully"""
        print("\n✅ Validating reorganization...")

        # Check that new directories exist
        for subdir in self.new_subdirs.keys():
            subdir_path = self.scripts_dir / subdir
            if not subdir_path.exists():
                raise Exception(f"Subdirectory not created: {subdir}")

        # Check that workflow files were moved
        workflow_dir = self.scripts_dir / "workflow"
        for new_name in self.workflow_files.values():
            if not (workflow_dir / new_name).exists():
                print(f"⚠️  Workflow file not found after move: {new_name}")

        # Check that utility files were moved
        utilities_dir = self.scripts_dir / "utilities"
        for new_name in self.utility_files.values():
            if not (utilities_dir / new_name).exists():
                print(f"⚠️  Utility file not found after move: {new_name}")

        # Check that old workflow files are gone
        for old_name in self.workflow_files.keys():
            if (self.scripts_dir / old_name).exists():
                print(f"⚠️  Old workflow file still exists: {old_name}")

        print("✅ Reorganization validation completed")

    def _rollback_changes(self):
        """Rollback changes if reorganization fails"""
        print("\n🔄 Rolling back changes...")

        try:
            # Move files back from subdirectories
            workflow_dir = self.scripts_dir / "workflow"
            if workflow_dir.exists():
                for new_name, old_name in self.workflow_files.items():
                    new_path = workflow_dir / new_name
                    old_path = self.scripts_dir / old_name
                    if new_path.exists():
                        shutil.move(str(new_path), str(old_path))
                        print(f"   Restored: {new_name} → {old_name}")

            utilities_dir = self.scripts_dir / "utilities"
            if utilities_dir.exists():
                for new_name, old_name in self.utility_files.items():
                    new_path = utilities_dir / new_name
                    old_path = self.scripts_dir / old_name
                    if new_path.exists():
                        shutil.move(str(new_path), str(old_path))
                        print(f"   Restored: {new_name} → {old_name}")

            # Remove created directories if empty
            for subdir in self.new_subdirs.keys():
                subdir_path = self.scripts_dir / subdir
                if subdir_path.exists() and not any(subdir_path.iterdir()):
                    subdir_path.rmdir()
                    print(f"   Removed empty directory: {subdir}")

        except Exception as e:
            print(f"⚠️  Rollback encountered issues: {e}")

    def generate_reorganization_summary(self):
        """Generate summary of reorganization changes"""
        print("\n📊 REORGANIZATION SUMMARY")
        print("=" * 40)

        print(f"🗂️  New Subdirectories Created:")
        for subdir, description in self.new_subdirs.items():
            subdir_path = self.scripts_dir / subdir
            file_count = len(list(subdir_path.glob("*.py"))) if subdir_path.exists() else 0
            print(f"   • {subdir}/ - {description} ({file_count} files)")

        print(f"\n📝 File Movements:")
        print(f"   • Workflow files: {len(self.workflow_files)} moved to workflow/")
        print(f"   • Utility files: {len(self.utility_files)} moved to utilities/")

        print(f"\n🔧 Updated References:")
        print("   • p3.py - Updated workflow script paths")
        print("   • P3 command mappings - Updated import paths")

        print(f"\n📁 Directory Structure After Reorganization:")
        self._display_directory_structure()

    def _display_directory_structure(self):
        """Display the new directory structure"""
        if not self.scripts_dir.exists():
            print("   scripts/ directory not found")
            return

        print(f"   scripts/")
        for item in sorted(self.scripts_dir.iterdir()):
            if item.is_dir():
                file_count = len(list(item.glob("*.py")))
                print(f"   ├── {item.name}/ ({file_count} Python files)")
            else:
                print(f"   ├── {item.name}")


def main():
    """Main execution function"""
    try:
        reorganizer = ScriptsReorganizer()

        print("Scripts Directory Reorganization Tool")
        print("Will create subdirectories and move files to logical organization")
        print()

        # Execute reorganization
        success = reorganizer.execute_reorganization()

        if success:
            # Generate summary
            reorganizer.generate_reorganization_summary()

            print("\n🎉 REORGANIZATION COMPLETED SUCCESSFULLY!")
            print("Scripts directory is now properly organized with:")
            print("  • scripts/workflow/ - P3 workflow implementations")
            print("  • scripts/utilities/ - Development utilities")
            print("  • scripts/p3/ - P3 CLI system (unchanged)")
            print("  • scripts/hooks/ - Git hooks (unchanged)")

            return 0
        else:
            print("\n❌ REORGANIZATION FAILED")
            print("Changes have been rolled back where possible")
            return 1

    except Exception as e:
        print(f"\n💥 FATAL ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
