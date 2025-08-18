#!/usr/bin/env python3
"""
Quality Reporter - 与构建流程集成的质量报告模块
参考 common/logger.py 的设计，在每个stage完成时自动生成质量报告
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List

try:
    from .config import load_common_config
except ImportError:
    def load_common_config():
        return {"logging": {"level": "INFO"}}


class QualityReporter:
    """质量报告生成器，集成到构建流程中"""
    
    def __init__(self, build_id: str, tier_name: str):
        """
        初始化质量报告器
        
        Args:
            build_id: 构建ID
            tier_name: 数据集层级 (f2, m7, n100, v3k)
        """
        self.build_id = build_id
        self.tier_name = tier_name
        self.date_str = datetime.now().strftime("%y%m%d-%H%M%S")
        
        # 参考logger模块的目录结构：data/quality_reports/<build_id>/
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.quality_base_dir = os.path.join(root_dir, "data", "quality_reports")
        self.quality_dir = os.path.join(self.quality_base_dir, build_id)
        os.makedirs(self.quality_dir, exist_ok=True)
        
        # 阶段质量数据存储
        self.stage_reports = {}
        
        # CIK映射
        self.cik_to_ticker = {
            "0000320193": "AAPL", "0000789019": "MSFT", "0001018724": "AMZN",
            "0001652044": "GOOGL", "0001326801": "META", "0001318605": "TSLA", 
            "0001065280": "NFLX"
        }
        
    def report_stage_quality(self, stage_name: str, partition: str = None, **stage_data) -> Dict[str, Any]:
        """
        生成stage质量报告（在tracker.complete_stage()时调用）
        
        Args:
            stage_name: Stage名称 (stage_01_extract, stage_02_transform, etc.)
            partition: 数据分区 (通常是日期)
            **stage_data: Stage执行的额外数据
            
        Returns:
            质量报告数据
        """
        print(f"📊 Generating quality report for {stage_name}...")
        
        report = {
            "stage": stage_name,
            "build_id": self.build_id,
            "tier": self.tier_name,
            "partition": partition or datetime.now().strftime("%Y%m%d"),
            "timestamp": datetime.now().isoformat(),
            "quality_metrics": {},
            "data_analysis": {},
            "issues": [],
            "recommendations": []
        }
        
        # 根据stage类型生成不同的质量报告
        if stage_name == "stage_01_extract":
            report = self._analyze_extract_quality(report, **stage_data)
        elif stage_name == "stage_02_transform":
            report = self._analyze_transform_quality(report, **stage_data)
        elif stage_name == "stage_03_load":
            report = self._analyze_load_quality(report, **stage_data)
        elif stage_name == "stage_04_analysis":
            report = self._analyze_analysis_quality(report, **stage_data)
        elif stage_name == "stage_05_reporting":
            report = self._analyze_reporting_quality(report, **stage_data)
        
        # 保存stage报告
        self.stage_reports[stage_name] = report
        self._save_stage_report(report)
        
        # 输出质量摘要到控制台
        self._print_quality_summary(report)
        
        return report
        
    def _analyze_extract_quality(self, report: Dict[str, Any], **stage_data) -> Dict[str, Any]:
        """分析数据提取阶段的质量"""
        data_dir = Path("data")
        
        # 分析YFinance数据
        yfinance_metrics = self._analyze_yfinance_extraction(data_dir)
        
        # 分析SEC Edgar数据
        sec_edgar_metrics = self._analyze_sec_edgar_extraction(data_dir)
        
        report["data_analysis"] = {
            "yfinance": yfinance_metrics,
            "sec_edgar": sec_edgar_metrics
        }
        
        # 计算整体质量指标
        total_expected = (yfinance_metrics.get("expected_files", 0) + 
                         sec_edgar_metrics.get("expected_files", 0))
        total_actual = (yfinance_metrics.get("actual_files", 0) + 
                       sec_edgar_metrics.get("actual_files", 0))
        
        success_rate = (total_actual / total_expected * 100) if total_expected > 0 else 0
        
        report["quality_metrics"] = {
            "overall_success_rate": success_rate,
            "yfinance_success_rate": yfinance_metrics.get("success_rate", 0),
            "sec_edgar_success_rate": sec_edgar_metrics.get("success_rate", 0),
            "total_files_expected": total_expected,
            "total_files_actual": total_actual
        }
        
        # 生成问题和建议
        if success_rate < 80:
            report["issues"].append(f"Data extraction success rate below 80%: {success_rate:.1f}%")
            report["recommendations"].append("Check API connections and rate limits")
            
        if yfinance_metrics.get("success_rate", 0) < 70:
            report["recommendations"].append("Improve YFinance API reliability")
            
        if sec_edgar_metrics.get("success_rate", 0) < 70:
            report["recommendations"].append("Check SEC Edgar API access")
            
        return report
        
    def _analyze_transform_quality(self, report: Dict[str, Any], **stage_data) -> Dict[str, Any]:
        """分析数据转换阶段的质量"""
        # 分析转换输出
        stage_02_dir = Path("data/stage_02_transform")
        
        if not stage_02_dir.exists():
            report["issues"].append("Stage 02 directory not found")
            return report
            
        # 统计转换文件
        cleaned_files = len(list(stage_02_dir.rglob("*cleaned*")))
        normalized_files = len(list(stage_02_dir.rglob("*normalized*")))
        enriched_files = len(list(stage_02_dir.rglob("*enriched*")))
        
        total_transformed = cleaned_files + normalized_files + enriched_files
        
        # 从上一阶段获取输入文件数
        extract_report = self.stage_reports.get("stage_01_extract", {})
        input_files = extract_report.get("quality_metrics", {}).get("total_files_actual", 0)
        
        transform_rate = (total_transformed / input_files * 100) if input_files > 0 else 0
        
        report["quality_metrics"] = {
            "transformation_rate": transform_rate,
            "input_files": input_files,
            "output_files": total_transformed,
            "cleaned_files": cleaned_files,
            "normalized_files": normalized_files,
            "enriched_files": enriched_files
        }
        
        report["data_analysis"] = {
            "cleaning_efficiency": (cleaned_files / input_files * 100) if input_files > 0 else 0,
            "normalization_efficiency": (normalized_files / input_files * 100) if input_files > 0 else 0,
            "enrichment_efficiency": (enriched_files / input_files * 100) if input_files > 0 else 0
        }
        
        if transform_rate < 85:
            report["issues"].append(f"Low transformation rate: {transform_rate:.1f}%")
            report["recommendations"].append("Review transformation pipeline")
            
        return report
        
    def _analyze_load_quality(self, report: Dict[str, Any], **stage_data) -> Dict[str, Any]:
        """分析数据加载阶段的质量"""
        stage_03_dir = Path("data/stage_03_load")
        
        if not stage_03_dir.exists():
            report["issues"].append("Stage 03 directory not found")
            return report
            
        # 统计加载文件
        graph_nodes = len(list(stage_03_dir.rglob("*graph_nodes*")))
        embeddings = len(list(stage_03_dir.rglob("*embeddings*")))
        vector_indices = len(list(stage_03_dir.rglob("*vector_index*")))
        dcf_results = len(list(stage_03_dir.rglob("*dcf_results*")))
        
        total_loaded = graph_nodes + embeddings + vector_indices + dcf_results
        
        # 获取处理的ticker数量
        tickers_processed = self._get_tickers_from_files(stage_03_dir)
        
        # 从上一阶段获取输入
        transform_report = self.stage_reports.get("stage_02_transform", {})
        input_files = transform_report.get("quality_metrics", {}).get("output_files", 0)
        
        load_rate = (total_loaded / input_files * 100) if input_files > 0 else 0
        
        report["quality_metrics"] = {
            "load_rate": load_rate,
            "input_files": input_files,
            "output_files": total_loaded,
            "tickers_processed_count": len(tickers_processed)
        }
        
        report["data_analysis"] = {
            "graph_node_files": graph_nodes,
            "embedding_files": embeddings,
            "vector_index_files": vector_indices,
            "dcf_result_files": dcf_results,
            "tickers_processed": list(tickers_processed)
        }
        
        if load_rate < 80:
            report["issues"].append(f"Low load rate: {load_rate:.1f}%")
            report["recommendations"].append("Check database connections and indexing")
            
        expected_tickers = self._get_expected_ticker_count()
        if len(tickers_processed) < expected_tickers * 0.8:  # 80% threshold
            report["issues"].append(f"Only {len(tickers_processed)} of {expected_tickers} expected tickers processed")
            
        return report
        
    def _analyze_analysis_quality(self, report: Dict[str, Any], **stage_data) -> Dict[str, Any]:
        """分析DCF分析阶段的质量"""
        companies_analyzed = stage_data.get("companies_analyzed", [])
        
        report["quality_metrics"] = {
            "companies_analyzed_count": len(companies_analyzed),
            "analysis_success_rate": 100 if companies_analyzed else 0
        }
        
        report["data_analysis"] = {
            "companies_analyzed": companies_analyzed,
            "dcf_models_generated": len(companies_analyzed)
        }
        
        expected_companies = self._get_expected_ticker_count()
        if len(companies_analyzed) < expected_companies * 0.8:
            report["issues"].append(f"DCF analysis incomplete: {len(companies_analyzed)}/{expected_companies}")
            report["recommendations"].append("Check DCF calculation logic and data availability")
            
        return report
        
    def _analyze_reporting_quality(self, report: Dict[str, Any], **stage_data) -> Dict[str, Any]:
        """分析报告生成阶段的质量"""
        # 从stage_data获取报告生成数量，如果传递了的话
        reports_generated = stage_data.get("reports_generated", 0)
        
        # 检查当前构建目录中的DCF报告
        current_build_dir = Path(f"data/stage_99_build/build_{self.build_id}")
        dcf_reports_in_build = 0
        dcf_artifacts = []
        latest_release_dcf = 0
        
        if current_build_dir.exists():
            # 检查构建目录中的artifacts
            artifacts_dir = current_build_dir / "artifacts"
            if artifacts_dir.exists():
                dcf_artifacts.extend(list(artifacts_dir.glob("*dcf_report*")))
                
            # 检查构建目录中直接生成的DCF报告
            dcf_reports_in_build = len(list(current_build_dir.glob("*DCF_Report*")))
        
        # 检查最新的release目录中的DCF报告 (真正的DCF报告位置)
        if Path("data/release").exists():
            release_dirs = list(Path("data/release").glob("*build*"))
            if release_dirs:
                # 获取最新的release目录
                latest_release = max(release_dirs, key=lambda x: x.name)
                latest_release_dcf = len(list(latest_release.glob("*DCF_Report*")))
        
        # 综合评估报告生成质量
        total_dcf_reports = max(reports_generated, dcf_reports_in_build, latest_release_dcf)
        success_rate = 100 if total_dcf_reports > 0 or reports_generated > 0 else 0
        
        report["quality_metrics"] = {
            "reports_generated_count": reports_generated,
            "dcf_reports_in_build": dcf_reports_in_build,
            "dcf_artifacts_count": len(dcf_artifacts),
            "latest_release_dcf_count": latest_release_dcf if 'latest_release_dcf' in locals() else 0,
            "reporting_success_rate": success_rate
        }
        
        report["data_analysis"] = {
            "build_artifacts": [str(f.name) for f in dcf_artifacts],
            "dcf_generation_method": "PureLLMDCFAnalyzer + LLMDCFGenerator",
            "expected_outputs": ["M7_LLM_DCF_Report_<timestamp>.md", "DCF_Report_<timestamp>.txt"]
        }
        
        # 生成问题和建议
        if success_rate == 0:
            report["issues"].append("No DCF reports generated in reporting stage")
            report["recommendations"].append("Check PureLLMDCFAnalyzer and report generation logic")
        elif total_dcf_reports > 0:
            report["data_analysis"]["dcf_reports_found"] = f"Found {total_dcf_reports} DCF reports"
            
        return report
        
    def _analyze_yfinance_extraction(self, data_dir: Path) -> Dict[str, Any]:
        """分析YFinance数据提取"""
        yfinance_dir = data_dir / "stage_00_original" / "yfinance"
        
        if not yfinance_dir.exists():
            return {"error": "YFinance directory not found", "success_rate": 0, "actual_files": 0, "expected_files": 0}
            
        # 统计实际文件
        actual_files = len(list(yfinance_dir.rglob("*.json")))
        
        # 估算期望文件数 (基于tier)
        expected_files = self._get_expected_ticker_count() * 3  # 假设每个ticker 3个文件
        
        success_rate = (actual_files / expected_files * 100) if expected_files > 0 else 0
        
        return {
            "actual_files": actual_files,
            "expected_files": expected_files,
            "success_rate": success_rate
        }
        
    def _analyze_sec_edgar_extraction(self, data_dir: Path) -> Dict[str, Any]:
        """分析SEC Edgar数据提取"""
        sec_edgar_dir = data_dir / "stage_00_original" / "sec-edgar"
        
        if not sec_edgar_dir.exists():
            return {"error": "SEC Edgar directory not found", "success_rate": 0, "actual_files": 0, "expected_files": 0}
            
        # 统计实际文件
        actual_files = 0
        companies_found = set()
        
        for cik_dir in sec_edgar_dir.iterdir():
            if cik_dir.is_dir() and cik_dir.name.startswith("00"):
                ticker = self.cik_to_ticker.get(cik_dir.name, "UNKNOWN")
                if ticker != "UNKNOWN":
                    companies_found.add(ticker)
                    
                for filing_type in ["10-K", "10-Q", "8-K"]:
                    filing_dir = cik_dir / filing_type.lower()
                    if filing_dir.exists():
                        actual_files += len(list(filing_dir.glob("*.txt")))
                        
        # M7公司的期望文件数
        expected_companies = 7 if self.tier_name in ["m7", "n100", "v3k"] else 2
        expected_files = expected_companies * 15  # 每公司约15个文件
        
        success_rate = (actual_files / expected_files * 100) if expected_files > 0 else 0
        
        return {
            "actual_files": actual_files,
            "expected_files": expected_files,
            "success_rate": success_rate,
            "companies_found": len(companies_found),
            "expected_companies": expected_companies
        }
        
    def _get_tickers_from_files(self, directory: Path) -> set:
        """从文件路径中提取ticker符号"""
        tickers = set()
        
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                # 从文件名提取ticker
                parts = file_path.name.split('_')
                if parts:
                    potential_ticker = parts[0].upper()
                    if len(potential_ticker) <= 5 and potential_ticker.isalpha():
                        tickers.add(potential_ticker)
                        
        return tickers
        
    def _get_expected_ticker_count(self) -> int:
        """根据tier获取期望的ticker数量"""
        tier_counts = {"f2": 2, "m7": 7, "n100": 100, "v3k": 3500}
        return tier_counts.get(self.tier_name, 7)
        
    def _save_stage_report(self, report: Dict[str, Any]):
        """保存单个stage的质量报告"""
        stage_name = report["stage"]
        filename = f"{stage_name}_{self.date_str}.json"
        filepath = os.path.join(self.quality_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
    def _print_quality_summary(self, report: Dict[str, Any]):
        """打印质量摘要到控制台"""
        stage_name = report["stage"]
        metrics = report.get("quality_metrics", {})
        
        print(f"📋 Quality Summary for {stage_name}:")
        
        # 根据stage类型打印关键指标
        if "overall_success_rate" in metrics:
            rate = metrics["overall_success_rate"]
            status = "✅" if rate >= 80 else "⚠️" if rate >= 60 else "❌"
            print(f"   Overall Success Rate: {rate:.1f}% {status}")
            
        if "transformation_rate" in metrics:
            rate = metrics["transformation_rate"]
            status = "✅" if rate >= 85 else "⚠️" if rate >= 70 else "❌"
            print(f"   Transformation Rate: {rate:.1f}% {status}")
            
        if "load_rate" in metrics:
            rate = metrics["load_rate"]
            status = "✅" if rate >= 80 else "⚠️" if rate >= 60 else "❌"
            print(f"   Load Rate: {rate:.1f}% {status}")
            
        if "companies_analyzed_count" in metrics:
            count = metrics["companies_analyzed_count"]
            expected = self._get_expected_ticker_count()
            status = "✅" if count >= expected * 0.8 else "⚠️"
            print(f"   Companies Analyzed: {count}/{expected} {status}")
            
        # 打印问题和建议
        issues = report.get("issues", [])
        if issues:
            print(f"   Issues: {len(issues)} identified")
            for issue in issues[:2]:  # 只显示前2个
                print(f"     • {issue}")
                
        recommendations = report.get("recommendations", [])
        if recommendations:
            print(f"   Recommendations: {len(recommendations)} generated")
            
    def generate_build_summary_report(self) -> Dict[str, Any]:
        """生成整个构建的汇总质量报告"""
        print("📊 Generating build summary quality report...")
        
        summary = {
            "build_id": self.build_id,
            "tier": self.tier_name,
            "generated_at": datetime.now().isoformat(),
            "stages_analyzed": list(self.stage_reports.keys()),
            "overall_health": "unknown",
            "quality_summary": {},
            "recommendations": []
        }
        
        # 计算各阶段平均成功率
        stage_rates = []
        for stage_name, stage_report in self.stage_reports.items():
            metrics = stage_report.get("quality_metrics", {})
            # 提取主要成功率指标
            if "overall_success_rate" in metrics:
                stage_rates.append(metrics["overall_success_rate"])
            elif "transformation_rate" in metrics:
                stage_rates.append(metrics["transformation_rate"])
            elif "load_rate" in metrics:
                stage_rates.append(metrics["load_rate"])
            elif "analysis_success_rate" in metrics:
                stage_rates.append(metrics["analysis_success_rate"])
                
        if stage_rates:
            avg_success_rate = sum(stage_rates) / len(stage_rates)
            summary["quality_summary"]["average_success_rate"] = avg_success_rate
            summary["quality_summary"]["stage_success_rates"] = {
                stage: rate for stage, rate in zip(self.stage_reports.keys(), stage_rates)
            }
            
            # 评估整体健康状况
            if avg_success_rate >= 90:
                summary["overall_health"] = "excellent"
            elif avg_success_rate >= 80:
                summary["overall_health"] = "good"
            elif avg_success_rate >= 60:
                summary["overall_health"] = "fair"
            else:
                summary["overall_health"] = "needs_attention"
                
        # 汇总所有建议
        all_recommendations = []
        for stage_report in self.stage_reports.values():
            all_recommendations.extend(stage_report.get("recommendations", []))
            
        # 去重并限制数量
        unique_recommendations = list(set(all_recommendations))[:10]
        summary["recommendations"] = unique_recommendations
        
        # 保存汇总报告
        summary_file = os.path.join(self.quality_dir, f"build_quality_summary_{self.date_str}.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
            
        # 生成Markdown摘要
        self._save_markdown_summary(summary)
        
        # 打印汇总
        print("\n" + "="*60)
        print("📊 BUILD QUALITY SUMMARY")
        print("="*60)
        print(f"🏥 Overall Health: {summary['overall_health'].title()}")
        if "average_success_rate" in summary["quality_summary"]:
            avg_rate = summary["quality_summary"]["average_success_rate"]
            print(f"📈 Average Success Rate: {avg_rate:.1f}%")
            
        print(f"📁 Quality Reports: {self.quality_dir}")
        print("="*60)
        
        return summary
        
    def _save_markdown_summary(self, summary: Dict[str, Any]):
        """生成Markdown格式的汇总报告"""
        md_file = os.path.join(self.quality_dir, f"quality_summary_{self.date_str}.md")
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# Build Quality Summary Report\n\n")
            f.write(f"**Build ID:** {summary['build_id']}\n")
            f.write(f"**Tier:** {summary['tier']}\n")
            f.write(f"**Generated:** {summary['generated_at']}\n\n")
            
            health = summary["overall_health"]
            f.write(f"## 🏥 Overall Health: {health.title()}\n\n")
            
            # 成功率表格
            quality_summary = summary.get("quality_summary", {})
            if "stage_success_rates" in quality_summary:
                f.write("## 📊 Stage Success Rates\n\n")
                f.write("| Stage | Success Rate | Status |\n")
                f.write("|-------|--------------|--------|\n")
                
                for stage, rate in quality_summary["stage_success_rates"].items():
                    status = "✅ Good" if rate >= 80 else "⚠️ Fair" if rate >= 60 else "❌ Poor"
                    f.write(f"| {stage} | {rate:.1f}% | {status} |\n")
                    
                f.write("\n")
                
            # 建议
            recommendations = summary.get("recommendations", [])
            if recommendations:
                f.write("## 💡 Recommendations\n\n")
                for i, rec in enumerate(recommendations, 1):
                    f.write(f"{i}. {rec}\n")
                    
        print(f"📝 Markdown summary saved: {md_file}")


def setup_quality_reporter(build_id: str, tier_name: str) -> QualityReporter:
    """
    设置质量报告器（类似setup_logger函数）
    
    Args:
        build_id: 构建ID
        tier_name: 数据集层级
        
    Returns:
        配置好的QualityReporter实例
    """
    return QualityReporter(build_id, tier_name)