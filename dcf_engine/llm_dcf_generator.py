#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-Powered DCF Generator

Main orchestrator for generating DCF reports using Ollama gpt-oss:20b
and FinLang financial embeddings.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .finlang_embedding import FinLangEmbedding
from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class LLMDCFGenerator:
    """
    Main DCF generator using LLM and financial embeddings.
    
    Orchestrates the complete workflow:
    1. Financial data preparation
    2. Semantic search for relevant context
    3. LLM-based DCF report generation
    4. Quality validation and debugging
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize LLM DCF generator.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.debug_dir = Path("data/llm_debug")
        
        # Initialize components
        self.embedding_model = FinLangEmbedding(config_path)
        self.ollama_client = OllamaClient(config_path)
        
        # Debug settings
        self.debug_mode = True
        self.save_intermediate_results = True
        
        logger.info("🚀 LLM DCF Generator initialized")

    def generate_comprehensive_dcf_report(
        self, 
        ticker: str,
        financial_data: Optional[Dict[str, Any]] = None,
        market_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive DCF report for a given ticker.
        
        Args:
            ticker: Stock ticker symbol
            financial_data: Financial metrics and ratios
            market_context: Market conditions and sector data
            
        Returns:
            Complete DCF analysis with all components
        """
        logger.info(f"📊 Generating comprehensive DCF report for {ticker}")
        
        # Initialize result structure
        result = {
            'ticker': ticker.upper(),
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'components': {},
            'debug_info': {},
            'errors': []
        }
        
        try:
            # Step 1: Prepare financial data
            if financial_data is None:
                financial_data = self._generate_mock_financial_data(ticker)
            
            if market_context is None:
                market_context = self._generate_mock_market_context(ticker)
            
            # Step 2: Generate financial embeddings and retrieve context
            semantic_results = self._retrieve_financial_context(ticker, financial_data)
            
            # Step 3: Generate DCF valuation report
            logger.info("🔍 Generating DCF valuation analysis...")
            dcf_result = self.ollama_client.generate_dcf_report(
                ticker=ticker,
                financial_data=financial_data,
                market_context=market_context,
                semantic_results=semantic_results
            )
            
            if dcf_result['success']:
                result['components']['dcf_valuation'] = dcf_result
                logger.info("✅ DCF valuation completed")
            else:
                result['errors'].append(f"DCF generation failed: {dcf_result.get('error', 'Unknown error')}")
            
            # Step 4: Generate risk analysis
            logger.info("⚠️ Generating risk analysis...")
            risk_result = self.ollama_client.generate_risk_analysis(
                ticker=ticker,
                financial_data=financial_data,
                semantic_results=semantic_results
            )
            
            if risk_result['success']:
                result['components']['risk_analysis'] = risk_result
                logger.info("✅ Risk analysis completed")
            else:
                result['errors'].append(f"Risk analysis failed: {risk_result.get('error', 'Unknown error')}")
            
            # Step 5: Generate investment recommendation
            logger.info("💡 Generating investment recommendation...")
            investment_result = self.ollama_client.generate_investment_recommendation(
                ticker=ticker,
                dcf_results=dcf_result if dcf_result['success'] else {},
                risk_analysis=risk_result if risk_result['success'] else {},
                semantic_results=semantic_results
            )
            
            if investment_result['success']:
                result['components']['investment_recommendation'] = investment_result
                logger.info("✅ Investment recommendation completed")
            else:
                result['errors'].append(f"Investment recommendation failed: {investment_result.get('error', 'Unknown error')}")
            
            # Step 6: Compile final report
            if result['components']:
                final_report = self._compile_final_report(ticker, result['components'])
                result['final_report'] = final_report
                result['success'] = True
                logger.info("🎉 Comprehensive DCF report generated successfully!")
            
            # Step 7: Save debug information
            if self.debug_mode:
                result['debug_info'] = {
                    'financial_data': financial_data,
                    'market_context': market_context,
                    'semantic_results_count': len(semantic_results),
                    'embedding_model_info': self.embedding_model.get_model_info(),
                    'generation_duration': self._calculate_total_duration(result['components'])
                }
                self._save_debug_results(ticker, result)
            
        except Exception as e:
            logger.error(f"❌ Error generating DCF report: {e}")
            result['errors'].append(f"Generation error: {str(e)}")
            result['success'] = False
        
        return result

    def _generate_mock_financial_data(self, ticker: str) -> Dict[str, Any]:
        """Generate mock financial data for testing purposes."""
        # This would normally fetch from your financial data sources
        mock_data = {
            'company_info': {
                'name': f'{ticker} Inc.',
                'sector': 'Technology',
                'industry': 'Software',
                'market_cap': 1500000000000,  # $1.5T
                'employees': 150000
            },
            'financial_metrics': {
                'revenue': 394328000000,  # $394B
                'net_income': 99803000000,  # $99.8B
                'free_cash_flow': 84726000000,  # $84.7B
                'total_debt': 109106000000,  # $109B
                'cash_and_equivalents': 63913000000,  # $63.9B
                'shareholders_equity': 62146000000,  # $62.1B
            },
            'ratios': {
                'pe_ratio': 28.5,
                'price_to_book': 12.8,
                'debt_to_equity': 1.76,
                'roe': 26.4,
                'roa': 11.2,
                'current_ratio': 1.76,
                'quick_ratio': 1.32
            },
            'historical': {
                'revenue_growth_5y': 0.078,  # 7.8% CAGR
                'earnings_growth_5y': 0.112, # 11.2% CAGR
                'dividend_yield': 0.0044,    # 0.44%
                'beta': 1.25
            },
            'current_price': 175.50,
            'analysis_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        return mock_data

    def _generate_mock_market_context(self, ticker: str) -> Dict[str, Any]:
        """Generate mock market context for testing."""
        return {
            'market_conditions': {
                'sp500_pe': 22.1,
                'sector_pe': 24.8,
                'risk_free_rate': 0.045,  # 4.5%
                'market_risk_premium': 0.065,  # 6.5%
                'sector_beta': 1.15
            },
            'economic_environment': {
                'gdp_growth': 0.024,  # 2.4%
                'inflation_rate': 0.031,  # 3.1%
                'unemployment_rate': 0.037,  # 3.7%
                'fed_funds_rate': 0.0525  # 5.25%
            },
            'sector_analysis': {
                'sector_growth_outlook': 'Positive',
                'competitive_intensity': 'High',
                'regulatory_environment': 'Moderate',
                'technological_disruption': 'High'
            }
        }

    def _retrieve_financial_context(
        self, 
        ticker: str, 
        financial_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant financial context using embeddings.
        
        This would normally search through your financial document database.
        For now, we'll create mock relevant context.
        """
        # Mock financial intelligence results
        mock_context = [
            {
                'content': f'{ticker} has demonstrated strong financial performance with consistent revenue growth and healthy cash generation. The company maintains a strong balance sheet position.',
                'source': 'Annual Report 10-K',
                'document_type': 'sec_filing',
                'similarity_score': 0.92,
                'timestamp': datetime.now().isoformat()
            },
            {
                'content': f'Risk factors for {ticker} include competitive pressure, regulatory changes, and macroeconomic headwinds that could impact future performance.',
                'source': 'Risk Factors - 10-K Filing',
                'document_type': 'risk_disclosure',
                'similarity_score': 0.88,
                'timestamp': datetime.now().isoformat()
            },
            {
                'content': f'{ticker} management outlook remains positive with strategic investments in growth areas and continued focus on operational efficiency.',
                'source': 'Management Discussion & Analysis',
                'document_type': 'md_and_a',
                'similarity_score': 0.85,
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        # In production, this would use the embedding model to search:
        # query_embedding = self.embedding_model.embed_financial_text(
        #     f"DCF valuation financial analysis {ticker}", "dcf"
        # )
        # semantic_results = self.embedding_model.find_similar_financial_content(
        #     query_text=f"Financial analysis {ticker}",
        #     document_embeddings=document_database,
        #     top_k=5,
        #     query_type="dcf"
        # )
        
        return mock_context

    def _compile_final_report(self, ticker: str, components: Dict[str, Any]) -> str:
        """Compile all components into a final comprehensive report."""
        report_sections = []
        
        # Header
        report_sections.append(f"""# Comprehensive Financial Analysis Report: {ticker}

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Type**: LLM-Powered DCF Valuation with Risk Assessment
**Model**: GPT-OSS:20B via Ollama + FinLang Embeddings

---
""")
        
        # DCF Valuation Section
        if 'dcf_valuation' in components and components['dcf_valuation']['success']:
            report_sections.append("## 📊 DCF Valuation Analysis\n")
            report_sections.append(components['dcf_valuation']['response'])
            report_sections.append("\n---\n")
        
        # Risk Analysis Section
        if 'risk_analysis' in components and components['risk_analysis']['success']:
            report_sections.append("## ⚠️ Risk Analysis\n")
            report_sections.append(components['risk_analysis']['response'])
            report_sections.append("\n---\n")
        
        # Investment Recommendation Section
        if 'investment_recommendation' in components and components['investment_recommendation']['success']:
            report_sections.append("## 💡 Investment Recommendation\n")
            report_sections.append(components['investment_recommendation']['response'])
            report_sections.append("\n---\n")
        
        # Footer with metadata
        report_sections.append(f"""## 🔧 Analysis Metadata

**Generation Components**:
- DCF Valuation: {'✅ Success' if components.get('dcf_valuation', {}).get('success') else '❌ Failed'}
- Risk Analysis: {'✅ Success' if components.get('risk_analysis', {}).get('success') else '❌ Failed'}
- Investment Recommendation: {'✅ Success' if components.get('investment_recommendation', {}).get('success') else '❌ Failed'}

**Technical Details**:
- Embedding Model: FinLang/finance-embeddings-investopedia
- Generation Model: GPT-OSS:20B
- Total Generation Time: {self._calculate_total_duration(components):.2f} seconds

---
*This report was generated using advanced LLM technology for financial analysis. Please conduct additional due diligence before making investment decisions.*
""")
        
        return "\n".join(report_sections)

    def _calculate_total_duration(self, components: Dict[str, Any]) -> float:
        """Calculate total generation duration from all components."""
        total_duration = 0.0
        for component in components.values():
            if isinstance(component, dict) and 'duration_seconds' in component:
                total_duration += component['duration_seconds']
        return total_duration

    def _save_debug_results(self, ticker: str, result: Dict[str, Any]):
        """Save comprehensive debug results."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save full result data
        debug_file = self.debug_dir / "logs" / f"dcf_generation_{ticker}_{timestamp}.json"
        debug_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(debug_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str)
        
        # Save final report separately
        if 'final_report' in result:
            report_file = self.debug_dir / "responses" / f"final_report_{ticker}_{timestamp}.md"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(result['final_report'])
        
        logger.info(f"🔍 Debug results saved: {debug_file}")

    def test_system_integration(self) -> Dict[str, Any]:
        """Test the complete system integration."""
        logger.info("🧪 Testing LLM DCF system integration...")
        
        test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'overall_status': 'unknown'
        }
        
        # Test 1: Embedding model
        embedding_test = self.embedding_model.test_embedding_quality([
            "Apple Inc. financial performance analysis",
            "Risk factors for technology companies",
            "DCF valuation methodology for growth stocks"
        ])
        test_results['tests']['embedding_model'] = embedding_test
        
        # Test 2: Ollama connection
        ollama_test = self.ollama_client.test_connection()
        test_results['tests']['ollama_connection'] = ollama_test
        
        # Test 3: End-to-end DCF generation
        try:
            dcf_test = self.generate_comprehensive_dcf_report('AAPL')
            test_results['tests']['dcf_generation'] = {
                'success': dcf_test['success'],
                'components_generated': len(dcf_test.get('components', {})),
                'errors': dcf_test.get('errors', [])
            }
        except Exception as e:
            test_results['tests']['dcf_generation'] = {
                'success': False,
                'error': str(e)
            }
        
        # Determine overall status
        if (embedding_test.get('status') == 'completed' and 
            ollama_test.get('success') and 
            test_results['tests']['dcf_generation'].get('success')):
            test_results['overall_status'] = 'success'
        else:
            test_results['overall_status'] = 'failure'
        
        # Save test results
        test_file = self.debug_dir / "logs" / "system_integration_test.json"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2)
        
        logger.info(f"🧪 System integration test completed: {test_results['overall_status']}")
        return test_results

    def generate_debug_report(self) -> str:
        """Generate a debug report showing system status and recent activity."""
        debug_info = []
        
        debug_info.append("# LLM DCF Generator Debug Report\n")
        debug_info.append(f"**Generated**: {datetime.now().isoformat()}\n")
        
        # System component status
        debug_info.append("## System Components\n")
        debug_info.append(f"- **Embedding Model**: {self.embedding_model.get_model_info()}")
        debug_info.append(f"- **Ollama Client**: Base URL: {self.ollama_client.base_url}, Model: {self.ollama_client.model_name}")
        debug_info.append(f"- **Debug Mode**: {self.debug_mode}")
        debug_info.append(f"- **Debug Directory**: {self.debug_dir}")
        
        # Recent log files
        debug_info.append("\n## Recent Activity\n")
        
        log_dir = self.debug_dir / "logs"
        if log_dir.exists():
            log_files = sorted(log_dir.glob("*.json*"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]
            for log_file in log_files:
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                debug_info.append(f"- {log_file.name} (Modified: {mtime.isoformat()})")
        
        # Recent reports
        debug_info.append("\n## Recent Reports\n")
        
        response_dir = self.debug_dir / "responses"
        if response_dir.exists():
            report_files = sorted(response_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]
            for report_file in report_files:
                mtime = datetime.fromtimestamp(report_file.stat().st_mtime)
                debug_info.append(f"- {report_file.name} (Generated: {mtime.isoformat()})")
        
        return "\n".join(debug_info)