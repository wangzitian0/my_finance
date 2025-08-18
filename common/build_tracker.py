#!/usr/bin/env python3
"""
Build tracking system for ETL pipeline executions.
Tracks every build execution with comprehensive manifests and logs.
"""

import json
import logging
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class BuildTracker:
    def __init__(self, base_path: str = None):
        if base_path is None:
            # Use project root relative path
            project_root = Path(__file__).parent.parent
            base_path = project_root / "data"
        self.base_path = Path(base_path)
        self.build_base_path = self.base_path / "stage_99_build"
        self.build_base_path.mkdir(exist_ok=True)

        self.build_id = self._generate_build_id()
        self.build_path = self.build_base_path / f"build_{self.build_id}"
        self.build_path.mkdir(exist_ok=True)

        # Create subdirectories
        (self.build_path / "stage_logs").mkdir(exist_ok=True)
        (self.build_path / "artifacts").mkdir(exist_ok=True)

        self.manifest = {
            "build_info": {
                "build_id": self.build_id,
                "start_time": datetime.now().isoformat(),
                "end_time": None,
                "status": "in_progress",
                "configuration": None,
                "command": None,
            },
            "stages": {
                "stage_01_extract": {
                    "status": "pending",
                    "start_time": None,
                    "end_time": None,
                    "artifacts": [],
                    "file_count": 0,
                },
                "stage_02_transform": {
                    "status": "pending",
                    "start_time": None,
                    "end_time": None,
                    "artifacts": [],
                    "file_count": 0,
                },
                "stage_03_load": {
                    "status": "pending",
                    "start_time": None,
                    "end_time": None,
                    "artifacts": [],
                    "file_count": 0,
                },
                "stage_04_analysis": {
                    "status": "pending",
                    "start_time": None,
                    "end_time": None,
                    "artifacts": [],
                    "companies_analyzed": 0,
                },
                "stage_05_reporting": {
                    "status": "pending",
                    "start_time": None,
                    "end_time": None,
                    "artifacts": [],
                    "reports_generated": 0,
                },
            },
            "data_partitions": {
                "extract_partition": None,
                "transform_partition": None,
                "load_partition": None,
            },
            "real_outputs": {
                "yfinance_files": [],
                "sec_edgar_files": [],
                "dcf_reports": [],
                "graph_rag_outputs": [],
            },
            "statistics": {
                "files_processed": 0,
                "companies_processed": 0,
                "errors": [],
                "warnings": [],
            },
        }

    def _generate_build_id(self) -> str:
        """Generate unique build ID with timestamp"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def start_build(self, config_name: str, command: str) -> str:
        """Start a new build execution"""
        logger.info(f"Starting build {self.build_id} with config: {config_name}")

        self.manifest["build_info"]["configuration"] = config_name
        self.manifest["build_info"]["command"] = command

        self._save_manifest()
        self._update_latest_symlink()

        return self.build_id

    def start_stage(self, stage: str) -> None:
        """Mark a stage as started"""
        if stage not in self.manifest["stages"]:
            raise ValueError(f"Unknown stage: {stage}")

        logger.info(f"Starting stage: {stage}")
        self.manifest["stages"][stage]["status"] = "in_progress"
        self.manifest["stages"][stage]["start_time"] = datetime.now().isoformat()

        self._save_manifest()

    def complete_stage(
        self,
        stage: str,
        partition: Optional[str] = None,
        artifacts: Optional[List[str]] = None,
        **kwargs,
    ) -> None:
        """Mark a stage as completed with optional metadata"""
        if stage not in self.manifest["stages"]:
            raise ValueError(f"Unknown stage: {stage}")

        logger.info(f"Completing stage: {stage}")
        self.manifest["stages"][stage]["status"] = "completed"
        self.manifest["stages"][stage]["end_time"] = datetime.now().isoformat()

        if artifacts:
            self.manifest["stages"][stage]["artifacts"].extend(artifacts)

        # Update stage-specific metadata
        for key, value in kwargs.items():
            if key in self.manifest["stages"][stage]:
                self.manifest["stages"][stage][key] = value

        # Update partition info
        if partition:
            if stage == "stage_01_extract":
                self.manifest["data_partitions"]["extract_partition"] = partition
            elif stage == "stage_02_transform":
                self.manifest["data_partitions"]["transform_partition"] = partition
            elif stage == "stage_03_load":
                self.manifest["data_partitions"]["load_partition"] = partition

        self._save_manifest()

    def fail_stage(self, stage: str, error_message: str) -> None:
        """Mark a stage as failed"""
        if stage not in self.manifest["stages"]:
            raise ValueError(f"Unknown stage: {stage}")

        logger.error(f"Stage {stage} failed: {error_message}")
        self.manifest["stages"][stage]["status"] = "failed"
        self.manifest["stages"][stage]["end_time"] = datetime.now().isoformat()
        self.manifest["statistics"]["errors"].append(
            {"stage": stage, "error": error_message, "timestamp": datetime.now().isoformat()}
        )

        self._save_manifest()

    def add_warning(self, stage: str, warning_message: str) -> None:
        """Add a warning to the build"""
        logger.warning(f"Stage {stage} warning: {warning_message}")
        self.manifest["statistics"]["warnings"].append(
            {"stage": stage, "warning": warning_message, "timestamp": datetime.now().isoformat()}
        )

        self._save_manifest()

    def log_stage_output(self, stage: str, log_content: str) -> None:
        """Save stage execution logs"""
        log_file = self.build_path / "stage_logs" / f"{stage}.log"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}]\n")
            f.write(log_content)
            f.write("\n\n")

    def save_artifact(self, stage: str, artifact_name: str, content: Any) -> str:
        """Save build artifacts (configs, intermediate results, etc.)"""
        artifact_path = self.build_path / "artifacts" / f"{stage}_{artifact_name}"

        if isinstance(content, (dict, list)):
            with open(artifact_path, "w", encoding="utf-8") as f:
                json.dump(content, f, indent=2)
        elif isinstance(content, str):
            with open(artifact_path, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            # Binary content
            with open(artifact_path, "wb") as f:
                f.write(content)

        # Add to manifest
        self.manifest["stages"][stage]["artifacts"].append(artifact_name)
        self._save_manifest()

        return str(artifact_path)

    def track_real_output(self, output_type: str, file_paths: List[str]) -> None:
        """Track real output files generated during build"""
        if output_type not in self.manifest["real_outputs"]:
            self.manifest["real_outputs"][output_type] = []

        # Add new files, avoiding duplicates
        for file_path in file_paths:
            if file_path not in self.manifest["real_outputs"][output_type]:
                self.manifest["real_outputs"][output_type].append(file_path)

        logger.info(f"Tracked {len(file_paths)} {output_type} files")
        self._save_manifest()

    def scan_and_track_outputs(self) -> None:
        """Scan filesystem for actual outputs and track them"""
        base_path = Path(self.base_path)

        # Track YFinance files
        yfinance_files = []
        yfinance_dir = base_path / "original" / "yfinance"
        if yfinance_dir.exists():
            for ticker_dir in yfinance_dir.iterdir():
                if ticker_dir.is_dir():
                    for json_file in ticker_dir.glob("*m7_daily*.json"):
                        yfinance_files.append(str(json_file.relative_to(base_path)))

        # Track SEC Edgar files
        sec_files = []
        sec_dir = base_path / "original" / "sec_edgar"
        if sec_dir.exists():
            for ticker_dir in sec_dir.iterdir():
                if ticker_dir.is_dir():
                    for json_file in ticker_dir.glob("*.json"):
                        sec_files.append(str(json_file.relative_to(base_path)))

        # Track DCF reports
        dcf_reports = []
        reports_dir = base_path / "reports"
        if reports_dir.exists():
            for report_file in reports_dir.glob("M7_DCF_Report_*.md"):
                dcf_reports.append(str(report_file.relative_to(base_path)))

        # Update manifest
        self.manifest["real_outputs"]["yfinance_files"] = yfinance_files
        self.manifest["real_outputs"]["sec_edgar_files"] = sec_files
        self.manifest["real_outputs"]["dcf_reports"] = dcf_reports

        # Update statistics
        self.manifest["statistics"]["files_processed"] = len(yfinance_files) + len(sec_files)

        logger.info(
            f"Scanned outputs: {len(yfinance_files)} YFinance, {len(sec_files)} SEC, {len(dcf_reports)} reports"
        )
        self._save_manifest()

    def complete_build(self, status: str = "completed") -> None:
        """Complete the build execution"""
        logger.info(f"Completing build {self.build_id} with status: {status}")

        self.manifest["build_info"]["status"] = status
        self.manifest["build_info"]["end_time"] = datetime.now().isoformat()

        self._save_manifest()
        self._generate_build_report()

    def _save_manifest(self) -> None:
        """Save the build manifest to file"""
        manifest_path = self.build_path / "BUILD_MANIFEST.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(self.manifest, f, indent=2)

    def _generate_build_report(self) -> None:
        """Generate human-readable build report"""
        report_path = self.build_path / "BUILD_MANIFEST.md"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# Build Report: {self.build_id}\n\n")

            # Build Info
            f.write("## Build Information\n\n")
            f.write(f"- **Build ID**: {self.manifest['build_info']['build_id']}\n")
            f.write(f"- **Configuration**: {self.manifest['build_info']['configuration']}\n")
            f.write(f"- **Command**: `{self.manifest['build_info']['command']}`\n")
            f.write(f"- **Status**: {self.manifest['build_info']['status']}\n")
            f.write(f"- **Start Time**: {self.manifest['build_info']['start_time']}\n")
            f.write(f"- **End Time**: {self.manifest['build_info']['end_time']}\n\n")

            # Stage Information
            f.write("## ETL Stages\n\n")
            for stage, info in self.manifest["stages"].items():
                f.write(f"### {stage}\n\n")
                f.write(f"- **Status**: {info['status']}\n")
                f.write(f"- **Start Time**: {info['start_time']}\n")
                f.write(f"- **End Time**: {info['end_time']}\n")
                f.write(f"- **Artifacts**: {len(info['artifacts'])} files\n")

                if info["artifacts"]:
                    f.write("  - " + "\n  - ".join(info["artifacts"]) + "\n")
                f.write("\n")

            # Data Partitions
            f.write("## Data Partitions\n\n")
            for partition_type, partition_date in self.manifest["data_partitions"].items():
                if partition_date:
                    f.write(f"- **{partition_type}**: `{partition_date}`\n")
            f.write("\n")

            # Statistics
            f.write("## Statistics\n\n")
            f.write(f"- **Files Processed**: {self.manifest['statistics']['files_processed']}\n")
            f.write(f"- **Errors**: {len(self.manifest['statistics']['errors'])}\n")
            f.write(f"- **Warnings**: {len(self.manifest['statistics']['warnings'])}\n\n")

            # Errors
            if self.manifest["statistics"]["errors"]:
                f.write("### Errors\n\n")
                for error in self.manifest["statistics"]["errors"]:
                    f.write(f"- **{error['stage']}** ({error['timestamp']}): {error['error']}\n")
                f.write("\n")

            # Warnings
            if self.manifest["statistics"]["warnings"]:
                f.write("### Warnings\n\n")
                for warning in self.manifest["statistics"]["warnings"]:
                    f.write(
                        f"- **{warning['stage']}** ({warning['timestamp']}): {warning['warning']}\n"
                    )
                f.write("\n")

            # File Locations
            f.write("## File Locations\n\n")
            f.write(f"- **Build Directory**: `{self.build_path.relative_to(Path.cwd())}`\n")
            f.write(f"- **Stage Logs**: `{self.build_path.relative_to(Path.cwd())}/stage_logs/`\n")
            f.write(f"- **Artifacts**: `{self.build_path.relative_to(Path.cwd())}/artifacts/`\n\n")

            # Copy SEC DCF Integration Process documentation and add reference
            sec_doc_copied = self._copy_sec_dcf_documentation()
            if sec_doc_copied:
                f.write("## 📋 SEC DCF Integration Process\n\n")
                f.write(
                    "This build includes comprehensive documentation of how SEC filings are integrated into DCF analysis:\n\n"
                )
                f.write(
                    "- **Documentation**: [`SEC_DCF_Integration_Process.md`](./SEC_DCF_Integration_Process.md)\n"
                )
                f.write(
                    "- **Process Overview**: Detailed explanation of the ETL pipeline and semantic retrieval system\n"
                )
                f.write(
                    "- **Build Integration**: Shows how SEC data flows through the system into final DCF reports\n\n"
                )

            # Generated Information
            f.write("---\n")
            f.write(f"*Generated on {datetime.now().isoformat()}*\n")

    def _update_latest_symlink(self) -> None:
        """Update the 'latest' symlink to point to current build"""
        # Update latest in common/ directory (worktree-specific)
        project_root = Path(__file__).parent.parent
        common_latest = project_root / "common" / "latest_build"

        if common_latest.exists():
            common_latest.unlink()

        # Create relative symlink to the build
        relative_path = self.build_path.relative_to(project_root)
        common_latest.symlink_to(f"../{relative_path}")
        logger.debug(f"Updated latest build symlink: {common_latest} -> {relative_path}")

        # Note: We no longer create latest symlink in build directory per issue #58
        # Only use common/latest_build for worktree isolation

    @classmethod
    def get_latest_build(cls, base_path: str = None) -> Optional["BuildTracker"]:
        """Get the most recent build tracker"""
        if base_path is None:
            # Use project root relative path
            project_root = Path(__file__).parent.parent
            base_path = project_root / "data"
        else:
            project_root = Path(base_path).parent

        # Set up build base path
        build_base_path = Path(base_path) / "stage_99_build"

        # Use common/latest_build location only (worktree-specific per issue #58)
        common_latest = project_root / "common" / "latest_build"
        if not common_latest.exists():
            return None

        latest_build_path = common_latest.resolve()
        build_id = latest_build_path.name.replace("build_", "")

        # Create a tracker instance for the existing build
        tracker = cls.__new__(cls)
        tracker.base_path = Path(base_path)
        tracker.build_base_path = build_base_path
        tracker.build_id = build_id
        tracker.build_path = latest_build_path

        # Load existing manifest
        manifest_path = latest_build_path / "BUILD_MANIFEST.json"
        if manifest_path.exists():
            with open(manifest_path, "r", encoding="utf-8") as f:
                tracker.manifest = json.load(f)

        return tracker

    def get_build_status(self) -> Dict[str, Any]:
        """Get current build status summary with comprehensive dataset information"""
        # Basic status
        status = {
            "build_id": self.build_id,
            "status": self.manifest["build_info"]["status"],
            "configuration": self.manifest["build_info"]["configuration"],
            "stages_completed": sum(
                1 for stage in self.manifest["stages"].values() if stage["status"] == "completed"
            ),
            "total_stages": len(self.manifest["stages"]),
            "errors": len(self.manifest["statistics"]["errors"]),
            "warnings": len(self.manifest["statistics"]["warnings"]),
        }

        # Enhanced dataset information for Issue #91
        real_outputs = self.manifest.get("real_outputs", {})
        status.update(
            {
                "dataset_summary": {
                    "yfinance_files": len(real_outputs.get("yfinance_files", [])),
                    "sec_edgar_files": len(real_outputs.get("sec_edgar_files", [])),
                    "dcf_reports": len(real_outputs.get("dcf_reports", [])),
                    "graph_rag_outputs": len(real_outputs.get("graph_rag_outputs", [])),
                    "total_files": len(real_outputs.get("yfinance_files", []))
                    + len(real_outputs.get("sec_edgar_files", [])),
                    "companies_processed": self.manifest["statistics"].get(
                        "companies_processed", 0
                    ),
                },
                "build_info": {
                    "start_time": self.manifest["build_info"]["start_time"],
                    "end_time": self.manifest["build_info"]["end_time"],
                    "duration": self._calculate_duration(),
                    "command": self.manifest["build_info"]["command"],
                },
                "directory_structure": {
                    "build_path": str(self.build_path),
                    "artifacts_count": (
                        len(list((self.build_path / "artifacts").glob("*")))
                        if (self.build_path / "artifacts").exists()
                        else 0
                    ),
                    "stage_logs_count": (
                        len(list((self.build_path / "stage_logs").glob("*")))
                        if (self.build_path / "stage_logs").exists()
                        else 0
                    ),
                },
            }
        )

        return status

    def _calculate_duration(self) -> Optional[str]:
        """Calculate build duration in human-readable format"""
        start_time = self.manifest["build_info"]["start_time"]
        end_time = self.manifest["build_info"]["end_time"]

        if not start_time or not end_time:
            return None

        try:
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)
            duration = end - start

            total_seconds = int(duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60

            if hours > 0:
                return f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"
        except Exception:
            return None

    def _copy_sec_dcf_documentation(self) -> bool:
        """Generate SEC DCF integration process documentation directly in build artifacts"""
        try:
            # Target location in build artifacts
            target_doc = self.build_path / "SEC_DCF_Integration_Process.md"

            # Generate documentation content directly
            doc_content = self._generate_sec_dcf_documentation()

            # Write the documentation
            with open(target_doc, "w", encoding="utf-8") as f:
                f.write(doc_content)

            logger.info(f"📋 Generated SEC DCF integration documentation: {target_doc}")
            return True

        except Exception as e:
            logger.error(f"Failed to generate SEC DCF documentation: {e}")
            return False

    def _generate_sec_dcf_documentation(self) -> str:
        """Generate the content for SEC DCF integration documentation"""
        return """# SEC Document Usage in DCF Valuation Process

