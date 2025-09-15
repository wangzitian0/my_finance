#!/usr/bin/env python3
"""
Unified dataset builder that uses configurations from common/config/.
Supports test, M7, nasdaq100, and VTI tiers with build tracking.
"""

import logging
import os
import sys

# Setup common logger for detailed debugging
sys.path.insert(0, str(os.path.dirname(__file__) + "/../"))
# Create debug logger with both console and file output using SSOT paths
from common.core.directory_manager import directory_manager
from common.utils.logging_setup import setup_logger

logger = setup_logger(
    name="build_dataset",
    level=logging.DEBUG,
    log_dir=str(directory_manager.get_logs_path() / "debug"),
    build_id="f2_build_debug",
    use_file_handler=True,
    use_console_handler=True,
)

logger.info("=== Starting ETL/build_dataset.py ===")
logger.info("Setting up imports...")

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

logger.info("Basic imports completed")

import yaml

logger.info("YAML imported")

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logger.info("Path setup completed")

logger.info("About to import BuildTracker...")
from common.build.build_tracker import BuildTracker

logger.info("BuildTracker imported successfully")

# Check for numpy issues and set fallback mode
NUMPY_ISSUE_DETECTED = False
logger.info("Testing numpy import...")
try:
    import numpy as np

    logger.info("Numpy imported successfully")
except Exception as e:
    if "circular import" in str(e):
        NUMPY_ISSUE_DETECTED = True
        logger.warning("Numpy circular import detected, enabling fallback mode")
    else:
        logger.error(f"Numpy import error: {e}")

logger.info("Initializing SSOT configuration management...")

from common.etl_loader import build_etl_config
from common.core.directory_manager import DataLayer, directory_manager

# Use new ETL loader configuration system
from ETL.tests.test_config import DatasetTier

logger.info("DatasetTier imported successfully")


def tier_to_config_name(tier: DatasetTier) -> str:
    """Convert DatasetTier to new ETL loader config name"""
    mapping = {
        DatasetTier.F2: "f2",
        DatasetTier.M7: "m7",
        DatasetTier.N100: "n100",
        DatasetTier.V3K: "v3k",
    }
    return mapping.get(tier, "f2")


