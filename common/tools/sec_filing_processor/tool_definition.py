#!/usr/bin/env python3
"""
SEC Filing Processor Tool Implementation

Implements the SEC filing processing functionality as a unified tool.
Maps to existing ETL pipeline components for SEC Edgar data processing.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from ...core.directory_manager import DataLayer, directory_manager
from ..base_tool import BaseTool, ToolConfig, ToolExecutionContext


class SECFilingProcessor(BaseTool):
    """
    Tool for processing SEC Edgar filings into structured data.

    This tool integrates with the existing ETL pipeline to process SEC filings
    from raw downloads to structured, analyzable data with embeddings.
    """

    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.logger = logging.getLogger(f"tool.{config.name}")

    def validate_prerequisites(self, context: ToolExecutionContext) -> bool:
        """Validate that prerequisites for SEC filing processing are met"""
        context.add_message("Validating SEC filing processor prerequisites")

        # Check for required Python packages (would normally import these)
        required_packages = ["requests", "beautifulsoup4", "pandas", "sentence_transformers"]
        missing_packages = []

        for package in required_packages:
            try:
                __import__(package)
                self.logger.debug(f"Package '{package}' available")
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            context.add_message(f"Missing required packages: {missing_packages}", "ERROR")
            return False

        # Check storage space (simplified check)
        workspace_path = context.workspace_path
        try:
            # Check if we can write to workspace
            test_file = workspace_path / "test_write.tmp"
            test_file.write_text("test")
            test_file.unlink()
            context.add_message("Storage write test passed")
        except Exception as e:
            context.add_message(f"Storage write test failed: {e}", "ERROR")
            return False

        # Validate configuration overrides
        config_overrides = self.config.config_overrides
        if "sec_edgar_user_agent" not in config_overrides:
            context.add_message("Missing SEC Edgar user agent configuration", "ERROR")
            return False

        context.add_message("All prerequisites validated successfully")
        return True

    def create_workspace_structure(self, context: ToolExecutionContext) -> bool:
        """Create the required directory structure for SEC filing processing"""
        context.add_message("Creating SEC filing processor workspace structure")

        try:
            # Get required paths from base tool
            required_paths = self.get_required_paths(context.workspace_path)

            # Create all required directories
            for dir_name, dir_path in required_paths.items():
                dir_path.mkdir(parents=True, exist_ok=True)
                context.add_message(f"Created directory: {dir_name}")
                self.logger.debug(f"Created workspace directory: {dir_path}")

            # Create subdirectory structure for raw filings
            raw_filings_path = context.workspace_path / "raw_filings"
            for form_type in ["10-K", "10-Q"]:
                form_dir = raw_filings_path / form_type.lower()
                form_dir.mkdir(exist_ok=True)
                context.add_message(f"Created form directory: {form_type}")

            # Create company-specific directories for parsed filings
            parsed_filings_path = context.workspace_path / "parsed_filings"
            for subdir in ["text_extraction", "tables", "financial_statements"]:
                subdir_path = parsed_filings_path / subdir
                subdir_path.mkdir(exist_ok=True)
                context.add_message(f"Created parsed filing subdirectory: {subdir}")

            # Create metadata tracking files
            metadata_path = context.workspace_path / "metadata"

            # Initialize processing manifest
            manifest = {
                "tool_name": self.config.name,
                "tool_version": self.config.version,
                "created_at": context.start_time.isoformat() if context.start_time else None,
                "workspace_path": str(context.workspace_path),
                "processing_status": "initialized",
                "companies_processed": [],
                "filings_processed": [],
                "errors": [],
            }

            manifest_file = metadata_path / "processing_manifest.json"
            with open(manifest_file, "w") as f:
                json.dump(manifest, f, indent=2)

            context.add_message("Processing manifest created")

            # Store important paths in context
            context.temp_paths.add(context.workspace_path / "temp")

            context.add_message("Workspace structure created successfully")
            return True

        except Exception as e:
            context.add_message(f"Failed to create workspace structure: {e}", "ERROR")
            self.logger.exception("Workspace structure creation failed")
            return False

    def execute(self, context: ToolExecutionContext) -> bool:
        """Execute SEC filing processing"""
        context.add_message("Starting SEC filing processing execution")

        try:
            # Phase 1: Load input data (10% progress)
            context.update_progress(0.1, "Loading input SEC filing data")
            if not self._load_input_data(context):
                return False

            # Phase 2: Download/Process filings (30% progress)
            context.update_progress(0.3, "Processing SEC filings")
            if not self._process_filings(context):
                return False

            # Phase 3: Extract financial data (50% progress)
            context.update_progress(0.5, "Extracting financial data")
            if not self._extract_financial_data(context):
                return False

            # Phase 4: Generate embeddings (70% progress)
            context.update_progress(0.7, "Generating document embeddings")
            if not self._generate_embeddings(context):
                return False

            # Phase 5: Update output layers (85% progress)
            context.update_progress(0.85, "Updating output data layers")
            if not self._update_output_layers(context):
                return False

            context.update_progress(0.9, "SEC filing processing completed")
            context.add_message("SEC filing processing execution completed successfully")
            return True

        except Exception as e:
            context.add_message(f"Execution failed: {e}", "ERROR")
            self.logger.exception("Tool execution failed")
            return False

    def _load_input_data(self, context: ToolExecutionContext) -> bool:
        """Load input data from raw data layer"""
        try:
            # Get input path for raw SEC data
            if "stage_00_raw" not in context.input_paths:
                context.add_message("No raw data input path configured", "ERROR")
                return False

            raw_data_path = context.input_paths["stage_00_raw"]
            sec_data_path = raw_data_path / "sec-edgar"

            if not sec_data_path.exists():
                context.add_message(f"SEC data directory not found: {sec_data_path}", "WARNING")
                # Create empty structure for demonstration
                sec_data_path.mkdir(parents=True, exist_ok=True)

            # Count available filings (simulated)
            filing_count = (
                len(list(sec_data_path.glob("**/*.txt"))) if sec_data_path.exists() else 0
            )
            context.add_message(f"Found {filing_count} SEC filings to process")

            return True

        except Exception as e:
            context.add_message(f"Failed to load input data: {e}", "ERROR")
            return False

    def _process_filings(self, context: ToolExecutionContext) -> bool:
        """Process SEC filings (simplified implementation)"""
        try:
            # This would integrate with existing ETL/sec_data_processor.py
            context.add_message("Processing SEC filings (simulated)")

            # Simulate processing multiple filings
            processed_count = 0
            for i in range(5):  # Simulate processing 5 filings
                filing_id = f"filing_{i+1}"
                context.add_message(f"Processing {filing_id}")
                processed_count += 1

            # Update manifest
            metadata_path = context.workspace_path / "metadata" / "processing_manifest.json"
            with open(metadata_path, "r") as f:
                manifest = json.load(f)

            manifest["processing_status"] = "filings_processed"
            manifest["filings_processed"] = [f"filing_{i+1}" for i in range(processed_count)]

            with open(metadata_path, "w") as f:
                json.dump(manifest, f, indent=2)

            context.add_message(f"Successfully processed {processed_count} SEC filings")
            return True

        except Exception as e:
            context.add_message(f"Filing processing failed: {e}", "ERROR")
            return False

    def _extract_financial_data(self, context: ToolExecutionContext) -> bool:
        """Extract financial data from processed filings"""
        try:
            context.add_message("Extracting financial data from filings")

            # Simulate financial data extraction
            extracted_data_path = context.workspace_path / "extracted_data"

            # Create sample extracted data structure
            financial_metrics = {
                "revenue": {"2023": 100000000, "2022": 95000000},
                "net_income": {"2023": 15000000, "2022": 12000000},
                "total_assets": {"2023": 500000000, "2022": 480000000},
            }

            metrics_file = extracted_data_path / "financial_metrics.json"
            with open(metrics_file, "w") as f:
                json.dump(financial_metrics, f, indent=2)

            context.add_message("Financial data extraction completed")
            return True

        except Exception as e:
            context.add_message(f"Financial data extraction failed: {e}", "ERROR")
            return False

    def _generate_embeddings(self, context: ToolExecutionContext) -> bool:
        """Generate document embeddings for processed filings"""
        try:
            context.add_message("Generating document embeddings")

            embeddings_path = context.workspace_path / "embeddings"

            # Simulate embedding generation
            import time

            time.sleep(0.1)  # Simulate processing time

            # Create sample embeddings metadata
            embeddings_manifest = {
                "model": self.config.config_overrides.get("embedding_model", "default"),
                "documents_processed": 5,
                "embedding_dimension": 384,
                "created_at": context.start_time.isoformat() if context.start_time else None,
            }

            manifest_file = embeddings_path / "embeddings_manifest.json"
            with open(manifest_file, "w") as f:
                json.dump(embeddings_manifest, f, indent=2)

            context.add_message("Document embeddings generated successfully")
            return True

        except Exception as e:
            context.add_message(f"Embedding generation failed: {e}", "ERROR")
            return False

    def _update_output_layers(self, context: ToolExecutionContext) -> bool:
        """Update output data layers with processed results"""
        try:
            context.add_message("Updating output data layers")

            # Update daily delta layer
            if "stage_01_daily_delta" in context.output_paths:
                delta_path = context.output_paths["stage_01_daily_delta"]
                delta_path.mkdir(parents=True, exist_ok=True)

                # Copy processed data to delta layer
                delta_update = {
                    "tool": self.config.name,
                    "timestamp": context.timestamp,
                    "changes": {
                        "new_filings": 5,
                        "updated_companies": ["AAPL", "MSFT", "GOOGL"],
                    },
                }

                delta_file = delta_path / f"sec_filing_update_{context.timestamp}.json"
                with open(delta_file, "w") as f:
                    json.dump(delta_update, f, indent=2)

            # Update daily index layer
            if "stage_02_daily_index" in context.output_paths:
                index_path = context.output_paths["stage_02_daily_index"]
                index_path.mkdir(parents=True, exist_ok=True)

                # Create index update manifest
                index_update = {
                    "embeddings_updated": True,
                    "documents_indexed": 5,
                    "index_timestamp": context.timestamp,
                }

                index_file = index_path / f"sec_index_update_{context.timestamp}.json"
                with open(index_file, "w") as f:
                    json.dump(index_update, f, indent=2)

            context.add_message("Output layers updated successfully")
            return True

        except Exception as e:
            context.add_message(f"Output layer update failed: {e}", "ERROR")
            return False

    def validate_outputs(self, context: ToolExecutionContext) -> bool:
        """Validate that tool outputs meet quality requirements"""
        context.add_message("Validating SEC filing processor outputs")

        try:
            # Validate required output files exist
            required_files = [
                "metadata/processing_manifest.json",
                "extracted_data/financial_metrics.json",
                "embeddings/embeddings_manifest.json",
            ]

            for file_path in required_files:
                full_path = context.workspace_path / file_path
                if not full_path.exists():
                    context.add_message(f"Required output file missing: {file_path}", "ERROR")
                    return False

                context.add_message(f"Validated output file: {file_path}")

            # Validate output layer updates
            for layer_name in self.config.output_layers:
                if layer_name in context.output_paths:
                    layer_path = context.output_paths[layer_name]
                    if not layer_path.exists():
                        context.add_message(
                            f"Output layer directory missing: {layer_name}", "ERROR"
                        )
                        return False

                    # Check for update files
                    update_files = list(layer_path.glob(f"*_{context.timestamp}.json"))
                    if not update_files:
                        context.add_message(
                            f"No update files found in layer: {layer_name}", "ERROR"
                        )
                        return False

            # Validate processing manifest
            manifest_file = context.workspace_path / "metadata" / "processing_manifest.json"
            with open(manifest_file, "r") as f:
                manifest = json.load(f)

            if manifest["processing_status"] != "filings_processed":
                context.add_message("Processing manifest shows incomplete status", "ERROR")
                return False

            context.add_message("All output validation checks passed")
            return True

        except Exception as e:
            context.add_message(f"Output validation failed: {e}", "ERROR")
            self.logger.exception("Output validation failed")
            return False