## Overview

The current LLM DCF system integrates SEC document data through Graph RAG architecture to provide regulatory-level financial insights for DCF valuation. This document details the complete process of SEC documents from extraction and processing to application in DCF analysis.

## System Architecture

### Core Components
1. **ETL Pipeline**: Data extraction, transformation, and loading
2. **Semantic Retrieval**: Semantic embedding and retrieval  
3. **Graph RAG Engine**: Question answering and context generation
4. **DCF Generator**: LLM-driven DCF report generation

### Data Flow
```
SEC Edgar Data → ETL Extract → Semantic Embeddings → Graph RAG → DCF Analysis → Build Artifacts
```

## Detailed Process Flow

### Stage 1: SEC Document Extraction (Stage 01 - Extract)

**Location**: `data/stage_01_extract/sec_edgar/`

**Document Types**:
- **10-K**: Annual reports containing complete business overview, risk factors, financial data
- **10-Q**: Quarterly reports providing latest financial performance and trends  
- **8-K**: Material event reports including strategic changes, acquisitions, etc.

**Storage Structure**:
```
data/stage_01_extract/sec_edgar/
├── latest/
│   ├── AAPL/
│   │   ├── AAPL_sec_edgar_10k_*.txt
│   │   ├── AAPL_sec_edgar_10q_*.txt
│   │   └── AAPL_sec_edgar_8k_*.txt
│   ├── GOOGL/
│   └── [Other M7 companies]
└── 20250809/ [Historical partitions]
```