def build_dataset(tier_name: str, config_path: str = None) -> bool:
    """
    Build dataset for specified tier using configuration.

    Args:
        tier_name: Dataset tier (test, m7, nasdaq100, vti)
        config_path: Optional path to specific config file

    Returns:
        bool: Success status
    """
    logger.info(f"=== Entering build_dataset(tier_name={tier_name}, config_path={config_path}) ===")

    try:
        import time

        logger.info("Time module imported")

        start_time = time.time()
        logger.info(f"Build start time: {start_time}")

        print(f"⏱️ [{time.strftime('%H:%M:%S')}] Starting build process...")
        logger.info("Build process starting...")

        # Initialize tier and config
        print(f"⏱️ [{time.strftime('%H:%M:%S')}] Initializing tier and config...")
        logger.info("About to create DatasetTier instance...")
        tier = DatasetTier(tier_name)
        logger.info(f"DatasetTier created: {tier}")

        logger.info("About to load dataset config...")
        # Use new ETL loader system
        try:
            stock_list_name = tier_to_config_name(tier)
            logger.info(f"Stock list name: {stock_list_name}")

            # Build runtime configuration with yfinance and development scenario
            runtime_config = build_etl_config(
                stock_list=stock_list_name,
                data_sources=['yfinance', 'sec_edgar'],
                scenario='development'
            )
            logger.info(f"Runtime config created: {runtime_config.combination}")

            # Convert to legacy format for compatibility - use API config directly
            config = {
                'companies': runtime_config.stock_list.companies,
                'data_sources': {
                    'yfinance': {
                        'enabled': 'yfinance' in runtime_config.enabled_sources,
                        'api_config': runtime_config.data_sources.get('yfinance', {}).api_config if 'yfinance' in runtime_config.enabled_sources else {}
                    },
                    'sec_edgar': {
                        'enabled': 'sec_edgar' in runtime_config.enabled_sources,
                        'api_config': runtime_config.data_sources.get('sec_edgar', {}).api_config if 'sec_edgar' in runtime_config.enabled_sources else {}
                    }
                }
            }
            config_description = runtime_config.combination
        except Exception as e:
            logger.error(f"ETL config loading error: {e}")
            return False
        logger.info(f"Config loaded: {config}")

        print(f"⏱️ [{time.strftime('%H:%M:%S')}] Config loaded in {time.time() - start_time:.1f}s")
        logger.info(f"Config loaded in {time.time() - start_time:.1f}s")

        logger.info("About to print build info...")
        print(f"🔧 Building {tier.value} dataset...")

        print(f"   Configuration: {config_description}")
        print(f"   Expected tickers: {len(config.get('companies', {}))}")
        logger.info("Build info printed")

        # Initialize build tracker
        logger.info("About to print build tracker init message...")
        print(f"⏱️ [{time.strftime('%H:%M:%S')}] Initializing build tracker...")
        logger.info("About to create BuildTracker instance...")
        tracker = BuildTracker()
        logger.info("BuildTracker instance created")

        logger.info("About to call tracker.start_build()...")
        build_id = tracker.start_build(tier.value, f"p3 build run {tier_name}")
        logger.info(f"Build started with ID: {build_id}")
        logger.info("About to print build tracker initialized message...")
        print(f"⏱️ [{time.strftime('%H:%M:%S')}] Build tracker initialized, ID: {build_id}")
        logger.info("Build tracker initialized message printed")

        # Load YAML configuration
        logger.info("About to print YAML loading message...")
        print(f"⏱️ [{time.strftime('%H:%M:%S')}] Loading YAML configuration...")
        logger.info("About to assign yaml_config...")
        yaml_config = config
        logger.info("yaml_config assigned")
        logger.info("About to print YAML config loaded message...")
        print(f"⏱️ [{time.strftime('%H:%M:%S')}] YAML config loaded: {list(yaml_config.keys())}")
        logger.info("YAML config loaded message printed")

        # Start extract stage
        logger.info("About to print extract stage message...")
        print(f"⏱️ [{time.strftime('%H:%M:%S')}] Starting stage_01_extract...")
        logger.info("Extract stage message printed")
        logger.info("About to call tracker.start_stage...")
        tracker.start_stage("stage_01_extract")
        logger.info("tracker.start_stage completed")

        # Check if yfinance is enabled in data_sources
        logger.info("About to check yfinance data sources...")
        data_sources = yaml_config.get("data_sources", {})
        logger.info(f"data_sources obtained: {data_sources}")
        logger.info("About to check yfinance enabled status...")
        yfinance_config = data_sources.get("yfinance", {})
        logger.info(f"yfinance_config: {yfinance_config}")
        yfinance_enabled = yfinance_config.get("enabled", False)
        logger.info(f"yfinance_enabled: {yfinance_enabled}")

        if yfinance_enabled:
            logger.info("YFinance is enabled, building data...")
            print(f"⏱️ [{time.strftime('%H:%M:%S')}] Building YFinance data...")
            yf_start = time.time()
            success = build_yfinance_data(tier, yaml_config, tracker)
            print(
                f"⏱️ [{time.strftime('%H:%M:%S')}] YFinance data completed in {time.time() - yf_start:.1f}s, success: {success}"
            )
            if not success:
                tracker.fail_stage("stage_01_extract", "yfinance data collection failed")
                return False
        else:
            logger.info("YFinance is disabled, skipping...")
            print(f"⏱️ [{time.strftime('%H:%M:%S')}] YFinance disabled, skipping...")

        # Check SEC Edgar data source configuration
        logger.info("About to check SEC Edgar configuration...")
        print(f"⏱️ [{time.strftime('%H:%M:%S')}] Checking SEC Edgar configuration...")
        logger.info("SEC Edgar configuration message printed")
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

        try:
            print(f"⏱️ [{time.strftime('%H:%M:%S')}] Running DCF analysis...")
            companies_analyzed = run_dcf_analysis(tier, tracker)
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

        try:
            print(f"⏱️ [{time.strftime('%H:%M:%S')}] Running report generation...")
            reports_generated = run_report_generation(tier, tracker)
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

        # Get YFinance config from data sources (using API config directly)
        data_sources = yaml_config.get("data_sources", {})
        yfinance_config = data_sources.get("yfinance", {})
        if not yfinance_config.get("enabled", False):
            print(f"   📈 YFinance collection disabled for {tier.value}")
            return True

        # Use API config directly from the centralized configuration
        yf_api_config = yfinance_config.get("api_config", {})

        # Extract tickers from companies configuration passed from runtime config
        companies_config = yaml_config.get("companies", {})

        # Handle both dict (ticker as key) and list formats
        if isinstance(companies_config, dict):
            tickers = list(companies_config.keys())
        elif isinstance(companies_config, list):
            tickers = [
                company.get("ticker", company.get("symbol", "")) for company in companies_config
            ]
        else:
            tickers = []

        print(f"   📈 Collecting yfinance data...")
        print(f"   Tickers: {len(tickers)}")
        print(f"   Config: Using centralized API config")

        # Create config from centralized API configuration
        yf_config = yf_api_config.copy()
        yf_config["tickers"] = tickers

        # Ensure essential config fields are present with defaults
        if "user_agent" not in yf_config:
            yf_config["user_agent"] = "my_finance/1.0"
        if "timeout_seconds" not in yf_config:
            yf_config["timeout_seconds"] = 30

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
    """Build SEC Edgar data using SSOT configuration system"""
    try:
        from ETL.sec_edgar_spider import run_job

        # Check if SEC Edgar is enabled in data sources (SSOT config)
        data_sources = yaml_config.get("data_sources", {})
        sec_config = data_sources.get("sec_edgar", {})

        if not sec_config.get("enabled", False):
            print(f"   ⚪ SEC Edgar disabled in {tier.value} configuration")
            return True

        print(f"   📊 Collecting SEC Edgar data using new ETL config...")

        # Extract companies from yaml_config (passed from runtime config)
        companies = yaml_config.get("companies", {})

        # Use API config directly from the centralized configuration
        sec_api_config = sec_config.get("api_config", {})

        print(f"   📄 Using SSOT SEC config with {len(companies)} companies")

        tracker.log_stage_output(
            "stage_01_extract", f"Starting SSOT SEC Edgar collection for {tier.value}"
        )

        # Create temporary config for SEC spider using SSOT configuration
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

        # Build SEC config from centralized API configuration
        sec_spider_config = {
            "tickers": ciks,
            "count": 8,
            "file_types": ["10K", "10Q", "8K"],
            "email": sec_api_config.get("user_agent", "ZitianSG (wangzitian0@gmail.com)"),
            "collection": sec_api_config.get("collection", {}),

            # Include other API config parameters
            "base_url": sec_api_config.get("base_url", "https://data.sec.gov"),
            "timeout_seconds": sec_api_config.get("timeout_seconds", 60),
            "rate_limits": sec_api_config.get("rate_limits", {}),
        }

        # Write temporary config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as temp_f:
            yaml.dump(sec_spider_config, temp_f, default_flow_style=False)
            temp_config_path = temp_f.name

        print(f"   📋 Generated SEC config from SSOT system: {len(ciks)} CIKs")

        # Run SEC Edgar spider with SSOT config
        run_job(temp_config_path)

        # Clean up temp file
        import os

        os.unlink(temp_config_path)

        tracker.log_stage_output("stage_01_extract", "SSOT SEC Edgar collection completed")
        return True

    except Exception as e:
        print(f"   ❌ SSOT SEC Edgar collection failed: {e}")
        tracker.log_stage_output("stage_01_extract", f"SSOT SEC Edgar error: {e}")
        return False


