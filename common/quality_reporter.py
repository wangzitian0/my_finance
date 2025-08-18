#!/usr/bin/env python3
"""
Quality reporting system for ETL pipeline stages.
Follows the same pattern as logger.py with data/quality_reports/<build_id>/ structure.
Automatically generates quality reports during each stage completion.
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
except ImportError:
    yaml = None

logger = logging.getLogger(__name__)


class QualityReporter:
    """Quality reporting system integrated into build process"""

    def __init__(self, build_id: str, tier_name: str, base_path: str = None):
        if base_path is None:
            # Use project root relative path
            project_root = Path(__file__).parent.parent
            base_path = project_root / "data"

        self.base_path = Path(base_path)
        self.build_id = build_id
        self.tier_name = tier_name

        # Create quality reports directory structure
        self.quality_base_path = self.base_path / "quality_reports" / build_id
        self.quality_base_path.mkdir(parents=True, exist_ok=True)

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

    def report_stage_quality(
        self, stage: str, partition: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Generate quality report for a completed stage"""
        try:
            logger.info(f"Generating quality report for stage: {stage}")

            # Stage-specific quality analysis
            if stage == "stage_01_extract":
                quality_data = self._analyze_extract_stage(partition, **kwargs)
            elif stage == "stage_02_transform":
                quality_data = self._analyze_transform_stage(partition, **kwargs)
            elif stage == "stage_03_load":
                quality_data = self._analyze_load_stage(partition, **kwargs)
            elif stage == "stage_04_analysis":
                quality_data = self._analyze_analysis_stage(partition, **kwargs)
            elif stage == "stage_05_reporting":
                quality_data = self._analyze_reporting_stage(partition, **kwargs)
            else:
                quality_data = self._analyze_generic_stage(stage, partition, **kwargs)

            # Add metadata
            quality_data.update(
                {
                    "stage": stage,
                    "partition": partition,
                    "timestamp": datetime.now().isoformat(),
                    "build_id": self.build_id,
                    "tier_name": self.tier_name,
                }
            )

            # Store stage report
            self.stage_reports[stage] = quality_data
            self.build_summary["stages"][stage] = quality_data

            # Save stage quality report
            self._save_stage_report(stage, quality_data)

            logger.info(
                f"Quality report completed for {stage}: {quality_data.get('overall_success_rate', 'N/A')} success rate"
            )
            return quality_data

        except Exception as e:
            logger.error(f"Failed to generate quality report for {stage}: {e}")
            return {"error": str(e), "stage": stage, "timestamp": datetime.now().isoformat()}

    def _analyze_extract_stage(self, partition: str, **kwargs) -> Dict[str, Any]:
        """Analyze extraction stage quality"""
        quality_data = {
            "stage_name": "Data Extraction",
            "yfinance_quality": self._analyze_yfinance_extraction(partition),
            "sec_edgar_quality": self._analyze_sec_extraction(partition),
        }

        # Calculate overall success rate
        yf_rate = quality_data["yfinance_quality"].get("success_rate", 0)
        sec_rate = quality_data["sec_edgar_quality"].get("success_rate", 0)
        quality_data["overall_success_rate"] = (yf_rate + sec_rate) / 2

        return quality_data

    def _analyze_yfinance_extraction(self, partition: str) -> Dict[str, Any]:
        """Analyze YFinance data extraction quality"""
        try:
            # Look for YFinance data in extract stage
            yfinance_path = self.base_path / "stage_01_extract" / "yfinance"

            if partition:
                partition_path = yfinance_path / partition
            else:
                partition_path = yfinance_path / "latest"

            if not partition_path.exists():
                return {
                    "success_rate": 0,
                    "total_expected": 0,
                    "total_found": 0,
                    "companies_processed": [],
                    "missing_companies": [],
                    "status": "no_data_found",
                }

            # Count companies and files
            companies_found = []
            total_files = 0

            for company_dir in partition_path.iterdir():
                if company_dir.is_dir():
                    company_ticker = company_dir.name
                    json_files = list(company_dir.glob("*.json"))
                    if json_files:
                        companies_found.append(
                            {
                                "ticker": company_ticker,
                                "files_count": len(json_files),
                                "files": [f.name for f in json_files],
                            }
                        )
                        total_files += len(json_files)

            # Estimate expected count based on tier
            expected_companies = self._get_expected_companies_count()
            success_rate = len(companies_found) / max(expected_companies, 1)

            return {
                "success_rate": min(success_rate, 1.0),  # Cap at 100%
                "total_expected": expected_companies,
                "total_found": len(companies_found),
                "total_files": total_files,
                "companies_processed": companies_found,
                "missing_companies": max(0, expected_companies - len(companies_found)),
                "status": "completed" if companies_found else "failed",
            }

        except Exception as e:
            logger.error(f"Error analyzing YFinance extraction: {e}")
            return {"success_rate": 0, "error": str(e), "status": "error"}

    def _analyze_sec_extraction(self, partition: str) -> Dict[str, Any]:
        """Analyze SEC Edgar data extraction quality"""
        try:
            # Look for SEC data in extract stage
            sec_path = self.base_path / "stage_01_extract" / "sec_edgar"

            if partition:
                partition_path = sec_path / partition
            else:
                partition_path = sec_path / "latest"

            if not partition_path.exists():
                return {
                    "success_rate": 0,
                    "total_expected": 0,
                    "total_found": 0,
                    "companies_processed": [],
                    "document_types": {},
                    "status": "no_data_found",
                }

            # Count SEC documents by company and type
            companies_found = []
            document_counts = {"10-K": 0, "10-Q": 0, "8-K": 0}
            total_documents = 0

            for company_dir in partition_path.iterdir():
                if company_dir.is_dir():
                    company_ticker = company_dir.name
                    company_docs = {"10-K": 0, "10-Q": 0, "8-K": 0}

                    # Count by document type
                    for doc_type in ["10-K", "10-Q", "8-K"]:
                        doc_files = list(company_dir.rglob(f"*{doc_type.replace('-', '')}*.txt"))
                        company_docs[doc_type] = len(doc_files)
                        document_counts[doc_type] += len(doc_files)
                        total_documents += len(doc_files)

                    if sum(company_docs.values()) > 0:
                        companies_found.append(
                            {
                                "ticker": company_ticker,
                                "documents": company_docs,
                                "total_docs": sum(company_docs.values()),
                            }
                        )

            # Estimate expected SEC documents
            expected_companies = self._get_expected_companies_count()
            expected_docs_per_company = 15  # Rough estimate: 5 years × 3 doc types
            expected_total_docs = expected_companies * expected_docs_per_company

            success_rate = (
                total_documents / max(expected_total_docs, 1) if expected_total_docs > 0 else 0
            )

            return {
                "success_rate": min(success_rate, 1.0),  # Cap at 100%
                "total_expected": expected_total_docs,
                "total_found": total_documents,
                "companies_processed": companies_found,
                "document_types": document_counts,
                "companies_with_sec_data": len(companies_found),
                "status": "completed" if companies_found else "failed",
            }

        except Exception as e:
            logger.error(f"Error analyzing SEC extraction: {e}")
            return {"success_rate": 0, "error": str(e), "status": "error"}

    def _analyze_transform_stage(self, partition: str, **kwargs) -> Dict[str, Any]:
        """Analyze transformation stage quality"""
        try:
            transform_path = self.base_path / "stage_02_transform"

            if partition:
                partition_path = transform_path / partition
            else:
                # Look for latest partition
                partition_dirs = [d for d in transform_path.iterdir() if d.is_dir()]
                partition_path = (
                    max(partition_dirs, key=lambda x: x.name) if partition_dirs else None
                )

            if not partition_path or not partition_path.exists():
                return {
                    "success_rate": 0,
                    "status": "no_data_found",
                    "error": "Transform partition not found",
                }

            # Count transformed files
            cleaned_files = (
                len(list(partition_path.glob("**/cleaned/*.json")))
                if (partition_path / "cleaned").exists()
                else 0
            )
            enriched_files = (
                len(list(partition_path.glob("**/enriched/*.json")))
                if (partition_path / "enriched").exists()
                else 0
            )
            normalized_files = (
                len(list(partition_path.glob("**/normalized/*.json")))
                if (partition_path / "normalized").exists()
                else 0
            )

            total_transformed = cleaned_files + enriched_files + normalized_files
            expected_files = self._get_expected_companies_count() * 3  # Rough estimate

            return {
                "success_rate": min(total_transformed / max(expected_files, 1), 1.0),
                "cleaned_files": cleaned_files,
                "enriched_files": enriched_files,
                "normalized_files": normalized_files,
                "total_transformed": total_transformed,
                "status": "completed" if total_transformed > 0 else "failed",
            }

        except Exception as e:
            logger.error(f"Error analyzing transform stage: {e}")
            return {"success_rate": 0, "error": str(e), "status": "error"}

    def _analyze_load_stage(self, partition: str, **kwargs) -> Dict[str, Any]:
        """Analyze load stage quality"""
        try:
            load_path = self.base_path / "stage_03_load"

            if partition:
                partition_path = load_path / partition
            else:
                # Look for latest partition
                partition_dirs = [d for d in load_path.iterdir() if d.is_dir()]
                partition_path = (
                    max(partition_dirs, key=lambda x: x.name) if partition_dirs else None
                )

            if not partition_path or not partition_path.exists():
                return {
                    "success_rate": 0,
                    "status": "no_data_found",
                    "error": "Load partition not found",
                }

            # Count loaded artifacts
            graph_nodes = (
                len(list(partition_path.glob("**/graph_nodes/*.json")))
                if (partition_path / "graph_nodes").exists()
                else 0
            )
            embeddings = (
                len(list(partition_path.glob("**/embeddings/*.npy")))
                if (partition_path / "embeddings").exists()
                else 0
            )
            dcf_results = (
                len(list(partition_path.glob("**/dcf_results/*.json")))
                if (partition_path / "dcf_results").exists()
                else 0
            )

            total_loaded = graph_nodes + embeddings + dcf_results
            expected_artifacts = self._get_expected_companies_count() * 2  # Rough estimate

            return {
                "success_rate": min(total_loaded / max(expected_artifacts, 1), 1.0),
                "graph_nodes": graph_nodes,
                "embeddings_files": embeddings,
                "dcf_results": dcf_results,
                "total_loaded": total_loaded,
                "status": "completed" if total_loaded > 0 else "failed",
            }

        except Exception as e:
            logger.error(f"Error analyzing load stage: {e}")
            return {"success_rate": 0, "error": str(e), "status": "error"}

    def _analyze_analysis_stage(self, partition: str, **kwargs) -> Dict[str, Any]:
        """Analyze DCF analysis stage quality"""
        try:
            companies_analyzed = kwargs.get("companies_analyzed", 0)
            expected_companies = self._get_expected_companies_count()

            success_rate = (
                companies_analyzed / max(expected_companies, 1) if expected_companies > 0 else 0
            )

            return {
                "success_rate": min(success_rate, 1.0),
                "companies_analyzed": companies_analyzed,
                "expected_companies": expected_companies,
                "companies_failed": max(0, expected_companies - companies_analyzed),
                "status": "completed" if companies_analyzed > 0 else "failed",
            }

        except Exception as e:
            logger.error(f"Error analyzing analysis stage: {e}")
            return {"success_rate": 0, "error": str(e), "status": "error"}

    def _analyze_reporting_stage(self, partition: str, **kwargs) -> Dict[str, Any]:
        """Analyze reporting stage quality"""
        try:
            reports_generated = kwargs.get("reports_generated", 0)
            expected_reports = 1  # Typically one comprehensive report per build

            success_rate = (
                reports_generated / max(expected_reports, 1) if expected_reports > 0 else 0
            )

            return {
                "success_rate": min(success_rate, 1.0),
                "reports_generated": reports_generated,
                "expected_reports": expected_reports,
                "status": "completed" if reports_generated > 0 else "failed",
            }

        except Exception as e:
            logger.error(f"Error analyzing reporting stage: {e}")
            return {"success_rate": 0, "error": str(e), "status": "error"}

    def _analyze_generic_stage(self, stage: str, partition: str, **kwargs) -> Dict[str, Any]:
        """Generic stage analysis for unknown stages"""
        return {
            "success_rate": 1.0,  # Assume success if no specific analysis
            "status": "completed",
            "note": f"Generic analysis for {stage} - no specific quality metrics defined",
        }

    def _get_expected_companies_count(self) -> int:
        """Get expected number of companies based on tier"""
        tier_mapping = {
            "f2": 2,
            "test": 2,
            "m7": 7,
            "n100": 100,
            "nasdaq100": 100,
            "v3k": 3500,
            "vti": 3500,
        }
        return tier_mapping.get(self.tier_name.lower(), 7)

    def _save_stage_report(self, stage: str, quality_data: Dict[str, Any]) -> None:
        """Save individual stage quality report"""
        try:
            # Save JSON format
            json_file = self.quality_base_path / f"{stage}_quality_report.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(quality_data, f, indent=2)

            # Save Markdown format
            md_file = self.quality_base_path / f"{stage}_quality_report.md"
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(self._format_stage_report_markdown(stage, quality_data))

            logger.debug(f"Saved quality report for {stage}: {json_file}")

        except Exception as e:
            logger.error(f"Failed to save stage report for {stage}: {e}")

    def _format_stage_report_markdown(self, stage: str, quality_data: Dict[str, Any]) -> str:
        """Format stage quality report as Markdown"""
        md_content = f"""# Quality Report: {stage}

**Build ID**: {self.build_id}  
**Tier**: {self.tier_name}  
**Timestamp**: {quality_data.get('timestamp', 'N/A')}  
**Overall Success Rate**: {quality_data.get('overall_success_rate', 0):.1%}  
**Status**: {quality_data.get('status', 'unknown')}

## Stage Details

"""

        # Add stage-specific details
        if stage == "stage_01_extract":
            md_content += self._format_extract_details(quality_data)
        elif stage == "stage_04_analysis":
            md_content += self._format_analysis_details(quality_data)
        elif stage == "stage_05_reporting":
            md_content += self._format_reporting_details(quality_data)
        else:
            # Generic details
            for key, value in quality_data.items():
                if key not in ["stage", "timestamp", "build_id", "tier_name"]:
                    md_content += f"- **{key.replace('_', ' ').title()}**: {value}\n"

        md_content += f"\n---\n*Generated: {datetime.now().isoformat()}*\n"
        return md_content

    def _format_extract_details(self, quality_data: Dict[str, Any]) -> str:
        """Format extraction stage details"""
        details = "### YFinance Data Quality\n\n"
        yf_data = quality_data.get("yfinance_quality", {})
        details += f"- **Success Rate**: {yf_data.get('success_rate', 0):.1%}\n"
        details += f"- **Companies Found**: {yf_data.get('total_found', 0)}\n"
        details += f"- **Total Files**: {yf_data.get('total_files', 0)}\n\n"

        details += "### SEC Edgar Data Quality\n\n"
        sec_data = quality_data.get("sec_edgar_quality", {})
        details += f"- **Success Rate**: {sec_data.get('success_rate', 0):.1%}\n"
        details += f"- **Companies with SEC Data**: {sec_data.get('companies_with_sec_data', 0)}\n"
        details += f"- **Total Documents**: {sec_data.get('total_found', 0)}\n"

        doc_types = sec_data.get("document_types", {})
        if doc_types:
            details += "- **Document Types**:\n"
            for doc_type, count in doc_types.items():
                details += f"  - {doc_type}: {count}\n"

        return details

    def _format_analysis_details(self, quality_data: Dict[str, Any]) -> str:
        """Format analysis stage details"""
        details = "### DCF Analysis Results\n\n"
        details += f"- **Companies Analyzed**: {quality_data.get('companies_analyzed', 0)}\n"
        details += f"- **Expected Companies**: {quality_data.get('expected_companies', 0)}\n"
        details += f"- **Companies Failed**: {quality_data.get('companies_failed', 0)}\n"
        return details

    def _format_reporting_details(self, quality_data: Dict[str, Any]) -> str:
        """Format reporting stage details"""
        details = "### Report Generation Results\n\n"
        details += f"- **Reports Generated**: {quality_data.get('reports_generated', 0)}\n"
        details += f"- **Expected Reports**: {quality_data.get('expected_reports', 1)}\n"
        return details

    def generate_build_summary_report(self) -> Dict[str, Any]:
        """Generate comprehensive build quality summary"""
        try:
            # Calculate overall build health
            stage_success_rates = []
            for stage_data in self.stage_reports.values():
                if "overall_success_rate" in stage_data:
                    stage_success_rates.append(stage_data["overall_success_rate"])
                elif "success_rate" in stage_data:
                    stage_success_rates.append(stage_data["success_rate"])

            overall_health = (
                sum(stage_success_rates) / len(stage_success_rates) if stage_success_rates else 0
            )

            summary = {
                "build_id": self.build_id,
                "tier_name": self.tier_name,
                "overall_build_health": overall_health,
                "stages_completed": len(self.stage_reports),
                "stages_successful": sum(
                    1 for data in self.stage_reports.values() if data.get("status") == "completed"
                ),
                "timestamp": datetime.now().isoformat(),
                "stage_summaries": {},
            }

            # Add stage summaries
            for stage, data in self.stage_reports.items():
                summary["stage_summaries"][stage] = {
                    "success_rate": data.get("overall_success_rate", data.get("success_rate", 0)),
                    "status": data.get("status", "unknown"),
                }

            # Update build summary
            self.build_summary["overall_statistics"] = summary
            self.build_summary["end_time"] = datetime.now().isoformat()

            # Save summary reports
            self._save_build_summary(summary)

            logger.info(f"Build quality summary generated: {overall_health:.1%} overall health")
            return summary

        except Exception as e:
            logger.error(f"Failed to generate build summary: {e}")
            return {"error": str(e), "build_id": self.build_id}

    def _save_build_summary(self, summary: Dict[str, Any]) -> None:
        """Save build quality summary"""
        try:
            # Save JSON summary
            json_file = self.quality_base_path / "build_quality_summary.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)

            # Save Markdown summary
            md_file = self.quality_base_path / "build_quality_summary.md"
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(self._format_build_summary_markdown(summary))

            # Save complete build data
            complete_file = self.quality_base_path / "complete_build_quality.json"
            with open(complete_file, "w", encoding="utf-8") as f:
                json.dump(self.build_summary, f, indent=2)

            logger.info(f"Build quality summary saved: {json_file}")

        except Exception as e:
            logger.error(f"Failed to save build summary: {e}")

    def _format_build_summary_markdown(self, summary: Dict[str, Any]) -> str:
        """Format build quality summary as Markdown"""
        md_content = f"""# Build Quality Summary

**Build ID**: {summary['build_id']}  
**Tier**: {summary['tier_name']}  
**Overall Health**: {summary['overall_build_health']:.1%}  
**Timestamp**: {summary['timestamp']}

## Stage Performance

| Stage | Success Rate | Status |
|-------|-------------|--------|
"""

        for stage, data in summary.get("stage_summaries", {}).items():
            stage_name = stage.replace("stage_", "").replace("_", " ").title()
            success_rate = f"{data['success_rate']:.1%}"
            status = data["status"].replace("_", " ").title()
            md_content += f"| {stage_name} | {success_rate} | {status} |\n"

        # Add summary statistics
        md_content += f"""

## Summary Statistics

- **Total Stages**: {summary['stages_completed']}
- **Successful Stages**: {summary['stages_successful']}
- **Failed Stages**: {summary['stages_completed'] - summary['stages_successful']}
- **Success Rate**: {summary['stages_successful'] / max(summary['stages_completed'], 1):.1%}

## Build Health Assessment

"""

        health = summary["overall_build_health"]
        if health >= 0.9:
            md_content += "🟢 **Excellent** - Build completed with high quality\n"
        elif health >= 0.7:
            md_content += "🟡 **Good** - Build completed with acceptable quality\n"
        elif health >= 0.5:
            md_content += "🟠 **Fair** - Build completed but with quality concerns\n"
        else:
            md_content += "🔴 **Poor** - Build completed with significant quality issues\n"

        md_content += f"\n---\n*Generated: {datetime.now().isoformat()}*\n"
        return md_content