**Data Statistics**:
- Total of 336 SEC documents covering Magnificent 7 companies
- Contains 10-K, 10-Q, 8-K multi-year historical data
- Average of 48 documents per company

### Stage 2: Semantic Embedding Generation (Stage 02-03 - Transform & Load)

**Core File**: `ETL/semantic_retrieval.py`

**Processing Steps**:
1. **Document Chunking**: Split long documents into manageable chunks (default 1000 chars, 200 char overlap)
2. **Keyword Filtering**: Identify DCF-relevant content (revenue, cash flow, profitability, guidance, risk factors)
3. **Vector Embedding**: Generate semantic vectors using sentence-transformers
4. **Index Building**: Create FAISS vector index for fast retrieval

**Generated Data**:
```python
# Each document chunk contains:
{
    'node_id': 'chunk_AAPL_sec_edgar_10k_0',
    'content': 'Actual document content...',
    'content_type': 'SEC_10K',
    'embedding_vector': [384-dimensional vector],
    'ticker': 'AAPL',
    'metadata': {
        'file_path': 'Original file path',
        'chunk_start': 0,
        'chunk_end': 1000
    }
}
```

**Storage Location**:
```
data/stage_03_load/embeddings/
├── embeddings_vectors.npy      # Vector data
├── embeddings_metadata.json    # Metadata
└── vector_index.faiss          # FAISS index
```

