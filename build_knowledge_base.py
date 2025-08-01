#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Knowledge Base Builder for My Finance DCF Analysis Tool

This script implements a layered data management strategy:
- Tier 1 (M7): Stable test dataset, tracked in git
- Tier 2 (NASDAQ100): Buildable dataset, gitignored
- Tier 3 (US-ALL): Full dataset, buildable on-demand

Usage:
    python build_knowledge_base.py --tier m7              # Build M7 stable test set
    python build_knowledge_base.py --tier nasdaq100       # Build NASDAQ100 dataset
    python build_knowledge_base.py --tier us-all          # Build full US dataset
    python build_knowledge_base.py --rebuild              # Rebuild everything
    python build_knowledge_base.py --validate             # Validate existing data
"""

import argparse
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
import subprocess
import yaml
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('knowledge_base_build.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class KnowledgeBaseBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.config_dir = self.data_dir / "config"
        self.original_dir = self.data_dir / "original"
        
        # Data tier configurations
        self.tiers = {
            'm7': {
                'name': 'Magnificent 7',
                'description': 'Stable test dataset for core development',
                'configs': ['job_yfinance_m7.yml', 'sec_edgar_m7.yml'],
                'tracked_in_git': True,
                'max_size_mb': 500  # Keep reasonable for git
            },
            'nasdaq100': {
                'name': 'NASDAQ 100',
                'description': 'Extended validation dataset',
                'configs': ['yfinance_nasdaq100.yml', 'sec_edgar_nasdaq100.yml'],
                'tracked_in_git': False,
                'max_size_mb': 5000  # 5GB limit
            },
            'us-all': {
                'name': 'All US Stocks',
                'description': 'Complete US stock universe',
                'configs': ['yfinance_us_all.yml', 'sec_edgar_us_all.yml'],
                'tracked_in_git': False,
                'max_size_mb': 50000  # 50GB limit
            }
        }
    
    def create_missing_configs(self):
        """Create missing configuration files for NASDAQ100 and US-ALL tiers"""
        
        # Create NASDAQ100 SEC config
        nasdaq100_sec_config = self.config_dir / "sec_edgar_nasdaq100.yml"
        if not nasdaq100_sec_config.exists():
            logger.info("Creating SEC Edgar NASDAQ100 configuration...")
            # This would need to be populated with NASDAQ100 CIK numbers
            nasdaq100_sec_content = {
                'job': 'sec_edgar_nasdaq100',
                'source': 'sec_edgar',
                'description': 'SEC Edgar filings for NASDAQ 100 companies',
                'file_types': ['10K', '10Q', '8K'],
                'email': 'ZitianSG (wangzitian0@gmail.com)',
                'tickers': []  # To be populated with CIK numbers
            }
            with open(nasdaq100_sec_config, 'w') as f:
                yaml.dump(nasdaq100_sec_content, f, default_flow_style=False)
        
        # Create US-ALL configs (placeholder for future implementation)
        us_all_yfinance_config = self.config_dir / "yfinance_us_all.yml"
        if not us_all_yfinance_config.exists():
            logger.info("Creating placeholder US-ALL Yahoo Finance configuration...")
            us_all_content = {
                'job': 'yfinance_us_all',
                'source': 'yfinance',
                'description': 'Yahoo Finance data for all US stocks (placeholder)',
                'note': 'To be implemented: fetch from stock screener APIs',
                'data_periods': [
                    {'oid': 'us_all_D1', 'period': '1y', 'interval': '1d'},
                    {'oid': 'us_all_W7', 'period': '7y', 'interval': '1wk'},
                    {'oid': 'us_all_M30', 'period': '30y', 'interval': '1mo'}
                ]
            }
            with open(us_all_yfinance_config, 'w') as f:
                yaml.dump(us_all_content, f, default_flow_style=False)
    
    def build_tier(self, tier_name, force_rebuild=False):
        """Build data for a specific tier"""
        
        if tier_name not in self.tiers:
            raise ValueError(f"Unknown tier: {tier_name}")
        
        tier_config = self.tiers[tier_name]
        logger.info(f"Building {tier_config['name']} dataset...")
        
        start_time = time.time()
        total_files_processed = 0
        
        for config_file in tier_config['configs']:
            config_path = self.config_dir / config_file
            
            if not config_path.exists():
                logger.warning(f"Configuration file {config_file} not found, skipping...")
                continue
            
            logger.info(f"Processing configuration: {config_file}")
            
            # Check if data already exists and is recent (unless force rebuild)
            if not force_rebuild and self._is_data_recent(config_file, tier_name):
                logger.info(f"Data for {config_file} is recent, skipping...")
                continue
            
            # Run the job
            try:
                result = subprocess.run([
                    sys.executable, 
                    str(self.project_root / "run_job.py"), 
                    config_file
                ], capture_output=True, text=True, timeout=3600)  # 1 hour timeout
                
                if result.returncode == 0:
                    logger.info(f"Successfully processed {config_file}")
                    total_files_processed += 1
                else:
                    logger.error(f"Error processing {config_file}: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                logger.error(f"Timeout processing {config_file}")
            except Exception as e:
                logger.error(f"Exception processing {config_file}: {e}")
        
        build_time = time.time() - start_time
        
        # Generate build report
        self._generate_build_report(tier_name, total_files_processed, build_time)
        
        # Validate data size if not tracked in git
        if not tier_config['tracked_in_git']:
            self._validate_data_size(tier_name)
        
        logger.info(f"Completed building {tier_config['name']} dataset in {build_time:.2f} seconds")
    
    def _is_data_recent(self, config_file, tier_name, max_age_hours=24):
        """Check if data for a config is recent enough"""
        
        # For M7 tier, always check recency; for others, be more flexible
        if tier_name == 'm7':
            max_age_hours = 6  # More frequent updates for test data
        
        # Check log files for recent runs
        log_dir = self.data_dir / "log"
        if not log_dir.exists():
            return False
        
        config_base = config_file.replace('.yml', '')
        recent_logs = []
        
        for log_subdir in log_dir.iterdir():
            if log_subdir.is_dir() and config_base in log_subdir.name:
                for log_file in log_subdir.glob("*.txt"):
                    if log_file.stat().st_mtime > (time.time() - max_age_hours * 3600):
                        recent_logs.append(log_file)
        
        return len(recent_logs) > 0
    
    def _validate_data_size(self, tier_name):
        """Validate that data size doesn't exceed tier limits"""
        
        tier_config = self.tiers[tier_name]
        max_size_bytes = tier_config['max_size_mb'] * 1024 * 1024
        
        # Calculate actual size
        actual_size = 0
        for root, dirs, files in os.walk(self.original_dir):
            for file in files:
                file_path = os.path.join(root, file)
                actual_size += os.path.getsize(file_path)
        
        actual_size_mb = actual_size / (1024 * 1024)
        
        logger.info(f"Data size for {tier_name}: {actual_size_mb:.2f} MB")
        
        if actual_size > max_size_bytes:
            logger.warning(f"Data size ({actual_size_mb:.2f} MB) exceeds limit for {tier_name} ({tier_config['max_size_mb']} MB)")
            
            # For non-git tiers, suggest cleanup
            if not tier_config['tracked_in_git']:
                logger.info("Consider running cleanup to remove old data files")
    
    def _generate_build_report(self, tier_name, files_processed, build_time):
        """Generate a build report"""
        
        report = {
            'tier': tier_name,
            'build_timestamp': datetime.now().isoformat(),
            'files_processed': files_processed,
            'build_time_seconds': round(build_time, 2),
            'data_statistics': self._collect_data_statistics(tier_name)
        }
        
        report_file = self.data_dir / f"build_report_{tier_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Build report saved to: {report_file}")
    
    def _collect_data_statistics(self, tier_name):
        """Collect statistics about the built data"""
        
        stats = {
            'total_companies': 0,
            'sec_filings': 0,
            'yfinance_files': 0,
            'data_size_mb': 0
        }
        
        if not self.original_dir.exists():
            return stats
        
        for data_source_dir in self.original_dir.iterdir():
            if not data_source_dir.is_dir():
                continue
            
            if data_source_dir.name == 'sec-edgar':
                for company_dir in data_source_dir.iterdir():
                    if company_dir.is_dir():
                        stats['total_companies'] += 1
                        for filing_type_dir in company_dir.iterdir():
                            if filing_type_dir.is_dir():
                                stats['sec_filings'] += len(list(filing_type_dir.rglob('*.txt')))
            
            elif data_source_dir.name == 'yfinance':
                for company_dir in data_source_dir.iterdir():
                    if company_dir.is_dir():
                        stats['yfinance_files'] += len(list(company_dir.glob('*.json')))
        
        # Calculate total size
        total_size = 0
        for root, dirs, files in os.walk(self.original_dir):
            for file in files:
                total_size += os.path.getsize(os.path.join(root, file))
        
        stats['data_size_mb'] = round(total_size / (1024 * 1024), 2)
        
        return stats
    
    def validate_data(self):
        """Validate integrity of existing data"""
        
        logger.info("Validating data integrity...")
        
        validation_results = {}
        
        for tier_name, tier_config in self.tiers.items():
            logger.info(f"Validating {tier_config['name']} data...")
            
            tier_validation = {
                'data_exists': False,
                'file_count': 0,
                'corrupted_files': [],
                'missing_expected_files': []
            }
            
            # Check if data directory exists
            if self.original_dir.exists():
                tier_validation['data_exists'] = True
                
                # Count files and check for corruption
                for root, dirs, files in os.walk(self.original_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        tier_validation['file_count'] += 1
                        
                        # Basic corruption check - file size > 0
                        if os.path.getsize(file_path) == 0:
                            tier_validation['corrupted_files'].append(file_path)
            
            validation_results[tier_name] = tier_validation
        
        # Generate validation report
        validation_report_file = self.data_dir / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(validation_report_file, 'w') as f:
            json.dump(validation_results, f, indent=2)
        
        logger.info(f"Validation report saved to: {validation_report_file}")
        
        # Print summary
        for tier_name, results in validation_results.items():
            logger.info(f"{tier_name}: {results['file_count']} files, {len(results['corrupted_files'])} corrupted")
    
    def cleanup_old_data(self, tier_name, keep_days=30):
        """Clean up old data files for non-git tracked tiers"""
        
        if tier_name == 'm7':
            logger.warning("Cannot cleanup M7 data - it's tracked in git")
            return
        
        logger.info(f"Cleaning up old data for {tier_name} (keeping last {keep_days} days)...")
        
        cutoff_time = time.time() - (keep_days * 24 * 3600)
        removed_files = 0
        
        for root, dirs, files in os.walk(self.original_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.getmtime(file_path) < cutoff_time:
                    try:
                        os.remove(file_path)
                        removed_files += 1
                    except Exception as e:
                        logger.error(f"Error removing {file_path}: {e}")
        
        logger.info(f"Removed {removed_files} old files")

def main():
    parser = argparse.ArgumentParser(
        description="Build knowledge base for My Finance DCF Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--tier',
        choices=['m7', 'nasdaq100', 'us-all'],
        help='Build specific data tier'
    )
    
    parser.add_argument(
        '--rebuild',
        action='store_true',
        help='Force rebuild all data'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate existing data integrity'
    )
    
    parser.add_argument(
        '--cleanup',
        metavar='TIER',
        help='Clean up old data for specified tier'
    )
    
    parser.add_argument(
        '--keep-days',
        type=int,
        default=30,
        help='Days of data to keep during cleanup (default: 30)'
    )
    
    args = parser.parse_args()
    
    builder = KnowledgeBaseBuilder()
    
    try:
        # Create missing configuration files
        builder.create_missing_configs()
        
        if args.validate:
            builder.validate_data()
        
        elif args.cleanup:
            builder.cleanup_old_data(args.cleanup, args.keep_days)
        
        elif args.tier:
            builder.build_tier(args.tier, force_rebuild=args.rebuild)
        
        elif args.rebuild:
            # Rebuild all tiers
            for tier_name in builder.tiers.keys():
                builder.build_tier(tier_name, force_rebuild=True)
        
        else:
            # Default: build M7 tier only
            logger.info("No specific tier specified, building M7 stable test dataset...")
            builder.build_tier('m7')
    
    except Exception as e:
        logger.error(f"Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()