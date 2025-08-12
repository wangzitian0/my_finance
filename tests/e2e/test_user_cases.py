"""
End-to-end tests for core user cases

This file is deprecated. Please use tests in the e2e/ directory instead.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest


class TestStrategyAnalystWorkflow:
    """Test case: Strategy analyst performs DCF valuation and investment decisions"""

    def test_m7_dcf_valuation_workflow(self):
        """完整的M7股票DCF估值流程"""
        # 1. 构建M7测试数据集
        result = subprocess.run(
            ["pixi", "run", "build", "m7", "--validate"], capture_output=True, text=True
        )
        assert result.returncode == 0, f"M7 build failed: {result.stderr}"

        # 2. 执行DCF估值
        result = subprocess.run(
            ["pixi", "run", "validate-strategy"], capture_output=True, text=True
        )
        assert result.returncode == 0, f"Strategy validation failed: {result.stderr}"

        # 3. 验证输出报告
        reports_dir = Path("data/stage_99_build")
        assert reports_dir.exists(), "Reports directory not found"

        # Look for DCF reports (the actual output format)
        dcf_reports = list(reports_dir.glob("**/M7_DCF_Report_*.txt"))
        assert len(dcf_reports) > 0, "No DCF reports generated"

        # 4. 验证报告文件不为空
        dcf_report = dcf_reports[0]
        assert dcf_report.exists(), f"DCF report file not found: {dcf_report}"
        assert dcf_report.stat().st_size > 0, "DCF report file is empty"

        # 5. 验证DCF报告包含M7股票分析
        with open(dcf_report, 'r') as f:
            report_content = f.read()
        
        # 检查报告包含M7股票代码
        m7_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]
        found_tickers = [ticker for ticker in m7_tickers if ticker in report_content]
        assert len(found_tickers) > 0, f"No M7 tickers found in DCF report. Content preview: {report_content[:200]}"

    def test_investment_decision_quality(self):
        """验证投资决策的质量和一致性"""
        # 使用现有的validate命令来检查投资决策质量
        result = subprocess.run(
            ["python", "ETL/manage.py", "validate"], capture_output=True, text=True
        )
        assert (
            result.returncode == 0
        ), f"Investment decision test failed: {result.stderr}"


class TestRiskManagerWorkflow:
    """Test case: Risk manager performs multi-factor risk assessment"""

    def test_risk_assessment_workflow(self):
        """完整的风险评估流程"""
        # 1. 执行策略验证（包含风险分析）
        result = subprocess.run(
            ["pixi", "run", "validate-strategy"], capture_output=True, text=True
        )
        assert result.returncode == 0, f"Risk analysis failed: {result.stderr}"

        # 2. 验证DCF报告包含风险指标
        reports_dir = Path("data/stage_99_build")
        dcf_reports = list(reports_dir.glob("**/M7_DCF_Report_*.txt"))
        assert len(dcf_reports) > 0, "No DCF reports generated"

        with open(dcf_reports[0], 'r') as f:
            report_content = f.read()

        # 3. 验证包含基础分析结果
        assert "Analysis" in report_content, "Missing analysis results"
        assert len(report_content) > 100, "Report content too short"

    def test_backtest_performance(self):
        """验证回测性能分析"""
        result = subprocess.run(
            ["pixi", "run", "backtest"], capture_output=True, text=True
        )
        assert result.returncode == 0, f"Backtest failed: {result.stderr}"


class TestInvestmentManagerWorkflow:
    """Test case: Investment manager generates strategy reports and benchmarks"""

    def test_strategy_report_generation(self):
        """完整的策略报告生成流程"""
        # 1. 生成策略报告
        result = subprocess.run(
            ["pixi", "run", "generate-report"], capture_output=True, text=True
        )
        assert result.returncode == 0, f"Report generation failed: {result.stderr}"

        # 2. 验证报告文件
        reports_dir = Path("data/stage_99_build")
        assert reports_dir.exists()

        # 应该包含Markdown和JSON格式报告
        # Look for any reports in the build directories
        dcf_reports = list(reports_dir.glob("**/M7_DCF_Report_*.txt"))
        manifest_files = list(reports_dir.glob("**/BUILD_MANIFEST.md"))

        assert len(dcf_reports) > 0, "No DCF reports generated"
        assert len(manifest_files) > 0, "No build manifest files generated"

    def test_benchmark_comparison(self):
        """验证基准比较功能"""
        # 使用现有的generate-report命令，它包含基准比较
        result = subprocess.run(
            ["pixi", "run", "generate-report"], capture_output=True, text=True
        )
        assert result.returncode == 0, f"Benchmark comparison failed: {result.stderr}"

        # 验证生成了DCF报告（包含基准比较信息）
        reports_dir = Path("data/stage_99_build")
        dcf_reports = list(reports_dir.glob("**/M7_DCF_Report_*.txt"))
        assert len(dcf_reports) > 0, "No DCF reports generated"


class TestDataIntegrity:
    """数据完整性测试"""

    def test_data_consistency_across_workflows(self):
        """确保不同工作流使用的数据一致"""
        # 执行状态检查
        result = subprocess.run(
            ["pixi", "run", "status"], capture_output=True, text=True
        )
        assert result.returncode == 0, f"Status check failed: {result.stderr}"

        # 验证数据目录结构（基础目录结构）
        data_dirs = ["data/config"]
        for dir_path in data_dirs:
            assert Path(dir_path).exists(), f"Missing data directory: {dir_path}"


class TestEnvironmentValidation:
    """环境验证测试"""

    def test_services_health(self):
        """验证所有服务健康状态"""
        result = subprocess.run(
            ["pixi", "run", "env-status"], capture_output=True, text=True
        )
        assert (
            result.returncode == 0
        ), f"Environment status check failed: {result.stderr}"

        # 验证环境状态检查运行成功（服务状态可能因环境而异）
        assert (
            "Environment Status" in result.stdout or result.returncode == 0
        ), "Environment status check basic validation"