def run_dcf_analysis(tier: DatasetTier, tracker: BuildTracker) -> int:
    """Run DCF analysis on available data with SEC document integration"""

    # Check critical dependencies before starting
    print(f"   🔍 Checking DCF analysis dependencies...")
    try:
        # Test semantic retrieval availability
        from pathlib import Path as PathCheck

        from ETL.semantic_retrieval import SemanticRetriever

        # Try to create a minimal semantic retriever to test dependencies
        # Use SSOT path for embeddings check
        embeddings_path = directory_manager.get_subdir_path(DataLayer.PROCESSED_DATA, "embeddings")
        test_path = PathCheck(str(embeddings_path))
        if not test_path.exists():
            raise RuntimeError("Embeddings directory not found - semantic retrieval unavailable")

        test_retriever = SemanticRetriever(test_path)
        # This will trigger the dependency check and raise an exception if dependencies are missing
        test_retriever.load_embeddings()
        print(f"   ✅ Semantic retrieval dependencies verified")

    except Exception as e:
        error_msg = f"DCF analysis dependencies not available: {e}"
        print(f"   ❌ {error_msg}")
        tracker.log_stage_output("stage_04_analysis", error_msg)
        raise RuntimeError(error_msg) from e

    try:
        # Import SEC-integrated DCF analyzer
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from dcf_engine.llm_dcf_generator import LLMDCFGenerator

        print(f"   📊 Running SEC-enhanced DCF analysis for {tier.value}...")
        tracker.log_stage_output(
            "stage_04_analysis", f"Starting SEC-enhanced DCF analysis for {tier.value}"
        )

        # Get companies list from new ETL configuration system
        # Build runtime config to get companies
        stock_list_name = tier_to_config_name(tier)
        runtime_config = build_etl_config(
            stock_list=stock_list_name,
            data_sources=['yfinance', 'sec_edgar'],
            scenario='development'
        )

        companies = runtime_config.stock_list.companies

        if not companies:
            print(f"   ⚠️  No companies found in {tier.value} configuration")
            return 0

        # Use SEC-integrated DCF generator
        analyzer = LLMDCFGenerator(config_path=None)
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


