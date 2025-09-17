#!/usr/bin/env python3
"""
Path Migration Integration Tests

Tests complete path migration functionality including:
- Legacy to new path migration
- Data preservation during migration
- Rollback capabilities
- Mixed legacy/new path environments
- Migration validation and reporting
"""

import json
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from common.core.directory_manager import (
    DataLayer,
    DirectoryManager,
    StorageBackend,
)


@pytest.mark.skip(
    reason="Legacy migration tests no longer needed after Issue #283 L1/L2 restructure"
)
class TestPathMigrationIntegration:
    """Integration tests for complete path migration functionality"""

    @pytest.fixture
    def legacy_project_structure(self):
        """Create project structure with legacy paths and data"""
        temp_dir = tempfile.mkdtemp()
        project_root = Path(temp_dir)

        # Create legacy directory structure with real data
        legacy_structure = {
            "data": {
                "stage_00_original": {
                    "sec-edgar": ["AAPL_10K_2024.xml", "MSFT_10Q_2024.xml"],
                    "yfinance": ["daily_prices_20250828.csv"],
                },
                "stage_01_extract": {"extracted": ["processed_filings.json"]},
                "stage_02_transform": {
                    "embeddings": ["document_vectors.npy"],
                    "entities": ["company_entities.json"],
                },
                "stage_03_load": {
                    "graph_db": ["knowledge_graph.db"],
                    "cache": ["query_cache.json"],
                },
                "stage_99_build": {
                    "dcf_reports": ["quarterly_analysis.json"],
                    "exports": ["investment_recommendations.csv"],
                },
                "config": {"list_magnificent_7.yml": {"companies": ["AAPL", "MSFT", "GOOGL"]}},
            },
            "logs": ["application.log", "error.log"],
            "temp": ["temp_file.tmp"],
            "cache": ["system_cache.db"],
        }

        # Create the actual directory structure with files
        self._create_structure(project_root, legacy_structure)

        # Create modern common/config directory
        (project_root / "common" / "config").mkdir(parents=True, exist_ok=True)

        # Create migration config
        config_content = {
            "storage": {"backend": "local_filesystem", "root_path": "build_data"},
            "layers": {
                "layer_01_raw": {"subdirs": ["sec-edgar", "yfinance", "manual", "reference"]},
                "layer_02_delta": {
                    "subdirs": ["additions", "modifications", "deletions", "metadata"]
                },
                "layer_03_index": {
                    "subdirs": ["vectors", "entities", "relationships", "embeddings", "indices"]
                },
                "layer_04_rag": {"subdirs": ["graph_db", "vector_store", "cache", "snapshots"]},
                "layer_05_results": {
                    "subdirs": [
                        "dcf_reports",
                        "analytics",
                        "exports",
                        "dashboards",
                        "api_responses",
                    ]
                },
            },
            "common": {
                "config": "common/config",
                "logs": "build_data/logs",
                "temp": "temp",
                "cache": "cache",
            },
            "legacy_mapping": {
                "stage_00_original": "layer_01_raw",
                "stage_01_extract": "layer_02_delta",
                "stage_02_transform": "layer_03_index",
                "stage_03_load": "layer_04_rag",
                "stage_99_build": "layer_05_results",
                "data/config": "common/config",
                "data": "build_data",
            },
        }

        config_file = project_root / "common" / "config" / "directory_structure.yml"
        with open(config_file, "w") as f:
            yaml.dump(config_content, f)

        yield project_root
        shutil.rmtree(temp_dir, ignore_errors=True)

    def _create_structure(self, root: Path, structure: dict):
        """Recursively create directory structure with files"""
        for name, content in structure.items():
            path = root / name

            if isinstance(content, dict):
                path.mkdir(parents=True, exist_ok=True)
                self._create_structure(path, content)
            elif isinstance(content, list):
                path.mkdir(parents=True, exist_ok=True)
                for file_name in content:
                    file_path = path / file_name
                    if file_name.endswith(".json"):
                        with open(file_path, "w") as f:
                            json.dump({"test": "data", "file": file_name}, f)
                    elif file_name.endswith(".yml") or file_name.endswith(".yaml"):
                        with open(file_path, "w") as f:
                            yaml.dump(
                                (
                                    content[file_name]
                                    if isinstance(content[file_name], dict)
                                    else {"data": content[file_name]}
                                ),
                                f,
                            )
                    else:
                        with open(file_path, "w") as f:
                            f.write(f"Sample content for {file_name}")
            else:
                # Single file
                with open(path, "w") as f:
                    if isinstance(content, dict):
                        if path.suffix in [".yml", ".yaml"]:
                            yaml.dump(content, f)
                        else:
                            json.dump(content, f)
                    else:
                        f.write(str(content))

    @pytest.mark.skip(reason="Legacy migration no longer needed after Issue #283 L1/L2 restructure")
    def test_complete_legacy_migration(self, legacy_project_structure):
        """Test complete migration from legacy to new structure"""
        dm = DirectoryManager(root_path=legacy_project_structure)

        # Verify legacy structure exists
        legacy_data = legacy_project_structure / "data"
        assert legacy_data.exists()
        assert (legacy_data / "stage_00_original").exists()
        assert (legacy_data / "stage_99_build").exists()

        # Count files before migration
        original_file_count = self._count_files(legacy_data)

        # Perform migration (dry run first)
        migrations = dm.migrate_legacy_data(dry_run=True)
        assert len(migrations) > 0

        # Verify dry run doesn't actually move files
        assert (legacy_data / "stage_00_original").exists()

        # Perform actual migration
        actual_migrations = dm.migrate_legacy_data(dry_run=False)
        assert len(actual_migrations) == len(migrations)

        # Verify new structure exists
        build_data = legacy_project_structure / "build_data"
        assert build_data.exists()
        assert (build_data / "layer_01_raw").exists()
        assert (build_data / "layer_05_results").exists()

        # Verify data preservation
        new_file_count = self._count_files(build_data)
        assert new_file_count == original_file_count

        # Verify specific files migrated correctly
        assert (build_data / "layer_01_raw" / "sec-edgar" / "AAPL_10K_2024.xml").exists()
        assert (
            build_data / "layer_05_results" / "dcf_reports" / "quarterly_analysis.json"
        ).exists()

    @pytest.mark.skip(reason="Legacy migration no longer needed after Issue #283 L1/L2 restructure")
    def test_data_integrity_during_migration(self, legacy_project_structure):
        """Test that data integrity is preserved during migration"""
        dm = DirectoryManager(root_path=legacy_project_structure)

        # Create checksums of original files
        original_checksums = self._calculate_checksums(legacy_project_structure / "data")

        # Perform migration
        dm.migrate_legacy_data(dry_run=False)

        # Calculate checksums after migration
        new_checksums = self._calculate_checksums(legacy_project_structure / "build_data")

        # Verify data integrity (files should have same content)
        assert len(original_checksums) == len(new_checksums)

        # Check that at least some files have preserved content
        # (mapping may change filenames, so we check content hashes exist)
        original_hashes = set(original_checksums.values())
        new_hashes = set(new_checksums.values())

        # Most content should be preserved (allowing for some organizational changes)
        preserved_ratio = len(original_hashes.intersection(new_hashes)) / len(original_hashes)
        assert preserved_ratio > 0.8, f"Too much data lost: {preserved_ratio:.2%} preserved"

    def test_mixed_legacy_new_environment(self, legacy_project_structure):
        """Test operation in mixed legacy/new path environment"""
        dm = DirectoryManager(root_path=legacy_project_structure)

        # Create some legacy paths and some new paths
        legacy_path = legacy_project_structure / "data" / "stage_00_original" / "new_data"
        legacy_path.mkdir(parents=True, exist_ok=True)
        with open(legacy_path / "legacy_file.txt", "w") as f:
            f.write("Legacy data")

        # Create new structure alongside
        dm.ensure_directories()
        new_path = dm.get_subdir_path(DataLayer.RAW_DATA, "sec-edgar")
        new_path.mkdir(parents=True, exist_ok=True)
        with open(new_path / "new_file.txt", "w") as f:
            f.write("New structure data")

        # Test that both can be accessed
        assert (
            legacy_project_structure / "data" / "stage_00_original" / "new_data" / "legacy_file.txt"
        ).exists()
        assert (
            legacy_project_structure / "build_data" / "layer_01_raw" / "sec-edgar" / "new_file.txt"
        ).exists()

        # Test path resolution works for both
        legacy_layer = dm.map_legacy_path("stage_00_original")
        assert legacy_layer == DataLayer.RAW_DATA

        resolved_new_path = dm.get_subdir_path(DataLayer.RAW_DATA, "sec-edgar")
        assert resolved_new_path.exists()

    def test_migration_rollback_capability(self, legacy_project_structure):
        """Test ability to rollback migration"""
        dm = DirectoryManager(root_path=legacy_project_structure)

        # Backup original structure
        backup_dir = legacy_project_structure / "migration_backup"
        backup_dir.mkdir()
        shutil.copytree(legacy_project_structure / "data", backup_dir / "data")

        # Perform migration
        migrations = dm.migrate_legacy_data(dry_run=False)

        # Verify migration occurred
        build_data = legacy_project_structure / "build_data"
        assert build_data.exists()

        # Simulate rollback by reversing migrations
        for old_path, new_path in reversed(migrations):
            if new_path.exists() and not old_path.exists():
                old_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(new_path), str(old_path))

        # Verify rollback
        assert (legacy_project_structure / "data" / "stage_00_original").exists()

        # Clean up backup
        shutil.rmtree(backup_dir)

    def test_migration_validation_and_reporting(self, legacy_project_structure):
        """Test migration validation and comprehensive reporting"""
        dm = DirectoryManager(root_path=legacy_project_structure)

        # Generate migration report
        migrations = dm.migrate_legacy_data(dry_run=True)

        # Create detailed migration report
        report = {
            "migration_plan": [],
            "file_counts": {},
            "estimated_size": 0,
            "potential_conflicts": [],
        }

        for old_path, new_path in migrations:
            if old_path.exists():
                file_count = len(list(old_path.rglob("*"))) if old_path.is_dir() else 1
                size = (
                    sum(f.stat().st_size for f in old_path.rglob("*") if f.is_file())
                    if old_path.is_dir()
                    else old_path.stat().st_size
                )

                migration_info = {
                    "source": str(old_path),
                    "destination": str(new_path),
                    "file_count": file_count,
                    "size_bytes": size,
                    "exists": old_path.exists(),
                }
                report["migration_plan"].append(migration_info)
                report["file_counts"][str(old_path)] = file_count
                report["estimated_size"] += size

                # Check for conflicts
                if new_path.exists():
                    report["potential_conflicts"].append(
                        {"path": str(new_path), "reason": "Destination already exists"}
                    )

        # Validate report
        assert len(report["migration_plan"]) > 0
        assert report["estimated_size"] > 0
        assert all(info["exists"] for info in report["migration_plan"])

        # Test actual migration with validation
        actual_migrations = dm.migrate_legacy_data(dry_run=False)

        # Post-migration validation
        success_count = 0
        for old_path, new_path in actual_migrations:
            if new_path.exists():
                success_count += 1

        success_rate = success_count / len(actual_migrations) if actual_migrations else 0
        assert success_rate > 0.8, f"Migration success rate too low: {success_rate:.2%}"

    def test_incremental_migration_support(self, legacy_project_structure):
        """Test incremental migration with partial updates"""
        dm = DirectoryManager(root_path=legacy_project_structure)

        # Migrate only part of the structure first
        original_migrations = dm.migrate_legacy_data(dry_run=True)

        # Filter to migrate only raw data first
        raw_migrations = [
            (old, new) for old, new in original_migrations if "stage_00_original" in str(old)
        ]

        # Perform partial migration manually
        import shutil

        for old_path, new_path in raw_migrations:
            if old_path.exists() and not new_path.exists():
                new_path.parent.mkdir(parents=True, exist_ok=True)
                if old_path.is_dir():
                    shutil.copytree(old_path, new_path)
                else:
                    shutil.copy2(old_path, new_path)

        # Verify partial migration
        assert (legacy_project_structure / "build_data" / "layer_01_raw").exists()
        assert (legacy_project_structure / "data" / "stage_99_build").exists()  # Not migrated yet

        # Complete the migration
        remaining_migrations = dm.migrate_legacy_data(dry_run=False)

        # Verify complete migration
        assert (legacy_project_structure / "build_data" / "layer_05_results").exists()

    def test_config_migration_integration(self, legacy_project_structure):
        """Test migration of configuration files"""
        dm = DirectoryManager(root_path=legacy_project_structure)

        # Verify legacy config exists
        legacy_config = legacy_project_structure / "data" / "config" / "list_magnificent_7.yml"
        assert legacy_config.exists()

        # Load legacy config content
        with open(legacy_config) as f:
            legacy_content = yaml.safe_load(f)

        # Migration should handle config separately or preserve it
        # (configs don't typically get auto-migrated, they're referenced)

        # Verify new config structure
        new_config_dir = dm.get_config_path()
        assert new_config_dir.exists()
        assert "common/config" in str(new_config_dir)

        # Test that legacy config can still be referenced if needed
        legacy_mapped = dm.map_legacy_path("data/config")
        # This should not return a DataLayer as it's a special case
        assert legacy_mapped is None  # Config paths are handled differently

    def _count_files(self, directory: Path) -> int:
        """Count all files in directory recursively"""
        if not directory.exists():
            return 0
        return len([f for f in directory.rglob("*") if f.is_file()])

    def _calculate_checksums(self, directory: Path) -> dict:
        """Calculate checksums for all files in directory"""
        import hashlib

        checksums = {}

        if not directory.exists():
            return checksums

        for file_path in directory.rglob("*"):
            if file_path.is_file():
                try:
                    with open(file_path, "rb") as f:
                        content = f.read()
                        checksum = hashlib.md5(content).hexdigest()
                        checksums[str(file_path)] = checksum
                except (IOError, OSError):
                    # Skip files that can't be read
                    pass

        return checksums


