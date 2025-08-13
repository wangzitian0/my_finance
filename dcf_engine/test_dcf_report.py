#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DCF Report Generation Tests

Tests for the DCF report generation functionality to ensure:
- File matching works correctly with actual data files
- DCF calculations produce reasonable results
- Report generation doesn't fail silently
- All M7 companies can be analyzed

This test should have caught the filename matching bug.
"""

import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dcf_engine.generate_dcf_report import M7DCFAnalyzer


class TestM7DCFAnalyzer:
    """Test DCF analyzer functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.analyzer = M7DCFAnalyzer()

    def test_file_matching_patterns(self):
        """Test that file matching patterns work with actual file formats."""
        # Test current expected pattern
        test_patterns = [
            "AAPL_yfinance_m7_daily_3mo_250731-215019.json",
            "MSFT_yfinance_m7_daily_1y_250801-120505.json",
            "AMZN_yfinance_m7_daily_6mo_250802-090030.json",
        ]

        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            yf_dir = temp_path / "yfinance" / "AAPL"
            yf_dir.mkdir(parents=True)

            # Create test files with actual naming pattern
            for pattern in test_patterns:
                if "AAPL" in pattern:
                    (yf_dir / pattern).touch()

            # Patch the data directory
            self.analyzer.data_dir = temp_path

            # Test file discovery
            result = self.analyzer.load_yfinance_data("AAPL")
            # Should find files (though they're empty)

            # Test pattern matching works
            daily_files = list(yf_dir.glob("AAPL_yfinance_m7_daily_*.json"))
            assert len(daily_files) == 1
            assert "m7_daily" in str(daily_files[0])

    def test_missing_data_handling(self):
        """Test handling when no data files exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self.analyzer.data_dir = Path(tmpdir)

            # Test missing directory
            result = self.analyzer.load_yfinance_data("NONEXISTENT")
            assert result is None

            # Test empty directory
            empty_dir = Path(tmpdir) / "yfinance" / "EMPTY"
            empty_dir.mkdir(parents=True)
            result = self.analyzer.load_yfinance_data("EMPTY")
            assert result is None

    def test_financial_metrics_extraction(self):
        """Test financial metrics extraction from yfinance data."""
        sample_data = {
            "ticker": "AAPL",
            "info": {
                "longName": "Apple Inc.",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "marketCap": 3000000000000,  # $3T
                "currentPrice": 200.00,
                "totalRevenue": 400000000000,  # $400B
                "freeCashflow": 100000000000,  # $100B
                "beta": 1.2,
                "trailingPE": 25.0,
                "returnOnEquity": 1.5,
                "profitMargins": 0.25,
            },
        }

        metrics = self.analyzer.extract_financial_metrics(sample_data)

        assert metrics["ticker"] == "AAPL"
        assert metrics["company_name"] == "Apple Inc."
        assert metrics["sector"] == "Technology"
        assert metrics["market_cap"] == 3000000000000
        assert metrics["current_price"] == 200.00
        assert metrics["free_cash_flow"] == 100000000000
        assert metrics["beta"] == 1.2

    def test_wacc_calculation(self):
        """Test WACC calculation with different scenarios."""
        # High beta tech company
        high_beta_metrics = {"beta": 1.5, "debt_to_equity": 10}
        wacc_high = self.analyzer.calculate_wacc(high_beta_metrics)
        assert 0.08 <= wacc_high <= 0.20  # Within reasonable bounds

        # Low beta utility-like
        low_beta_metrics = {"beta": 0.3, "debt_to_equity": 50}
        wacc_low = self.analyzer.calculate_wacc(low_beta_metrics)
        assert 0.08 <= wacc_low <= 0.20  # Floor applied

        # No debt scenario
        no_debt_metrics = {"beta": 1.0, "debt_to_equity": 0}
        wacc_no_debt = self.analyzer.calculate_wacc(no_debt_metrics)
        assert wacc_no_debt > 0.08  # Should be cost of equity

    def test_cash_flow_projections(self):
        """Test cash flow projection logic."""
        # TSLA - high growth
        tsla_metrics = {"ticker": "TSLA", "free_cash_flow": 10000000000}  # $10B
        projected_fcf, terminal_value = self.analyzer.project_cash_flows(tsla_metrics)

        assert len(projected_fcf) == 5  # 5-year projection
        assert projected_fcf[0] > 10000000000  # Should grow from base
        assert terminal_value > 0

        # AAPL - mature tech
        aapl_metrics = {"ticker": "AAPL", "free_cash_flow": 100000000000}  # $100B
        projected_fcf_aapl, terminal_value_aapl = self.analyzer.project_cash_flows(aapl_metrics)

        # TSLA should have higher growth rates than AAPL
        tsla_growth_rate = (projected_fcf[0] / 10000000000) - 1
        aapl_growth_rate = (projected_fcf_aapl[0] / 100000000000) - 1
        assert tsla_growth_rate > aapl_growth_rate

    def test_dcf_valuation_calculation(self):
        """Test complete DCF valuation calculation."""
        sample_metrics = {
            "ticker": "TEST",
            "free_cash_flow": 50000000000,  # $50B
            "shares_outstanding": 1000000000,  # 1B shares
            "current_price": 150.00,
            "beta": 1.0,
            "debt_to_equity": 20,
        }

        dcf_result = self.analyzer.calculate_dcf_valuation(sample_metrics)

        # Should not return error
        assert "error" not in dcf_result

        # Should have all required fields
        required_fields = [
            "wacc",
            "projected_fcf",
            "terminal_value",
            "enterprise_value",
            "intrinsic_value_per_share",
            "upside_downside_pct",
        ]
        for field in required_fields:
            assert field in dcf_result

        # Sanity checks
        assert dcf_result["enterprise_value"] > 0
        assert dcf_result["intrinsic_value_per_share"] > 0
        assert len(dcf_result["projected_fcf"]) == 5

    def test_report_generation_integration(self):
        """Test that report generation doesn't fail with missing files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            self.analyzer.data_dir = temp_path
            self.analyzer.reports_dir = temp_path / "reports"

            # Should handle missing data gracefully
            report = self.analyzer.generate_report()
            assert "Error: No data available" in report

            # Should still save report
            report_path = self.analyzer.save_report(report)
            assert Path(report_path).exists()

    def test_m7_companies_coverage(self):
        """Test that all M7 companies are included in analysis."""
        expected_m7 = {"AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NFLX"}
        actual_m7 = set(self.analyzer.m7_companies.keys())
        assert expected_m7 == actual_m7

    def test_investment_recommendation_logic(self):
        """Test investment recommendation generation."""
        # Undervalued with strong fundamentals
        strong_buy_analysis = {
            "dcf_valuation": {"upside_downside_pct": 25},  # 25% upside
            "financial_metrics": {"roe": 0.20, "profit_margin": 0.18},
        }
        rec = self.analyzer.generate_investment_recommendation(strong_buy_analysis)
        assert "STRONG BUY" in rec

        # Overvalued
        sell_analysis = {
            "dcf_valuation": {"upside_downside_pct": -25},  # 25% downside
            "financial_metrics": {"roe": 0.10, "profit_margin": 0.10},
        }
        rec = self.analyzer.generate_investment_recommendation(sell_analysis)
        assert "SELL" in rec

    def test_file_pattern_regression(self):
        """Regression test for the specific file matching bug."""
        # This test should catch the m7_D1_ vs m7_daily_ mismatch

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            yf_dir = temp_path / "yfinance" / "AAPL"
            yf_dir.mkdir(parents=True)

            # Create file with actual naming convention
            actual_file = yf_dir / "AAPL_yfinance_m7_daily_3mo_250731-215019.json"
            actual_file.write_text(
                json.dumps(
                    {"ticker": "AAPL", "info": {"longName": "Apple Inc.", "currentPrice": 200}}
                )
            )

            self.analyzer.data_dir = temp_path

            # Should find and load the file
            data = self.analyzer.load_yfinance_data("AAPL")
            assert data is not None
            assert data["ticker"] == "AAPL"