### Stage 3: Semantic Retrieval

**Trigger Point**: When DCF analysis begins

**Retrieval Strategy**: 
```python
# Generate multiple DCF-related queries
search_queries = [
    f"{ticker} financial performance revenue growth cash flow",
    f"{ticker} risk factors competitive regulatory risks", 
    f"{ticker} management discussion analysis future outlook",
    f"{ticker} research development innovation strategy",
    f"{ticker} capital allocation investments acquisitions",
    f"{ticker} market position competitive advantages"
]
```

**Similarity Threshold**: 0.75 (only returns highly relevant content)

**Retrieval Results**:
```python
# Each retrieval result contains:
{
    'content': 'SEC document relevant paragraph',
    'source': 'AAPL_sec_edgar_10k_20231002.txt',
    'document_type': 'SEC_10K',
    'similarity_score': 0.85,
    'metadata': {'filing_date': '2023-10-02'},
    'thinking_process': 'Retrieval reasoning and relevance analysis'
}
```

### Stage 4: DCF Analysis Integration

**Core File**: `dcf_engine/llm_dcf_generator.py`

**Integration Point**: `_retrieve_financial_context()` method

**Processing Flow**:
1. **Context Building**: Classify retrieved SEC document fragments by DCF components
2. **LLM Prompt Generation**: Create structured prompts containing SEC data
3. **Citation Management**: Ensure each insight includes SEC document source
4. **Quality Validation**: Verify relevance of retrieved content to DCF analysis