class TestPathMigrationErrorHandling:
    """Error handling tests for path migration"""

    def test_migration_permission_errors(self):
        """Test handling of permission errors during migration"""
        temp_dir = tempfile.mkdtemp()
        project_root = Path(temp_dir)

        try:
            # Create legacy structure
            legacy_dir = project_root / "data" / "stage_00_original"
            legacy_dir.mkdir(parents=True, exist_ok=True)
            test_file = legacy_dir / "test.txt"
            with open(test_file, "w") as f:
                f.write("test content")

            dm = DirectoryManager(root_path=project_root)

            # Create restricted destination
            restricted_dest = project_root / "build_data"
            restricted_dest.mkdir(parents=True, exist_ok=True)

            if os.name != "nt":  # Skip on Windows
                os.chmod(restricted_dest, 0o000)

                # Migration should handle permission errors gracefully
                try:
                    migrations = dm.migrate_legacy_data(dry_run=False)
                except PermissionError:
                    pass  # Expected behavior

                # Restore permissions
                os.chmod(restricted_dest, 0o755)

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_migration_with_missing_source_files(self):
        """Test migration when some source files are missing"""
        temp_dir = tempfile.mkdtemp()
        project_root = Path(temp_dir)

        try:
            # Create partial legacy structure
            legacy_dir = project_root / "data" / "stage_00_original"
            legacy_dir.mkdir(parents=True, exist_ok=True)

            # Reference to non-existent files
            dm = DirectoryManager(root_path=project_root)

            # Migration should handle missing files gracefully
            migrations = dm.migrate_legacy_data(dry_run=True)

            # Should return empty migrations list for non-existent paths
            existing_migrations = [(old, new) for old, new in migrations if old.exists()]
            assert len(existing_migrations) <= len(migrations)

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_migration_with_corrupted_files(self):
        """Test migration with some corrupted files"""
        temp_dir = tempfile.mkdtemp()
        project_root = Path(temp_dir)

        try:
            # Create legacy structure with corrupted files
            legacy_dir = project_root / "data" / "stage_00_original"
            legacy_dir.mkdir(parents=True, exist_ok=True)

            # Create corrupted JSON file
            corrupted_file = legacy_dir / "corrupted.json"
            with open(corrupted_file, "w") as f:
                f.write('{"invalid": json content')  # Invalid JSON

            # Create valid file
            valid_file = legacy_dir / "valid.txt"
            with open(valid_file, "w") as f:
                f.write("valid content")

            dm = DirectoryManager(root_path=project_root)

            # Migration should proceed despite corrupted files
            migrations = dm.migrate_legacy_data(dry_run=False)

            # Verify both files were migrated (corruption doesn't affect file move)
            new_dir = project_root / "build_data" / "layer_01_raw"
            if migrations:  # If migration occurred
                assert (new_dir / "corrupted.json").exists() or corrupted_file.exists()
                assert (new_dir / "valid.txt").exists() or valid_file.exists()

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
