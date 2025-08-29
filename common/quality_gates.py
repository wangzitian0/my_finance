#!/usr/bin/env python3
"""
Data Pipeline Quality Gates System
Comprehensive validation to prevent build regressions and ensure data quality.

Addresses critical issue where builds showed SUCCESS with 0 data files,
preventing future regressions in data collection pipeline.
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.directory_manager import DataLayer, DirectoryManager

logger = logging.getLogger(__name__)


class DataQualityValidation:
    """Data volume and quality validation for build systems"""

    # Critical volume thresholds - builds MUST fail if below these numbers
    CRITICAL_THRESHOLDS = {
        "f2": {  # F2 development scope - 2 companies (MSFT + NVDA)
            "sec_edgar_files": 20,  # Minimum SEC documents
            "yfinance_files": 5,  # Minimum YFinance data files
            "total_files": 25,  # Total minimum files
        },
        "m7": {  # M7 testing scope - 7 companies (Magnificent 7)
            "sec_edgar_files": 100,  # Minimum SEC documents
            "yfinance_files": 20,  # Minimum YFinance data files
            "total_files": 120,  # Total minimum files
        },
        "n100": {  # N100 validation scope - NASDAQ 100
            "sec_edgar_files": 1000,  # Minimum SEC documents
            "yfinance_files": 300,  # Minimum YFinance data files
            "total_files": 1300,  # Total minimum files
        },
        "v3k": {  # V3K production scope - VTI 3500+
            "sec_edgar_files": 5000,  # Minimum SEC documents
            "yfinance_files": 1500,  # Minimum YFinance data files
            "total_files": 6500,  # Total minimum files
        },
    }

    # Warning thresholds - log warnings but don't fail build
    WARNING_THRESHOLDS = {
        "regression_percentage": 0.5,  # Warn if 50%+ drop from previous build
        "expected_multiplier": 0.8,  # Warn if less than 80% of expected
    }

    def __init__(self):
        self.directory_manager = DirectoryManager()
        self.data_root = self.directory_manager.get_data_root()

    def validate_data_collection(self, scope: str, build_metadata: Dict = None) -> Dict:
        """
        Comprehensive data collection validation

        Args:
            scope: Build scope (f2, m7, n100, v3k)
            build_metadata: Optional build tracking metadata

        Returns:
            Dict with validation results and detailed metrics
        """
        validation_result = {
            "scope": scope,
            "timestamp": datetime.now().isoformat(),
            "passed": False,
            "critical_failures": [],
            "warnings": [],
            "metrics": {},
            "recommendation": "",
        }

        try:
            # Get scope-specific thresholds
            if scope not in self.CRITICAL_THRESHOLDS:
                validation_result["critical_failures"].append(
                    f"Unknown scope: {scope}. Valid scopes: {list(self.CRITICAL_THRESHOLDS.keys())}"
                )
                return validation_result

            thresholds = self.CRITICAL_THRESHOLDS[scope]

            # Count data files in all relevant locations
            file_counts = self._count_data_files()
            validation_result["metrics"] = file_counts

            # Critical volume validation
            critical_failures = []

            # Check SEC Edgar files
            if file_counts["sec_edgar_files"] < thresholds["sec_edgar_files"]:
                critical_failures.append(
                    f"SEC Edgar files: {file_counts['sec_edgar_files']} < {thresholds['sec_edgar_files']} (minimum)"
                )

            # Check YFinance files
            if file_counts["yfinance_files"] < thresholds["yfinance_files"]:
                critical_failures.append(
                    f"YFinance files: {file_counts['yfinance_files']} < {thresholds['yfinance_files']} (minimum)"
                )

            # Check total files
            if file_counts["total_files"] < thresholds["total_files"]:
                critical_failures.append(
                    f"Total files: {file_counts['total_files']} < {thresholds['total_files']} (minimum)"
                )

            # Zero data collection - CRITICAL FAILURE
            if file_counts["total_files"] == 0:
                critical_failures.append(
                    "ZERO DATA COLLECTION DETECTED - Build marked as FAILED to prevent regression"
                )

            validation_result["critical_failures"] = critical_failures

            # Warnings for potential issues
            warnings = self._generate_warnings(scope, file_counts, build_metadata)
            validation_result["warnings"] = warnings

            # Overall validation result
            validation_result["passed"] = len(critical_failures) == 0

            # Generate recommendations
            validation_result["recommendation"] = self._generate_recommendation(
                validation_result["passed"], critical_failures, warnings, scope
            )

            return validation_result

        except Exception as e:
            validation_result["critical_failures"].append(f"Validation system error: {str(e)}")
            validation_result["recommendation"] = "Fix validation system before proceeding"
            logger.error(f"Data quality validation failed: {e}")
            return validation_result

    def _count_data_files(self) -> Dict[str, int]:
        """Count data files in all relevant data layer locations"""
        file_counts = {
            "sec_edgar_files": 0,
            "yfinance_files": 0,
            "total_files": 0,
            "locations_checked": [],
        }

        try:
            # Check RAW_DATA layer
            raw_data_path = self.data_root / "stage_00_raw"
            if raw_data_path.exists():
                sec_raw = raw_data_path / "sec-edgar"
                if sec_raw.exists():
                    sec_files = len(list(sec_raw.rglob("*.txt")))
                    file_counts["sec_edgar_files"] += sec_files
                    file_counts["locations_checked"].append(
                        f"stage_00_raw/sec-edgar: {sec_files} files"
                    )

                yf_raw = raw_data_path / "yfinance"
                if yf_raw.exists():
                    yf_files = len(list(yf_raw.rglob("*.json")))
                    file_counts["yfinance_files"] += yf_files
                    file_counts["locations_checked"].append(
                        f"stage_00_raw/yfinance: {yf_files} files"
                    )

            # Check DAILY_DELTA layer
            delta_data_path = self.data_root / "stage_01_daily_delta"
            if delta_data_path.exists():
                sec_delta = delta_data_path / "sec-edgar"
                if sec_delta.exists():
                    sec_files = len(list(sec_delta.rglob("*.txt")))
                    file_counts["sec_edgar_files"] += sec_files
                    file_counts["locations_checked"].append(
                        f"stage_01_daily_delta/sec-edgar: {sec_files} files"
                    )

                yf_delta = delta_data_path / "yfinance"
                if yf_delta.exists():
                    yf_files = len(list(yf_delta.rglob("*.json")))
                    file_counts["yfinance_files"] += yf_files
                    file_counts["locations_checked"].append(
                        f"stage_01_daily_delta/yfinance: {yf_files} files"
                    )

            # Check LEGACY EXTRACT layer (for backward compatibility)
            legacy_data_path = self.data_root / "data" / "stage_01_extract"
            if legacy_data_path.exists():
                sec_legacy = legacy_data_path / "sec_edgar"
                if sec_legacy.exists():
                    sec_files = len(list(sec_legacy.rglob("*.txt")))
                    file_counts["sec_edgar_files"] += sec_files
                    file_counts["locations_checked"].append(
                        f"data/stage_01_extract/sec_edgar: {sec_files} files"
                    )

                yf_legacy = legacy_data_path / "yfinance"
                if yf_legacy.exists():
                    yf_files = len(list(yf_legacy.rglob("*.json")))
                    file_counts["yfinance_files"] += yf_files
                    file_counts["locations_checked"].append(
                        f"data/stage_01_extract/yfinance: {yf_files} files"
                    )

            # Calculate totals
            file_counts["total_files"] = (
                file_counts["sec_edgar_files"] + file_counts["yfinance_files"]
            )

        except Exception as e:
            logger.error(f"Error counting data files: {e}")
            file_counts["error"] = str(e)

        return file_counts

    def _generate_warnings(
        self, scope: str, file_counts: Dict, build_metadata: Dict = None
    ) -> List[str]:
        """Generate warnings for potential data quality issues"""
        warnings = []

        try:
            thresholds = self.CRITICAL_THRESHOLDS[scope]
            warning_thresholds = self.WARNING_THRESHOLDS

            # Check for significant reduction from expected
            for file_type in ["sec_edgar_files", "yfinance_files", "total_files"]:
                expected = thresholds[file_type]
                actual = file_counts[file_type]

                if actual < expected * warning_thresholds["expected_multiplier"]:
                    percentage = (actual / expected) * 100 if expected > 0 else 0
                    warnings.append(
                        f"{file_type}: {actual} is {percentage:.1f}% of expected {expected} (< 80% threshold)"
                    )

            # Check for regression if previous build data available
            if build_metadata and "previous_build_files" in build_metadata:
                prev_total = build_metadata["previous_build_files"]
                current_total = file_counts["total_files"]

                if prev_total > 0:
                    reduction_ratio = (prev_total - current_total) / prev_total
                    if reduction_ratio > warning_thresholds["regression_percentage"]:
                        warnings.append(
                            f"Significant regression: {current_total} files vs {prev_total} previous "
                            f"({reduction_ratio:.1%} reduction > 50% threshold)"
                        )

            # Imbalanced data source warnings
            if file_counts["sec_edgar_files"] == 0 and file_counts["yfinance_files"] > 0:
                warnings.append("SEC Edgar collection failed - only YFinance data available")
            elif file_counts["yfinance_files"] == 0 and file_counts["sec_edgar_files"] > 0:
                warnings.append("YFinance collection failed - only SEC Edgar data available")

        except Exception as e:
            warnings.append(f"Warning generation failed: {e}")

        return warnings

    def _generate_recommendation(
        self, passed: bool, failures: List[str], warnings: List[str], scope: str
    ) -> str:
        """Generate actionable recommendation based on validation results"""

        if not passed:
            if any("ZERO DATA COLLECTION" in failure for failure in failures):
                return (
                    "CRITICAL: Zero data collection detected. This build MUST be marked as FAILED. "
                    "Check ETL pipeline configuration and data source connectivity. "
                    "Run 'p3 env-status' to verify environment setup."
                )
            else:
                return (
                    f"BUILD FAILURE: Data volume below critical thresholds for {scope.upper()} scope. "
                    "Review ETL pipeline logs, check data source connectivity, and verify ticker configurations. "
                    "Do not proceed with DCF analysis until data collection is fixed."
                )

        elif warnings:
            return (
                f"BUILD WARNING: Data collection successful but with concerns for {scope.upper()} scope. "
                "Monitor data quality trends and investigate any significant reductions. "
                "Consider running validation tests before DCF analysis."
            )
        else:
            return f"BUILD SUCCESS: Data collection validated for {scope.upper()} scope. Safe to proceed with DCF analysis."

    def export_validation_report(self, validation_result: Dict, output_path: Path = None) -> Path:
        """Export detailed validation report for build tracking"""

        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = (
                self.data_root / f"quality_validation_{validation_result['scope']}_{timestamp}.json"
            )

        try:
            with open(output_path, "w") as f:
                json.dump(validation_result, f, indent=2)

            logger.info(f"Quality validation report exported: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to export validation report: {e}")
            raise


class DCFReportQualityValidator:
    """DCF report quality validation to detect mock data vs real SEC filings"""

    # Realistic ranges for Magnificent 7 companies (as of 2024-2025)
    COMPANY_METRICS_VALIDATION = {
        "MSFT": {
            "market_cap_range": (2_500_000_000_000, 3_500_000_000_000),  # $2.5T - $3.5T
            "industry_keywords": ["software", "technology", "cloud", "enterprise"],
            "rd_intensity_min": 0.10,  # R&D should be >10% of revenue
        },
        "NVDA": {
            "market_cap_range": (2_000_000_000_000, 4_000_000_000_000),  # $2T - $4T
            "industry_keywords": ["semiconductor", "gpu", "ai", "chip", "hardware"],
            "rd_intensity_min": 0.15,  # R&D should be >15% of revenue
        },
        "AAPL": {
            "market_cap_range": (2_800_000_000_000, 4_000_000_000_000),  # $2.8T - $4T
            "industry_keywords": ["technology", "hardware", "consumer", "electronics"],
            "rd_intensity_min": 0.05,  # R&D should be >5% of revenue
        },
        "GOOGL": {
            "market_cap_range": (1_500_000_000_000, 2_500_000_000_000),  # $1.5T - $2.5T
            "industry_keywords": ["technology", "software", "search", "advertising"],
            "rd_intensity_min": 0.12,  # R&D should be >12% of revenue
        },
        "META": {
            "market_cap_range": (800_000_000_000, 1_500_000_000_000),  # $800B - $1.5T
            "industry_keywords": ["technology", "social", "software", "advertising"],
            "rd_intensity_min": 0.18,  # R&D should be >18% of revenue
        },
        "TSLA": {
            "market_cap_range": (700_000_000_000, 1_200_000_000_000),  # $700B - $1.2T
            "industry_keywords": ["automotive", "electric", "vehicle", "energy"],
            "rd_intensity_min": 0.03,  # R&D should be >3% of revenue
        },
        "AMZN": {
            "market_cap_range": (1_400_000_000_000, 2_000_000_000_000),  # $1.4T - $2T
            "industry_keywords": ["technology", "e-commerce", "cloud", "retail"],
            "rd_intensity_min": 0.10,  # R&D should be >10% of revenue
        },
    }

    # Mock data detection patterns
    MOCK_DATA_INDICATORS = [
        "1500b",  # Unrealistic simplified market cap format
        "rd_intensity: 0.0",  # Zero R&D intensity (unrealistic)
        "mock",
        "test",
        "placeholder",
        "example",  # Direct mock indicators
    ]

    def validate_dcf_report(self, ticker: str, dcf_data: Dict) -> Dict:
        """
        Validate DCF report quality and detect mock data usage

        Args:
            ticker: Stock ticker (e.g., 'MSFT', 'NVDA')
            dcf_data: DCF analysis data dictionary

        Returns:
            Dict with validation results and quality metrics
        """
        validation_result = {
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "passed": False,
            "quality_failures": [],
            "warnings": [],
            "mock_data_detected": False,
            "recommendation": "",
        }

        try:
            if ticker not in self.COMPANY_METRICS_VALIDATION:
                validation_result["warnings"].append(f"No validation rules for ticker {ticker}")
                validation_result["passed"] = True  # Pass unknown tickers with warning
                return validation_result

            expected_metrics = self.COMPANY_METRICS_VALIDATION[ticker]
            quality_failures = []

            # Market cap validation
            if "market_cap" in dcf_data:
                market_cap = self._parse_market_cap(dcf_data["market_cap"])
                if market_cap:
                    min_cap, max_cap = expected_metrics["market_cap_range"]
                    if not (min_cap <= market_cap <= max_cap):
                        quality_failures.append(
                            f"Market cap ${market_cap:,.0f} outside expected range "
                            f"${min_cap:,.0f} - ${max_cap:,.0f}"
                        )

            # Industry classification validation
            if "industry" in dcf_data:
                industry_text = str(dcf_data["industry"]).lower()
                expected_keywords = expected_metrics["industry_keywords"]
                if not any(keyword in industry_text for keyword in expected_keywords):
                    quality_failures.append(
                        f"Industry '{dcf_data['industry']}' doesn't match expected keywords: {expected_keywords}"
                    )

            # R&D intensity validation
            if "rd_intensity" in dcf_data:
                rd_intensity = self._parse_percentage(dcf_data["rd_intensity"])
                if rd_intensity is not None:
                    min_rd = expected_metrics["rd_intensity_min"]
                    if rd_intensity < min_rd:
                        quality_failures.append(
                            f"R&D intensity {rd_intensity:.1%} below expected minimum {min_rd:.1%}"
                        )

            # Mock data detection
            mock_detected = self._detect_mock_data(dcf_data)
            validation_result["mock_data_detected"] = mock_detected
            if mock_detected:
                quality_failures.append(
                    "Mock data patterns detected - report may not use real SEC filings"
                )

            validation_result["quality_failures"] = quality_failures
            validation_result["passed"] = len(quality_failures) == 0 and not mock_detected

            # Generate recommendation
            if not validation_result["passed"]:
                if mock_detected:
                    validation_result["recommendation"] = (
                        "CRITICAL: Mock data detected in DCF report. Verify SEC filing integration "
                        "and ensure real financial data is being used for analysis."
                    )
                else:
                    validation_result["recommendation"] = (
                        f"DCF report quality issues detected for {ticker}. Review data sources "
                        "and SEC filing integration to ensure accurate financial metrics."
                    )
            else:
                validation_result["recommendation"] = f"DCF report quality validated for {ticker}"

            return validation_result

        except Exception as e:
            validation_result["quality_failures"].append(f"Validation system error: {str(e)}")
            validation_result["recommendation"] = "Fix DCF validation system before proceeding"
            logger.error(f"DCF report validation failed for {ticker}: {e}")
            return validation_result

    def _parse_market_cap(self, market_cap_str: str) -> Optional[float]:
        """Parse market cap string to numeric value"""
        try:
            if not market_cap_str:
                return None

            # Handle various formats: $1.5T, 1500B, $2,500,000,000,000
            cap_str = str(market_cap_str).replace("$", "").replace(",", "").upper()

            if "T" in cap_str:
                return float(cap_str.replace("T", "")) * 1_000_000_000_000
            elif "B" in cap_str:
                return float(cap_str.replace("B", "")) * 1_000_000_000
            else:
                return float(cap_str)

        except (ValueError, TypeError):
            return None

    def _parse_percentage(self, percentage_str: str) -> Optional[float]:
        """Parse percentage string to decimal value"""
        try:
            if not percentage_str:
                return None

            pct_str = str(percentage_str).replace("%", "")
            value = float(pct_str)

            # Convert to decimal if given as percentage
            if value > 1.0:
                value = value / 100.0

            return value

        except (ValueError, TypeError):
            return None

    def _detect_mock_data(self, dcf_data: Dict) -> bool:
        """Detect mock data patterns in DCF report"""

        # Convert entire data structure to lowercase string for pattern detection
        data_str = json.dumps(dcf_data).lower()

        # Check for direct mock indicators
        for indicator in self.MOCK_DATA_INDICATORS:
            if indicator in data_str:
                return True

        # Check for unrealistic simplified values (common in mock data)
        if "1500b" in data_str or "1.5t" in data_str:  # Oversimplified market caps
            return True

        # Check for zero R&D (unrealistic for tech companies)
        if "rd_intensity" in data_str and ("0.0" in data_str or "0%" in data_str):
            return True

        return False


def run_quality_gate_validation(scope: str = "f2", build_metadata: Dict = None) -> bool:
    """
    Main quality gate validation entry point for build systems

    Args:
        scope: Build scope (f2, m7, n100, v3k)
        build_metadata: Optional build tracking metadata

    Returns:
        bool: True if all quality gates pass, False if build should fail
    """
    print(f"🔍 Running comprehensive quality gate validation for {scope.upper()} scope...")

    # Data pipeline validation
    data_validator = DataQualityValidation()
    data_result = data_validator.validate_data_collection(scope, build_metadata)

    # Print validation results
    print(f"\n📊 DATA PIPELINE VALIDATION RESULTS:")
    print(f"   Scope: {data_result['scope'].upper()}")
    print(f"   Status: {'✅ PASSED' if data_result['passed'] else '❌ FAILED'}")

    if data_result["metrics"]:
        metrics = data_result["metrics"]
        print(f"   SEC Edgar files: {metrics.get('sec_edgar_files', 0)}")
        print(f"   YFinance files: {metrics.get('yfinance_files', 0)}")
        print(f"   Total files: {metrics.get('total_files', 0)}")

    # Show failures and warnings
    if data_result["critical_failures"]:
        print(f"\n❌ CRITICAL FAILURES:")
        for failure in data_result["critical_failures"]:
            print(f"   • {failure}")

    if data_result["warnings"]:
        print(f"\n⚠️  WARNINGS:")
        for warning in data_result["warnings"]:
            print(f"   • {warning}")

    print(f"\n💡 RECOMMENDATION: {data_result['recommendation']}")

    # Export validation report for tracking
    try:
        report_path = data_validator.export_validation_report(data_result)
        print(f"📄 Validation report exported: {report_path}")
    except Exception as e:
        print(f"⚠️  Could not export validation report: {e}")

    return data_result["passed"]


if __name__ == "__main__":
    import sys

    # Command line usage for testing
    scope = sys.argv[1] if len(sys.argv) > 1 else "f2"

    # Run validation
    success = run_quality_gate_validation(scope)

    # Exit with appropriate code for build systems
    sys.exit(0 if success else 1)
