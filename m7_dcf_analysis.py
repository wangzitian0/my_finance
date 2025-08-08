#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M7 DCF Analysis using Graph RAG System

Generate DCF valuation reports for Magnificent 7 companies using our Graph RAG system.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(level=logging.WARNING)

try:
    from graph_rag import GraphRAGSystem
except ImportError:
    print("❌ Graph RAG system not available")
    sys.exit(1)


class M7DCFAnalyzer:
    """M7 DCF Analysis using Graph RAG."""
    
    def __init__(self):
        """Initialize the analyzer."""
        print("🚀 Initializing M7 DCF Analyzer with Graph RAG...")
        try:
            self.graph_rag = GraphRAGSystem()
            print("✅ Graph RAG System initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Graph RAG: {e}")
            self.graph_rag = None
        
        self.m7_companies = {
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation', 
            'AMZN': 'Amazon.com Inc.',
            'GOOGL': 'Alphabet Inc.',
            'META': 'Meta Platforms Inc.',
            'TSLA': 'Tesla Inc.',
            'NFLX': 'Netflix Inc.'
        }
        
        # Create reports directory
        self.reports_dir = Path("data/reports")
        self.reports_dir.mkdir(exist_ok=True)
    
    def analyze_company_dcf(self, ticker: str) -> dict:
        """Analyze a single company's DCF valuation."""
        company_name = self.m7_companies.get(ticker, ticker)
        print(f"🔍 Analyzing {ticker} ({company_name})...")
        
        if not self.graph_rag:
            return {"error": "Graph RAG system not available"}
        
        # DCF-specific questions for each company
        dcf_questions = [
            f"What is the current financial performance of {company_name} ({ticker})?",
            f"What is the intrinsic value estimate for {ticker} based on DCF analysis?",
            f"What are the key growth drivers for {company_name}?",
            f"What are the main risk factors affecting {ticker} valuation?",
            f"How does {ticker} compare to its industry peers in terms of valuation?",
        ]
        
        analysis_results = {}
        
        for i, question in enumerate(dcf_questions, 1):
            try:
                print(f"  📊 Processing question {i}/5: {question[:50]}...")
                response = self.graph_rag.process_query(question)
                
                analysis_results[f"question_{i}"] = {
                    "question": question,
                    "answer": response.get("answer", "No answer available"),
                    "confidence": response.get("confidence", 0),
                    "reasoning": response.get("reasoning", [])
                }
                
            except Exception as e:
                print(f"  ⚠️  Error processing question {i}: {e}")
                analysis_results[f"question_{i}"] = {
                    "question": question,
                    "answer": f"Error: {str(e)}",
                    "confidence": 0,
                    "reasoning": []
                }
        
        return {
            "ticker": ticker,
            "company_name": company_name,
            "analysis_timestamp": datetime.now().isoformat(),
            "dcf_analysis": analysis_results
        }
    
    def generate_m7_report(self) -> str:
        """Generate comprehensive M7 DCF report."""
        print("📈 Generating Magnificent 7 DCF Analysis Report...")
        
        # Analyze all M7 companies
        company_analyses = {}
        for ticker in self.m7_companies:
            try:
                analysis = self.analyze_company_dcf(ticker)
                if "error" not in analysis:
                    company_analyses[ticker] = analysis
                else:
                    print(f"⚠️  Skipping {ticker}: {analysis['error']}")
            except Exception as e:
                print(f"❌ Failed to analyze {ticker}: {e}")
        
        if not company_analyses:
            return "❌ No company analyses could be completed."
        
        # Generate report
        report_lines = []
        
        # Header
        report_lines.extend([
            "=" * 80,
            "MAGNIFICENT 7 (M7) DCF VALUATION ANALYSIS REPORT",
            "Generated using Graph RAG System",
            "=" * 80,
            f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Companies Analyzed: {len(company_analyses)}/{len(self.m7_companies)}",
            ""
        ])
        
        # Executive Summary
        report_lines.extend([
            "EXECUTIVE SUMMARY",
            "-" * 40,
            ""
        ])
        
        summary_info = []
        for ticker, analysis in company_analyses.items():
            company_name = analysis["company_name"]
            summary_info.append(f"✅ {ticker} ({company_name}) - Analysis completed")
        
        report_lines.extend(summary_info)
        report_lines.append("")
        
        # Individual Company Analysis
        report_lines.extend([
            "DETAILED COMPANY ANALYSIS",
            "=" * 50,
            ""
        ])
        
        for ticker in sorted(company_analyses.keys()):
            analysis = company_analyses[ticker]
            
            report_lines.extend([
                f"{ticker} - {analysis['company_name']}",
                "-" * 60,
                f"Analysis Timestamp: {analysis['analysis_timestamp']}",
                ""
            ])
            
            # DCF Analysis Results
            dcf_analysis = analysis.get("dcf_analysis", {})
            
            for question_key in sorted(dcf_analysis.keys()):
                question_data = dcf_analysis[question_key]
                
                report_lines.extend([
                    f"📋 {question_data['question']}",
                    f"💡 Answer: {question_data['answer']}",
                    f"🎯 Confidence: {question_data['confidence']:.1f}",
                    ""
                ])
                
                # Add reasoning if available
                reasoning = question_data.get("reasoning", [])
                if reasoning:
                    report_lines.append("🔍 Reasoning:")
                    for step in reasoning[:3]:  # Show first 3 reasoning steps
                        report_lines.append(f"   • {step}")
                    report_lines.append("")
            
            report_lines.append("-" * 60)
            report_lines.append("")
        
        # Methodology and Disclaimers
        report_lines.extend([
            "METHODOLOGY & DISCLAIMERS",
            "=" * 40,
            "",
            "METHODOLOGY:",
            "• Analysis performed using Graph RAG (Retrieval-Augmented Generation) system",
            "• Data sourced from Yahoo Finance and SEC Edgar filings",
            "• Combines financial data with natural language processing",
            "• Multi-step reasoning approach for comprehensive analysis",
            "",
            "DATA SOURCES:",
            "• Yahoo Finance: Real-time financial metrics and historical data",
            "• SEC Edgar: Official company filings (10-K, 10-Q, 8-K)",
            "• Graph database: Neo4j with neomodel ORM",
            "",
            "LIMITATIONS:",
            "• Analysis based on available historical data",
            "• Market conditions and assumptions may change rapidly",
            "• Graph RAG responses are AI-generated estimates",
            "• Results should be verified with additional analysis",
            "",
            "DISCLAIMER:",
            "This analysis is for educational and research purposes only.",
            "It should not be considered as investment advice.",
            "Past performance does not guarantee future results.",
            "Please consult with qualified financial advisors before making",
            "investment decisions.",
            "",
            "=" * 80
        ])
        
        return "\n".join(report_lines)
    
    def save_report(self, report: str) -> str:
        """Save the report to a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"M7_DCF_GraphRAG_Report_{timestamp}.txt"
        filepath = self.reports_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return str(filepath)
    
    def run_analysis(self):
        """Run the complete M7 DCF analysis."""
        try:
            # Generate report
            report = self.generate_m7_report()
            
            # Save report
            report_path = self.save_report(report)
            
            print(f"\n✅ M7 DCF Analysis completed!")
            print(f"📄 Report saved to: {report_path}")
            
            # Show preview
            print("\n" + "="*60)
            print("REPORT PREVIEW (First 30 lines):")
            print("="*60)
            
            lines = report.split('\n')
            for line in lines[:30]:
                print(line)
            
            if len(lines) > 30:
                print(f"\n... and {len(lines) - 30} more lines")
                print(f"📄 Full report: {report_path}")
            
            return report_path
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            return None


def main():
    """Main function."""
    print("🚀 Starting M7 DCF Analysis with Graph RAG...")
    
    analyzer = M7DCFAnalyzer()
    result = analyzer.run_analysis()
    
    if result:
        print(f"\n🎉 Analysis completed successfully!")
        print(f"📊 Report available at: {result}")
    else:
        print("\n❌ Analysis failed. Please check the logs.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())