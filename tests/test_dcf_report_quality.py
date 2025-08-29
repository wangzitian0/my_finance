#!/usr/bin/env python3
"""
DCF Report Quality Validation Tests
Automated tests to detect mock data vs real SEC filings in DCF reports.

These tests ensure DCF reports use authentic SEC filing data and catch
regressions where mock data is accidentally used in production reports.
"""

import json

# Add project root to path for imports
import sys
from pathlib import Path
from typing import Dict, List

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.quality_gates import DCFReportQualityValidator


class TestDCFReportQuality:
    """Test suite for DCF report quality validation"""

    def setup_method(self):
        """Setup test environment"""
        self.validator = DCFReportQualityValidator()

    def test_msft_market_cap_validation(self):
        """Test Microsoft market cap is within realistic range"""

        # Valid MSFT data (realistic market cap)
        valid_dcf_data = {
            "ticker": "MSFT",
            "market_cap": "$3,100,000,000,000",  # $3.1T - realistic for MSFT
            "industry": "Software & Technology Services",
            "rd_intensity": "15.2%",
        }

        result = self.validator.validate_dcf_report("MSFT", valid_dcf_data)
        assert result["passed"], f"Valid MSFT data should pass: {result['quality_failures']}"
        assert not result["mock_data_detected"]

        # Invalid MSFT data (unrealistic market cap from mock data)
        invalid_dcf_data = {
            "ticker": "MSFT",
            "market_cap": "1500B",  # $1.5T - too low for MSFT, suggests mock data
            "industry": "Software",
            "rd_intensity": "0%",  # Zero R&D is unrealistic
        }

        result = self.validator.validate_dcf_report("MSFT", invalid_dcf_data)
        assert not result["passed"], "Invalid MSFT data should fail validation"
        assert len(result["quality_failures"]) > 0
        assert "Market cap" in str(result["quality_failures"])

    def test_nvda_industry_classification(self):
        """Test NVIDIA industry classification is correct (semiconductor, not software)"""

        # Correct NVDA industry classification
        correct_dcf_data = {
            "ticker": "NVDA",
            "market_cap": "$2,800,000,000,000",  # Realistic for NVDA
            "industry": "Semiconductor & GPU Technology",  # Correct industry
            "rd_intensity": "20.1%",
        }

        result = self.validator.validate_dcf_report("NVDA", correct_dcf_data)
        assert result["passed"], f"Correct NVDA industry should pass: {result['quality_failures']}"

        # Incorrect NVDA industry (common mistake - calling NVDA "software")
        incorrect_dcf_data = {
            "ticker": "NVDA",
            "market_cap": "$2,800,000,000,000",
            "industry": "Software & Technology",  # WRONG - NVDA is semiconductor
            "rd_intensity": "20.1%",
        }

        result = self.validator.validate_dcf_report("NVDA", incorrect_dcf_data)
        assert not result["passed"], "Incorrect NVDA industry should fail validation"
        assert any("Industry" in failure for failure in result["quality_failures"])

    def test_rd_intensity_validation(self):
        """Test R&D intensity is realistic for tech companies"""

        # Test cases for different companies and their expected R&D ranges
        test_cases = [
            {
                "ticker": "MSFT",
                "valid_rd": "13.5%",  # Above 10% minimum
                "invalid_rd": "2.0%",  # Below 10% minimum
                "zero_rd": "0.0%",  # Zero R&D (unrealistic)
            },
            {
                "ticker": "NVDA",
                "valid_rd": "18.7%",  # Above 15% minimum
                "invalid_rd": "8.0%",  # Below 15% minimum
                "zero_rd": "0%",  # Zero R&D (unrealistic)
            },
        ]

        for case in test_cases:
            ticker = case["ticker"]

            # Test valid R&D intensity - use appropriate industry for each ticker
            industry = "Software Technology" if ticker == "MSFT" else "Semiconductor Technology"
            valid_data = {
                "ticker": ticker,
                "market_cap": "$3,000,000,000,000",
                "industry": industry,
                "rd_intensity": case["valid_rd"],
            }
            result = self.validator.validate_dcf_report(ticker, valid_data)
            assert result[
                "passed"
            ], f"{ticker} with valid R&D should pass: {result['quality_failures']}"

            # Test invalid R&D intensity (too low)
            invalid_data = valid_data.copy()
            invalid_data["rd_intensity"] = case["invalid_rd"]
            result = self.validator.validate_dcf_report(ticker, invalid_data)
            assert not result["passed"], f"{ticker} with low R&D should fail validation"

            # Test zero R&D intensity (mock data indicator)
            zero_data = valid_data.copy()
            zero_data["rd_intensity"] = case["zero_rd"]
            result = self.validator.validate_dcf_report(ticker, zero_data)
            assert not result["passed"], f"{ticker} with zero R&D should fail validation"
            assert result["mock_data_detected"], "Zero R&D should trigger mock data detection"

    def test_mock_data_detection(self):
        """Test detection of various mock data patterns"""

        mock_data_examples = [
            {
                "name": "direct_mock_keyword",
                "data": {"ticker": "AAPL", "note": "This is mock data for testing"},
                "should_detect": True,
            },
            {
                "name": "simplified_market_cap",
                "data": {"ticker": "MSFT", "market_cap": "1500B"},  # Oversimplified format
                "should_detect": True,
            },
            {
                "name": "zero_rd_intensity",
                "data": {"ticker": "GOOGL", "rd_intensity": "0.0%"},  # Zero R&D unrealistic
                "should_detect": True,
            },
            {
                "name": "placeholder_values",
                "data": {"ticker": "META", "revenue": "placeholder", "industry": "example"},
                "should_detect": True,
            },
            {
                "name": "realistic_data",
                "data": {
                    "ticker": "AAPL",
                    "market_cap": "$3,200,000,000,000",
                    "industry": "Consumer Electronics Technology",
                    "rd_intensity": "6.8%",
                },
                "should_detect": False,  # This should NOT be detected as mock
            },
        ]

        for example in mock_data_examples:
            result = self.validator.validate_dcf_report(example["data"]["ticker"], example["data"])

            if example["should_detect"]:
                assert result[
                    "mock_data_detected"
                ], f"Should detect mock data in: {example['name']}"
            else:
                assert not result[
                    "mock_data_detected"
                ], f"Should NOT detect mock data in: {example['name']}"

    def test_market_cap_parsing(self):
        """Test market cap parsing for various formats"""

        test_cases = [
            ("$3,100,000,000,000", 3_100_000_000_000),  # Full numeric with commas
            ("$3.1T", 3_100_000_000_000),  # Trillion format
            ("2800B", 2_800_000_000_000),  # Billion format
            ("1.5T", 1_500_000_000_000),  # Without dollar sign
            ("invalid", None),  # Invalid format
            ("", None),  # Empty string
        ]

        for input_str, expected in test_cases:
            result = self.validator._parse_market_cap(input_str)
            assert (
                result == expected
            ), f"Failed parsing '{input_str}': expected {expected}, got {result}"

    def test_percentage_parsing(self):
        """Test percentage parsing for R&D intensity"""

        test_cases = [
            ("15.2%", 0.152),  # Standard percentage format
            ("15.2", 0.152),  # Without % symbol
            ("0.152", 0.152),  # Already in decimal format
            ("0%", 0.0),  # Zero percentage
            ("invalid", None),  # Invalid format
            ("", None),  # Empty string
        ]

        for input_str, expected in test_cases:
            result = self.validator._parse_percentage(input_str)
            assert (
                result == expected
            ), f"Failed parsing '{input_str}': expected {expected}, got {result}"

    def test_comprehensive_dcf_validation(self):
        """Test comprehensive DCF validation with realistic scenarios"""

        # Scenario 1: Perfect DCF report (should pass all validations)
        perfect_report = {
            "ticker": "MSFT",
            "market_cap": "$3,100,000,000,000",
            "industry": "Cloud & Software Technology Services",
            "rd_intensity": "13.5%",
            "revenue": "$211,915,000,000",
            "free_cash_flow": "$65,149,000,000",
            "analysis_date": "2025-01-28",
            "data_source": "SEC 10-K filing 2024",
        }

        result = self.validator.validate_dcf_report("MSFT", perfect_report)
        assert result["passed"], f"Perfect MSFT report should pass: {result}"
        assert not result["mock_data_detected"]
        assert len(result["quality_failures"]) == 0

        # Scenario 2: Problematic DCF report (multiple issues)
        problematic_report = {
            "ticker": "NVDA",
            "market_cap": "1500B",  # Too low for NVDA + simplified format
            "industry": "Software",  # Wrong industry for NVDA
            "rd_intensity": "0%",  # Zero R&D unrealistic
            "note": "Using mock data for testing",  # Direct mock indicator
        }

        result = self.validator.validate_dcf_report("NVDA", problematic_report)
        assert not result["passed"], "Problematic NVDA report should fail"
        assert result["mock_data_detected"], "Should detect mock data patterns"
        assert len(result["quality_failures"]) >= 3, "Should detect multiple quality issues"

        # Verify specific failures are detected
        failures_str = " ".join(result["quality_failures"])
        assert "Market cap" in failures_str, "Should detect market cap issue"
        assert "Industry" in failures_str, "Should detect industry classification issue"
        assert "Mock data" in failures_str, "Should detect mock data usage"

    def test_unknown_ticker_handling(self):
        """Test handling of unknown/unsupported tickers"""

        unknown_ticker_data = {
            "ticker": "UNKNOWN",
            "market_cap": "$1,000,000,000",
            "industry": "Unknown Industry",
        }

        result = self.validator.validate_dcf_report("UNKNOWN", unknown_ticker_data)

        # Should pass with warnings for unknown tickers
        assert result["passed"], "Unknown tickers should pass with warnings"
        assert len(result["warnings"]) > 0, "Should generate warning for unknown ticker"
        assert "No validation rules" in result["warnings"][0]

    @pytest.mark.integration
    def test_integration_with_real_dcf_reports(self):
        """Integration test with real DCF report files (if available)"""

        # Look for actual DCF reports in build directories
        from common.directory_manager import DirectoryManager

        directory_manager = DirectoryManager()
        data_root = directory_manager.get_data_root()
        query_results_path = data_root / "stage_04_query_results"

        if not query_results_path.exists():
            pytest.skip("No query results directory found - skipping integration test")

        # Find DCF report files
        dcf_reports = list(query_results_path.rglob("*DCF_Report*.md"))

        if not dcf_reports:
            pytest.skip("No DCF report files found - skipping integration test")

        print(f"\n🔍 Found {len(dcf_reports)} DCF reports for integration testing")

        # Test each report for basic quality indicators
        for report_path in dcf_reports[:3]:  # Limit to first 3 reports
            print(f"   Testing: {report_path.name}")

            try:
                # Read report content
                with open(report_path, "r") as f:
                    content = f.read()

                # Extract ticker from filename (assumes format like "MSFT_DCF_Report_...")
                ticker = None
                for company_ticker in ["MSFT", "NVDA", "AAPL", "GOOGL", "META", "TSLA", "AMZN"]:
                    if company_ticker in report_path.name:
                        ticker = company_ticker
                        break

                if not ticker:
                    continue  # Skip if we can't identify ticker

                # Basic quality checks on report content
                quality_issues = []

                # Check for mock data indicators
                content_lower = content.lower()
                mock_indicators = ["mock", "test", "placeholder", "example", "1500b"]
                for indicator in mock_indicators:
                    if indicator in content_lower:
                        quality_issues.append(f"Potential mock data indicator: '{indicator}'")

                # Check for realistic market cap formats
                if "1500b" in content_lower:
                    quality_issues.append(
                        "Simplified market cap format detected (possible mock data)"
                    )

                # Check for zero R&D patterns
                if "r&d: 0%" in content_lower or "rd_intensity: 0" in content_lower:
                    quality_issues.append("Zero R&D intensity detected (unrealistic)")

                # Report integration test results
                if quality_issues:
                    print(f"     ⚠️  Quality concerns: {len(quality_issues)} issues")
                    for issue in quality_issues:
                        print(f"       • {issue}")
                else:
                    print(f"     ✅ Quality check passed")

            except Exception as e:
                print(f"     ❌ Error analyzing {report_path.name}: {e}")