**DCF Component Mapping**:
```python
dcf_components = {
    'revenue_growth': 'Revenue Growth Analysis',
    'cash_flow_analysis': 'Cash Flow Forecasting', 
    'profitability_trends': 'Profitability Assessment',
    'forward_guidance': 'Forward-looking Guidance',
    'risk_factors': 'Risk Factor Analysis'
}
```

### Stage 5: LLM Report Generation

**Bilingual Support**: Generate both Chinese and English DCF reports

**SEC Data Application**:
- **Revenue Forecasting**: Based on historical revenue data and management guidance from SEC filings
- **Cash Flow Forecasting**: Combines SEC-disclosed capital expenditure plans and operating cash flow trends
- **Risk Adjustment**: Uses SEC risk factors section to adjust discount rates
- **Terminal Value Calculation**: References SEC strategic outlook to determine long-term growth rates

**Generation Example**:
```markdown
## 📊 DCF Valuation Analysis (Based on SEC Filing Insights)

### Revenue Forecasting
According to SEC 10-K filings, AAPL's revenue grew 2.8% year-over-year to $383.3B in 2023...
*Source: AAPL_sec_edgar_10k_20231002.txt - SEC 10K Filing*

### Cash Flow Analysis  
SEC filings show company free cash flow of $84.7B, with capital expenditure guidance of...
*Source: AAPL_sec_edgar_10q_20231101.txt - SEC 10Q Filing*
```

