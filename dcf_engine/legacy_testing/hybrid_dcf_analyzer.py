#!/usr/bin/env python3
"""
Hybrid DCF Analyzer - Combines traditional DCF with LLM insights
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

sys.path.append(str(Path(__file__).parent))

from generate_dcf_report import M7DCFAnalyzer
from ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class HybridDCFAnalyzer:
    """
    Combines traditional quantitative DCF analysis with LLM-powered insights.

    Workflow:
    1. Run traditional DCF calculations (fast, reliable)
    2. Generate LLM insights for key companies (selective)
    3. Combine results into enhanced report
    """

    def __init__(self):
        self.traditional_analyzer = M7DCFAnalyzer()
        self.llm_client = None
        self.llm_enabled = False

        # Try to initialize LLM client
        try:
            self.llm_client = OllamaClient()
            self.llm_enabled = True
            print("✅ LLM client initialized successfully")
        except Exception as e:
            print(f"⚠️ LLM client initialization failed: {e}")
            print("📊 Falling back to traditional DCF only")

    def generate_llm_insight(self, ticker: str, analysis: Dict) -> Optional[str]:
        """Generate LLM insight for a specific company analysis"""
        if not self.llm_enabled:
            return None

        try:
            metrics = analysis.get("financial_metrics", {})
            dcf = analysis.get("dcf_valuation", {})

            # Create concise prompt
            prompt = f"""Quick investment insight for {ticker}:

Financial Snapshot:
- Market Cap: ${metrics.get('market_cap', 0)/1e12:.2f}T
- Revenue: ${metrics.get('total_revenue', 0)/1e9:.1f}B
- Free Cash Flow: ${metrics.get('free_cash_flow', 0)/1e9:.1f}B
- Current Price: ${metrics.get('current_price', 0):.2f}
- DCF Value: ${dcf.get('intrinsic_value_per_share', 0):.2f}
- Upside: {dcf.get('upside_downside_pct', 0):.1f}%

