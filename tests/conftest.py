#!/usr/bin/env python3
"""
Test configuration and fixtures for release manager tests.

Provides common test fixtures and utilities for testing the release management system.
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Dict, Any


@pytest.fixture
def temp_project_root() -> Generator[Path, None, None]:
    """Create a temporary project root directory for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    project_root = temp_dir / "test_project"
    project_root.mkdir()
    
    yield project_root
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_build_structure(temp_project_root: Path) -> Dict[str, Any]:
    """Create a sample build structure for testing."""
    data_dir = temp_project_root / "data"
    
    # Build directory
    build_dir = data_dir / "stage_99_build" / "build_20250820_123000"
    build_dir.mkdir(parents=True)
    
    # Build manifests
    (build_dir / "BUILD_MANIFEST.md").write_text("# Build Manifest\n\nBuild ID: 20250820_123000")
    (build_dir / "BUILD_MANIFEST.json").write_text('{"build_id": "20250820_123000", "status": "completed"}')
    
    # LLM responses
    llm_dir = data_dir / "llm" / "responses"
    llm_dir.mkdir(parents=True)
    
    test_files = {
        "dcf_en_AAPL_test.md": "# DCF Analysis for AAPL\n\nIntrinsic value: $150",
        "dcf_zh_MSFT_test.md": "# MSFT DCF 分析\n\n内在价值: $300",
        "dcf_en_GOOGL_test.md": "# GOOGL DCF Analysis\n\nFair value: $2500"
    }
    
    for filename, content in test_files.items():
        (llm_dir / filename).write_text(content)
    
    # Quality reports
    quality_dir = data_dir / "quality_reports" / "20250820_123000"
    quality_dir.mkdir(parents=True)
    (quality_dir / "quality_summary.json").write_text('{"quality_score": 95, "errors": 0, "warnings": 2}')
    (quality_dir / "quality_summary.md").write_text("# Quality Report\n\nOverall quality: Excellent")
    
    # Semantic results
    semantic_dir = data_dir / "llm" / "semantic_results"
    semantic_dir.mkdir(parents=True)
    (semantic_dir / "retrieved_docs_AAPL.json").write_text('{"documents": ["doc1", "doc2"], "query": "AAPL financial data"}')
    
    # Config files
    config_dir = data_dir / "config"
    config_dir.mkdir()
    (config_dir / "database.yml").write_text("host: localhost\nport: 5432\ndatabase: finance")
    (config_dir / "llm.yml").write_text("model: gpt-4\ntemperature: 0.7\nmax_tokens: 2000")
    
    return {
        "project_root": temp_project_root,
        "build_dir": build_dir,
        "data_dir": data_dir,
        "expected_files": {
            "manifests": 2,
            "llm_responses": 3,
            "quality_reports": 2,
            "semantic_results": 1,
            "configs": 2
        }
    }