## Build Artifact Integration

### Document Storage Location
```
data/stage_99_build/build_YYYYMMDD_HHMMSS/
├── thinking_process/
│   └── semantic_retrieval_TICKER_YYYYMMDD_HHMMSS.txt
├── semantic_results/
│   └── retrieved_docs_TICKER_YYYYMMDD_HHMMSS.json
├── sec_integration_examples/
│   ├── SEC_Integration_Guide.md
│   ├── sec_context_example_TICKER.json
│   └── sec_enhanced_dcf_prompt_TICKER.md
├── SEC_DCF_Integration_Process.md (this document)
└── M7_LLM_DCF_Report_YYYYMMDD_HHMMSS.md
```

### Thinking Process Recording
Each semantic retrieval generates detailed thinking process logs:
```
🧠 Semantic Retrieval Thinking Process for AAPL
====================================================

📋 Step-by-Step Thinking Process:
🔍 Starting semantic retrieval for AAPL
📊 Financial data available: ['company_info', 'financial_metrics', 'ratios']
🎯 Generated 6 search queries:
   Query 1: AAPL financial performance revenue growth cash flow
   Query 2: AAPL risk factors competitive regulatory risks
   ...
✅ Semantic retrieval system found - attempting real document search
🔍 Executing query 1: AAPL financial performance revenue growth cash flow
📄 Found 3 documents with similarity >= 0.75
   • AAPL_sec_edgar_10k_20231002.txt (score: 0.876)
     Content preview: Revenue increased 2.8% year over year to $383.3 billion...
```