Provide a 2-sentence investment insight: (1) key strength or concern, (2) investment implication."""

            result = self.llm_client.generate_completion(
                prompt=prompt, max_tokens=150, temperature=0.3
            )

            if result["success"]:
                logger.info(
                    f"✅ Generated LLM insight for {ticker} ({result.get('duration_seconds', 0):.1f}s)"
                )
                return result["response"].strip()
            else:
                logger.warning(
                    f"⚠️ LLM insight failed for {ticker}: {result.get('error', 'Unknown')}"
                )
                return None

        except Exception as e:
            logger.error(f"❌ Error generating LLM insight for {ticker}: {e}")
            return None

    def generate_enhanced_report(self, target_companies: Optional[List[str]] = None) -> str:
        """
        Generate enhanced DCF report with selective LLM insights.

        Args:
            target_companies: List of tickers to get LLM insights for (None = top holdings)
        """
        print("📊 Generating hybrid DCF report (Traditional + LLM)...")

        # 1. Generate traditional DCF report
        traditional_report = self.traditional_analyzer.generate_report()

        if not self.llm_enabled:
            print("⚠️ LLM not available, returning traditional report only")
            return traditional_report

        # 2. Analyze which companies to enhance with LLM
        analyses = {}
        for ticker in self.traditional_analyzer.m7_companies:
            analysis = self.traditional_analyzer.generate_company_analysis(ticker)
            if analysis:
                analyses[ticker] = analysis

        # Select companies for LLM enhancement (default: top 3 by market cap or most interesting)
        if target_companies is None:
            # Get companies with most interesting valuations (high upside/downside)
            interesting_companies = []
            for ticker, analysis in analyses.items():
                dcf = analysis.get("dcf_valuation", {})
                upside = abs(dcf.get("upside_downside_pct", 0))
                interesting_companies.append((ticker, upside))

            # Sort by absolute upside/downside and take top 3
            interesting_companies.sort(key=lambda x: x[1], reverse=True)
            target_companies = [ticker for ticker, _ in interesting_companies[:3]]

        print(f"🤖 Generating LLM insights for: {', '.join(target_companies)}")

        # 3. Generate LLM insights for selected companies
        llm_insights = {}
        for ticker in target_companies:
            if ticker in analyses:
                insight = self.generate_llm_insight(ticker, analyses[ticker])
                if insight:
                    llm_insights[ticker] = insight

        # 4. Create enhanced report
        enhanced_report = self._merge_reports(traditional_report, llm_insights)

        print(f"✅ Enhanced report completed with {len(llm_insights)} LLM insights")
        return enhanced_report

    def _merge_reports(self, traditional_report: str, llm_insights: Dict[str, str]) -> str:
        """Merge traditional DCF report with LLM insights"""
        if not llm_insights:
            return traditional_report

        lines = traditional_report.split("\n")
        enhanced_lines = []

        # Track which company section we're in
        current_ticker = None
        in_company_section = False

        for line in lines:
            enhanced_lines.append(line)

            # Detect company sections
            for ticker in self.traditional_analyzer.m7_companies:
                if line.startswith(f"{ticker} - "):
                    current_ticker = ticker
                    in_company_section = True
                    break

            # Insert LLM insight after DCF Analysis Details section
            if (
                current_ticker
                and current_ticker in llm_insights
                and line.startswith("5-YEAR FREE CASH FLOW PROJECTIONS:")
            ):

                # Find the end of cash flow projections
                projection_end = False
                for future_line in lines[lines.index(line) :]:
                    if future_line.strip() == "":
                        projection_end = True
                        break

                if projection_end:
                    enhanced_lines.append("")
                    enhanced_lines.append("LLM INVESTMENT INSIGHT")
                    enhanced_lines.append(llm_insights[current_ticker])
                    enhanced_lines.append("")

                    # Reset tracker
                    current_ticker = None
                    in_company_section = False

        # Add LLM summary at the end
        enhanced_lines.append("")
        enhanced_lines.append("=" * 40)
        enhanced_lines.append("🤖 AI-ENHANCED INSIGHTS SUMMARY")
        enhanced_lines.append("=" * 40)
        enhanced_lines.append("")
        enhanced_lines.append("The following companies received additional AI analysis:")
        enhanced_lines.append("")

        for ticker, insight in llm_insights.items():
            company_name = self.traditional_analyzer.m7_companies.get(ticker, ticker)
            enhanced_lines.append(f"**{ticker} - {company_name}**")
            enhanced_lines.append(insight)
            enhanced_lines.append("")

        enhanced_lines.append("💡 AI insights complement traditional DCF analysis")
        enhanced_lines.append("for deeper investment understanding.")
        enhanced_lines.append("")

        return "\n".join(enhanced_lines)

    def save_enhanced_report(self, report: str, output_dir: Path = None) -> str:
        """Save enhanced report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"M7_Enhanced_DCF_Report_{timestamp}.md"

        target_dir = output_dir if output_dir is not None else self.traditional_analyzer.reports_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        filepath = target_dir / filename

        with open(filepath, "w") as f:
            f.write(report)

        return str(filepath)


def main():
    """Generate enhanced M7 DCF report"""
    analyzer = HybridDCFAnalyzer()

    try:
        # Generate enhanced report
        report = analyzer.generate_enhanced_report()

        # Create timestamped build directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        build_dir = Path(f"data/stage_99_build/build_{timestamp}")
        build_dir.mkdir(parents=True, exist_ok=True)

        # Save report
        report_path = analyzer.save_enhanced_report(report, output_dir=build_dir)

        print(f"\n✅ Enhanced DCF Report generated successfully!")
        print(f"📄 Report saved to: {report_path}")

        return report_path

    except Exception as e:
        print(f"❌ Error generating enhanced DCF report: {e}")
        return None


if __name__ == "__main__":
    main()
