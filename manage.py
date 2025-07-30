#!/usr/bin/env python3
"""
My Finance DCF Analysis Tool - Management Script

This script provides a simple interface for managing the layered data system:
- Tier 1 (M7): Stable test dataset, tracked in git (~500MB)
- Tier 2 (NASDAQ100): Extended dataset, buildable (~5GB) 
- Tier 3 (US-ALL): Full dataset, buildable (~50GB)

Usage:
    python manage.py build m7              # Build M7 stable test set
    python manage.py build nasdaq100       # Build NASDAQ100 dataset
    python manage.py build us-all          # Build full US dataset
    python manage.py validate              # Validate existing data
    python manage.py status                # Show data status
    python manage.py clean nasdaq100       # Clean old NASDAQ100 data
    python manage.py setup                 # Initial project setup
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
import json
from datetime import datetime

class FinanceManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        
        self.tiers = {
            'm7': {
                'name': 'Magnificent 7 (M7)',
                'description': 'Stable test dataset - tracked in git',
                'companies': 7,
                'size_estimate': '~500MB',
                'tracked_in_git': True
            },
            'nasdaq100': {
                'name': 'NASDAQ 100',
                'description': 'Extended validation dataset - buildable',
                'companies': 100,
                'size_estimate': '~5GB',
                'tracked_in_git': False
            },
            'us-all': {
                'name': 'All US Stocks',
                'description': 'Complete stock universe - buildable',
                'companies': 8000,
                'size_estimate': '~50GB',
                'tracked_in_git': False
            }
        }
    
    def show_help(self):
        """Show help information"""
        print("My Finance DCF Analysis Tool - Management Script")
        print("=" * 50)
        print()
        print("Commands:")
        print("  build <tier>     Build knowledge base for specific tier")
        print("  validate         Validate existing data integrity")
        print("  status           Show current data status")
        print("  clean <tier>     Clean old data for tier (keep last 30 days)")
        print("  setup            Initial project setup")
        print()
        print("Available Tiers:")
        for tier_id, tier_info in self.tiers.items():
            status = "📌 tracked in git" if tier_info['tracked_in_git'] else "🔄 buildable"
            print(f"  {tier_id:<12} {tier_info['name']} - {tier_info['companies']} companies, {tier_info['size_estimate']} ({status})")
        print()
        print("Examples:")
        print("  python manage.py build m7           # Build core test dataset")
        print("  python manage.py build nasdaq100    # Build extended dataset")
        print("  python manage.py status             # Check current status")
    
    def build_tier(self, tier_name):
        """Build knowledge base for specific tier"""
        if tier_name not in self.tiers:
            print(f"❌ Unknown tier: {tier_name}")
            print(f"Available tiers: {', '.join(self.tiers.keys())}")
            return False
        
        tier_info = self.tiers[tier_name]
        
        print(f"🔧 Building {tier_info['name']} knowledge base...")
        print(f"   Companies: {tier_info['companies']}")
        print(f"   Size: {tier_info['size_estimate']}")
        print(f"   Git tracked: {'Yes' if tier_info['tracked_in_git'] else 'No'}")
        print()
        
        # Warning for large datasets
        if not tier_info['tracked_in_git'] and tier_name != 'm7':
            response = input(f"⚠️  This will download {tier_info['size_estimate']} of data. Continue? [y/N]: ")
            if response.lower() != 'y':
                print("❌ Cancelled")
                return False
        
        # Run the knowledge base builder
        try:
            cmd = [sys.executable, "build_knowledge_base.py", "--tier", tier_name]
            result = subprocess.run(cmd, check=True)
            print(f"✅ Successfully built {tier_info['name']} knowledge base")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to build {tier_name}: {e}")
            return False
        except FileNotFoundError:
            print("❌ build_knowledge_base.py not found. Run 'python manage.py setup' first.")
            return False
    
    def validate_data(self):
        """Validate existing data integrity"""
        print("🔍 Validating data integrity...")
        
        try:
            cmd = [sys.executable, "build_knowledge_base.py", "--validate"]
            result = subprocess.run(cmd, check=True)
            print("✅ Data validation completed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Validation failed: {e}")
            return False
        except FileNotFoundError:
            print("❌ build_knowledge_base.py not found. Run 'python manage.py setup' first.")
            return False
    
    def show_status(self):
        """Show current data status"""
        print("📊 Knowledge Base Status")
        print("=" * 30)
        print()
        
        if not self.data_dir.exists():
            print("❌ Data directory not found. Run 'python manage.py setup' first.")
            return
        
        original_dir = self.data_dir / "original"
        if not original_dir.exists():
            print("📭 No data found. Run 'python manage.py build m7' to get started.")
            return
        
        # Check each tier
        for tier_id, tier_info in self.tiers.items():
            print(f"{tier_info['name']}:")
            
            # Count files for this tier
            file_count = 0
            data_size = 0
            
            # Check yfinance data
            yfinance_dir = original_dir / "yfinance"
            if yfinance_dir.exists():
                if tier_id == 'm7':
                    # Count M7 companies specifically
                    m7_companies = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'TSLA', 'NFLX']
                    for company in m7_companies:
                        company_files = list(yfinance_dir.glob(f"{company}/*.json"))
                        file_count += len(company_files)
                        for f in company_files:
                            data_size += f.stat().st_size
                else:
                    # Count files with tier pattern
                    pattern = f"*{tier_id}*" if tier_id != 'us-all' else "*us_all*"
                    tier_files = list(yfinance_dir.rglob(f"*{pattern}*.json"))
                    file_count += len(tier_files)
                    for f in tier_files:
                        data_size += f.stat().st_size
            
            # Check SEC data
            sec_dir = original_dir / "sec-edgar"
            if sec_dir.exists():
                if tier_id == 'm7':
                    # Count M7 CIK directories
                    m7_ciks = ['0000320193', '0000789019', '0001018724', '0001652044', '0001326801', '0001318605', '0001065280']
                    for cik in m7_ciks:
                        cik_files = list(sec_dir.rglob(f"{cik}/**/*.txt"))
                        file_count += len(cik_files)
                        for f in cik_files:
                            data_size += f.stat().st_size
            
            # Display status
            if file_count > 0:
                size_mb = data_size / (1024 * 1024)
                status_icon = "📌" if tier_info['tracked_in_git'] else "💾"
                print(f"  {status_icon} {file_count} files, {size_mb:.1f} MB")
            else:
                print(f"  📭 No data found")
            
            print()
        
        # Check Neo4j status
        print("Database Status:")
        try:
            result = subprocess.run(["docker", "ps", "--filter", "name=neo4j-finance"], 
                                  capture_output=True, text=True)
            if "neo4j-finance" in result.stdout:
                print("  🟢 Neo4j running")
            else:
                print("  🔴 Neo4j not running")
        except FileNotFoundError:
            print("  ❓ Docker not found")
    
    def clean_tier(self, tier_name):
        """Clean old data for specified tier"""
        if tier_name not in self.tiers:
            print(f"❌ Unknown tier: {tier_name}")
            return False
        
        if tier_name == 'm7':
            print("❌ Cannot clean M7 data - it's tracked in git")
            return False
        
        tier_info = self.tiers[tier_name]
        print(f"🧹 Cleaning old {tier_info['name']} data (keeping last 30 days)...")
        
        try:
            cmd = [sys.executable, "build_knowledge_base.py", "--cleanup", tier_name]
            result = subprocess.run(cmd, check=True)
            print(f"✅ Cleaned old {tier_name} data")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to clean {tier_name}: {e}")
            return False
    
    def setup_project(self):
        """Initial project setup"""
        print("🚀 Setting up My Finance DCF Analysis Tool...")
        print()
        
        # Check Python environment
        print("1. Checking Python environment...")
        try:
            import pipenv
            print("   ✅ pipenv found")
        except ImportError:
            print("   📦 Installing pipenv...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pipenv"], check=True)
        
        # Install dependencies
        print("2. Installing dependencies...")
        try:
            subprocess.run(["pipenv", "install"], check=True)
            print("   ✅ Dependencies installed")
        except subprocess.CalledProcessError:
            print("   ❌ Failed to install dependencies")
            return False
        
        # Create data directories
        print("3. Creating data directories...")
        (self.data_dir / "original").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "log").mkdir(parents=True, exist_ok=True)
        print("   ✅ Data directories created")
        
        # Validate setup
        print("4. Validating setup...")
        if (self.project_root / "build_knowledge_base.py").exists():
            print("   ✅ Build system ready")
        else:
            print("   ❌ Build system files missing")
            return False
        
        print()
        print("🎉 Setup complete!")
        print()
        print("Next steps:")
        print("  1. Start Neo4j: docker run -d --name neo4j-finance -p 7474:7474 -p 7687:7687 neo4j:5.15")
        print("  2. Build M7 dataset: python manage.py build m7")
        print("  3. Check status: python manage.py status")
        
        return True

def main():
    parser = argparse.ArgumentParser(
        description="My Finance DCF Analysis Tool - Management Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Build command
    build_parser = subparsers.add_parser('build', help='Build knowledge base for specific tier')
    build_parser.add_argument('tier', choices=['m7', 'nasdaq100', 'us-all'], help='Data tier to build')
    
    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Clean old data for tier')
    clean_parser.add_argument('tier', choices=['nasdaq100', 'us-all'], help='Data tier to clean')
    
    # Other commands
    subparsers.add_parser('validate', help='Validate existing data integrity')
    subparsers.add_parser('status', help='Show current data status')
    subparsers.add_parser('setup', help='Initial project setup')
    
    args = parser.parse_args()
    
    manager = FinanceManager()
    
    if not args.command:
        manager.show_help()
        return
    
    if args.command == 'build':
        success = manager.build_tier(args.tier)
        sys.exit(0 if success else 1)
    
    elif args.command == 'validate':
        success = manager.validate_data()
        sys.exit(0 if success else 1)
    
    elif args.command == 'status':
        manager.show_status()
    
    elif args.command == 'clean':
        success = manager.clean_tier(args.tier)
        sys.exit(0 if success else 1)
    
    elif args.command == 'setup':
        success = manager.setup_project()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()