## Core Implementation Files

### 1. `dcf_engine/llm_dcf_generator.py`
- `_retrieve_financial_context()`: Main SEC document retrieval entry point
- Integrates semantic retrieval to obtain relevant SEC content
- Converts SEC data to DCF analysis context

### 2. `ETL/semantic_retrieval.py`
- `SemanticRetrieval` class: Core semantic retrieval engine
- `search_similar_content()`: Executes vector similarity search
- `build_embeddings()`: Builds document embedding vectors and indexes

### 3. `dcf_engine/sec_integration_template.py`
- `SECIntegrationTemplate` class: SEC integration templates and examples
- Provides standardized SEC data extraction and formatting methods
- Generates LLM-ready SEC-enhanced prompts

## Data Quality Assurance

### Content Filtering Standards
- **Keyword Matching**: Uses DCF-related keyword lists to filter content
- **Relevance Scoring**: Multi-keyword matching paragraphs have higher priority
- **Content Length**: Ensures substantial content (>200 characters)

### Citation Standards
- **Source Attribution**: Each fragment includes original document name
- **Filing Date**: Extracts filing date from filename (if available)
- **Document Classification**: Correct classification (10-K, 10-Q, 8-K)

### Error Handling
- **File Access**: Gracefully handles unreadable files
- **Content Extraction**: UTF-8 encoding with error tolerance
- **Missing Data**: Fallback to available information

## Usage Examples

### Semantic Retrieval Trigger
```python
# Automatically triggered in DCF analysis
retrieval_system = SemanticRetrieval()
relevant_docs = retrieval_system.search_similar_content(
    ticker="AAPL",
    queries=dcf_search_queries,
    similarity_threshold=0.75
)
```

### SEC Data Application in DCF
```python
# Generate SEC-enhanced DCF prompt
dcf_prompt = f'''
Perform DCF analysis based on the following SEC filing insights:

Revenue Growth Analysis:
{sec_revenue_insights}

Cash Flow Analysis:
{sec_cashflow_insights}

Risk Factors:
{sec_risk_factors}
'''
```

## Conclusion

Through this comprehensive SEC document integration system, DCF valuation analysis gains:

1. **Regulatory Support**: Financial insights based on actual SEC filings
2. **Data Quality**: High-precision semantic retrieval and filtering
3. **Complete Traceability**: Each insight has clear SEC document sources
4. **Automated Processing**: End-to-end automation from raw SEC data to DCF reports
5. **Quality Assurance**: Multi-layered validation and error handling

This approach ensures DCF valuations are not only based on mathematical models, but more importantly built on the company's actual disclosed regulatory-level financial data, improving the credibility and accuracy of valuations.

---
*This document is automatically generated during each build process, providing detailed records of the complete SEC document usage flow in the DCF valuation system.*
"""
