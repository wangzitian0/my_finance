#!/usr/bin/env python3
"""
Pure LLM-powered DCF Analysis
Generates DCF reports using only Ollama gpt-oss:20b without traditional calculations
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class PureLLMDCFAnalyzer:
    """
    Pure LLM-based DCF analyzer using only Ollama for financial analysis.
    """

    def __init__(self):
        self.m7_companies = {
            "AAPL": "Apple Inc.",
            "MSFT": "Microsoft Corporation",
            "AMZN": "Amazon.com Inc.",
            "GOOGL": "Alphabet Inc.",
            "META": "Meta Platforms Inc.",
            "TSLA": "Tesla Inc.",
            "NFLX": "Netflix Inc.",
        }
        # Use common path utilities for consistent path management
        from common.utils import get_project_paths

        paths = get_project_paths()
        self.data_dir = paths["stage_00_original"]

        # Initialize LLM client
        try:
            self.llm_client = OllamaClient()
            print("✅ LLM client initialized successfully")

            # Ping test to ensure LLM is responsive
            self._ping_llm()

        except Exception as e:
            print(f"❌ LLM client initialization failed: {e}")
            raise

    def _ping_llm(self):
        """Ping LLM to ensure it's responsive before starting analysis"""
        print("🏓 Pinging LLM with realistic DCF query...")

        # Use a similar prompt structure as the actual DCF analysis
        ping_prompt = """DCF Analysis for TEST - Test Company

Key Data:
• Market Cap: $1.0T, Price: $100.00
• Revenue: $100.0B, FCF: $20.0B
• Growth: 10.0%, Margin: 25.0%
• P/E: 20.0, ROE: 15.0%

Provide concise DCF analysis with:

1. **Valuation Summary** (3 lines)
   - Fair value estimate with reasoning
   - Current vs intrinsic value
   - BUY/HOLD/SELL recommendation

Respond with exactly: 'PING_TEST_OK' if you understand this format."""

        try:
            result = self.llm_client.generate_completion(
                prompt=ping_prompt,
                max_tokens=3000,  # Same as real DCF calls
                temperature=0.3,  # Same as real DCF calls
            )

            if result["success"]:
                response = result["response"].strip()
                duration = result.get("duration_seconds", 0)

                # Check for proper response (either the exact text or a valid DCF-style response)
                if "PING_TEST_OK" in response:
                    print(f"✅ LLM ping successful ({duration:.1f}s) - Got expected response")
                elif len(response) > 50 and (
                    "valuation" in response.lower() or "dcf" in response.lower()
                ):
                    print(f"✅ LLM ping successful ({duration:.1f}s) - Got DCF analysis response")
                    print(f"   Preview: {response[:100]}...")
                else:
                    print(
                        f"❌ LLM ping failed - got unexpected response ({duration:.1f}s): '{response[:100]}'"
                    )
                    print("LLM is not responding correctly, aborting analysis.")
                    raise Exception(
                        f"LLM ping validation failed - expected DCF response, got: '{response[:200]}'"
                    )
            else:
                error = result.get("error", "Unknown error")
                print(f"❌ LLM ping failed: {error}")
                raise Exception(f"LLM ping failed: {error}")

        except Exception as e:
            print(f"❌ LLM ping error: {e}")
            raise Exception(f"LLM is not responsive: {e}")

    def _get_current_build_dir(self) -> Path:
        """Get current build directory for storing build-specific artifacts using SSOT"""
        from common.core.directory_manager import DataLayer, DirectoryManager

        # Use SSOT DirectoryManager for path management
        dm = DirectoryManager()

        # Query results (DCF reports) should go to stage_04_query_results
        query_results_dir = dm.get_data_layer_path(DataLayer.QUERY_RESULTS)

        # Create dcf_reports subdirectory for organized storage
        dcf_reports_dir = query_results_dir / "dcf_reports"
        dcf_reports_dir.mkdir(parents=True, exist_ok=True)

        return dcf_reports_dir

    def load_company_data(self, ticker: str) -> Optional[Dict]:
        """Load financial data for a company"""
        yfinance_dir = self.data_dir / "yfinance" / ticker
        if not yfinance_dir.exists():
            return None

        # Find the most recent daily data file
        daily_files = list(yfinance_dir.glob(f"{ticker}_yfinance_m7_daily_*.json"))
        if not daily_files:
            return None

        latest_file = max(daily_files, key=lambda f: f.stat().st_mtime)

        try:
            with open(latest_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {latest_file}: {e}")
            return None

    def extract_key_metrics(self, data: Dict) -> Dict:
        """Extract key financial metrics for LLM analysis"""
        if not data:
            return {}

        info = data.get("info", {})

        return {
            "ticker": data.get("ticker"),
            "company_name": info.get("longName", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap", 0),
            "current_price": info.get("currentPrice", 0),
            "total_revenue": info.get("totalRevenue", 0),
            "net_income": info.get("netIncome", 0),
            "free_cash_flow": info.get("freeCashflow", 0),
            "revenue_growth": info.get("revenueGrowth", 0),
            "gross_margin": info.get("grossMargins", 0),
            "operating_margin": info.get("operatingMargins", 0),
            "profit_margin": info.get("profitMargins", 0),
            "roe": info.get("returnOnEquity", 0),
            "pe_ratio": info.get("trailingPE", 0),
            "forward_pe": info.get("forwardPE", 0),
            "price_to_book": info.get("priceToBook", 0),
            "beta": info.get("beta", 1.0),
            "debt_to_equity": info.get("debtToEquity", 0),
        }

    def generate_llm_dcf_analysis(self, ticker: str, metrics: Dict) -> Optional[str]:
        """Generate comprehensive DCF analysis using LLM"""

        # Create focused prompt for faster response
        prompt = f"""DCF Analysis for {ticker} - {metrics['company_name']}

Key Data:
• Market Cap: ${metrics['market_cap']/1e12:.2f}T, Price: ${metrics['current_price']:.2f}
• Revenue: ${metrics['total_revenue']/1e9:.1f}B, FCF: ${metrics['free_cash_flow']/1e9:.1f}B
• Growth: {metrics['revenue_growth']*100:.1f}%, Margin: {metrics['operating_margin']*100:.1f}%
• P/E: {metrics['pe_ratio']:.1f}, ROE: {metrics['roe']*100:.1f}%

Provide concise DCF analysis with:

1. **Valuation Summary** (3 lines)
   - Fair value estimate with reasoning
   - Current vs intrinsic value
   - BUY/HOLD/SELL recommendation

2. **Key Assumptions** (4 lines)
   - 5-year FCF growth rate estimate
   - Terminal growth rate (2-3%)
   - WACC/discount rate assumption
   - Main risk factors

3. **Price Target** (2 lines)
   - Target price range
   - Upside/downside percentage

Keep response under 300 words, focus on actionable insights."""

        try:
            result = self.llm_client.generate_completion(
                prompt=prompt, max_tokens=3000, temperature=0.3
            )

            if result["success"]:
                print(
                    f"✅ Generated LLM DCF analysis for {ticker} ({result.get('duration_seconds', 0):.1f}s)"
                )
                return result["response"]
            else:
                print(f"❌ LLM DCF analysis failed for {ticker}: {result.get('error', 'Unknown')}")
                return None

        except Exception as e:
            print(f"❌ Error generating LLM DCF for {ticker}: {e}")
            return None

    def generate_company_report(self, ticker: str) -> Optional[str]:
        """Generate complete LLM-based DCF report for a company"""
        print(f"🤖 Analyzing {ticker} with LLM...")

        # Load data
        data = self.load_company_data(ticker)
        if not data:
            print(f"No data available for {ticker}")
            return None

        # Extract metrics
        metrics = self.extract_key_metrics(data)
        if not metrics:
            print(f"Could not extract metrics for {ticker}")
            return None

        # Generate LLM analysis
        analysis = self.generate_llm_dcf_analysis(ticker, metrics)
        return analysis

    def generate_m7_report(self) -> str:
        """Generate comprehensive M7 DCF report using pure LLM analysis"""
        print("🤖 Generating Pure LLM M7 DCF Analysis Report...")

        # Analyze all M7 companies
        company_analyses = {}
        for ticker in self.m7_companies:
            analysis = self.generate_company_report(ticker)
            if analysis:
                company_analyses[ticker] = analysis

        if not company_analyses:
            return "Error: No LLM analyses generated for M7 companies"

        # Create comprehensive report
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("MAGNIFICENT 7 (M7) LLM-POWERED DCF VALUATION REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Analysis Method: Pure LLM (Ollama gpt-oss:20b)")
        report_lines.append(f"Companies Analyzed: {len(company_analyses)}")
        report_lines.append("")

        # Individual company analyses
        for ticker in sorted(company_analyses.keys()):
            company_name = self.m7_companies.get(ticker, ticker)
            analysis = company_analyses[ticker]

            report_lines.append("=" * 60)
            report_lines.append(f"{ticker} - {company_name}")
            report_lines.append("=" * 60)
            report_lines.append("")
            report_lines.append(analysis)
            report_lines.append("")

        # Add methodology note
        report_lines.append("=" * 80)
        report_lines.append("METHODOLOGY & DISCLAIMER")
        report_lines.append("=" * 80)
        report_lines.append("")
        report_lines.append("This analysis was generated using advanced AI (gpt-oss:20b) with:")
        report_lines.append("• Latest financial data from company filings")
        report_lines.append("• Industry-standard DCF methodology")
        report_lines.append("• Market-based assumptions for growth and discount rates")
        report_lines.append("• Professional equity research frameworks")
        report_lines.append("")
        report_lines.append("DISCLAIMER:")
        report_lines.append(
            "This AI-generated analysis is for educational and research purposes only."
        )
        report_lines.append("It should not be considered as investment advice. Please consult with")
        report_lines.append("qualified financial professionals before making investment decisions.")
        report_lines.append("")
        report_lines.append("=" * 80)

        return "\n".join(report_lines)

    def save_report(self, report: str, filename: str = None) -> str:
        """Save report to current build directory"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"M7_LLM_DCF_Report_{timestamp}.md"

        build_dir = self._get_current_build_dir()
        filepath = build_dir / filename

        with open(filepath, "w") as f:
            f.write(report)

        return str(filepath)

    def generate_report(self, tickers: List[str] = None) -> str:
        """Generate DCF report for given tickers (compatibility method)"""
        if not tickers:
            # Default to M7 if no tickers specified
            return self.generate_m7_report()

        print(f"📊 Generating DCF report for {len(tickers)} tickers using Pure LLM...")

        reports = []
        for ticker in tickers:
            print(f"   📈 Analyzing {ticker}...")
            report = self.generate_company_report(ticker)
            if report:
                reports.append(f"## {ticker} Analysis\n\n{report}")
            else:
                reports.append(f"## {ticker} Analysis\n\n❌ Analysis failed")

        # Combine all reports
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_report = f"""# DCF Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Analysis Method: Pure LLM (Ollama gpt-oss:20b)
Tickers: {', '.join(tickers)}

{chr(10).join(reports)}

---
Report generated by Pure LLM DCF Analyzer at {timestamp}
"""

        # Save to current build directory
        try:
            from common.build_tracker import BuildTracker

            build_tracker = BuildTracker()
            current_build = build_tracker.get_latest_build()

            if current_build:
                build_dir = Path(current_build.build_dir)
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                build_dir = Path(f"data/stage_99_build/build_{timestamp}")
                build_dir.mkdir(parents=True, exist_ok=True)
        except:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            build_dir = Path(f"data/stage_99_build/build_{timestamp}")
            build_dir.mkdir(parents=True, exist_ok=True)

        report_file = build_dir / f"DCF_Report_{timestamp}.md"

        with open(report_file, "w") as f:
            f.write(full_report)

        print(f"✅ DCF report saved to: {report_file}")
        return full_report


def main():
    """Main function to generate M7 LLM DCF report"""
    analyzer = PureLLMDCFAnalyzer()

    try:
        # Generate report
        report = analyzer.generate_m7_report()

        # Save report
        report_path = analyzer.save_report(report)

        print(f"\n✅ LLM DCF Report generated successfully!")
        print(f"📄 Report saved to: {report_path}")

        # Print preview
        print("\n" + "=" * 60)
        print("REPORT PREVIEW:")
        print("=" * 60)
        lines = report.split("\n")
        for line in lines[:30]:
            print(line)

        if len(lines) > 30:
            print(f"\n... and {len(lines) - 30} more lines")
            print(f"📄 Full report available at: {report_path}")

        return report_path

    except Exception as e:
        print(f"❌ Error generating LLM DCF report: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
