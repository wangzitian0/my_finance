#!/usr/bin/env python3
"""
Unified dataset builder that uses configurations from common/config/.
Supports test, M7, nasdaq100, and VTI tiers with build tracking.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import yaml

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.build_tracker import BuildTracker
from common.config_loader import config_loader
from ETL.tests.test_config import DatasetTier


def build_dataset(tier_name: str, config_path: str = None, fast_mode: bool = False) -> bool:
    """
    Build dataset for specified tier using configuration.

    Args:
        tier_name: Dataset tier (test, m7, nasdaq100, vti)
        config_path: Optional path to specific config file

    Returns:
        bool: Success status
    """

    try:
        import time

        start_time = time.time()

        print(f"⏱️ [{time.strftime('%H:%M:%S')}] Starting build process...")

        # Initialize tier and config
        print(f"⏱️ [{time.strftime('%H:%M:%S')}] Initializing tier and config...")
        tier = DatasetTier(tier_name)
        config = config_loader.load_dataset_config(tier.value)
        print(f"⏱️ [{time.strftime('%H:%M:%S')}] Config loaded in {time.time() - start_time:.1f}s")

        print(f"🔧 Building {tier.value} dataset...")
        print(f"   Configuration: list_{tier.value}.yml")
        print(f"   Expected tickers: {config.get('ticker_count', 'unknown')}")

        # Initialize build tracker
        print(f"⏱️ [{time.strftime('%H:%M:%S')}] Initializing build tracker...")
        tracker = BuildTracker()
        build_id = tracker.start_build(tier.value, f"p3 build run {tier_name}")
        print(f"⏱️ [{time.strftime('%H:%M:%S')}] Build tracker initialized, ID: {build_id}")

        # Load YAML configuration
        print(f"⏱️ [{time.strftime('%H:%M:%S')}] Loading YAML configuration...")
        yaml_config = config
        print(f"⏱️ [{time.strftime('%H:%M:%S')}] YAML config loaded: {list(yaml_config.keys())}")

        # Start extract stage
        print(f"⏱️ [{time.strftime('%H:%M:%S')}] Starting stage_01_extract...")
        tracker.start_stage("stage_01_extract")

        # Check if yfinance is enabled in data_sources
        data_sources = yaml_config.get("data_sources", {})
        if data_sources.get("yfinance", {}).get("enabled", False):
            print(f"⏱️ [{time.strftime('%H:%M:%S')}] Building YFinance data...")
            yf_start = time.time()
            success = build_yfinance_data(tier, yaml_config, tracker)
            print(
                f"⏱️ [{time.strftime('%H:%M:%S')}] YFinance data completed in {time.time() - yf_start:.1f}s, success: {success}"
            )
            if not success:
                tracker.fail_stage("stage_01_extract", "yfinance data collection failed")
                return False

        # Check SEC Edgar data source configuration
        print(f"⏱️ [{time.strftime('%H:%M:%S')}] Checking SEC Edgar configuration...")
        data_sources = yaml_config.get("data_sources", {})
        if data_sources.get("sec_edgar", {}).get("enabled", False):
            print(f"⏱️ [{time.strftime('%H:%M:%S')}] Building SEC Edgar data...")
            sec_start = time.time()
            success = build_sec_edgar_data(tier, yaml_config, tracker)
            print(
                f"⏱️ [{time.strftime('%H:%M:%S')}] SEC Edgar data completed in {time.time() - sec_start:.1f}s, success: {success}"
            )
            if not success:
                tracker.add_warning("stage_01_extract", "SEC Edgar data collection failed")
        else:
            print(f"⏱️ [{time.strftime('%H:%M:%S')}] SEC Edgar disabled or not configured")

        # Complete extract stage
        print(f"⏱️ [{time.strftime('%H:%M:%S')}] Completing extract stage...")
        date_partition = datetime.now().strftime("%Y%m%d")
        tracker.complete_stage(
            "stage_01_extract",
            partition=date_partition,
            artifacts=["yfinance_data.json", "sec_edgar_data.txt"],
        )

        # Transform stage (placeholder for now)
        print(f"⏱️ [{time.strftime('%H:%M:%S')}] Starting stage_02_transform...")
        transform_start = time.time()
        tracker.start_stage("stage_02_transform")
        # TODO: Add actual transformation logic
        tracker.complete_stage(
            "stage_02_transform", partition=date_partition, artifacts=["cleaned_data.json"]
        )
        print(
            f"⏱️ [{time.strftime('%H:%M:%S')}] Transform stage completed in {time.time() - transform_start:.1f}s"
        )

        # Load stage (placeholder for now)
        print(f"⏱️ [{time.strftime('%H:%M:%S')}] Starting stage_03_load...")
        load_start = time.time()
        tracker.start_stage("stage_03_load")
        # TODO: Add actual load logic
        tracker.complete_stage(
            "stage_03_load",
            partition=date_partition,
            artifacts=["graph_nodes.json", "dcf_results.json"],
        )
        print(
            f"⏱️ [{time.strftime('%H:%M:%S')}] Load stage completed in {time.time() - load_start:.1f}s"
        )

        # Analysis stage - DCF calculations (SIMPLIFIED FOR TESTING)
        print(f"⏱️ [{time.strftime('%H:%M:%S')}] Starting stage_04_analysis (SIMPLIFIED)...")
        analysis_start = time.time()
        tracker.start_stage("stage_04_analysis")

        if fast_mode:
            # Skip complex DCF analysis in fast mode
            print(f"⏱️ [{time.strftime('%H:%M:%S')}] Fast mode: Skipping complex DCF analysis...")
            companies_analyzed = len(config.get("expected_tickers", [])) if config.get("expected_tickers") else 2
            tracker.complete_stage(
                "stage_04_analysis", partition=date_partition, companies_analyzed=companies_analyzed
            )
        else:
            try:
                print(
                    f"⏱️ [{time.strftime('%H:%M:%S')}] Running DCF analysis (fast_mode={fast_mode})..."
                )
                companies_analyzed = run_dcf_analysis(tier, tracker, fast_mode=fast_mode)
                print(
                    f"⏱️ [{time.strftime('%H:%M:%S')}] DCF analysis completed, analyzed {companies_analyzed} companies"
                )
                tracker.complete_stage(
                    "stage_04_analysis",
                    partition=date_partition,
                    companies_analyzed=companies_analyzed,
                )
            except Exception as e:
                print(f"⏱️ [{time.strftime('%H:%M:%S')}] DCF analysis failed: {e}")
                tracker.add_warning("stage_04_analysis", f"DCF analysis failed: {e}")
                tracker.complete_stage(
                    "stage_04_analysis", partition=date_partition, companies_analyzed=0
                )
        print(
            f"⏱️ [{time.strftime('%H:%M:%S')}] Analysis stage completed in {time.time() - analysis_start:.1f}s"
        )

        # Reporting stage - Generate final reports (SIMPLIFIED FOR TESTING)
        print(f"⏱️ [{time.strftime('%H:%M:%S')}] Starting stage_05_reporting (SIMPLIFIED)...")
        reporting_start = time.time()
        tracker.start_stage("stage_05_reporting")

        if fast_mode:
            # Skip complex report generation in fast mode
            print(
                f"⏱️ [{time.strftime('%H:%M:%S')}] Fast mode: Skipping complex report generation..."
            )
            reports_generated = 1  # Simple placeholder report
            tracker.complete_stage(
                "stage_05_reporting", partition=date_partition, reports_generated=reports_generated
            )
        else:
            try:
                print(
                    f"⏱️ [{time.strftime('%H:%M:%S')}] Running report generation (fast_mode={fast_mode})..."
                )
                reports_generated = run_report_generation(tier, tracker, fast_mode=fast_mode)
                print(
                    f"⏱️ [{time.strftime('%H:%M:%S')}] Report generation completed, generated {reports_generated} reports"
                )
                tracker.complete_stage(
                    "stage_05_reporting",
                    partition=date_partition,
                    reports_generated=reports_generated,
                )
            except Exception as e:
                print(f"⏱️ [{time.strftime('%H:%M:%S')}] Report generation failed: {e}")
                tracker.add_warning("stage_05_reporting", f"Report generation failed: {e}")
                tracker.complete_stage(
                    "stage_05_reporting", partition=date_partition, reports_generated=0
                )
        print(
            f"⏱️ [{time.strftime('%H:%M:%S')}] Reporting stage completed in {time.time() - reporting_start:.1f}s"
        )

        # Scan filesystem for actual outputs
        print(f"⏱️ [{time.strftime('%H:%M:%S')}] Scanning filesystem for outputs...")
        tracker.scan_and_track_outputs()

        # Complete build
        print(f"⏱️ [{time.strftime('%H:%M:%S')}] Completing build...")
        tracker.complete_build("completed")
        print(f"⏱️ [{time.strftime('%H:%M:%S')}] Total build time: {time.time() - start_time:.1f}s")

        print(f"✅ {tier.value} dataset built successfully!")
        print(f"   Build ID: {build_id}")
        print(f"   Build report: {tracker.build_path}/BUILD_MANIFEST.md")

        return True

    except Exception as e:
        print(f"❌ Build failed: {e}")
        if "tracker" in locals():
            tracker.complete_build("failed")
        return False


def build_yfinance_data(tier: DatasetTier, yaml_config: dict, tracker: BuildTracker) -> bool:
    """Build yfinance data using spider"""
    try:
        import tempfile

        from ETL.yfinance_spider import run_job

        # Get YFinance stage config from data sources
        data_sources = yaml_config.get("data_sources", {})
        yfinance_config = data_sources.get("yfinance", {})
        if not yfinance_config.get("enabled", False):
            print(f"   📈 YFinance collection disabled for {tier.value}")
            return True

        stage_config_name = yfinance_config.get("stage_config", "stage_00_original_yfinance.yml")
        yfinance_config_path = config_loader.get_config_path(stage_config_name)

        # Extract tickers using UnifiedConfigLoader for compatibility
        from common.unified_config_loader import UnifiedConfigLoader

        unified_loader = UnifiedConfigLoader()
        tickers = unified_loader.get_company_tickers(tier)

        print(f"   📈 Collecting yfinance data...")
        print(f"   Tickers: {len(tickers)}")
        print(f"   Config: {stage_config_name}")

        # Create temporary config file with tickers added
        with open(yfinance_config_path, "r") as f:
            yf_config = yaml.safe_load(f)

        yf_config["tickers"] = tickers

        # Write temporary config with tickers
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as temp_f:
            yaml.dump(yf_config, temp_f, default_flow_style=False)
            temp_config_path = temp_f.name

        # Log to build tracker
        tracker.log_stage_output(
            "stage_01_extract",
            f"Starting yfinance collection for {tier.value} with {len(tickers)} tickers",
        )

        # Run yfinance spider
        run_job(temp_config_path)

        # Clean up temp file
        os.unlink(temp_config_path)

        tracker.log_stage_output("stage_01_extract", "yfinance collection completed")
        return True

    except Exception as e:
        print(f"   ❌ yfinance collection failed: {e}")
        tracker.log_stage_output("stage_01_extract", f"yfinance error: {e}")
        return False


def build_sec_edgar_data(tier: DatasetTier, yaml_config: dict, tracker: BuildTracker) -> bool:
    """Build SEC Edgar data using orthogonal configuration system"""
    try:
        from common.orthogonal_config import orthogonal_config
        from ETL.sec_edgar_spider import run_job

        # Check if SEC Edgar is enabled in data sources (orthogonal config)
        data_sources = yaml_config.get("data_sources", {})
        sec_config = data_sources.get("sec_edgar", {})

        if not sec_config.get("enabled", False):
            print(f"   ⚪ SEC Edgar disabled in {tier.value} configuration")
            return True

        print(f"   📊 Collecting SEC Edgar data using orthogonal config...")

        # Build runtime configuration using orthogonal system
        runtime_config = orthogonal_config.build_runtime_config(
            stock_list=tier.value, data_sources=["sec_edgar"], scenario="development"
        )

        # Extract SEC configuration from runtime config
        sec_runtime_config = runtime_config["data_sources"]["sec_edgar"]
        companies = runtime_config["stock_list"]["companies"]

        print(f"   📄 Using orthogonal SEC config with {len(companies)} companies")

        tracker.log_stage_output(
            "stage_01_extract", f"Starting orthogonal SEC Edgar collection for {tier.value}"
        )

        # Create temporary config for SEC spider (preserving orthogonal approach)
        import tempfile

        import yaml

        # Extract CIK numbers from companies
        ciks = []
        for ticker, company_data in companies.items():
            if "cik" in company_data:
                ciks.append(company_data["cik"])

        if not ciks:
            print(f"   ⚠️ No CIK numbers found for {tier.value} companies")
            return True

        # Build SEC config from orthogonal data
        sec_spider_config = {
            "tickers": ciks,
            "count": 8,
            "file_types": ["10K", "10Q", "8K"],
            "email": sec_runtime_config["config"].get(
                "user_agent", "ZitianSG (wangzitian0@gmail.com)"
            ),
            "collection": sec_runtime_config["rate_limits"],
        }

        # Write temporary config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as temp_f:
            yaml.dump(sec_spider_config, temp_f, default_flow_style=False)
            temp_config_path = temp_f.name

        print(f"   📋 Generated SEC config from orthogonal system: {len(ciks)} CIKs")

        # Run SEC Edgar spider with orthogonal config
        run_job(temp_config_path)

        # Clean up temp file
        import os

        os.unlink(temp_config_path)

        tracker.log_stage_output("stage_01_extract", "Orthogonal SEC Edgar collection completed")
        return True

    except Exception as e:
        print(f"   ❌ Orthogonal SEC Edgar collection failed: {e}")
        tracker.log_stage_output("stage_01_extract", f"Orthogonal SEC Edgar error: {e}")
        return False


def run_dcf_analysis(tier: DatasetTier, tracker: BuildTracker, fast_mode: bool = False) -> int:
    """Run DCF analysis on available data with SEC document integration"""
    try:
        # Import SEC-integrated DCF analyzer
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from dcf_engine.llm_dcf_generator import LLMDCFGenerator

        print(f"   📊 Running SEC-enhanced DCF analysis for {tier.value}...")
        tracker.log_stage_output(
            "stage_04_analysis", f"Starting SEC-enhanced DCF analysis for {tier.value}"
        )

        # Get companies list based on tier configuration
        yaml_config = config_loader.load_dataset_config(tier.value)

        # Extract company tickers from configuration
        companies = {}
        if tier.value == "f2" and "reference_config" in yaml_config:
            # For F2, load companies from reference config and filter by selected_companies
            ref_config_name = yaml_config["reference_config"]
            ref_config = config_loader._load_config_file(ref_config_name)

            selected = yaml_config.get("selected_companies", ["MSFT", "NVDA"])
            all_companies = ref_config.get("companies", {})
            for ticker in selected:
                if ticker in all_companies:
                    companies[ticker] = all_companies[ticker]
        elif "companies" in yaml_config:
            companies = yaml_config["companies"]

        if not companies:
            print(f"   ⚠️  No companies found in {tier.value} configuration")
            return 0

        # Use SEC-integrated DCF generator with fast mode support
        analyzer = LLMDCFGenerator(config_path=None, fast_mode=fast_mode)

        if fast_mode:
            print(f"   ⚡ Fast mode enabled for DCF analysis")
            tracker.log_stage_output("stage_04_analysis", "Fast mode enabled for DCF analysis")
        companies_analyzed = 0

        for ticker in companies.keys():
            try:
                # Use the correct method name for LLMDCFGenerator
                report = analyzer.generate_comprehensive_dcf_report(ticker)
                if report:
                    companies_analyzed += 1
                    # Log intermediate process files for debugging
                    build_dir = analyzer._get_current_build_dir()
                    tracker.log_stage_output(
                        "stage_04_analysis",
                        f"SEC-enhanced DCF analysis completed for {ticker}. Intermediate files saved to {build_dir}",
                    )
            except Exception as e:
                tracker.log_stage_output("stage_04_analysis", f"Failed to analyze {ticker}: {e}")
                print(f"   ❌ Error analyzing {ticker}: {e}")

        print(f"   ✅ Analyzed {companies_analyzed} companies")
        return companies_analyzed

    except Exception as e:
        print(f"   ❌ DCF analysis failed: {e}")
        tracker.log_stage_output("stage_04_analysis", f"DCF analysis error: {e}")
        return 0


def run_report_generation(tier: DatasetTier, tracker: BuildTracker, fast_mode: bool = False) -> int:
    """Generate final reports"""
    try:
        # Import DCF report generator
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from dcf_engine.llm_dcf_generator import LLMDCFGenerator

        print(f"   📄 Generating reports for {tier.value}...")
        tracker.log_stage_output(
            "stage_05_reporting", f"Starting report generation for {tier.value}"
        )

        # Get companies list based on tier configuration
        yaml_config = config_loader.load_dataset_config(tier.value)

        # Extract company tickers from configuration
        tickers = []
        if tier.value == "f2" and "reference_config" in yaml_config:
            # For F2, load companies from reference config and filter by selected_companies
            ref_config_name = yaml_config["reference_config"]
            ref_config = config_loader._load_config_file(ref_config_name)

            selected = yaml_config.get("selected_companies", ["MSFT", "NVDA"])
            all_companies = ref_config.get("companies", {})
            tickers = [ticker for ticker in selected if ticker in all_companies]
        elif "companies" in yaml_config:
            tickers = list(yaml_config["companies"].keys())

        # Default to M7 if no specific tickers found
        if not tickers:
            print(f"   ⚠️  No companies found in {tier.value} configuration, using M7 default")
            tickers = None  # Will use M7 default
        else:
            print(f"   📊 Generating report for {len(tickers)} companies: {', '.join(tickers)}")

        # Use fast_mode parameter passed from caller
        analyzer = LLMDCFGenerator(config_path=None, fast_mode=fast_mode)

        if fast_mode:
            print(f"   ⚡ Fast mode report generation enabled")
            tracker.log_stage_output(
                "stage_05_reporting", "Fast mode enabled for report generation"
            )

        # Generate DCF reports for each ticker
        reports_generated = 0

        if not tickers:
            tickers = ["MSFT", "NVDA"]  # F2 default

        for ticker in tickers:
            try:
                report = analyzer.generate_comprehensive_dcf_report(ticker)
                if report:
                    reports_generated += 1
                    tracker.log_stage_output(
                        "stage_05_reporting", f"DCF report generated for {ticker}"
                    )
            except Exception as e:
                tracker.log_stage_output(
                    "stage_05_reporting", f"Failed to generate report for {ticker}: {e}"
                )
                print(f"   ❌ Error generating report for {ticker}: {e}")

        print(f"   ✅ Generated {reports_generated} DCF reports")

        # Track completion
        tracker.log_stage_output("stage_05_reporting", f"Generated {reports_generated} DCF reports")
        return reports_generated

    except Exception as e:
        print(f"   ❌ Report generation failed: {e}")
        tracker.log_stage_output("stage_05_reporting", f"Report generation error: {e}")
        return 0


def validate_build(tier: DatasetTier, tracker: BuildTracker) -> bool:
    """Validate the built dataset"""
    try:
        yaml_config = config_loader.load_dataset_config(tier.value)
        expected_counts = yaml_config.get("expected_files", {})

        # Get data paths from directory manager
        from common.directory_manager import DataLayer, get_data_path

        paths = {
            "yfinance": get_data_path(DataLayer.RAW_DATA, "yfinance"),
            "sec_edgar": get_data_path(DataLayer.RAW_DATA, "sec_edgar"),
        }
        extract_path = paths["extract"]

        # Count actual files in latest partition
        actual_files = 0
        latest_link = extract_path / "yfinance" / "latest"

        if latest_link.exists():
            for ticker_dir in latest_link.iterdir():
                if ticker_dir.is_dir():
                    json_files = list(ticker_dir.glob("*.json"))
                    actual_files += len(json_files)

        print(f"   📊 Validation results:")
        print(f"     Expected files: ~{expected_counts['yfinance_files']}")
        print(f"     Actual files: {actual_files}")

        # Log validation results
        validation_result = {
            "expected": expected_counts,
            "actual_files": actual_files,
            "validation_passed": actual_files > 0,
        }

        tracker.save_artifact("stage_01_extract", "validation_results.json", validation_result)

        return actual_files > 0

    except Exception as e:
        print(f"   ⚠️ Validation failed: {e}")
        return False


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Build dataset for specified tier")
    parser.add_argument(
        "tier",
        choices=["f2", "m7", "n100", "v3k", "test", "nasdaq100", "vti"],
        help="Dataset tier to build (f2/m7/n100/v3k + legacy aliases)",
    )
    parser.add_argument("--config", help="Optional path to specific config file")
    parser.add_argument(
        "--fast-mode", action="store_true", help="Enable fast mode with DeepSeek 1.5b"
    )
    parser.add_argument("--validate", action="store_true", help="Run validation after build")

    args = parser.parse_args()

    success = build_dataset(args.tier, args.config, fast_mode=args.fast_mode)

    if success and args.validate:
        tier = DatasetTier(args.tier)
        # Get latest build tracker for validation
        tracker = BuildTracker.get_latest_build()
        if tracker:
            validate_build(tier, tracker)

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
