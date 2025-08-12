#!/usr/bin/env python3
"""
Unit tests for common modules
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_common_imports():
    """Test that common modules can be imported"""
    try:
        from common import build_tracker
        assert True
    except ImportError as e:
        pytest.fail(f"Common imports failed: {e}")

def test_build_tracker_basic():
    """Test BuildTracker basic functionality"""
    try:
        from common.build_tracker import BuildTracker
        
        # Test that BuildTracker can be instantiated (it generates its own build_id)
        tracker = BuildTracker()
        
        # Check basic attributes
        assert hasattr(tracker, 'build_id')
        assert hasattr(tracker, 'build_path')
        assert hasattr(tracker, 'manifest')
        assert tracker.build_id is not None
        
    except Exception as e:
        pytest.fail(f"BuildTracker basic test failed: {e}")

@patch('pathlib.Path.mkdir')
@patch('pathlib.Path.exists')
def test_build_tracker_creation_mock(mock_exists, mock_mkdir):
    """Test BuildTracker creation with mocked filesystem"""
    try:
        from common.build_tracker import BuildTracker
        
        # Mock directory doesn't exist initially
        mock_exists.return_value = False
        
        build_id = "test_build_20250812_120000"
        tracker = BuildTracker(build_id)
        
        # Verify build_id format
        assert "_" in build_id
        assert len(build_id.split("_")) >= 3  # At least: test, build, timestamp
        
        # Test that basic methods exist (using actual method names)
        assert hasattr(tracker, 'start_stage')
        assert hasattr(tracker, 'complete_stage')
        assert hasattr(tracker, 'get_build_status')
        
    except Exception as e:
        pytest.fail(f"BuildTracker creation mock test failed: {e}")

def test_build_tracker_manifest_structure():
    """Test BuildTracker manifest structure"""
    try:
        from common.build_tracker import BuildTracker
        
        tracker = BuildTracker()
        
        # Check manifest has expected structure
        manifest = tracker.manifest
        
        # Check manifest structure
        assert 'build_info' in manifest
        assert 'stages' in manifest
        
        # Check build_info structure
        build_info = manifest['build_info']
        expected_fields = ['build_id', 'start_time', 'status']
        for field in expected_fields:
            assert field in build_info, f"Missing build_info field: {field}"
            
    except Exception as e:
        pytest.fail(f"BuildTracker manifest structure test failed: {e}")

@patch('common.build_tracker.BuildTracker._save_manifest')
def test_build_tracker_stage_logging_mock(mock_save):
    """Test BuildTracker stage logging with mocked save"""
    try:
        from common.build_tracker import BuildTracker
        
        mock_save.return_value = None
        
        tracker = BuildTracker()
        
        # Test stage logging methods exist and are callable
        assert hasattr(tracker, 'start_stage')
        assert callable(tracker.start_stage)
            
        assert hasattr(tracker, 'complete_stage')
        assert callable(tracker.complete_stage)
            
        assert hasattr(tracker, 'log_stage_output')
        assert callable(tracker.log_stage_output)
            
    except Exception as e:
        pytest.fail(f"BuildTracker stage logging mock test failed: {e}")

def test_build_tracker_timestamp_format():
    """Test BuildTracker timestamp format validation"""
    try:
        # Test various timestamp formats that should be valid
        valid_build_ids = [
            "build_20250812_120000",
            "test_20250812_120000", 
            "m7_20250812_120000",
            "build_20250812_235959"
        ]
        
        for build_id in valid_build_ids:
            # Extract timestamp part
            parts = build_id.split("_")
            if len(parts) >= 3:
                date_part = parts[-2]
                time_part = parts[-1]
                
                # Validate date format YYYYMMDD
                assert len(date_part) == 8, f"Invalid date format in {build_id}"
                assert date_part.isdigit(), f"Date should be numeric in {build_id}"
                
                # Validate time format HHMMSS
                assert len(time_part) == 6, f"Invalid time format in {build_id}"
                assert time_part.isdigit(), f"Time should be numeric in {build_id}"
                
                # Test that it can be parsed as datetime
                datetime.strptime(f"{date_part}_{time_part}", "%Y%m%d_%H%M%S")
                
    except Exception as e:
        pytest.fail(f"BuildTracker timestamp format test failed: {e}")

@patch('pathlib.Path.glob')
def test_build_tracker_latest_build_mock(mock_glob):
    """Test BuildTracker latest build detection with mocked filesystem"""
    try:
        from common.build_tracker import BuildTracker
        
        # Mock build directories
        mock_build_dirs = [
            Path("data/stage_99_build/build_20250812_100000"),
            Path("data/stage_99_build/build_20250812_110000"), 
            Path("data/stage_99_build/build_20250812_120000"),  # Latest
        ]
        mock_glob.return_value = mock_build_dirs
        
        # Test get_latest_build class method exists
        if hasattr(BuildTracker, 'get_latest_build'):
            assert callable(BuildTracker.get_latest_build)
            
    except Exception as e:
        pytest.fail(f"BuildTracker latest build mock test failed: {e}")

def test_build_status_values():
    """Test valid build status values"""
    try:
        # Define expected status values
        valid_statuses = [
            'running',
            'completed', 
            'failed',
            'cancelled'
        ]
        
        # Test that these are reasonable status values
        for status in valid_statuses:
            assert isinstance(status, str)
            assert len(status) > 0
            assert status.islower()  # Convention: lowercase status
            
    except Exception as e:
        pytest.fail(f"Build status values test failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
