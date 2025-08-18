#!/usr/bin/env python3
"""
Stage Analysis and Reporting Tool
Generates comprehensive reports for each data processing stage
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import yaml
    from common.directory_manager import DirectoryManager
    from common.build_tracker import BuildTracker
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


class StageReporter:
    """Generate comprehensive reports for each stage"""

    def __init__(self):
        self.dm = DirectoryManager()
        self.data_dir = Path("data")
        self.report_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def analyze_stage_00_original(self) -> Dict[str, Any]:
        """Analyze SEC and YFinance data download success rates"""
        stage_dir = self.data_dir / "stage_00_original"
        
        results = {
            "stage": "Stage 00 - Original Data Collection",
            "analysis_time": datetime.now().isoformat(),
            "data_sources": {}
        }

        # Analyze YFinance data
        yfinance_stats = self._analyze_yfinance_data(stage_dir)
        results["data_sources"]["yfinance"] = yfinance_stats

        # Analyze SEC Edgar data  
        sec_edgar_stats = self._analyze_sec_edgar_data(stage_dir)
        results["data_sources"]["sec_edgar"] = sec_edgar_stats

        # Overall success metrics
        total_expected_files = yfinance_stats.get("total_expected", 0) + sec_edgar_stats.get("total_expected", 0)
        total_actual_files = yfinance_stats.get("total_files", 0) + sec_edgar_stats.get("total_files", 0)
        
        results["overall_success_rate"] = (total_actual_files / total_expected_files * 100) if total_expected_files > 0 else 0
        results["total_files"] = total_actual_files
        results["total_expected"] = total_expected_files

        return results

    def _analyze_yfinance_data(self, stage_dir: Path) -> Dict[str, Any]:
        """Analyze YFinance data collection success"""
        yfinance_dir = stage_dir / "yfinance"
        
        stats = {
            "source": "YFinance",
            "directory": str(yfinance_dir),
            "total_files": 0,
            "tickers_found": [],
            "file_types": {},
            "success_rate": 0,
            "issues": []
        }

        if not yfinance_dir.exists():
            stats["issues"].append("YFinance directory does not exist")
            return stats

        # Count files by ticker and type
        ticker_files = {}
        for file_path in yfinance_dir.rglob("*.json"):
            stats["total_files"] += 1
            
            # Extract ticker from filename (assuming format: TICKER_yfinance_*.json)
            parts = file_path.name.split('_')
            if len(parts) >= 2:
                ticker = parts[0]
                if ticker not in ticker_files:
                    ticker_files[ticker] = 0
                ticker_files[ticker] += 1
                
                if ticker not in stats["tickers_found"]:
                    stats["tickers_found"].append(ticker)

                # Categorize file type
                file_type = "daily" if "daily" in file_path.name else "quarterly"
                if file_type not in stats["file_types"]:
                    stats["file_types"][file_type] = 0
                stats["file_types"][file_type] += 1

        # Load expected tickers from config
        expected_tickers = self._get_expected_tickers_from_configs()
        stats["tickers_expected"] = len(expected_tickers)
        stats["tickers_actual"] = len(stats["tickers_found"])
        
        # Calculate success rates
        if stats["tickers_expected"] > 0:
            stats["ticker_success_rate"] = (stats["tickers_actual"] / stats["tickers_expected"]) * 100
        
        # Expected files: assume 3 files per ticker (daily, quarterly, info)
        stats["total_expected"] = stats["tickers_expected"] * 3
        stats["success_rate"] = (stats["total_files"] / stats["total_expected"] * 100) if stats["total_expected"] > 0 else 0

        # Identify missing tickers
        missing_tickers = set(expected_tickers) - set(stats["tickers_found"])
        if missing_tickers:
            stats["missing_tickers"] = list(missing_tickers)[:10]  # Show first 10
            stats["issues"].append(f"Missing data for {len(missing_tickers)} tickers")

        return stats

    def _analyze_sec_edgar_data(self, stage_dir: Path) -> Dict[str, Any]:
        """Analyze SEC Edgar data collection success"""
        sec_edgar_dir = stage_dir / "sec-edgar"
        
        stats = {
            "source": "SEC Edgar",
            "directory": str(sec_edgar_dir),
            "total_files": 0,
            "companies_found": [],
            "filing_types": {"10-K": 0, "10-Q": 0, "8-K": 0},
            "success_rate": 0,
            "issues": []
        }

        if not sec_edgar_dir.exists():
            stats["issues"].append("SEC Edgar directory does not exist")
            return stats

        # Analyze CIK-based directory structure
        cik_dirs = [d for d in sec_edgar_dir.iterdir() if d.is_dir() and d.name.startswith("00")]
        
        for cik_dir in cik_dirs:
            cik = cik_dir.name
            
            # Map CIK to ticker (for M7 companies)
            ticker = self._cik_to_ticker(cik)
            if ticker and ticker not in stats["companies_found"]:
                stats["companies_found"].append(ticker)
            
            # Count files by filing type
            for filing_type in ["10-K", "10-Q", "8-K"]:
                filing_dir = cik_dir / filing_type.lower()
                if filing_dir.exists():
                    files = list(filing_dir.glob("*.txt"))
                    count = len(files)
                    stats["filing_types"][filing_type] += count
                    stats["total_files"] += count

        # Expected data (M7 companies with SEC data)
        m7_companies_with_sec = 7  # All M7 have SEC data
        stats["companies_expected"] = m7_companies_with_sec
        stats["companies_actual"] = len(stats["companies_found"])
        
        # Expected files: assume 15 files per company (5 years × 3 filing types)
        stats["total_expected"] = m7_companies_with_sec * 15
        stats["success_rate"] = (stats["total_files"] / stats["total_expected"] * 100) if stats["total_expected"] > 0 else 0
        
        # Company success rate
        if stats["companies_expected"] > 0:
            stats["company_success_rate"] = (stats["companies_actual"] / stats["companies_expected"]) * 100

        if stats["companies_actual"] < stats["companies_expected"]:
            stats["issues"].append(f"Only {stats['companies_actual']}/{stats['companies_expected']} M7 companies have SEC data")

        return stats

    def analyze_stage_01_extract(self) -> Dict[str, Any]:
        """Analyze extraction stage success rates"""
        stage_dir = self.data_dir / "stage_01_extract"
        
        results = {
            "stage": "Stage 01 - Data Extraction",
            "analysis_time": datetime.now().isoformat(),
            "data_sources": {}
        }

        # Check for extracted YFinance data
        yfinance_dir = stage_dir / "yfinance"
        yf_stats = {
            "source": "YFinance Extraction",
            "total_files": 0,
            "tickers_processed": []
        }
        
        if yfinance_dir.exists():
            for file_path in yfinance_dir.rglob("*.json"):
                yf_stats["total_files"] += 1
                ticker = file_path.name.split('_')[0]
                if ticker not in yf_stats["tickers_processed"]:
                    yf_stats["tickers_processed"].append(ticker)
        
        results["data_sources"]["yfinance"] = yf_stats

        # Check for extracted SEC data
        sec_dir = stage_dir / "sec_edgar"  
        sec_stats = {
            "source": "SEC Edgar Extraction",
            "total_files": 0,
            "companies_processed": []
        }

        if sec_dir.exists():
            for file_path in sec_dir.rglob("*.txt"):
                sec_stats["total_files"] += 1
                # Extract ticker from path or filename
                ticker = self._extract_ticker_from_path(file_path)
                if ticker and ticker not in sec_stats["companies_processed"]:
                    sec_stats["companies_processed"].append(ticker)

        results["data_sources"]["sec_edgar"] = sec_stats

        # Calculate extraction efficiency
        stage_00_results = self.analyze_stage_00_original()
        original_yf_files = stage_00_results["data_sources"]["yfinance"]["total_files"]
        original_sec_files = stage_00_results["data_sources"]["sec_edgar"]["total_files"]
        
        results["extraction_efficiency"] = {
            "yfinance": (yf_stats["total_files"] / original_yf_files * 100) if original_yf_files > 0 else 0,
            "sec_edgar": (sec_stats["total_files"] / original_sec_files * 100) if original_sec_files > 0 else 0
        }

        return results

    def analyze_stage_02_transform(self) -> Dict[str, Any]:
        """Analyze transformation stage success rates"""
        stage_dir = self.data_dir / "stage_02_transform"
        
        results = {
            "stage": "Stage 02 - Data Transformation",
            "analysis_time": datetime.now().isoformat(),
            "transformation_outputs": {}
        }

        # Look for transformed data
        if stage_dir.exists():
            # Check for cleaned data
            cleaned_files = list(stage_dir.rglob("*cleaned*"))
            normalized_files = list(stage_dir.rglob("*normalized*"))
            enriched_files = list(stage_dir.rglob("*enriched*"))

            results["transformation_outputs"] = {
                "cleaned_files": len(cleaned_files),
                "normalized_files": len(normalized_files),
                "enriched_files": len(enriched_files),
                "total_transformed": len(cleaned_files) + len(normalized_files) + len(enriched_files)
            }

            # Calculate transformation success rate
            stage_01_results = self.analyze_stage_01_extract()
            input_files = (stage_01_results["data_sources"]["yfinance"]["total_files"] + 
                          stage_01_results["data_sources"]["sec_edgar"]["total_files"])
            
            results["transformation_success_rate"] = (
                results["transformation_outputs"]["total_transformed"] / input_files * 100
            ) if input_files > 0 else 0
        else:
            results["transformation_outputs"] = {"error": "Stage 02 directory not found"}
            results["transformation_success_rate"] = 0

        return results

    def analyze_stage_03_load(self) -> Dict[str, Any]:
        """Analyze load stage success rates"""
        stage_dir = self.data_dir / "stage_03_load"
        
        results = {
            "stage": "Stage 03 - Data Loading",
            "analysis_time": datetime.now().isoformat(),
            "load_outputs": {}
        }

        if stage_dir.exists():
            # Count different types of load outputs
            graph_nodes = list(stage_dir.rglob("*graph_nodes*"))
            embeddings = list(stage_dir.rglob("*embeddings*"))
            vector_indices = list(stage_dir.rglob("*vector_index*"))
            dcf_results = list(stage_dir.rglob("*dcf_results*"))

            results["load_outputs"] = {
                "graph_node_files": len(graph_nodes),
                "embedding_files": len(embeddings),
                "vector_index_files": len(vector_indices),
                "dcf_result_files": len(dcf_results),
                "total_loaded": len(graph_nodes) + len(embeddings) + len(vector_indices) + len(dcf_results)
            }

            # Analyze by ticker
            tickers_with_data = set()
            for file_path in stage_dir.rglob("*"):
                if file_path.is_file():
                    ticker = self._extract_ticker_from_path(file_path)
                    if ticker:
                        tickers_with_data.add(ticker)

            results["tickers_processed"] = list(tickers_with_data)
            results["ticker_count"] = len(tickers_with_data)

            # Calculate load success rate
            stage_02_results = self.analyze_stage_02_transform()
            input_files = stage_02_results["transformation_outputs"].get("total_transformed", 0)
            
            results["load_success_rate"] = (
                results["load_outputs"]["total_loaded"] / input_files * 100
            ) if input_files > 0 else 0

        else:
            results["load_outputs"] = {"error": "Stage 03 directory not found"}
            results["load_success_rate"] = 0

        return results

    def analyze_build_artifacts(self) -> Dict[str, Any]:
        """Analyze build artifacts and reports"""
        build_dir = self.data_dir / "stage_99_build"
        
        results = {
            "stage": "Stage 99 - Build Artifacts",
            "analysis_time": datetime.now().isoformat(),
            "build_summary": {}
        }

        if build_dir.exists():
            # Find latest build
            build_dirs = [d for d in build_dir.iterdir() if d.is_dir() and d.name.startswith("build_")]
            if build_dirs:
                latest_build = max(build_dirs, key=lambda x: x.name)
                results["latest_build"] = latest_build.name

                # Analyze build artifacts
                manifest_files = list(latest_build.glob("BUILD_MANIFEST.*"))
                dcf_reports = list(latest_build.glob("*DCF_Report*"))
                sec_examples = list((build_dir / "sec_integration_examples").glob("*")) if (build_dir / "sec_integration_examples").exists() else []

                results["build_summary"] = {
                    "manifest_files": len(manifest_files),
                    "dcf_reports": len(dcf_reports), 
                    "sec_integration_examples": len(sec_examples),
                    "build_directory": str(latest_build)
                }

                # Load build manifest if available
                if manifest_files:
                    manifest_path = manifest_files[0]
                    if manifest_path.suffix == '.json':
                        try:
                            with open(manifest_path) as f:
                                manifest = json.load(f)
                                results["build_details"] = {
                                    "build_info": manifest.get("build_info", {}),
                                    "stages_completed": len(manifest.get("stages", {})),
                                    "total_companies": manifest.get("statistics", {}).get("companies_processed", 0)
                                }
                        except Exception as e:
                            results["manifest_error"] = str(e)

        return results

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive report across all stages"""
        print("🔍 Analyzing all data processing stages...")
        
        comprehensive_report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_id": f"stage_analysis_{self.report_timestamp}",
                "analysis_scope": "Complete ETL Pipeline"
            },
            "stage_analyses": {}
        }

        # Analyze each stage
        stages = [
            ("stage_00", self.analyze_stage_00_original),
            ("stage_01", self.analyze_stage_01_extract),
            ("stage_02", self.analyze_stage_02_transform),
            ("stage_03", self.analyze_stage_03_load),
            ("stage_99", self.analyze_build_artifacts)
        ]

        for stage_name, analyzer in stages:
            print(f"📊 Analyzing {stage_name}...")
            try:
                comprehensive_report["stage_analyses"][stage_name] = analyzer()
            except Exception as e:
                comprehensive_report["stage_analyses"][stage_name] = {
                    "error": str(e),
                    "status": "analysis_failed"
                }

        # Generate summary metrics
        comprehensive_report["pipeline_summary"] = self._generate_pipeline_summary(comprehensive_report["stage_analyses"])

        return comprehensive_report

    def _generate_pipeline_summary(self, stage_analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall pipeline success metrics"""
        summary = {
            "overall_pipeline_health": "unknown",
            "data_flow_analysis": {},
            "recommendations": []
        }

        # Extract key metrics
        stage_00 = stage_analyses.get("stage_00", {})
        stage_01 = stage_analyses.get("stage_01", {})
        stage_02 = stage_analyses.get("stage_02", {})
        stage_03 = stage_analyses.get("stage_03", {})
        stage_99 = stage_analyses.get("stage_99", {})

        # Data flow analysis
        original_files = stage_00.get("total_files", 0)
        extracted_files = (stage_01.get("data_sources", {}).get("yfinance", {}).get("total_files", 0) +
                          stage_01.get("data_sources", {}).get("sec_edgar", {}).get("total_files", 0))
        transformed_files = stage_02.get("transformation_outputs", {}).get("total_transformed", 0)
        loaded_files = stage_03.get("load_outputs", {}).get("total_loaded", 0)

        summary["data_flow_analysis"] = {
            "stage_00_files": original_files,
            "stage_01_files": extracted_files,
            "stage_02_files": transformed_files,
            "stage_03_files": loaded_files,
            "extraction_rate": (extracted_files / original_files * 100) if original_files > 0 else 0,
            "transformation_rate": (transformed_files / extracted_files * 100) if extracted_files > 0 else 0,
            "load_rate": (loaded_files / transformed_files * 100) if transformed_files > 0 else 0
        }

        # Health assessment
        extraction_rate = summary["data_flow_analysis"]["extraction_rate"]
        transformation_rate = summary["data_flow_analysis"]["transformation_rate"]
        load_rate = summary["data_flow_analysis"]["load_rate"]

        if all(rate >= 80 for rate in [extraction_rate, transformation_rate, load_rate]):
            summary["overall_pipeline_health"] = "excellent"
        elif all(rate >= 60 for rate in [extraction_rate, transformation_rate, load_rate]):
            summary["overall_pipeline_health"] = "good"
        elif all(rate >= 40 for rate in [extraction_rate, transformation_rate, load_rate]):
            summary["overall_pipeline_health"] = "fair"
        else:
            summary["overall_pipeline_health"] = "needs_attention"

        # Generate recommendations
        if extraction_rate < 80:
            summary["recommendations"].append("Improve data extraction processes - low success rate detected")
        if transformation_rate < 80:
            summary["recommendations"].append("Review data transformation logic - files may be failing processing")
        if load_rate < 80:
            summary["recommendations"].append("Check data loading mechanisms - load failures detected")

        # SEC-specific recommendations
        sec_success = stage_00.get("data_sources", {}).get("sec_edgar", {}).get("success_rate", 0)
        if sec_success < 80:
            summary["recommendations"].append("SEC Edgar data collection needs improvement")

        return summary

    def _get_expected_tickers_from_configs(self) -> List[str]:
        """Get expected tickers from configuration files"""
        tickers = set()
        
        config_files = [
            "data/config/list_fast_2.yml",
            "data/config/list_magnificent_7.yml",
            "data/config/list_nasdaq_100.yml"
        ]
        
        for config_file in config_files:
            config_path = Path(config_file)
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        config = yaml.safe_load(f)
                        if "companies" in config:
                            tickers.update(config["companies"].keys())
                except Exception:
                    continue
        
        return list(tickers)

    def _cik_to_ticker(self, cik: str) -> Optional[str]:
        """Map CIK to ticker for M7 companies"""
        cik_mapping = {
            "0000320193": "AAPL",
            "0000789019": "MSFT", 
            "0001018724": "AMZN",
            "0001652044": "GOOGL",
            "0001326801": "META",
            "0001318605": "TSLA",
            "0001065280": "NFLX"
        }
        return cik_mapping.get(cik)

    def _extract_ticker_from_path(self, file_path: Path) -> Optional[str]:
        """Extract ticker symbol from file path or filename"""
        # Try to extract from filename first
        parts = file_path.name.split('_')
        if len(parts) >= 1:
            potential_ticker = parts[0].upper()
            if len(potential_ticker) <= 5 and potential_ticker.isalpha():
                return potential_ticker
        
        # Try to extract from parent directory
        for part in file_path.parts:
            if len(part) <= 5 and part.isupper() and part.isalpha():
                return part
                
        return None

    def save_report(self, report: Dict[str, Any], output_dir: Optional[Path] = None) -> Path:
        """Save comprehensive report to file"""
        if output_dir is None:
            output_dir = self.data_dir / "reports"
        
        output_dir.mkdir(exist_ok=True)
        
        # Save JSON report
        json_path = output_dir / f"stage_analysis_report_{self.report_timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save markdown summary
        md_path = output_dir / f"stage_analysis_summary_{self.report_timestamp}.md"
        self._save_markdown_summary(report, md_path)
        
        print(f"📊 Reports saved:")
        print(f"   JSON: {json_path}")
        print(f"   Markdown: {md_path}")
        
        return json_path

    def _save_markdown_summary(self, report: Dict[str, Any], output_path: Path):
        """Save markdown summary of the report"""
        with open(output_path, 'w') as f:
            f.write(f"# ETL Pipeline Stage Analysis Report\n\n")
            f.write(f"**Generated:** {report['report_metadata']['generated_at']}\n")
            f.write(f"**Report ID:** {report['report_metadata']['report_id']}\n\n")
            
            # Pipeline summary
            summary = report.get("pipeline_summary", {})
            f.write(f"## Pipeline Health: {summary.get('overall_pipeline_health', 'Unknown').title()}\n\n")
            
            # Data flow
            flow = summary.get("data_flow_analysis", {})
            f.write("## Data Flow Analysis\n\n")
            f.write(f"- **Stage 00 (Original):** {flow.get('stage_00_files', 0)} files\n")
            f.write(f"- **Stage 01 (Extract):** {flow.get('stage_01_files', 0)} files ({flow.get('extraction_rate', 0):.1f}% success)\n")
            f.write(f"- **Stage 02 (Transform):** {flow.get('stage_02_files', 0)} files ({flow.get('transformation_rate', 0):.1f}% success)\n")
            f.write(f"- **Stage 03 (Load):** {flow.get('stage_03_files', 0)} files ({flow.get('load_rate', 0):.1f}% success)\n\n")
            
            # Recommendations
            recommendations = summary.get("recommendations", [])
            if recommendations:
                f.write("## Recommendations\n\n")
                for i, rec in enumerate(recommendations, 1):
                    f.write(f"{i}. {rec}\n")
                f.write("\n")
            
            # Stage details
            f.write("## Stage Details\n\n")
            
            for stage_name, stage_data in report.get("stage_analyses", {}).items():
                stage_title = stage_data.get("stage", stage_name)
                f.write(f"### {stage_title}\n\n")
                
                if "error" in stage_data:
                    f.write(f"❌ **Error:** {stage_data['error']}\n\n")
                    continue
                
                # Stage-specific details
                if stage_name == "stage_00":
                    self._write_stage_00_details(f, stage_data)
                elif stage_name == "stage_01":
                    self._write_stage_01_details(f, stage_data)
                elif stage_name == "stage_02":
                    self._write_stage_02_details(f, stage_data)
                elif stage_name == "stage_03":
                    self._write_stage_03_details(f, stage_data)
                elif stage_name == "stage_99":
                    self._write_stage_99_details(f, stage_data)

    def _write_stage_00_details(self, f, stage_data):
        """Write Stage 00 specific details to markdown"""
        f.write(f"**Overall Success Rate:** {stage_data.get('overall_success_rate', 0):.1f}%\n\n")
        
        for source_name, source_data in stage_data.get("data_sources", {}).items():
            f.write(f"#### {source_data.get('source', source_name)}\n")
            f.write(f"- Files: {source_data.get('total_files', 0)}/{source_data.get('total_expected', 0)}\n")
            f.write(f"- Success Rate: {source_data.get('success_rate', 0):.1f}%\n")
            if source_name == "yfinance":
                f.write(f"- Tickers: {source_data.get('tickers_actual', 0)}/{source_data.get('tickers_expected', 0)}\n")
            elif source_name == "sec_edgar":
                f.write(f"- Companies: {source_data.get('companies_actual', 0)}/{source_data.get('companies_expected', 0)}\n")
            f.write("\n")

    def _write_stage_01_details(self, f, stage_data):
        """Write Stage 01 specific details to markdown"""
        for source_name, source_data in stage_data.get("data_sources", {}).items():
            f.write(f"#### {source_data.get('source', source_name)}\n")
            f.write(f"- Files: {source_data.get('total_files', 0)}\n")
            if 'tickers_processed' in source_data:
                f.write(f"- Tickers: {len(source_data['tickers_processed'])}\n")
            if 'companies_processed' in source_data:
                f.write(f"- Companies: {len(source_data['companies_processed'])}\n")
            f.write("\n")

    def _write_stage_02_details(self, f, stage_data):
        """Write Stage 02 specific details to markdown"""
        outputs = stage_data.get("transformation_outputs", {})
        f.write(f"- Cleaned files: {outputs.get('cleaned_files', 0)}\n")
        f.write(f"- Normalized files: {outputs.get('normalized_files', 0)}\n") 
        f.write(f"- Enriched files: {outputs.get('enriched_files', 0)}\n")
        f.write(f"- Success Rate: {stage_data.get('transformation_success_rate', 0):.1f}%\n\n")

    def _write_stage_03_details(self, f, stage_data):
        """Write Stage 03 specific details to markdown"""
        outputs = stage_data.get("load_outputs", {})
        f.write(f"- Graph nodes: {outputs.get('graph_node_files', 0)}\n")
        f.write(f"- Embeddings: {outputs.get('embedding_files', 0)}\n")
        f.write(f"- Vector indices: {outputs.get('vector_index_files', 0)}\n")
        f.write(f"- DCF results: {outputs.get('dcf_result_files', 0)}\n")
        f.write(f"- Tickers processed: {stage_data.get('ticker_count', 0)}\n")
        f.write(f"- Success Rate: {stage_data.get('load_success_rate', 0):.1f}%\n\n")

    def _write_stage_99_details(self, f, stage_data):
        """Write Stage 99 specific details to markdown""" 
        build_summary = stage_data.get("build_summary", {})
        f.write(f"- Latest build: {stage_data.get('latest_build', 'None')}\n")
        f.write(f"- Manifest files: {build_summary.get('manifest_files', 0)}\n")
        f.write(f"- DCF reports: {build_summary.get('dcf_reports', 0)}\n")
        f.write(f"- SEC examples: {build_summary.get('sec_integration_examples', 0)}\n\n")


def main():
    """Main execution function"""
    print("🚀 Starting comprehensive ETL stage analysis...")
    
    reporter = StageReporter()
    
    # Generate comprehensive report
    report = reporter.generate_comprehensive_report()
    
    # Save reports
    report_path = reporter.save_report(report)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 ETL PIPELINE ANALYSIS SUMMARY")
    print("="*60)
    
    summary = report.get("pipeline_summary", {})
    health = summary.get("overall_pipeline_health", "unknown").title()
    print(f"🏥 Pipeline Health: {health}")
    
    flow = summary.get("data_flow_analysis", {})
    print(f"📈 Data Flow:")
    print(f"   Stage 00: {flow.get('stage_00_files', 0)} files")
    print(f"   Stage 01: {flow.get('stage_01_files', 0)} files ({flow.get('extraction_rate', 0):.1f}% success)")
    print(f"   Stage 02: {flow.get('stage_02_files', 0)} files ({flow.get('transformation_rate', 0):.1f}% success)")
    print(f"   Stage 03: {flow.get('stage_03_files', 0)} files ({flow.get('load_rate', 0):.1f}% success)")
    
    recommendations = summary.get("recommendations", [])
    if recommendations:
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    
    print(f"\n📄 Full report saved to: {report_path}")
    print("="*60)


if __name__ == "__main__":
    main()