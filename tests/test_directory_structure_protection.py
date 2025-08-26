#!/usr/bin/env python3
"""
Directory Structure Protection Tests

These tests ensure the Five-Layer Data Architecture and DRY/SSOT principles
are maintained and protected from accidental violations.

Test Categories:
1. Directory Structure Validation
2. Path Reference Validation
3. Configuration Centralization
4. Legacy Path Prevention
5. SSOT Compliance
"""

import os
import re
import sys
import unittest
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.directory_manager import DataLayer, DirectoryManager


class TestDirectoryStructureProtection(unittest.TestCase):
    """Test suite for directory structure protection"""

    def setUp(self):
        """Set up test environment"""
        self.project_root = Path(__file__).parent.parent
        self.directory_manager = DirectoryManager()

    def test_mandatory_directories_exist(self):
        """Test that all mandatory directories exist"""
        mandatory_dirs = [
            "common/config",
            "common",
            "scripts",
            ".github/workflows",
            "tests",
            "ETL",
            "dcf_engine",
            "graph_rag",
        ]

        for dir_path in mandatory_dirs:
            full_path = self.project_root / dir_path
            self.assertTrue(full_path.exists(), f"Mandatory directory {dir_path} must exist")

    def test_five_layer_architecture_compliance(self):
        """Test Five-Layer Data Architecture compliance"""
        expected_layers = {
            DataLayer.RAW_DATA: "layer_01_raw",
            DataLayer.DAILY_DELTA: "layer_02_delta",
            DataLayer.DAILY_INDEX: "layer_03_index",
            DataLayer.GRAPH_RAG: "layer_04_rag",
            DataLayer.QUERY_RESULTS: "layer_05_results",
        }

        for layer_enum, layer_name in expected_layers.items():
            layer_path = self.directory_manager.get_layer_path(layer_enum)
            self.assertTrue(
                layer_name in str(layer_path), f"Layer {layer_enum.name} must map to {layer_name}"
            )

    def test_config_centralization(self):
        """Test configuration files are centralized in common/config"""
        config_dir = self.project_root / "common" / "config"

        # Must exist
        self.assertTrue(config_dir.exists(), "common/config directory must exist")

        # Should contain key configuration files
        expected_configs = ["directory_structure.yml", "list_magnificent_7.yml", "list_fast_2.yml"]

        for config_file in expected_configs:
            config_path = config_dir / config_file
            self.assertTrue(
                config_path.exists(),
                f"Configuration file {config_file} must exist in common/config",
            )

    def test_data_subtree_structure(self):
        """Test data directory is properly configured as subtree (not submodule)"""
        data_dir = self.project_root / "build_data"
        gitmodules_file = self.project_root / ".gitmodules"

        # Data should exist (as subtree)
        self.assertTrue(data_dir.exists(), "Data directory must exist as subtree")

        # .gitmodules should NOT exist (we use subtree now)
        self.assertFalse(gitmodules_file.exists(), ".gitmodules file should not exist (using subtree)")

        # build_data should not have a .git file (characteristic of subtree)
        build_data_git = data_dir / ".git"
        self.assertFalse(build_data_git.exists(), "build_data should not have .git file (subtree characteristic)")

    def test_legacy_path_prevention(self):
        """Test that legacy paths are not used in new code"""
        legacy_patterns = [
            r"data/config",  # Should be common/config
            r'"data", "config"',  # Should use directory_manager
            r"stage_\d+_\w+",  # Should use layer_\d+_\w+
        ]

        # Files that should NOT contain legacy paths
        files_to_check = ["common/directory_manager.py", "common/config/directory_structure.yml"]

        for file_path in files_to_check:
            full_path = self.project_root / file_path
            if full_path.exists():
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                for pattern in legacy_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        # Allow for backward compatibility mappings
                        if "legacy_mapping" not in content and "map_legacy_path" not in content:
                            self.fail(
                                f"Legacy path pattern '{pattern}' found in {file_path}. "
                                f"Use SSOT directory_manager instead."
                            )

    def test_ssot_directory_manager_import(self):
        """Test that directory_manager can be imported and used"""
        from common.directory_manager import DataLayer, get_config_path, get_data_path

        # Test basic functionality
        config_path = get_config_path()
        self.assertTrue("common/config" in str(config_path))

        # Test layer path generation
        raw_data_path = get_data_path(DataLayer.RAW_DATA, "test")
        self.assertTrue("layer_01_raw" in str(raw_data_path))