def run_report_generation(tier: DatasetTier, tracker: BuildTracker) -> int:
    """Generate final reports"""

    # Check critical dependencies before starting (same as DCF analysis)
    print(f"   🔍 Checking report generation dependencies...")
    try:
        # Test semantic retrieval availability
        from pathlib import Path as PathCheck

        from ETL.semantic_retrieval import SemanticRetriever

        # Try to create a minimal semantic retriever to test dependencies
        # Use SSOT path for embeddings check
        embeddings_path = directory_manager.get_subdir_path(DataLayer.PROCESSED_DATA, "embeddings")
        test_path = PathCheck(str(embeddings_path))
        if not test_path.exists():
            raise RuntimeError("Embeddings directory not found - semantic retrieval unavailable")

        test_retriever = SemanticRetriever(test_path)
        # This will trigger the dependency check and raise an exception if dependencies are missing
        test_retriever.load_embeddings()
        print(f"   ✅ Report generation dependencies verified")

    except Exception as e:
        error_msg = f"Report generation dependencies not available: {e}"
        print(f"   ❌ {error_msg}")
        tracker.log_stage_output("stage_05_reporting", error_msg)
        raise RuntimeError(error_msg) from e

    try:
        # Import DCF report generator
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from dcf_engine.llm_dcf_generator import LLMDCFGenerator

        print(f"   📄 Generating reports for {tier.value}...")
        tracker.log_stage_output(
            "stage_05_reporting", f"Starting report generation for {tier.value}"
        )

        # Get companies list from new ETL configuration system
        # Build runtime config to get companies
        stock_list_name = tier_to_config_name(tier)
        runtime_config = build_etl_config(
            stock_list=stock_list_name,
            data_sources=['yfinance', 'sec_edgar'],
            scenario='development'
        )

        # Extract company tickers from configuration
        tickers = list(runtime_config.stock_list.companies.keys())

        # Default to M7 if no specific tickers found
        if not tickers:
            print(f"   ⚠️  No companies found in {tier.value} configuration, using M7 default")
            tickers = None  # Will use M7 default
        else:
            print(f"   📊 Generating report for {len(tickers)} companies: {', '.join(tickers)}")

        # Initialize DCF generator for report generation
        analyzer = LLMDCFGenerator(config_path=None)

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
        # Use new ETL configuration management
        stock_list_name = tier_to_config_name(tier)
        runtime_config = build_etl_config(
            stock_list=stock_list_name,
            data_sources=['yfinance', 'sec_edgar'],
            scenario='development'
        )

        # Estimate expected files based on stock count
        expected_counts = {
            "yfinance_files": len(runtime_config.stock_list.companies) * 3  # rough estimate
        }

        # Use SSOT directory manager for paths
        extract_path = directory_manager.get_layer_path(DataLayer.RAW_DATA)
        paths = {
            "yfinance": directory_manager.get_subdir_path(DataLayer.RAW_DATA, "yfinance"),
            "sec_edgar": directory_manager.get_subdir_path(DataLayer.RAW_DATA, "sec_edgar"),
        }

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
    logger.info("=== Entering main() function ===")
    parser = argparse.ArgumentParser(description="Build dataset for specified tier")
    logger.info("ArgumentParser created")
    logger.info("Adding arguments to parser...")
    parser.add_argument(
        "tier",
        choices=["f2", "m7", "n100", "v3k", "test", "nasdaq100", "vti"],
        help="Dataset tier to build (f2/m7/n100/v3k + legacy aliases)",
    )
    parser.add_argument("--config", help="Optional path to specific config file")
    parser.add_argument("--validate", action="store_true", help="Run validation after build")

    logger.info("About to parse arguments...")
    args = parser.parse_args()
    logger.info(
        f"Arguments parsed: tier={args.tier}, config={args.config}, validate={args.validate}"
    )

    logger.info("About to call build_dataset()...")
    success = build_dataset(args.tier, args.config)
    logger.info(f"build_dataset() returned: {success}")

    if success and args.validate:
        tier = DatasetTier(args.tier)
        # Get latest build tracker for validation
        tracker = BuildTracker.get_latest_build()
        if tracker:
            validate_build(tier, tracker)

    return 0 if success else 1


if __name__ == "__main__":
    print("DEBUG: Script starting, about to call main()")
    result = main()
    print(f"DEBUG: main() returned {result}, exiting")
    exit(result)
