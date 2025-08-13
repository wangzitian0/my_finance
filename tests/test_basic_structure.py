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


def test_m7_commit_message_validation():
    """Test that M7 test validation is embedded in commit message (if available)"""
    import subprocess
    
    try:
        # Get latest commit message
        result = subprocess.run(["git", "log", "-1", "--pretty=%B"], 
                              capture_output=True, text=True, check=True)
        commit_msg = result.stdout.strip()
        
        # Check if this commit has M7 validation
        if "✅ M7-TESTED" in commit_msg:
            assert "📊 Test Results:" in commit_msg, "M7 validation should include test results"
            assert "🕐 Test Time:" in commit_msg, "M7 validation should include test timestamp"
            assert "🔍 Test Host:" in commit_msg, "M7 validation should include test host"
            assert "📝 Commit Hash:" in commit_msg, "M7 validation should include commit hash"
        else:
            pytest.skip("M7 validation not found in commit message (test may run before validation)")
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("Git not available or not in a git repository")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])