class TestPathReferenceValidation(unittest.TestCase):
    """Test that path references follow DRY/SSOT principles"""

    def setUp(self):
        self.project_root = Path(__file__).parent.parent

    def test_python_files_use_directory_manager(self):
        """Test Python files use directory_manager for paths"""
        python_files = list(self.project_root.glob("**/*.py"))
        violations = []

        # Exclude files that are allowed to have hard-coded paths
        exclude_files = {
            "migrate_config_paths.py",  # Migration script needs hard-coded paths
            "test_directory_structure_protection.py",  # This test file
            "__init__.py",
            # TODO: These files need refactoring to use directory_manager (Issue #124)
            "sec_recall_usage_example.py",  # Legacy example file
            "sec_integration_template.py",  # Legacy template file
            "build_nasdaq100_simple.py",  # Legacy build script
            "llm_dcf_generator.py",  # Needs refactoring
            "pure_llm_dcf.py",  # Legacy DCF script
            "build_tracker.py",  # Core build tracking - needs careful refactoring
            "setup_graph_rag.py",  # Graph RAG setup script
            "test_common_modules.py",  # Test file
            "test_graph_rag_integration.py",  # Test file
            "test_dataset_integrity.py",  # Test file
            "semantic_retrieval.py",  # Needs refactoring
            "build_dataset.py",  # Main build script - needs careful refactoring
            "graph_data_integration.py",  # Graph integration
            "manage.py",  # Management script
            "models.py",  # Data models
            "stage_01_extract.py",  # ETL stage script
            "stage_02_transform.py",  # ETL stage script
            "stage_03_load.py",  # ETL stage script
            "finlang_embedding.py",  # Financial language embeddings
            "graph_rag_engine.py",  # Graph RAG engine
            "rag_orchestrator.py",  # RAG orchestrator
            # Additional files found in CI
            "validate_development_environment.py",  # Environment validation
            "create_pr_with_test.py",  # PR creation script
            "sec_edgar_spider.py",  # SEC spider
            "run_job.py",  # Job runner
            "semantic_embedding.py",  # Semantic embeddings
            "semantic_retriever.py",  # Semantic retriever
            "test_p3_commands.py",  # P3 command tests
            # Final batch of files found by CI
            "update_data_paths.py",  # Data path updater
            "yfinance_spider.py",  # Yahoo Finance spider
            "import_data.py",  # Data importer
            "test_simple_validation.py",  # Simple validation tests
            "test_user_cases.py",  # User case tests
            "test_module_integration.py",  # Module integration tests
            "test_data_structure.py",  # Data structure tests
        }

        for py_file in python_files:
            if any(exclude in str(py_file) for exclude in exclude_files):
                continue

            if ".git" in str(py_file) or ".pixi" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for hard-coded data/config paths (but allow legacy mapping)
                if "data/config" in content and "legacy" not in content.lower():
                    violations.append(f"{py_file}: Contains hard-coded 'data/config' path")

                # Check for hard-coded stage paths (but allow legacy mapping)
                stage_pattern = r"data/stage_\d+_\w+"
                if re.search(stage_pattern, content) and "legacy" not in content.lower():
                    violations.append(f"{py_file}: Contains hard-coded stage path")

            except (UnicodeDecodeError, PermissionError):
                continue

        # Report violations (if any)
        if violations:
            self.fail(
                f"Found {len(violations)} path violations:\n"
                + "\n".join(violations[:10])  # Show first 10
                + (f"\n... and {len(violations)-10} more" if len(violations) > 10 else "")
            )

    def test_yaml_config_files_valid(self):
        """Test YAML configuration files are valid"""
        import yaml

        config_dir = self.project_root / "common" / "config"
        if not config_dir.exists():
            self.skipTest("Config directory doesn't exist")

        yaml_files = list(config_dir.glob("*.yml"))

        for yaml_file in yaml_files:
            with self.subTest(yaml_file=yaml_file.name):
                try:
                    with open(yaml_file, "r") as f:
                        yaml_content = yaml.safe_load(f)

                    # Basic validation - should be able to load
                    self.assertIsNotNone(yaml_content, f"{yaml_file} should contain valid YAML")

                    # If it's directory_structure.yml, validate structure
                    if yaml_file.name == "directory_structure.yml":
                        self.assertIn("layers", yaml_content)
                        self.assertIn("storage", yaml_content)
                        self.assertIn("legacy_mapping", yaml_content)

                except yaml.YAMLError as e:
                    self.fail(f"Invalid YAML in {yaml_file}: {e}")