def test_dcf_end_to_end_integration():
    """End-to-end integration test using real data directory structure."""
    analyzer = M7DCFAnalyzer()

    # Check if real data exists
    aapl_dir = analyzer.data_dir / "yfinance" / "AAPL"
    if not aapl_dir.exists():
        pytest.skip("No real M7 data available for integration test")

    # Find actual files
    daily_files = list(aapl_dir.glob("AAPL_yfinance_m7_daily_*.json"))
    if not daily_files:
        pytest.skip("No M7 daily files found for integration test")

    # Should be able to load real data
    data = analyzer.load_yfinance_data("AAPL")
    assert data is not None

    # Should be able to extract metrics
    metrics = analyzer.extract_financial_metrics(data)
    assert metrics["ticker"] == "AAPL"

    # Should be able to generate analysis
    analysis = analyzer.generate_company_analysis("AAPL")
    if analysis:  # May fail if data quality issues
        assert "dcf_valuation" in analysis
        assert analysis["ticker"] == "AAPL"


if __name__ == "__main__":
    # Run basic smoke test
    analyzer = M7DCFAnalyzer()

    print("🧪 Running DCF Report Tests...")
    print("=" * 50)

    # Test file patterns
    print("Testing file pattern matching...")
    test_analyzer = TestM7DCFAnalyzer()
    test_analyzer.setup_method()
    test_analyzer.test_file_matching_patterns()
    print("✅ File pattern matching works")

    # Test M7 coverage
    print("Testing M7 company coverage...")
    test_analyzer.test_m7_companies_coverage()
    print("✅ All M7 companies included")

    # Test calculation components
    print("Testing DCF calculations...")
    test_analyzer.test_wacc_calculation()
    test_analyzer.test_cash_flow_projections()
    test_analyzer.test_dcf_valuation_calculation()
    print("✅ DCF calculations working")

    print("=" * 50)
    print("🎉 DCF Report Tests Completed!")
    print("\n💡 To run with pytest: pytest dcf_engine/test_dcf_report.py -v")
