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
        """Get current build status summary"""
        return {
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

    def _copy_sec_dcf_documentation(self) -> bool:
        """Generate SEC DCF integration process documentation directly in build artifacts"""
        try:
            # Target location in build artifacts
            target_doc = self.build_path / "SEC_DCF_Integration_Process.md"
            
            # Generate documentation content directly
            doc_content = self._generate_sec_dcf_documentation()
            
            # Write the documentation
            with open(target_doc, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            
            logger.info(f"📋 Generated SEC DCF integration documentation: {target_doc}")
            return True

        except Exception as e:
            logger.error(f"Failed to generate SEC DCF documentation: {e}")
            return False

    def _generate_sec_dcf_documentation(self) -> str:
        """Generate the content for SEC DCF integration documentation"""
        return """# SEC文档在DCF估值中的使用过程

## 概述

当前的LLM DCF系统通过Graph RAG架构集成SEC文档数据，为DCF估值提供监管级别的财务洞察。本文档详细描述了SEC文档从提取、处理到应用于DCF分析的完整过程。

## 系统架构

### 核心组件
1. **ETL Pipeline**: 数据提取、转换、加载
2. **Semantic Retrieval**: 语义嵌入和检索  
3. **Graph RAG Engine**: 问答和上下文生成
4. **DCF Generator**: LLM驱动的DCF报告生成

### 数据流向
```
SEC Edgar Data → ETL Extract → Semantic Embeddings → Graph RAG → DCF Analysis → Build Artifacts
```

## 详细处理流程

### 第一阶段：SEC文档提取 (Stage 01 - Extract)

**位置**: `data/stage_01_extract/sec_edgar/`

**文档类型**:
- **10-K**: 年度报告，包含完整业务概述、风险因素、财务数据
- **10-Q**: 季度报告，提供最新财务表现和趋势  
- **8-K**: 重大事件报告，包含战略变更、收购等

**存储结构**:
```
data/stage_01_extract/sec_edgar/
├── latest/
│   ├── AAPL/
│   │   ├── AAPL_sec_edgar_10k_*.txt
│   │   ├── AAPL_sec_edgar_10q_*.txt
│   │   └── AAPL_sec_edgar_8k_*.txt
│   ├── GOOGL/
│   └── [其他M7公司]
└── 20250809/ [历史分区]
```

**数据统计**:
- 总计336个SEC文档覆盖Magnificent 7公司
- 包含10-K、10-Q、8-K多年份历史数据
- 每个公司平均48个文档

### 第二阶段：语义嵌入生成 (Stage 02-03 - Transform & Load)

**核心文件**: `ETL/semantic_retrieval.py`

**处理步骤**:
1. **文档分块**: 将长文档切分为可管理的chunk（默认1000字符，重叠200字符）
2. **关键词过滤**: 识别DCF相关内容（收入、现金流、盈利能力、指引、风险因素）
3. **向量嵌入**: 使用sentence-transformers生成语义向量
4. **索引构建**: 创建FAISS向量索引用于快速检索

**生成的数据**:
```python
# 每个文档chunk包含：
{
    'node_id': 'chunk_AAPL_sec_edgar_10k_0',
    'content': '实际文档内容...',
    'content_type': 'SEC_10K',
    'embedding_vector': [384维向量],
    'ticker': 'AAPL',
    'metadata': {
        'file_path': '原始文件路径',
        'chunk_start': 0,
        'chunk_end': 1000
    }
}
```

**存储位置**:
```
data/stage_03_load/embeddings/
├── embeddings_vectors.npy      # 向量数据
├── embeddings_metadata.json    # 元数据
└── vector_index.faiss          # FAISS索引
```

### 第三阶段：语义检索 (Semantic Retrieval)

**触发时机**: DCF分析开始时

**检索策略**: 
```python
# 生成多个DCF相关查询
search_queries = [
    f"{ticker} financial performance revenue growth cash flow",
    f"{ticker} risk factors competitive regulatory risks", 
    f"{ticker} management discussion analysis future outlook",
    f"{ticker} research development innovation strategy",
    f"{ticker} capital allocation investments acquisitions",
    f"{ticker} market position competitive advantages"
]
```

**相似度阈值**: 0.75（仅返回高度相关的内容）

**检索结果**:
```python
# 每个检索结果包含：
{
    'content': 'SEC文档相关段落',
    'source': 'AAPL_sec_edgar_10k_20231002.txt',
    'document_type': 'SEC_10K',
    'similarity_score': 0.85,
    'metadata': {'filing_date': '2023-10-02'},
    'thinking_process': '检索原因和相关性分析'
}
```

### 第四阶段：DCF分析集成

**核心文件**: `dcf_engine/llm_dcf_generator.py`

**集成点**: `_retrieve_financial_context()` 方法

**处理流程**:
1. **上下文构建**: 将检索到的SEC文档片段按DCF组件分类
2. **LLM提示生成**: 创建包含SEC数据的结构化提示
3. **引用管理**: 确保每个洞察都包含SEC文档来源
4. **质量验证**: 验证检索内容与DCF分析的相关性

**DCF组件映射**:
```python
dcf_components = {
    'revenue_growth': '收入增长分析',
    'cash_flow_analysis': '现金流预测', 
    'profitability_trends': '盈利能力评估',
    'forward_guidance': '前瞻性指引',
    'risk_factors': '风险因素分析'
}
```

### 第五阶段：LLM报告生成

**双语支持**: 同时生成中英文DCF报告

**SEC数据应用**:
- **收入预测**: 基于SEC文件中的历史收入数据和管理层指引
- **现金流预测**: 结合SEC披露的资本支出计划和运营现金流趋势
- **风险调整**: 利用SEC风险因素部分调整折现率
- **终值计算**: 参考SEC战略展望确定长期增长率

**生成示例**:
```markdown
## 📊 DCF估值分析 (基于SEC文件洞察)

### 收入预测
根据SEC 10-K文件显示，AAPL在2023年收入增长2.8%达到$383.3B...
*来源: AAPL_sec_edgar_10k_20231002.txt - SEC 10K Filing*

### 现金流分析  
SEC文件显示公司自由现金流为$84.7B，资本支出指引为...
*来源: AAPL_sec_edgar_10q_20231101.txt - SEC 10Q Filing*
```

## Build产物集成

### 文档保存位置
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
├── SEC_DCF_Integration_Process.md (本文档)
└── M7_LLM_DCF_Report_YYYYMMDD_HHMMSS.md
```

### 思考过程记录
每次语义检索都会生成详细的思考过程日志：
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

## 核心实现文件

### 1. `dcf_engine/llm_dcf_generator.py`
- `_retrieve_financial_context()`: 主要的SEC文档检索入口
- 集成semantic retrieval获取相关SEC内容
- 将SEC数据转换为DCF分析的上下文

### 2. `ETL/semantic_retrieval.py`
- `SemanticRetrieval` 类: 核心的语义检索引擎
- `search_similar_content()`: 执行向量相似度搜索
- `build_embeddings()`: 构建文档嵌入向量和索引

### 3. `dcf_engine/sec_integration_template.py`
- `SECIntegrationTemplate` 类: SEC集成模板和示例
- 提供标准化的SEC数据提取和格式化方法
- 生成LLM可用的SEC增强提示

## 数据质量保证

### 内容过滤标准
- **关键词匹配**: 使用DCF相关关键词列表过滤内容
- **相关性评分**: 多关键词匹配的段落优先级更高
- **内容长度**: 确保实质性内容（>200字符）

### 引用标准
- **来源归属**: 每个片段包含原始文档名称
- **申报日期**: 从文件名提取申报日期（如可用）
- **文档分类**: 正确分类（10-K、10-Q、8-K）

### 错误处理
- **文件访问**: 优雅处理不可读文件
- **内容提取**: UTF-8编码，容错处理
- **缺失数据**: 回退到可用信息

## 使用示例

### 语义检索触发
```python
# 在DCF分析中自动触发
retrieval_system = SemanticRetrieval()
relevant_docs = retrieval_system.search_similar_content(
    ticker="AAPL",
    queries=dcf_search_queries,
    similarity_threshold=0.75
)
```

### SEC数据在DCF中的应用
```python
# 生成SEC增强的DCF提示
dcf_prompt = f'''
基于以下SEC文件洞察进行DCF分析:

收入增长分析:
{sec_revenue_insights}

现金流分析:
{sec_cashflow_insights}

风险因素:
{sec_risk_factors}
'''
```

## 结论

通过这个综合的SEC文档集成系统，DCF估值分析获得了：

1. **监管支持**: 基于实际SEC申报的财务洞察
2. **数据质量**: 高精度的语义检索和过滤
3. **完整追溯**: 每个洞察都有明确的SEC文档来源
4. **自动化处理**: 从原始SEC数据到DCF报告的端到端自动化
5. **质量保证**: 多层次的验证和错误处理

这种方法确保DCF估值不仅基于数学模型，更重要的是建立在公司实际披露的监管级财务数据基础上，提高了估值的可信度和准确性。

---
*本文档自动生成于每次build过程中，详细记录了SEC文档在DCF估值系统中的完整使用流程。*
"""