def setup_quality_reporter(build_id: str, tier_name: str) -> QualityReporter:
    """Setup quality reporter instance for a build (similar to setup_logger)"""
    try:
        reporter = QualityReporter(build_id, tier_name)
        logger.info(f"Quality reporter initialized for build {build_id} ({tier_name})")
        return reporter
    except Exception as e:
        logger.error(f"Failed to setup quality reporter: {e}")
        # Return a dummy reporter that won't fail
        return _DummyQualityReporter(build_id, tier_name)


class _DummyQualityReporter:
    """Fallback dummy reporter when setup fails"""

    def __init__(self, build_id: str, tier_name: str):
        self.build_id = build_id
        self.tier_name = tier_name

    def report_stage_quality(self, stage: str, partition: str = None, **kwargs) -> Dict[str, Any]:
        return {"error": "Quality reporter not available", "stage": stage}

    def generate_build_summary_report(self) -> Dict[str, Any]:
        return {"error": "Quality reporter not available", "build_id": self.build_id}


# Global flag to track if quality reporting is available
QUALITY_REPORTING_AVAILABLE = True

try:
    # Test imports to verify dependencies
    import json
    import logging
    from datetime import datetime
    from pathlib import Path
except ImportError as e:
    logger.warning(f"Quality reporting dependencies not available: {e}")
    QUALITY_REPORTING_AVAILABLE = False