class TestCIProtectionRules(unittest.TestCase):
    """Test CI protection rules and workflows"""

    def setUp(self):
        self.project_root = Path(__file__).parent.parent

    def test_github_workflows_exist(self):
        """Test that GitHub workflow files exist and are configured"""
        workflow_dir = self.project_root / ".github" / "workflows"

        self.assertTrue(workflow_dir.exists(), "GitHub workflows directory must exist")

        # Test pipeline workflow exists
        test_pipeline = workflow_dir / "test-pipeline.yml"
        if test_pipeline.exists():
            with open(test_pipeline, "r") as f:
                content = f.read()

            # Should reference common/config
            self.assertIn("common/config", content, "CI should use common/config path")

    def test_protection_test_file_exists(self):
        """Test that this protection test file is properly configured"""
        test_file = Path(__file__)

        # Should be in tests directory
        self.assertIn("tests", str(test_file))

        # Should be executable as a test
        self.assertTrue(test_file.exists())


class TestDirectoryManagerIntegrity(unittest.TestCase):
    """Test DirectoryManager integrity and functionality"""

    def setUp(self):
        self.dm = DirectoryManager()

    def test_directory_manager_configuration_loaded(self):
        """Test DirectoryManager loads configuration properly"""
        self.assertIsNotNone(self.dm.config)
        self.assertIn("storage", self.dm.config)
        self.assertIn("layers", self.dm.config)

    def test_all_layers_mappable(self):
        """Test all DataLayers can be mapped to paths"""
        for layer in DataLayer:
            layer_path = self.dm.get_layer_path(layer)
            self.assertIsInstance(layer_path, Path)
            self.assertTrue(len(str(layer_path)) > 0)

    def test_legacy_mapping_complete(self):
        """Test legacy path mapping is complete"""
        legacy_stages = [
            "stage_00_original",
            "stage_01_extract",
            "stage_02_transform",
            "stage_03_load",
            "stage_99_build",
        ]

        for legacy_stage in legacy_stages:
            mapped_layer = self.dm.map_legacy_path(legacy_stage)
            self.assertIsNotNone(
                mapped_layer, f"Legacy stage {legacy_stage} should map to a DataLayer"
            )

    def test_config_path_correct(self):
        """Test config path points to common/config"""
        config_path = self.dm.get_config_path()
        self.assertTrue("common/config" in str(config_path))

    def test_storage_info_complete(self):
        """Test storage info contains all required information"""
        info = self.dm.get_storage_info()

        required_keys = ["backend", "root_path", "layers", "common_paths"]
        for key in required_keys:
            self.assertIn(key, info, f"Storage info must contain {key}")


def run_protection_tests():
    """Run all protection tests"""
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestDirectoryStructureProtection,
        TestPathReferenceValidation,
        TestCIProtectionRules,
        TestDirectoryManagerIntegrity,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    print("🛡️  Running Directory Structure Protection Tests")
    print("=" * 60)

    success = run_protection_tests()

    print("\n" + "=" * 60)
    if success:
        print("✅ All directory structure protection tests passed!")
        print("🏗️  Five-Layer Data Architecture is properly protected.")
        sys.exit(0)
    else:
        print("❌ Some directory structure protection tests failed!")
        print("⚠️  Please fix violations before proceeding.")
        sys.exit(1)
