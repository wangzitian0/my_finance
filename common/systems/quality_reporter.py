#!/usr/bin/env python3
"""
Quality reporting system for ETL pipeline stages.
Refactored from oversized module (689 lines) into focused components.

Issue #184: Moved to systems/ and refactored for better maintainability
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Try to import yaml, fall back if not available
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

logger = logging.getLogger(__name__)

# Quality reporting availability flag
QUALITY_REPORTING_AVAILABLE = True


class QualityMetrics:
    """Encapsulates quality metrics calculation and analysis."""
    
    @staticmethod
    def calculate_success_rate(found: int, expected: int) -> float:
        """Calculate success rate with bounds checking."""
        if expected <= 0:
            return 0.0
        return min(found / expected, 1.0)  # Cap at 100%
    
    @staticmethod
    def analyze_file_quality(file_path: Path) -> Dict[str, Any]:
        """Analyze quality of a single file."""
        if not file_path.exists():
            return {"status": "missing", "size": 0, "valid": False}
        
        try:
            size = file_path.stat().st_size
            valid = size > 0
            
            # Additional validation for JSON files
            if file_path.suffix == ".json" and valid:
                try:
                    with open(file_path) as f:
                        json.load(f)
                    valid = True
                except json.JSONDecodeError:
                    valid = False
            
            return {
                "status": "found",
                "size": size,
                "valid": valid,
                "path": str(file_path)
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "valid": False}


class StageAnalyzer:
    """Handles analysis of individual pipeline stages."""
    
    def __init__(self, base_path: Path, tier_name: str):
        self.base_path = base_path
        self.tier_name = tier_name
        self.metrics = QualityMetrics()
    
    def analyze_extract_stage(self, partition: str = None) -> Dict[str, Any]:
        """Analyze extraction stage quality."""
        yf_quality = self._analyze_yfinance_extraction(partition)
        sec_quality = self._analyze_sec_extraction(partition)
        
        # Calculate combined success rate
        yf_rate = yf_quality.get("success_rate", 0)
        sec_rate = sec_quality.get("success_rate", 0)
        overall_rate = (yf_rate + sec_rate) / 2
        
        return {
            "stage_name": "Data Extraction",
            "yfinance_quality": yf_quality,
            "sec_edgar_quality": sec_quality,
            "overall_success_rate": overall_rate,
            "status": "completed" if overall_rate > 0.5 else "failed"
        }
    
    def analyze_transform_stage(self, partition: str = None) -> Dict[str, Any]:
        """Analyze transformation stage quality."""
        transform_path = self.base_path / "stage_02_transform"
        
        partition_path = self._find_best_partition(transform_path, partition)
        if not partition_path:
            return {"success_rate": 0, "status": "no_data_found"}
        
        # Count transformed files
        cleaned_files = len(list(partition_path.glob("**/cleaned/*.json")))
        processed_files = len(list(partition_path.glob("**/processed/*.json")))
        
        expected_files = self._get_expected_files_count()
        total_transformed = cleaned_files + processed_files
        
        return {
            "stage_name": "Data Transformation",
            "success_rate": self.metrics.calculate_success_rate(total_transformed, expected_files),
            "cleaned_files": cleaned_files,
            "processed_files": processed_files,
            "total_transformed": total_transformed,
            "expected_files": expected_files,
            "status": "completed" if total_transformed > 0 else "failed"
        }
    
    def analyze_load_stage(self, partition: str = None) -> Dict[str, Any]:
        """Analyze load stage quality."""
        load_path = self.base_path / "stage_03_load"
        
        partition_path = self._find_best_partition(load_path, partition)
        if not partition_path:
            return {"success_rate": 0, "status": "no_data_found"}
        
        # Count loaded records
        vector_files = len(list(partition_path.glob("**/vectors/*.json")))
        graph_files = len(list(partition_path.glob("**/graph/*.json")))
        
        expected_count = self._get_expected_companies_count()
        total_loaded = vector_files + graph_files
        
        return {
            "stage_name": "Data Loading",
            "success_rate": self.metrics.calculate_success_rate(total_loaded, expected_count),
            "vector_files": vector_files,
            "graph_files": graph_files,
            "total_loaded": total_loaded,
            "expected_count": expected_count,
            "status": "completed" if total_loaded > 0 else "failed"
        }
    
    def analyze_generic_stage(self, stage: str, partition: str = None) -> Dict[str, Any]:
        """Generic stage analysis for unknown stages."""
        stage_path = self.base_path / stage
        
        if not stage_path.exists():
            return {"success_rate": 0, "status": "stage_not_found"}
        
        # Count all files in stage
        all_files = list(stage_path.rglob("*"))
        file_count = len([f for f in all_files if f.is_file()])
        
        return {
            "stage_name": stage.replace("_", " ").title(),
            "success_rate": 1.0 if file_count > 0 else 0.0,
            "total_files": file_count,
            "status": "completed" if file_count > 0 else "empty"
        }
    
    def _analyze_yfinance_extraction(self, partition: str = None) -> Dict[str, Any]:
        """Analyze YFinance data extraction quality."""
        try:
            yfinance_path = self.base_path / "stage_01_extract" / "yfinance"
            partition_path = self._find_best_partition(yfinance_path, partition)
            
            if not partition_path:
                return {
                    "success_rate": 0,
                    "total_found": 0,
                    "companies_processed": [],
                    "status": "no_data_found"
                }
            
            # Count companies and files
            companies_found = []
            total_files = 0
            
            for company_dir in partition_path.iterdir():
                if company_dir.is_dir():
                    json_files = list(company_dir.glob("*.json"))
                    if json_files:
                        companies_found.append({
                            "ticker": company_dir.name,
                            "files_count": len(json_files)
                        })
                        total_files += len(json_files)
            
            expected_companies = self._get_expected_companies_count()
            success_rate = self.metrics.calculate_success_rate(len(companies_found), expected_companies)
            
            return {
                "success_rate": success_rate,
                "total_found": len(companies_found),
                "total_files": total_files,
                "companies_processed": companies_found,
                "expected_companies": expected_companies,
                "status": "completed" if companies_found else "failed"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing YFinance extraction: {e}")
            return {"success_rate": 0, "error": str(e), "status": "error"}
    
    def _analyze_sec_extraction(self, partition: str = None) -> Dict[str, Any]:
        """Analyze SEC Edgar data extraction quality."""
        try:
            sec_path = self.base_path / "stage_01_extract" / "sec_edgar"
            partition_path = self._find_best_partition(sec_path, partition)
            
            if not partition_path:
                return {
                    "success_rate": 0,
                    "total_found": 0,
                    "companies_processed": [],
                    "status": "no_data_found"
                }
            
            # Count SEC documents
            companies_found = []
            document_counts = {"10-K": 0, "10-Q": 0, "8-K": 0}
            total_documents = 0
            
            for company_dir in partition_path.iterdir():
                if company_dir.is_dir():
                    company_docs = {"10-K": 0, "10-Q": 0, "8-K": 0}
                    
                    for doc_type in ["10-K", "10-Q", "8-K"]:
                        doc_files = list(company_dir.rglob(f"*{doc_type.replace('-', '')}*.txt"))
                        company_docs[doc_type] = len(doc_files)
                        document_counts[doc_type] += len(doc_files)
                        total_documents += len(doc_files)
                    
                    if sum(company_docs.values()) > 0:
                        companies_found.append({
                            "ticker": company_dir.name,
                            "documents": company_docs,
                            "total_docs": sum(company_docs.values())
                        })
            
            expected_companies = self._get_expected_companies_count()
            expected_docs = expected_companies * 15  # Rough estimate
            success_rate = self.metrics.calculate_success_rate(total_documents, expected_docs)
            
            return {
                "success_rate": success_rate,
                "total_found": total_documents,
                "companies_processed": companies_found,
                "document_types": document_counts,
                "expected_documents": expected_docs,
                "status": "completed" if companies_found else "failed"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing SEC extraction: {e}")
            return {"success_rate": 0, "error": str(e), "status": "error"}
    
    def _find_best_partition(self, base_path: Path, partition: str = None) -> Optional[Path]:
        """Find the best available partition for analysis."""
        if not base_path.exists():
            return None
        
        # Try specific partition first
        if partition:
            partition_path = base_path / partition
            if partition_path.exists() and any(partition_path.iterdir()):
                return partition_path
        
        # Try 'latest' partition
        latest_path = base_path / "latest"
        if latest_path.exists() and any(latest_path.iterdir()):
            return latest_path
        
        # Find any available partition
        for item in base_path.iterdir():
            if item.is_dir() and item.name != "latest" and any(item.iterdir()):
                return item
        
        return None
    
    def _get_expected_companies_count(self) -> int:
        """Get expected number of companies based on tier."""
        tier_mapping = {
            "f2": 2,
            "fast_2": 2,
            "m7": 7,
            "magnificent_7": 7,
            "n100": 101,
            "nasdaq_100": 101,
            "v3k": 3485,
            "vti_3500": 3485
        }
        return tier_mapping.get(self.tier_name.lower(), 10)
    
    def _get_expected_files_count(self) -> int:
        """Get expected number of files based on companies and processing stages."""
        return self._get_expected_companies_count() * 3  # Estimate: 3 files per company


class QualityReporter:
    """Refactored quality reporting system with focused responsibilities."""

    def __init__(self, build_id: str, tier_name: str, base_path: str = None):
        if base_path is None:
            # Use project root relative path
            project_root = Path(__file__).parent.parent.parent
            base_path = project_root / "build_data"

        self.base_path = Path(base_path)
        self.build_id = build_id
        self.tier_name = tier_name
        
        # Create quality reports directory structure
        self.quality_base_path = self.base_path / "quality_reports" / build_id
        self.quality_base_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize stage analyzer
        self.stage_analyzer = StageAnalyzer(self.base_path, tier_name)
        
        # Initialize report storage
        self.stage_reports = {}
        self.build_summary = {
            "build_id": build_id,
            "tier_name": tier_name,
            "start_time": datetime.now().isoformat(),
            "stages": {},
            "overall_statistics": {},
        }

        logger.info(f"Quality reporter initialized for build {build_id} ({tier_name})")

    def report_stage_quality(self, stage: str, partition: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Generate quality report for a completed stage."""
        try:
            logger.info(f"Generating quality report for stage: {stage}")

            # Stage-specific quality analysis
            if stage in ["stage_01_extract", "extract"]:
                quality_data = self.stage_analyzer.analyze_extract_stage(partition)
            elif stage in ["stage_02_transform", "transform"]:
                quality_data = self.stage_analyzer.analyze_transform_stage(partition)
            elif stage in ["stage_03_load", "load"]:
                quality_data = self.stage_analyzer.analyze_load_stage(partition)
            else:
                quality_data = self.stage_analyzer.analyze_generic_stage(stage, partition)

            # Add metadata
            quality_data.update({
                "stage": stage,
                "partition": partition,
                "timestamp": datetime.now().isoformat(),
                "build_id": self.build_id,
                "tier_name": self.tier_name,
            })

            # Store stage report
            self.stage_reports[stage] = quality_data
            self.build_summary["stages"][stage] = quality_data

            # Save stage quality report
            self._save_stage_report(stage, quality_data)

            logger.info(
                f"Quality report completed for {stage}: {quality_data.get('overall_success_rate', quality_data.get('success_rate', 'N/A'))} success rate"
            )
            return quality_data

        except Exception as e:
            logger.error(f"Failed to generate quality report for {stage}: {e}")
            return {"error": str(e), "stage": stage, "timestamp": datetime.now().isoformat()}

    def finalize_build_report(self) -> Dict[str, Any]:
        """Generate final build-wide quality report."""
        try:
            # Calculate overall statistics
            success_rates = []
            total_stages = len(self.stage_reports)
            failed_stages = 0
            
            for stage_data in self.stage_reports.values():
                rate = stage_data.get("overall_success_rate", stage_data.get("success_rate", 0))
                success_rates.append(rate)
                if stage_data.get("status") == "failed":
                    failed_stages += 1
            
            overall_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0
            
            self.build_summary.update({
                "end_time": datetime.now().isoformat(),
                "overall_statistics": {
                    "overall_success_rate": overall_success_rate,
                    "total_stages": total_stages,
                    "successful_stages": total_stages - failed_stages,
                    "failed_stages": failed_stages,
                    "build_status": "success" if overall_success_rate >= 0.8 else "partial" if overall_success_rate >= 0.5 else "failed"
                }
            })
            
            # Save final report
            self._save_build_summary()
            
            logger.info(f"Build quality report finalized: {overall_success_rate:.2%} overall success rate")
            return self.build_summary
            
        except Exception as e:
            logger.error(f"Failed to finalize build report: {e}")
            return {"error": str(e)}

    def _save_stage_report(self, stage: str, quality_data: Dict[str, Any]) -> None:
        """Save individual stage quality report."""
        try:
            stage_report_path = self.quality_base_path / f"{stage}_quality.json"
            with open(stage_report_path, "w") as f:
                json.dump(quality_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save stage report for {stage}: {e}")

    def _save_build_summary(self) -> None:
        """Save build-wide quality summary."""
        try:
            summary_path = self.quality_base_path / "build_quality_summary.json"
            with open(summary_path, "w") as f:
                json.dump(self.build_summary, f, indent=2, ensure_ascii=False)
                
            # Also save as YAML if available
            if YAML_AVAILABLE:
                yaml_path = self.quality_base_path / "build_quality_summary.yml"
                with open(yaml_path, "w") as f:
                    yaml.dump(self.build_summary, f, default_flow_style=False)
                    
        except Exception as e:
            logger.error(f"Failed to save build summary: {e}")

    def get_stage_reports(self) -> Dict[str, Dict[str, Any]]:
        """Get all stage reports."""
        return self.stage_reports.copy()

    def get_build_summary(self) -> Dict[str, Any]:
        """Get build summary."""
        return self.build_summary.copy()


# Convenience function for setup
def setup_quality_reporter(build_id: str, tier_name: str, base_path: str = None) -> QualityReporter:
    """Set up and return a quality reporter instance."""
    return QualityReporter(build_id, tier_name, base_path)