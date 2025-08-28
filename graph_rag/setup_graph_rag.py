#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Graph RAG System Setup Script

This script helps set up the Graph RAG system dependencies and validates the installation.
"""

import importlib.util
import logging
import os
import subprocess
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class GraphRAGSetup:
    """
    Handles setup and dependency management for the Graph RAG system.
    """

    def __init__(self):
        """Initialize setup manager."""
        self.project_root = Path(__file__).parent

        # Required packages for Graph RAG functionality
        self.required_packages = {
            "core": [
                "neomodel>=4.0.0",  # Neo4j ORM
                "numpy>=1.21.0",  # Numerical operations
                "python-dateutil",  # Date parsing
            ],
            "embedding": [
                "sentence-transformers>=2.2.0",  # Semantic embeddings
                "torch>=1.12.0",  # PyTorch (dependency of transformers)
            ],
            "parsing": [
                "beautifulsoup4>=4.11.0",  # HTML/XML parsing
                "lxml>=4.9.0",  # XML parser
                "pyyaml>=6.0",  # YAML configuration
            ],
            "optional": [
                "openai>=1.0.0",  # OpenAI API (for advanced LLM features)
                "chromadb>=0.4.0",  # Vector database (alternative to Neo4j for embeddings)
                "pandas>=1.5.0",  # Data manipulation
                "matplotlib>=3.5.0",  # Plotting (for analysis visualizations)
            ],
        }

        # System requirements
        self.min_python_version = (3, 8)
        self.recommended_python_version = (3, 10)

    def run_setup(self, install_optional: bool = False):
        """
        Run complete setup process.

        Args:
            install_optional: Whether to install optional packages
        """
        logger.info("Starting Graph RAG system setup")

        # Step 1: Check Python version
        self.check_python_version()

        # Step 2: Check and install core dependencies
        self.install_dependencies("core")

        # Step 3: Install embedding dependencies
        self.install_dependencies("embedding")

        # Step 4: Install parsing dependencies
        self.install_dependencies("parsing")

        # Step 5: Install optional dependencies if requested
        if install_optional:
            self.install_dependencies("optional")

        # Step 6: Create necessary directories
        self.create_directories()

        # Step 7: Run validation
        self.validate_installation()

        logger.info("Graph RAG system setup completed!")

    def check_python_version(self):
        """Check if Python version meets requirements."""
        current_version = sys.version_info[:2]

        logger.info(f"Current Python version: {sys.version}")

        if current_version < self.min_python_version:
            logger.error(
                f"Python {'.'.join(map(str, self.min_python_version))} or higher is required"
            )
            logger.error(f"Current version: {'.'.join(map(str, current_version))}")
            sys.exit(1)

        if current_version < self.recommended_python_version:
            logger.warning(
                f"Python {'.'.join(map(str, self.recommended_python_version))} or higher is recommended"
            )
            logger.warning("Some features may not work optimally")

        logger.info("✅ Python version check passed")

    def install_dependencies(self, category: str):
        """
        Install dependencies for a specific category.

        Args:
            category: Category of dependencies to install
        """
        if category not in self.required_packages:
            logger.error(f"Unknown dependency category: {category}")
            return

        packages = self.required_packages[category]
        logger.info(f"Installing {category} dependencies...")

        for package in packages:
            try:
                self.install_package(package)
            except Exception as e:
                if category == "optional":
                    logger.warning(f"Failed to install optional package {package}: {e}")
                else:
                    logger.error(f"Failed to install required package {package}: {e}")
                    if category in ["core", "embedding", "parsing"]:
                        logger.error("This package is required for Graph RAG functionality")

    def install_package(self, package: str):
        """
        Install a single package using pip.

        Args:
            package: Package specification (e.g., 'numpy>=1.21.0')
        """
        package_name = package.split(">=")[0].split("==")[0]

        # Check if package is already installed
        if self.is_package_installed(package_name):
            logger.info(f"✅ {package_name} already installed")
            return

        logger.info(f"Installing {package}...")

        try:
            # Use pip to install the package
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                capture_output=True,
                text=True,
                check=True,
            )

            logger.info(f"✅ {package_name} installed successfully")

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install {package}")
            logger.error(f"Error output: {e.stderr}")

            # Suggest alternative installation methods
            if "torch" in package_name:
                logger.info(
                    "For PyTorch, you might want to visit https://pytorch.org/get-started/locally/"
                )
            elif "sentence-transformers" in package_name:
                logger.info("sentence-transformers requires PyTorch. Install PyTorch first.")

            raise

    def is_package_installed(self, package_name: str) -> bool:
        """
        Check if a package is installed.

        Args:
            package_name: Name of the package to check

        Returns:
            True if package is installed
        """
        try:
            importlib.import_module(package_name.replace("-", "_"))
            return True
        except ImportError:
            return False

    def create_directories(self):
        """Create necessary directories for the Graph RAG system."""

        # Use new directory management system
        from pathlib import Path
        from common import get_data_path, get_source_path, DataLayer
        from common.core.directory_manager import directory_manager
        
        directories = [
            get_data_path(DataLayer.RAW_DATA),
            get_source_path("yfinance", DataLayer.DAILY_DELTA),
            get_source_path("sec-edgar", DataLayer.RAW_DATA),
            "common/config",  # Config directory remains the same
            str(directory_manager.get_logs_path()),  # Use centralized log path management
            str(Path(get_data_path(DataLayer.RAW_DATA)).parent / "neo4j"),
        ]

        logger.info("Creating project directories...")

        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created directory: {directory}")

    def validate_installation(self):
        """Validate that the Graph RAG system can be imported and initialized."""

        logger.info("Validating Graph RAG installation...")

        validation_tests = [
            ("neomodel", "Neo4j ORM"),
            ("numpy", "Numerical operations"),
            ("yaml", "YAML parsing"),
            ("bs4", "BeautifulSoup HTML parsing"),
            ("dateutil", "Date utilities"),
        ]

        # Optional validations
        optional_tests = [
            ("sentence_transformers", "Sentence Transformers"),
            ("torch", "PyTorch"),
        ]

        # Test core imports
        all_core_passed = True

        for module_name, description in validation_tests:
            try:
                importlib.import_module(module_name)
                logger.info(f"✅ {description} import successful")
            except ImportError as e:
                logger.error(f"❌ {description} import failed: {e}")
                all_core_passed = False

        # Test optional imports
        optional_available = 0

        for module_name, description in optional_tests:
            try:
                importlib.import_module(module_name)
                logger.info(f"✅ {description} available")
                optional_available += 1
            except ImportError:
                logger.warning(f"⚠️  {description} not available (optional)")

        # Test Graph RAG system import
        try:
            sys.path.insert(0, str(self.project_root))
            from graph_rag import GraphRAGSystem

            # Try to initialize the system
            graph_rag = GraphRAGSystem()
            logger.info("✅ Graph RAG system import and initialization successful")

        except Exception as e:
            logger.error(f"❌ Graph RAG system initialization failed: {e}")
            all_core_passed = False

        # Summary
        if all_core_passed:
            logger.info("🎉 Graph RAG system validation passed!")
            logger.info(f"Optional features available: {optional_available}/{len(optional_tests)}")

            if optional_available == 0:
                logger.warning("Consider installing optional dependencies for full functionality:")
                logger.warning("python setup_graph_rag.py --install-optional")
        else:
            logger.error("❌ Graph RAG system validation failed")
            logger.error("Please check the error messages above and install missing dependencies")
            sys.exit(1)

    def check_system_requirements(self):
        """Check system requirements and provide recommendations."""

        logger.info("Checking system requirements...")

        # Check available memory
        try:
            import psutil

            memory_gb = psutil.virtual_memory().total / (1024**3)
            logger.info(f"Available RAM: {memory_gb:.1f} GB")

            if memory_gb < 4:
                logger.warning("⚠️  Less than 4GB RAM available")
                logger.warning("Graph RAG may run slowly or encounter memory issues")
            elif memory_gb < 8:
                logger.warning("⚠️  Less than 8GB RAM available")
                logger.warning("Consider closing other applications when running Graph RAG")
            else:
                logger.info("✅ Sufficient RAM available")

        except ImportError:
            logger.info("psutil not available - cannot check memory")

        # Check disk space
        try:
            disk_usage = os.statvfs(self.project_root)
            free_gb = (disk_usage.f_frsize * disk_usage.f_bavail) / (1024**3)
            logger.info(f"Available disk space: {free_gb:.1f} GB")

            if free_gb < 1:
                logger.warning("⚠️  Less than 1GB disk space available")
                logger.warning("May not be sufficient for data storage")
            else:
                logger.info("✅ Sufficient disk space available")

        except (OSError, AttributeError):
            logger.info("Cannot check disk space on this system")

    def generate_config_files(self):
        """Generate sample configuration files."""

        logger.info("Generating sample configuration files...")

        # Sample M7 configuration
        m7_config = {
            "job": "yfinance_m7",
            "source": "yfinance",
            "description": "Yahoo Finance data for Magnificent 7 companies",
            "tickers": ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NFLX"],
            "period": "3y",
            "interval": "1d",
            "data_types": ["info", "history", "recommendations", "sustainability"],
        }

        config_file = self.project_root / "data" / "config" / "yfinance_m7.yml"

        try:
            import yaml

            with open(config_file, "w") as f:
                yaml.dump(m7_config, f, default_flow_style=False)
            logger.info(f"✅ Created sample config: {config_file}")
        except Exception as e:
            logger.error(f"Failed to create config file: {e}")


def main():
    """Main setup function."""

    import argparse

    parser = argparse.ArgumentParser(description="Setup Graph RAG system")
    parser.add_argument(
        "--install-optional", action="store_true", help="Install optional dependencies"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check system requirements without installing",
    )
    parser.add_argument(
        "--generate-config",
        action="store_true",
        help="Generate sample configuration files",
    )

    args = parser.parse_args()

    try:
        setup = GraphRAGSetup()

        if args.check_only:
            setup.check_system_requirements()
            setup.validate_installation()
        elif args.generate_config:
            setup.generate_config_files()
        else:
            setup.run_setup(install_optional=args.install_optional)

            if (
                args.generate_config
                or input("\nGenerate sample config files? (y/n): ").strip().lower() == "y"
            ):
                setup.generate_config_files()

        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run the demo: python demo_graph_rag.py")
        print("2. Run tests: python test_graph_rag.py")
        print("3. Set up Neo4j database using: p3 env setup")

    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
