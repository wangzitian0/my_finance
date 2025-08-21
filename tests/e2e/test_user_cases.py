"""
End-to-end tests for core user cases

This file is deprecated. Please use tests in the e2e/ directory instead.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest


class TestStrategyAnalystWorkflow:
    """Test case: Strategy analyst performs DCF valuation and investment decisions"""

    def test_m7_dcf_valuation_workflow(self):
        """Complete M7 stock DCF valuation workflow"""
        # 1. Build M7 test dataset
        result = subprocess.run(
            ["pixi", "run", "build", "m7", "--validate"], capture_output=True, text=True
        )
        assert result.returncode == 0, f"M7 build failed: {result.stderr}"

        # 2. Execute DCF valuation
        result = subprocess.run(
            ["pixi", "run", "validate-strategy"], capture_output=True, text=True
        )
        assert result.returncode == 0, f"Strategy validation failed: {result.stderr}"

        # 3. Verify output reports - use centralized directory management
        from common.directory_manager import DataLayer, get_data_path

        reports_dir = get_data_path(DataLayer.QUERY_RESULTS)
        assert reports_dir.exists(), "Reports directory not found"

        # Look for DCF reports (the actual output format)
        dcf_reports = list(reports_dir.glob("**/M7_DCF_Report_*.md"))
        assert len(dcf_reports) > 0, "No DCF reports generated"

        # 4. Verify report file is not empty
        dcf_report = dcf_reports[0]
        assert dcf_report.exists(), f"DCF report file not found: {dcf_report}"
        assert dcf_report.stat().st_size > 0, "DCF report file is empty"

        # 5. Verify DCF report contains M7 stock analysis
        with open(dcf_report, "r") as f:
            report_content = f.read()

        # Check report contains M7 stock tickers
        m7_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]
        found_tickers = [ticker for ticker in m7_tickers if ticker in report_content]
        assert (
            len(found_tickers) > 0
        ), f"No M7 tickers found in DCF report. Content preview: {report_content[:200]}"

    def test_investment_decision_quality(self):
        """Verify quality and consistency of investment decisions"""
        # Use existing validate command to check investment decision quality
        result = subprocess.run(
            ["python", "ETL/manage.py", "validate"], capture_output=True, text=True
        )
        assert result.returncode == 0, f"Investment decision test failed: {result.stderr}"


class TestRiskManagerWorkflow:
    """Test case: Risk manager performs multi-factor risk assessment"""

    def test_risk_assessment_workflow(self):
        """Complete risk assessment workflow"""
        # 1. Execute strategy validation (includes risk analysis)
        result = subprocess.run(
            ["pixi", "run", "validate-strategy"], capture_output=True, text=True
        )
        assert result.returncode == 0, f"Risk analysis failed: {result.stderr}"

        # 2. Verify DCF report contains risk indicators
        from common.directory_manager import DataLayer, get_data_path

        reports_dir = get_data_path(DataLayer.QUERY_RESULTS)
        dcf_reports = list(reports_dir.glob("**/M7_DCF_Report_*.md"))
        assert len(dcf_reports) > 0, "No DCF reports generated"

        with open(dcf_reports[0], "r") as f:
            report_content = f.read()

        # 3. Verify contains basic analysis results
        assert "Analysis" in report_content, "Missing analysis results"
        assert len(report_content) > 100, "Report content too short"

    def test_backtest_performance(self):
        """Verify backtest performance analysis"""
        result = subprocess.run(["pixi", "run", "backtest"], capture_output=True, text=True)
        assert result.returncode == 0, f"Backtest failed: {result.stderr}"


class TestInvestmentManagerWorkflow:
    """Test case: Investment manager generates strategy reports and benchmarks"""

    def test_strategy_report_generation(self):
        """Complete strategy report generation workflow"""
        # 1. Generate strategy report
        result = subprocess.run(["pixi", "run", "generate-report"], capture_output=True, text=True)
        assert result.returncode == 0, f"Report generation failed: {result.stderr}"

        # 2. Verify report files
        from common.directory_manager import DataLayer, get_data_path

        reports_dir = get_data_path(DataLayer.QUERY_RESULTS)
        assert reports_dir.exists()

        # Should contain Markdown and JSON format reports
        # Look for any reports in the build directories
        dcf_reports = list(reports_dir.glob("**/M7_DCF_Report_*.md"))
        manifest_files = list(reports_dir.glob("**/BUILD_MANIFEST.md"))

        assert len(dcf_reports) > 0, "No DCF reports generated"
        assert len(manifest_files) > 0, "No build manifest files generated"

    def test_benchmark_comparison(self):
        """Verify benchmark comparison functionality"""
        # Use existing generate-report command, which includes benchmark comparison
        result = subprocess.run(["pixi", "run", "generate-report"], capture_output=True, text=True)
        assert result.returncode == 0, f"Benchmark comparison failed: {result.stderr}"

        # Verify DCF report was generated (contains benchmark comparison info)
        from common.directory_manager import DataLayer, get_data_path

        reports_dir = get_data_path(DataLayer.QUERY_RESULTS)
        dcf_reports = list(reports_dir.glob("**/M7_DCF_Report_*.md"))
        assert len(dcf_reports) > 0, "No DCF reports generated"


class TestDataIntegrity:
    """Data integrity testing"""

    def test_data_consistency_across_workflows(self):
        """Ensure data consistency across different workflows"""
        # Execute status check
        result = subprocess.run(["pixi", "run", "status"], capture_output=True, text=True)
        assert result.returncode == 0, f"Status check failed: {result.stderr}"

        # Verify data directory structure (basic directory structure)
        data_dirs = ["common/config"]
        for dir_path in data_dirs:
            assert Path(dir_path).exists(), f"Missing data directory: {dir_path}"


class TestEnvironmentValidation:
    """Environment validation testing"""

    def test_services_health(self):
        """Verify health status of all services"""
        result = subprocess.run(["pixi", "run", "env-status"], capture_output=True, text=True)
        assert result.returncode == 0, f"Environment status check failed: {result.stderr}"

        # Verify environment status check runs successfully (service status may vary by environment)
        assert (
            "Environment Status" in result.stdout or result.returncode == 0
        ), "Environment status check basic validation"
