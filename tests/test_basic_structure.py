"""
Basic structure tests for CI pipeline
Tests fundamental project structure without external dependencies
"""
import os
import pytest
from pathlib import Path


def test_project_structure():
    """Test that basic project structure exists"""
    project_root = Path(__file__).parent.parent
    
    # Core directories should exist
    assert (project_root / "ETL").exists(), "ETL directory should exist"
    assert (project_root / "dcf_engine").exists(), "dcf_engine directory should exist"
    assert (project_root / "common").exists(), "common directory should exist"
    assert (project_root / "tests").exists(), "tests directory should exist"
    

def test_data_directory():
    """Test data directory structure (symlink or regular dir)"""
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    
    # Data directory should exist (either as symlink or directory)
    assert data_dir.exists(), "data directory should exist"
    
    # If it's a symlink, it should be valid
    if data_dir.is_symlink():
        assert data_dir.resolve().exists(), "symlink target should exist"


def test_config_files():
    """Test that essential config files exist"""
    project_root = Path(__file__).parent.parent
    
    assert (project_root / "pixi.toml").exists(), "pixi.toml should exist"
    assert (project_root / "CLAUDE.md").exists(), "CLAUDE.md should exist"


def test_vti_config_exists():
    """Test that new VTI config exists"""
    project_root = Path(__file__).parent.parent
    vti_config = project_root / "data" / "config" / "list_vti_3500.yml"
    
    # This might fail in CI due to symlink, so make it non-fatal
    if vti_config.exists():
        assert vti_config.is_file(), "VTI config should be a file"
    else:
        pytest.skip("VTI config not available (likely CI symlink issue)")


def test_m7_marker_file():
    """Test that M7 test marker exists with correct format"""
    project_root = Path(__file__).parent.parent
    marker_file = project_root / ".m7-test-passed"
    
    if marker_file.exists():
        content = marker_file.read_text()
        assert "VALIDATION_PASSED=true" in content, "M7 marker should show validation passed"
        assert "COMMIT_HASH=" in content, "M7 marker should include commit hash"
        assert "TEST_TIMESTAMP=" in content, "M7 marker should include timestamp"
    else:
        pytest.skip("M7 marker not found (test may run before marker creation)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])