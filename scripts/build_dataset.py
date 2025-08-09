#!/usr/bin/env python3
"""
Unified dataset builder that uses configurations from data/config/.
Supports test, M7, nasdaq100, and VTI tiers with build tracking.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.build_tracker import BuildTracker
from tests.test_config import TestConfigManager, DatasetTier

def build_dataset(tier_name: str, config_path: str = None) -> bool:
    """
    Build dataset for specified tier using configuration.
    
    Args:
        tier_name: Dataset tier (test, m7, nasdaq100, vti)
        config_path: Optional path to specific config file
    
    Returns:
        bool: Success status
    """
    
    try:
        # Initialize tier and config
        tier = DatasetTier(tier_name)
        config_manager = TestConfigManager()
        config = config_manager.get_config(tier)
        
        print(f"🔧 Building {tier.value} dataset...")
        print(f"   Configuration: {config.config_file}")
        print(f"   Expected tickers: {len(config.expected_tickers) if config.expected_tickers else 'dynamic'}")
        
        # Initialize build tracker
        tracker = BuildTracker()
        build_id = tracker.start_build(tier.value, f"pixi run build-dataset {tier_name}")
        
        # Load YAML configuration
        yaml_config = config_manager.load_yaml_config(tier)
        
        # Start extract stage
        tracker.start_stage("stage_01_extract")
        
        if "yfinance" in yaml_config.get("source", ""):
            success = build_yfinance_data(tier, yaml_config, tracker)
            if not success:
                tracker.fail_stage("stage_01_extract", "yfinance data collection failed")
                return False
        
        if yaml_config.get("enable_sec_edgar", False):
            success = build_sec_edgar_data(tier, yaml_config, tracker) 
            if not success:
                tracker.add_warning("stage_01_extract", "SEC Edgar data collection failed")
        
        # Complete extract stage
        date_partition = datetime.now().strftime("%Y%m%d")
        tracker.complete_stage("stage_01_extract", partition=date_partition, 
                              artifacts=["yfinance_data.json", "sec_edgar_data.txt"])
        
        # Transform stage (placeholder for now)
        tracker.start_stage("stage_02_transform")
        # TODO: Add actual transformation logic
        tracker.complete_stage("stage_02_transform", partition=date_partition,
                              artifacts=["cleaned_data.json"])
        
        # Load stage (placeholder for now)  
        tracker.start_stage("stage_03_load")
        # TODO: Add actual load logic
        tracker.complete_stage("stage_03_load", partition=date_partition,
                              artifacts=["graph_nodes.json", "dcf_results.json"])
        
        # Complete build
        tracker.complete_build("completed")
        
        print(f"✅ {tier.value} dataset built successfully!")
        print(f"   Build ID: {build_id}")
        print(f"   Build report: {tracker.build_path}/BUILD_MANIFEST.md")
        
        return True
        
    except Exception as e:
        print(f"❌ Build failed: {e}")
        if 'tracker' in locals():
            tracker.complete_build("failed")
        return False

def build_yfinance_data(tier: DatasetTier, yaml_config: dict, tracker: BuildTracker) -> bool:
    """Build yfinance data using spider"""
    try:
        from spider.yfinance_spider import run_job
        
        # Create temp config file path for the spider
        config_manager = TestConfigManager()
        config_path = config_manager.config_dir / config_manager.get_config(tier).config_file
        
        print(f"   📈 Collecting yfinance data...")
        print(f"   Tickers: {len(yaml_config.get('tickers', []))}")
        
        # Log to build tracker
        tracker.log_stage_output("stage_01_extract", f"Starting yfinance collection for {tier.value}")
        
        # Run yfinance spider
        run_job(str(config_path))
        
        tracker.log_stage_output("stage_01_extract", "yfinance collection completed")
        return True
        
    except Exception as e:
        print(f"   ❌ yfinance collection failed: {e}")
        tracker.log_stage_output("stage_01_extract", f"yfinance error: {e}")
        return False

def build_sec_edgar_data(tier: DatasetTier, yaml_config: dict, tracker: BuildTracker) -> bool:
    """Build SEC Edgar data using spider"""
    try:
        from spider.sec_edgar_spider import run_job
        
        # Find SEC Edgar config for this tier
        config_manager = TestConfigManager()
        sec_config_map = {
            DatasetTier.TEST: "sec_edgar_test.yml",  # Create if needed
            DatasetTier.M7: "sec_edgar_m7.yml",
            DatasetTier.NASDAQ100: "sec_edgar_nasdaq100.yml"
        }
        
        sec_config_file = sec_config_map.get(tier)
        if not sec_config_file:
            print(f"   ⚪ SEC Edgar not configured for {tier.value}")
            return True
            
        sec_config_path = config_manager.config_dir / sec_config_file
        
        if not sec_config_path.exists():
            print(f"   ⚪ SEC Edgar config not found: {sec_config_file}")
            return True
        
        print(f"   📊 Collecting SEC Edgar data...")
        
        tracker.log_stage_output("stage_01_extract", f"Starting SEC Edgar collection for {tier.value}")
        
        # Run SEC Edgar spider
        run_job(str(sec_config_path))
        
        tracker.log_stage_output("stage_01_extract", "SEC Edgar collection completed")
        return True
        
    except Exception as e:
        print(f"   ❌ SEC Edgar collection failed: {e}")
        tracker.log_stage_output("stage_01_extract", f"SEC Edgar error: {e}")
        return False

def validate_build(tier: DatasetTier, tracker: BuildTracker) -> bool:
    """Validate the built dataset"""
    try:
        config_manager = TestConfigManager()
        expected_counts = config_manager.get_expected_file_count(tier)
        
        paths = config_manager.get_data_paths(tier)
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
            "validation_passed": actual_files > 0
        }
        
        tracker.save_artifact("stage_01_extract", "validation_results.json", validation_result)
        
        return actual_files > 0
        
    except Exception as e:
        print(f"   ⚠️ Validation failed: {e}")
        return False

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Build dataset for specified tier")
    parser.add_argument("tier", choices=["test", "m7", "nasdaq100", "vti"], 
                       help="Dataset tier to build")
    parser.add_argument("--config", help="Optional path to specific config file")
    parser.add_argument("--validate", action="store_true", help="Run validation after build")
    
    args = parser.parse_args()
    
    success = build_dataset(args.tier, args.config)
    
    if success and args.validate:
        tier = DatasetTier(args.tier)
        # Get latest build tracker for validation
        tracker = BuildTracker.get_latest_build()
        if tracker:
            validate_build(tier, tracker)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())