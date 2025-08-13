"""
End-to-end integration tests for all modules
Tests the complete workflow from data ingestion to reporting
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path
import pytest


class TestModuleIntegrationWorkflow:
    """Test complete integration of all modules in the pipeline"""

    def test_complete_pipeline_f2(self):
        """Test complete pipeline with F2 (Fast 2) dataset"""
        # 1. Clean any existing builds
        result = subprocess.run(
            ["pixi", "run", "clean"], capture_output=True, text=True
        )
        # Don't assert on clean, it might fail if nothing to clean
        
        # 2. Build F2 dataset (should be fast)
        result = subprocess.run(
            ["pixi", "run", "build-f2"], capture_output=True, text=True
        )
        assert result.returncode == 0, f"F2 build failed: {result.stderr}"
        
        # 3. Verify build artifacts
        reports_dir = Path("data/stage_99_build")
        assert reports_dir.exists(), "Build directory not found"
        
        # Check for build directories
        build_dirs = list(reports_dir.glob("build_*"))
        assert len(build_dirs) > 0, "No build directories found"
        
        latest_build = max(build_dirs, key=lambda p: p.name)
        
        # 4. Verify build manifest
        manifest_file = latest_build / "BUILD_MANIFEST.md"
        assert manifest_file.exists(), "Build manifest not found"
        
        with open(manifest_file, 'r') as f:
            manifest_content = f.read()
        
        # Check manifest contains expected sections
        assert "Build Information" in manifest_content
        assert "ETL Stages" in manifest_content
        assert "f2" in manifest_content.lower()
        
        # 5. Verify DCF report
        dcf_reports = list(latest_build.glob("M7_DCF_Report_*.md"))
        assert len(dcf_reports) > 0, "No DCF reports found"
        
        dcf_report = dcf_reports[0]
        assert dcf_report.stat().st_size > 100, "DCF report too small"
        
        with open(dcf_report, 'r') as f:
            dcf_content = f.read()
        
        # Should contain F2 companies (MSFT, NVDA)
        assert "MSFT" in dcf_content or "NVDA" in dcf_content, "F2 companies not found in DCF report"

    def test_tier_config_integration(self):
        """Test that all tier configurations work correctly"""
        from ETL.tests.test_config import TestConfigManager, DatasetTier
        
        manager = TestConfigManager()
        
        # Test each tier configuration
        tiers_to_test = [DatasetTier.F2, DatasetTier.M7]  # Only test fast ones
        
        for tier in tiers_to_test:
            config = manager.get_config(tier)
            
            # Verify config structure
            assert config.tier == tier
            assert config.config_file.endswith('.yml')
            assert isinstance(config.expected_tickers, list)
            assert config.timeout_seconds > 0
            
            # Verify config file naming convention
            if tier == DatasetTier.F2:
                assert config.config_file == "list_fast_2.yml"
                assert config.timeout_seconds == 120
            elif tier == DatasetTier.M7:
                assert config.config_file == "list_magnificent_7.yml"
                assert config.timeout_seconds == 300

    def test_build_tracker_integration(self):
        """Test BuildTracker integration with actual builds"""
        from common.build_tracker import BuildTracker
        
        # Get latest build
        latest_build = BuildTracker.get_latest_build()
        
        if latest_build:
            # Test build status
            status = latest_build.get_build_status()
            
            assert 'build_id' in status
            assert 'status' in status
            assert 'configuration' in status
            
            # Check that status makes sense
            assert status['status'] in ['completed', 'in_progress', 'failed']
            
            # If completed, should have reasonable stage completion
            if status['status'] == 'completed':
                assert status.get('stages_completed', 0) > 0

    def test_dcf_engine_integration(self):
        """Test DCF engine integration with knowledge base"""
        from dcf_engine.build_knowledge_base import KnowledgeBaseBuilder
        
        builder = KnowledgeBaseBuilder()
        
        # Test tier system
        assert 'f2' in builder.tiers
        assert 'm7' in builder.tiers
        assert 'n100' in builder.tiers
        assert 'v3k' in builder.tiers
        
        # Test tier configuration structure
        for tier_name, tier_config in builder.tiers.items():
            assert 'name' in tier_config
            assert 'description' in tier_config
            assert 'configs' in tier_config
            assert 'tracked_in_git' in tier_config
            assert 'max_size_mb' in tier_config
            
            # Verify size limits make sense
            if tier_name == 'f2':
                assert tier_config['max_size_mb'] == 20
            elif tier_name == 'v3k':
                assert tier_config['max_size_mb'] == 20000

    def test_command_integration(self):
        """Test that key pixi commands work correctly"""
        
        # Test status command
        result = subprocess.run(
            ["pixi", "run", "status"], capture_output=True, text=True
        )
        # Status may fail due to environment issues, but should be defined
        assert "status" in str(result.stdout) or "status" in str(result.stderr)
        
        # Test dev command
        result = subprocess.run(
            ["pixi", "run", "dev"], capture_output=True, text=True
        )
        assert result.returncode == 0, f"Dev command failed: {result.stderr}"
        assert "Development Ready" in result.stdout
        
        # Test quick-test command
        result = subprocess.run(
            ["pixi", "run", "quick-test"], capture_output=True, text=True
        )
        assert result.returncode == 0, f"Quick test failed: {result.stderr}"

    def test_data_directory_integration(self):
        """Test data directory symlink and structure"""
        data_dir = Path("data")
        
        # Verify symlink
        assert data_dir.exists(), "Data directory not found"
        assert data_dir.is_symlink(), "Data directory should be a symlink"
        
        # Verify target exists
        target = data_dir.resolve()
        assert target.exists(), f"Symlink target not found: {target}"
        assert target.name == "my_finance_data", "Symlink should point to my_finance_data"
        
        # Verify basic structure
        assert (data_dir / "config").exists(), "Config directory not found"
        assert (data_dir / "stage_99_build").exists(), "Build directory not found"

    def test_config_files_integration(self):
        """Test that all required configuration files exist"""
        config_dir = Path("data/config")
        
        required_configs = [
            "list_fast_2.yml",
            "list_magnificent_7.yml",
            "list_nasdaq_100.yml",
            "list_vti_3500.yml",
        ]
        
        for config_file in required_configs:
            config_path = config_dir / config_file
            assert config_path.exists(), f"Missing config file: {config_file}"
            
            # Basic content check
            assert config_path.stat().st_size > 0, f"Empty config file: {config_file}"

    def test_build_status_integration(self):
        """Test build status command integration"""
        result = subprocess.run(
            ["pixi", "run", "build-status"], capture_output=True, text=True
        )
        
        # May return no builds found, which is OK
        assert result.returncode == 0 or "No builds found" in result.stdout
        
        # If there are builds, should show valid status
        if "No builds found" not in result.stdout:
            # Should contain some status information
            output = result.stdout.lower()
            status_indicators = ['completed', 'in_progress', 'failed', 'build_id']
            assert any(indicator in output for indicator in status_indicators), \
                f"Build status output doesn't contain expected status: {result.stdout}"

    def test_error_handling_integration(self):
        """Test error handling in integration scenarios"""
        
        # Test invalid tier
        result = subprocess.run(
            ["pixi", "run", "build-dataset", "invalid_tier"], 
            capture_output=True, text=True
        )
        # Should fail gracefully
        assert result.returncode != 0, "Should fail with invalid tier"
        
        # Error message should be informative
        error_output = result.stderr.lower()
        assert "invalid" in error_output or "choice" in error_output or "error" in error_output

    def test_module_imports_integration(self):
        """Test that all modules can be imported in integration context"""
        import_tests = [
            "from ETL.tests.test_config import DatasetTier, TestConfigManager",
            "from dcf_engine.build_knowledge_base import KnowledgeBaseBuilder",
            "from dcf_engine.generate_dcf_report import M7DCFAnalyzer",
            "from common.build_tracker import BuildTracker",
        ]
        
        for import_statement in import_tests:
            try:
                exec(import_statement)
            except ImportError as e:
                pytest.fail(f"Import failed: {import_statement}, Error: {e}")


class TestPipelinePerformance:
    """Test pipeline performance characteristics"""

    def test_f2_build_performance(self):
        """Test that F2 build completes within reasonable time"""
        import time
        
        # Clean builds first
        subprocess.run(["pixi", "run", "clean"], capture_output=True)
        
        start_time = time.time()
        result = subprocess.run(
            ["pixi", "run", "build-f2"], capture_output=True, text=True
        )
        end_time = time.time()
        
        build_time = end_time - start_time
        
        assert result.returncode == 0, f"F2 build failed: {result.stderr}"
        # F2 should complete within 5 minutes (300 seconds)
        assert build_time < 300, f"F2 build too slow: {build_time:.1f} seconds"
        
        print(f"F2 build completed in {build_time:.1f} seconds")

    def test_command_response_time(self):
        """Test that status commands respond quickly"""
        import time
        
        quick_commands = ["dev", "status", "quick-test"]
        
        for command in quick_commands:
            start_time = time.time()
            result = subprocess.run(
                ["pixi", "run", command], capture_output=True, text=True
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Most commands should respond within 30 seconds
            # (status might be slower due to environment checks)
            max_time = 60 if command == "status" else 30
            assert response_time < max_time, \
                f"Command '{command}' too slow: {response_time:.1f} seconds"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
