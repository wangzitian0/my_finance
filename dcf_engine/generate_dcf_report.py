#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Magnificent 7 DCF Valuation Report Generator

This script generates comprehensive DCF (Discounted Cash Flow) valuation reports
for the Magnificent 7 companies using collected financial data.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


class M7DCFAnalyzer:
    """DCF Analysis for Magnificent 7 companies."""

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
        self.data_dir = Path("data/stage_00_original")
        self.reports_dir = Path("data/stage_99_build")
        self.reports_dir.mkdir(exist_ok=True)

    def load_yfinance_data(self, ticker: str) -> Optional[Dict]:
        """Load Yahoo Finance data for a ticker."""
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

    def extract_financial_metrics(self, data: Dict) -> Dict:
        """Extract key financial metrics for DCF analysis."""
        if not data:
            return {}

        info = data.get("info", {})

        # Extract key financial metrics
        metrics = {
            "ticker": data.get("ticker"),
            "company_name": info.get("longName", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            # Valuation metrics
            "market_cap": info.get("marketCap", 0),
            "enterprise_value": info.get("enterpriseValue", 0),
            "shares_outstanding": info.get("sharesOutstanding", 0),
            "current_price": info.get("currentPrice", 0),
            # Financial strength
            "total_revenue": info.get("totalRevenue", 0),
            "gross_profit": info.get("grossProfit", 0),
            "operating_income": info.get("operatingIncome", 0),
            "net_income": info.get("netIncome", 0),
            "free_cash_flow": info.get("freeCashflow", 0),
            # Growth metrics
            "revenue_growth": info.get("revenueGrowth", 0),
            "earnings_growth": info.get("earningsGrowth", 0),
            # Profitability ratios
            "gross_margin": info.get("grossMargins", 0),
            "operating_margin": info.get("operatingMargins", 0),
            "profit_margin": info.get("profitMargins", 0),
            "roe": info.get("returnOnEquity", 0),
            "roa": info.get("returnOnAssets", 0),
            # Valuation ratios
            "pe_ratio": info.get("trailingPE", 0),
            "forward_pe": info.get("forwardPE", 0),
            "peg_ratio": info.get("pegRatio", 0),
            "price_to_book": info.get("priceToBook", 0),
            "ev_to_revenue": info.get("enterpriseToRevenue", 0),
            "ev_to_ebitda": info.get("enterpriseToEbitda", 0),
            # Risk metrics
            "beta": info.get("beta", 1.0),
            "debt_to_equity": info.get("debtToEquity", 0),
            "current_ratio": info.get("currentRatio", 0),
            "quick_ratio": info.get("quickRatio", 0),
            # Recommendations
            "target_price": info.get("targetMeanPrice", 0),
            "recommendation": info.get("recommendationKey", "hold"),
            # Dividends
            "dividend_yield": info.get("dividendYield", 0),
            "payout_ratio": info.get("payoutRatio", 0),
        }

        return metrics

    def calculate_wacc(self, metrics: Dict) -> float:
        """Calculate Weighted Average Cost of Capital (WACC)."""
        # Risk-free rate (approximate US 10-year treasury)
        risk_free_rate = 0.045  # 4.5%

        # Market risk premium
        market_premium = 0.06  # 6%

        # Cost of equity using CAPM
        beta = max(metrics.get("beta", 1.0), 0.5)  # Floor beta at 0.5
        cost_of_equity = risk_free_rate + (beta * market_premium)

        # Cost of debt (approximate)
        cost_of_debt = 0.04  # 4%

        # Tax rate (approximate corporate rate)
        tax_rate = 0.21  # 21%

        # Debt-to-equity ratio
        debt_to_equity = (
            metrics.get("debt_to_equity", 0) / 100
            if metrics.get("debt_to_equity")
            else 0
        )

        # Calculate WACC
        if debt_to_equity > 0:
            equity_weight = 1 / (1 + debt_to_equity)
            debt_weight = debt_to_equity / (1 + debt_to_equity)
            wacc = (equity_weight * cost_of_equity) + (
                debt_weight * cost_of_debt * (1 - tax_rate)
            )
        else:
            wacc = cost_of_equity

        # Cap WACC at reasonable bounds
        return max(min(wacc, 0.20), 0.08)  # Between 8% and 20%

    def project_cash_flows(self, metrics: Dict) -> Tuple[List[float], float]:
        """Project future free cash flows and terminal value."""
        current_fcf = metrics.get("free_cash_flow", 0)

        if current_fcf <= 0:
            # Use net income as proxy if FCF not available
            current_fcf = metrics.get("net_income", 0) * 0.8  # Conservative estimate

        if current_fcf <= 0:
            return [], 0

        # Growth assumptions based on company profile
        ticker = metrics.get("ticker", "")

        # Different growth profiles for different companies
        if ticker in ["TSLA"]:
            # High growth company
            growth_rates = [0.25, 0.20, 0.15, 0.12, 0.10]  # 5 years
            terminal_growth = 0.03
        elif ticker in ["AAPL", "MSFT", "GOOGL", "META"]:
            # Mature tech leaders
            growth_rates = [0.12, 0.10, 0.08, 0.06, 0.05]
            terminal_growth = 0.025
        elif ticker in ["AMZN"]:
            # E-commerce/cloud hybrid
            growth_rates = [0.15, 0.12, 0.10, 0.08, 0.06]
            terminal_growth = 0.03
        else:  # NFLX and others
            # Maturing digital services
            growth_rates = [0.10, 0.08, 0.06, 0.05, 0.04]
            terminal_growth = 0.025

        # Project cash flows
        projected_fcf = []
        fcf = current_fcf

        for growth_rate in growth_rates:
            fcf = fcf * (1 + growth_rate)
            projected_fcf.append(fcf)

        # Terminal value using perpetuity growth model
        terminal_fcf = projected_fcf[-1] * (1 + terminal_growth)
        wacc = self.calculate_wacc(metrics)
        terminal_value = terminal_fcf / (wacc - terminal_growth)

        return projected_fcf, terminal_value

    def calculate_dcf_valuation(self, metrics: Dict) -> Dict:
        """Calculate DCF valuation for a company."""
        projected_fcf, terminal_value = self.project_cash_flows(metrics)

        if not projected_fcf:
            return {"error": "Insufficient cash flow data"}

        wacc = self.calculate_wacc(metrics)

        # Present value of projected cash flows
        pv_fcf = []
        for i, fcf in enumerate(projected_fcf):
            pv = fcf / ((1 + wacc) ** (i + 1))
            pv_fcf.append(pv)

        # Present value of terminal value
        pv_terminal = terminal_value / ((1 + wacc) ** len(projected_fcf))

        # Enterprise value
        enterprise_value = sum(pv_fcf) + pv_terminal

        # Equity value (simplified - assumes no net debt adjustment)
        equity_value = enterprise_value
        shares_outstanding = metrics.get("shares_outstanding", 1)
        intrinsic_value_per_share = (
            equity_value / shares_outstanding if shares_outstanding > 0 else 0
        )

        current_price = metrics.get("current_price", 0)
        upside_downside = (
            ((intrinsic_value_per_share - current_price) / current_price * 100)
            if current_price > 0
            else 0
        )

        return {
            "wacc": wacc,
            "projected_fcf": projected_fcf,
            "terminal_value": terminal_value,
            "pv_fcf": pv_fcf,
            "pv_terminal": pv_terminal,
            "enterprise_value": enterprise_value,
            "equity_value": equity_value,
            "intrinsic_value_per_share": intrinsic_value_per_share,
            "current_price": current_price,
            "upside_downside_pct": upside_downside,
        }

    def generate_company_analysis(self, ticker: str) -> Optional[Dict]:
        """Generate complete DCF analysis for a company."""
        print(f"Analyzing {ticker}...")

        # Load data
        yf_data = self.load_yfinance_data(ticker)
        if not yf_data:
            print(f"No data available for {ticker}")
            return None

        # Extract metrics
        metrics = self.extract_financial_metrics(yf_data)
        if not metrics:
            print(f"Could not extract metrics for {ticker}")
            return None

        # Calculate DCF
        dcf_results = self.calculate_dcf_valuation(metrics)
        if "error" in dcf_results:
            print(f"DCF calculation failed for {ticker}: {dcf_results['error']}")
            return None

        # Combine results
        analysis = {
            "ticker": ticker,
            "company_name": self.m7_companies.get(ticker, ticker),
            "analysis_date": datetime.now().isoformat(),
            "financial_metrics": metrics,
            "dcf_valuation": dcf_results,
        }

        return analysis

    def generate_investment_recommendation(self, analysis: Dict) -> str:
        """Generate investment recommendation based on DCF analysis."""
        if not analysis or "dcf_valuation" not in analysis:
            return "HOLD - Insufficient data for analysis"

        upside_downside = analysis["dcf_valuation"].get("upside_downside_pct", 0)
        metrics = analysis.get("financial_metrics", {})

        # Quality metrics
        roe = metrics.get("roe", 0)
        profit_margin = metrics.get("profit_margin", 0)
        revenue_growth = metrics.get("revenue_growth", 0)

        # Recommendation logic
        if upside_downside > 20 and roe > 0.15 and profit_margin > 0.15:
            return "STRONG BUY - Undervalued with strong fundamentals"
        elif upside_downside > 10 and roe > 0.10:
            return "BUY - Undervalued with good fundamentals"
        elif upside_downside > -10 and upside_downside <= 10:
            return "HOLD - Fairly valued"
        elif upside_downside > -20:
            return "WEAK SELL - Slightly overvalued"
        else:
            return "SELL - Significantly overvalued"

    def format_currency(self, value: float) -> str:
        """Format currency values."""
        if value >= 1e12:
            return f"${value/1e12:.2f}T"
        elif value >= 1e9:
            return f"${value/1e9:.2f}B"
        elif value >= 1e6:
            return f"${value/1e6:.2f}M"
        else:
            return f"${value:.2f}"

    def format_percentage(self, value: float) -> str:
        """Format percentage values."""
        return f"{value*100:.1f}%" if abs(value) < 10 else f"{value:.1f}%"

    def generate_report(self) -> str:
        """Generate comprehensive M7 DCF report."""
        print("Generating Magnificent 7 DCF Analysis Report...")

        # Analyze all M7 companies
        analyses = {}
        for ticker in self.m7_companies:
            analysis = self.generate_company_analysis(ticker)
            if analysis:
                analyses[ticker] = analysis

        if not analyses:
            return "Error: No data available for M7 companies"

        # Generate report
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("MAGNIFICENT 7 (M7) DCF VALUATION REPORT")
        report_lines.append("=" * 80)
        report_lines.append(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        report_lines.append(
            f"Analysis Period: Based on latest available financial data"
        )
        report_lines.append("")

        # Executive Summary
        report_lines.append("EXECUTIVE SUMMARY")
        report_lines.append("-" * 40)

        total_market_cap = 0
        recommendations = {"BUY": [], "HOLD": [], "SELL": []}

        for ticker, analysis in analyses.items():
            metrics = analysis["financial_metrics"]
            dcf = analysis["dcf_valuation"]

            market_cap = metrics.get("market_cap", 0)
            total_market_cap += market_cap

            upside = dcf.get("upside_downside_pct", 0)
            recommendation = self.generate_investment_recommendation(analysis)

            if "BUY" in recommendation:
                recommendations["BUY"].append(ticker)
            elif "SELL" in recommendation:
                recommendations["SELL"].append(ticker)
            else:
                recommendations["HOLD"].append(ticker)

        report_lines.append(
            f"Total M7 Market Cap: {self.format_currency(total_market_cap)}"
        )
        report_lines.append(f"Companies Analyzed: {len(analyses)}")
        report_lines.append(
            f"Buy Recommendations: {len(recommendations['BUY'])} ({', '.join(recommendations['BUY'])})"
        )
        report_lines.append(
            f"Hold Recommendations: {len(recommendations['HOLD'])} ({', '.join(recommendations['HOLD'])})"
        )
        report_lines.append(
            f"Sell Recommendations: {len(recommendations['SELL'])} ({', '.join(recommendations['SELL'])})"
        )
        report_lines.append("")

        # Individual Company Analysis
        report_lines.append("INDIVIDUAL COMPANY ANALYSIS")
        report_lines.append("=" * 50)

        for ticker in sorted(analyses.keys()):
            analysis = analyses[ticker]
            metrics = analysis["financial_metrics"]
            dcf = analysis["dcf_valuation"]

            report_lines.append("")
            report_lines.append(f"{ticker} - {metrics['company_name']}")
            report_lines.append("-" * 50)

            # Basic Info
            report_lines.append(f"Sector: {metrics['sector']}")
            report_lines.append(f"Industry: {metrics['industry']}")
            report_lines.append("")

            # Valuation Summary
            report_lines.append("VALUATION SUMMARY")
            current_price = dcf["current_price"]
            intrinsic_value = dcf["intrinsic_value_per_share"]
            upside = dcf["upside_downside_pct"]

            report_lines.append(f"Current Price: ${current_price:.2f}")
            report_lines.append(f"Intrinsic Value: ${intrinsic_value:.2f}")
            report_lines.append(f"Upside/Downside: {upside:.1f}%")
            report_lines.append(
                f"Recommendation: {self.generate_investment_recommendation(analysis)}"
            )
            report_lines.append("")

            # Key Financials
            report_lines.append("KEY FINANCIAL METRICS")
            report_lines.append(
                f"Market Cap: {self.format_currency(metrics['market_cap'])}"
            )
            report_lines.append(
                f"Revenue: {self.format_currency(metrics['total_revenue'])}"
            )
            report_lines.append(
                f"Net Income: {self.format_currency(metrics['net_income'])}"
            )
            report_lines.append(
                f"Free Cash Flow: {self.format_currency(metrics['free_cash_flow'])}"
            )
            report_lines.append("")

            # Profitability & Growth
            report_lines.append("PROFITABILITY & GROWTH")
            report_lines.append(
                f"Gross Margin: {self.format_percentage(metrics['gross_margin'])}"
            )
            report_lines.append(
                f"Operating Margin: {self.format_percentage(metrics['operating_margin'])}"
            )
            report_lines.append(
                f"Profit Margin: {self.format_percentage(metrics['profit_margin'])}"
            )
            report_lines.append(f"ROE: {self.format_percentage(metrics['roe'])}")
            report_lines.append(
                f"Revenue Growth: {self.format_percentage(metrics['revenue_growth'])}"
            )
            report_lines.append("")

            # Valuation Ratios
            report_lines.append("VALUATION RATIOS")
            report_lines.append(f"P/E Ratio: {metrics['pe_ratio']:.1f}")
            report_lines.append(f"Forward P/E: {metrics['forward_pe']:.1f}")
            report_lines.append(f"PEG Ratio: {metrics['peg_ratio']:.2f}")
            report_lines.append(f"Price-to-Book: {metrics['price_to_book']:.2f}")
            report_lines.append(f"EV/Revenue: {metrics['ev_to_revenue']:.2f}")
            report_lines.append("")

            # DCF Analysis Details
            report_lines.append("DCF ANALYSIS DETAILS")
            report_lines.append(f"WACC: {self.format_percentage(dcf['wacc'])}")
            report_lines.append(
                f"Enterprise Value: {self.format_currency(dcf['enterprise_value'])}"
            )
            report_lines.append(
                f"Terminal Value: {self.format_currency(dcf['terminal_value'])}"
            )

            # 5-Year Cash Flow Projections
            report_lines.append("5-YEAR FREE CASH FLOW PROJECTIONS:")
            for i, fcf in enumerate(dcf["projected_fcf"]):
                year = datetime.now().year + i + 1
                report_lines.append(f"  {year}: {self.format_currency(fcf)}")
            report_lines.append("")

        # Market Overview
        report_lines.append("MARKET OVERVIEW & RISKS")
        report_lines.append("=" * 40)
        report_lines.append("")
        report_lines.append("KEY ASSUMPTIONS:")
        report_lines.append("• Risk-free rate: 4.5% (10-year US Treasury)")
        report_lines.append("• Market risk premium: 6.0%")
        report_lines.append("• Corporate tax rate: 21%")
        report_lines.append(
            "• Terminal growth rates: 2.5-3.0% based on company maturity"
        )
        report_lines.append("")
        report_lines.append("RISKS TO CONSIDER:")
        report_lines.append("• Interest rate changes affecting discount rates")
        report_lines.append("• Regulatory risks in technology sector")
        report_lines.append("• Competition and market saturation")
        report_lines.append("• Economic recession impacts on growth assumptions")
        report_lines.append("• Currency fluctuations for international operations")
        report_lines.append("")

        report_lines.append("DISCLAIMER:")
        report_lines.append(
            "This analysis is for educational purposes only and should not be"
        )
        report_lines.append(
            "considered as investment advice. Past performance does not guarantee"
        )
        report_lines.append(
            "future results. Please consult with a financial advisor before making"
        )
        report_lines.append("investment decisions.")
        report_lines.append("")
        report_lines.append("=" * 80)

        return "\n".join(report_lines)

    def save_report(self, report: str, filename: str = None, output_dir: Path = None) -> str:
        """Save report to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"M7_DCF_Report_{timestamp}.txt"

        # Use output_dir if provided, otherwise use default reports_dir
        target_dir = output_dir if output_dir is not None else self.reports_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = target_dir / filename

        with open(filepath, "w") as f:
            f.write(report)

        return str(filepath)


def main():
    """Main function to generate M7 DCF report."""
    analyzer = M7DCFAnalyzer()

    try:
        # Generate report
        report = analyzer.generate_report()

        # Save report
        report_path = analyzer.save_report(report)

        print(f"\n✅ DCF Report generated successfully!")
        print(f"📄 Report saved to: {report_path}")
        print("\n" + "=" * 60)
        print("REPORT PREVIEW:")
        print("=" * 60)

        # Print first 50 lines of report
        lines = report.split("\n")
        for line in lines[:50]:
            print(line)

        if len(lines) > 50:
            print(f"\n... and {len(lines) - 50} more lines")
            print(f"\n📄 Full report available at: {report_path}")

        return report_path

    except Exception as e:
        print(f"❌ Error generating DCF report: {e}")
        return None


if __name__ == "__main__":
    main()