class TestDataQualityValidation:
    """Test suite for data pipeline quality validation"""

    def setup_method(self):
        """Setup test environment"""
        from common.quality_gates import DataQualityValidation

        self.validator = DataQualityValidation()

    def test_f2_validation_thresholds(self):
        """Test F2 scope validation thresholds"""

        # Test with data meeting F2 requirements (2 companies minimum)
        mock_build_metadata = {"scope": "f2", "companies": ["MSFT", "NVDA"]}

        result = self.validator.validate_data_collection("f2", mock_build_metadata)
        assert result["scope"] == "f2"
        assert "critical_failures" in result
        assert "warnings" in result
        assert "metrics" in result

    def test_zero_data_detection(self):
        """Test critical failure detection for zero data collection"""

        # Mock the file counting to return zero files
        original_count_method = self.validator._count_data_files
        self.validator._count_data_files = lambda: {
            "sec_edgar_files": 0,
            "yfinance_files": 0,
            "total_files": 0,
            "locations_checked": ["mocked_zero_files"],
        }

        try:
            result = self.validator.validate_data_collection("f2")

            # Should detect zero data as critical failure
            assert not result["passed"], "Zero data collection should fail validation"
            assert any("ZERO DATA COLLECTION" in failure for failure in result["critical_failures"])
            assert "CRITICAL" in result["recommendation"] and "FAILED" in result["recommendation"]

        finally:
            # Restore original method
            self.validator._count_data_files = original_count_method

    def test_scope_threshold_validation(self):
        """Test validation thresholds for different scopes"""

        scopes_to_test = ["f2", "m7", "n100", "v3k"]

        for scope in scopes_to_test:
            # Test with insufficient data
            mock_count_method = lambda: {
                "sec_edgar_files": 1,  # Way below any threshold
                "yfinance_files": 1,  # Way below any threshold
                "total_files": 2,  # Way below any threshold
                "locations_checked": [f"test_{scope}"],
            }

            original_method = self.validator._count_data_files
            self.validator._count_data_files = mock_count_method

            try:
                result = self.validator.validate_data_collection(scope)

                # Should fail for insufficient data
                assert not result["passed"], f"Scope {scope} should fail with insufficient data"
                assert len(result["critical_failures"]) > 0

                # Check that thresholds are mentioned in failures
                failures_str = " ".join(result["critical_failures"])
                assert "SEC Edgar files" in failures_str or "YFinance files" in failures_str

            finally:
                self.validator._count_data_files = original_method

    def test_validation_report_export(self):
        """Test validation report export functionality"""

        import tempfile

        # Create a test validation result
        test_result = {
            "scope": "f2",
            "timestamp": "2025-01-28T12:00:00",
            "passed": True,
            "critical_failures": [],
            "warnings": ["Test warning"],
            "metrics": {"total_files": 50},
        }

        # Export to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            output_path = Path(tmp.name)

        try:
            exported_path = self.validator.export_validation_report(test_result, output_path)

            assert exported_path.exists(), "Report file should be created"

            # Verify report content
            with open(exported_path, "r") as f:
                exported_data = json.load(f)

            assert exported_data["scope"] == "f2"
            assert exported_data["passed"] == True
            assert "Test warning" in exported_data["warnings"]

        finally:
            # Cleanup
            if output_path.exists():
                output_path.unlink()


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
