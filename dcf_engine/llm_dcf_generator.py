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

from common.core.directory_manager import directory_manager

# Import SSOT directory manager
from common.core.directory_manager import get_llm_config_path

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

    def __init__(self, config_path: Optional[str] = None, fast_mode: bool = False):
        """
        Initialize LLM DCF generator.

        Args:
            config_path: Path to configuration file
            fast_mode: Use fast configuration for testing
        """
        # Use fast config if requested
        if fast_mode and not config_path:
            config_path = str(get_llm_config_path("deepseek_fast.yml"))

        self.config_path = config_path
        self.debug_dir = get_llm_config_path().parent
        self.debug_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.embedding_model = FinLangEmbedding(config_path)
        self.ollama_client = OllamaClient(config_path, mock_mode=False)

        # Load configuration for settings
        self.config = self._load_config()

        # Debug settings from config
        dcf_config = self.config.get("dcf_generation", {})
        self.debug_mode = dcf_config.get("debug_mode", True)
        self.save_intermediate_results = dcf_config.get("save_intermediate_results", True)
        self.fast_mode = dcf_config.get("fast_mode", fast_mode)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        import yaml

        if not self.config_path:
            return {}

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Failed to load config from {self.config_path}: {e}")
            return {}

    def _get_current_build_dir(self) -> Path:
        """Get current build directory for storing build-specific artifacts"""
        try:
            from common.build_tracker import BuildTracker

            build_tracker = BuildTracker()
            current_build = build_tracker.get_latest_build()

            if current_build:
                return Path(current_build.build_dir)
        except:
            pass

        # Fallback: create new build directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        build_dir = Path(f"data/stage_99_build/build_{timestamp}")
        build_dir.mkdir(parents=True, exist_ok=True)
        return build_dir

        logger.info("🚀 LLM DCF Generator initialized")

    def generate_comprehensive_dcf_report(
        self,
        ticker: str,
        financial_data: Optional[Dict[str, Any]] = None,
        market_context: Optional[Dict[str, Any]] = None,
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
            "ticker": ticker.upper(),
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "components": {},
            "debug_info": {},
            "errors": [],
        }

        try:
            # Step 1: Prepare financial data
            if financial_data is None:
                financial_data = self._generate_mock_financial_data(ticker)

            if market_context is None:
                market_context = self._generate_mock_market_context(ticker)

            # Step 2: Generate financial embeddings and retrieve context
            semantic_results = self._retrieve_financial_context(ticker, financial_data)

            # Step 3: Generate bilingual DCF valuation reports
            logger.info("🔍 Generating bilingual DCF valuation analysis...")
            dcf_result = self.ollama_client.generate_bilingual_dcf_report(
                ticker=ticker,
                financial_data=financial_data,
                market_context=market_context,
                semantic_results=semantic_results,
            )

            if dcf_result["success"]:
                result["components"]["dcf_valuation"] = dcf_result
                logger.info("✅ DCF valuation completed")
            else:
                result["errors"].append(
                    f"DCF generation failed: {dcf_result.get('error', 'Unknown error')}"
                )

            # Step 4: Generate risk analysis
            logger.info("⚠️ Generating risk analysis...")
            # Debug: Check financial_data before risk analysis
            logger.debug(
                f"🐛 Before risk analysis - financial_data keys: {list(financial_data.keys()) if financial_data else 'None'}"
            )
            risk_result = self.ollama_client.generate_risk_analysis(
                ticker=ticker, financial_data=financial_data, semantic_results=semantic_results
            )

            if risk_result["success"]:
                result["components"]["risk_analysis"] = risk_result
                logger.info("✅ Risk analysis completed")
            else:
                result["errors"].append(
                    f"Risk analysis failed: {risk_result.get('error', 'Unknown error')}"
                )

            # Step 5: Generate investment recommendation
            logger.info("💡 Generating investment recommendation...")
            investment_result = self.ollama_client.generate_investment_recommendation(
                ticker=ticker,
                dcf_results=dcf_result if dcf_result["success"] else {},
                risk_analysis=risk_result if risk_result["success"] else {},
                semantic_results=semantic_results,
                financial_data=financial_data,
            )

            if investment_result["success"]:
                result["components"]["investment_recommendation"] = investment_result
                logger.info("✅ Investment recommendation completed")
            else:
                result["errors"].append(
                    f"Investment recommendation failed: {investment_result.get('error', 'Unknown error')}"
                )

            # Step 6: Compile final report
            if result["components"]:
                final_report = self._compile_final_report(ticker, result["components"])
                result["final_report"] = final_report
                result["success"] = True
                logger.info("🎉 Comprehensive DCF report generated successfully!")

            # Step 7: Save comprehensive debug information with thinking process
            if self.debug_mode:
                result["debug_info"] = {
                    "financial_data": financial_data,
                    "market_context": market_context,
                    "semantic_results_count": len(semantic_results),
                    "semantic_results_details": semantic_results,  # Include full semantic results
                    "embedding_model_info": self.embedding_model.get_model_info(),
                    "generation_duration": self._calculate_total_duration(result["components"]),
                    "thinking_process_files": {
                        "semantic_retrieval": f"data/stage_99_build/latest/thinking_process/semantic_retrieval_{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        "detailed_results": f"data/stage_99_build/latest/semantic_results/retrieved_docs_{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    },
                }
                self._save_comprehensive_debug_results(ticker, result, semantic_results)

        except Exception as e:
            logger.error(f"❌ Error generating DCF report: {e}")
            raise RuntimeError(f"DCF report generation failed for {ticker}: {e}") from e

    def _generate_mock_financial_data(self, ticker: str) -> Dict[str, Any]:
        """Generate mock financial data for testing purposes."""
        # This would normally fetch from your financial data sources
        mock_data = {
            "company_info": {
                "name": f"{ticker} Inc.",
                "sector": "Technology",
                "industry": "Software",
                "market_cap": 1500000000000,  # $1.5T
                "employees": 150000,
            },
            "financial_metrics": {
                "revenue": 394328000000,  # $394B
                "net_income": 99803000000,  # $99.8B
                "free_cash_flow": 84726000000,  # $84.7B
                "total_debt": 109106000000,  # $109B
                "cash_and_equivalents": 63913000000,  # $63.9B
                "shareholders_equity": 62146000000,  # $62.1B
            },
            "ratios": {
                "pe_ratio": 28.5,
                "price_to_book": 12.8,
                "debt_to_equity": 1.76,
                "roe": 26.4,
                "roa": 11.2,
                "current_ratio": 1.76,
                "quick_ratio": 1.32,
            },
            "historical": {
                "revenue_growth_5y": 0.078,  # 7.8% CAGR
                "earnings_growth_5y": 0.112,  # 11.2% CAGR
                "dividend_yield": 0.0044,  # 0.44%
                "beta": 1.25,
            },
            "current_price": 175.50,
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        }

        return mock_data

    def _generate_mock_market_context(self, ticker: str) -> Dict[str, Any]:
        """Generate mock market context for testing."""
        return {
            "market_conditions": {
                "sp500_pe": 22.1,
                "sector_pe": 24.8,
                "risk_free_rate": 0.045,  # 4.5%
                "market_risk_premium": 0.065,  # 6.5%
                "sector_beta": 1.15,
            },
            "economic_environment": {
                "gdp_growth": 0.024,  # 2.4%
                "inflation_rate": 0.031,  # 3.1%
                "unemployment_rate": 0.037,  # 3.7%
                "fed_funds_rate": 0.0525,  # 5.25%
            },
            "sector_analysis": {
                "sector_growth_outlook": "Positive",
                "competitive_intensity": "High",
                "regulatory_environment": "Moderate",
                "technological_disruption": "High",
            },
        }

    def _retrieve_financial_context(
        self, ticker: str, financial_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant financial context using embeddings with detailed thinking process.

        This method searches through financial documents and provides detailed debugging
        information about what was retrieved and why.
        """
        # Enhanced thinking process output
        thinking_log = []
        thinking_log.append(f"🔍 Starting semantic retrieval for {ticker}")
        thinking_log.append(f"📊 Financial data available: {list(financial_data.keys())}")

        # Create comprehensive search queries based on DCF analysis needs
        search_queries = [
            f"{ticker} financial performance revenue growth cash flow",
            f"{ticker} risk factors competitive regulatory risks",
            f"{ticker} management discussion analysis future outlook",
            f"{ticker} research development innovation strategy",
            f"{ticker} capital allocation investments acquisitions",
            f"{ticker} market position competitive advantages",
        ]

        thinking_log.append(f"🎯 Generated {len(search_queries)} search queries:")
        for i, query in enumerate(search_queries, 1):
            thinking_log.append(f"   Query {i}: {query}")

        # Try to use real semantic retrieval if available
        try:
            # Check if we have a real semantic retrieval system
            from pathlib import Path

            from ETL.semantic_retrieval import SemanticRetriever

            # Try to initialize and use real semantic retrieval
            try:
                # Try to find embeddings data
                embeddings_paths = [
                    Path("data/stage_03_load/embeddings"),
                    Path("data/stage_99_build").glob("*/embeddings"),
                ]

                embeddings_path = None
                for path in embeddings_paths:
                    if isinstance(path, Path) and path.exists():
                        embeddings_path = path
                        break
                    elif hasattr(path, "__iter__"):
                        for p in path:
                            if p.exists():
                                embeddings_path = p
                                break
                        if embeddings_path:
                            break

                if embeddings_path:
                    semantic_generator = SemanticRetriever(embeddings_path)
                else:
                    # No embeddings found, skip semantic retrieval
                    raise Exception("No embeddings found")
                thinking_log.append(
                    "✅ Semantic retrieval system found - attempting real document search"
                )

                all_results = []
                for i, query in enumerate(search_queries, 1):
                    thinking_log.append(f"🔍 Executing query {i}: {query}")

                    # Use real semantic search
                    results = semantic_generator.retrieve_relevant_content(
                        query=query,
                        top_k=3,
                        min_similarity=0.75,
                        content_filter={"ticker": ticker.upper()},
                    )

                    thinking_log.append(
                        f"   📄 Found {len(results)} documents with similarity >= 0.75"
                    )

                    for result in results:
                        thinking_log.append(
                            f"   • {result.source_document} (score: {result.similarity_score:.3f})"
                        )
                        thinking_log.append(f"     Content preview: {result.content[:100]}...")

                        # Convert to our format with real data
                        formatted_result = {
                            "content": result.content,
                            "source": result.source_document,
                            "document_type": (
                                result.document_type.value
                                if hasattr(result.document_type, "value")
                                else str(result.document_type)
                            ),
                            "similarity_score": result.similarity_score,
                            "metadata": result.metadata,
                            "thinking_process": f"Real semantic search result for query: {query}",
                            "timestamp": datetime.now().isoformat(),
                        }
                        all_results.append(formatted_result)

                # Remove duplicates and return real results
                seen_sources = set()
                unique_results = []
                for result in all_results:
                    if result["source"] not in seen_sources:
                        unique_results.append(result)
                        seen_sources.add(result["source"])

                if unique_results:
                    thinking_log.append(f"🎯 Retrieved {len(unique_results)} unique real documents")
                    self._log_thinking_process(ticker, thinking_log, unique_results)
                    return unique_results[:10]  # Limit to top 10
                else:
                    thinking_log.append("📄 No documents found in semantic search")

            except ImportError:
                thinking_log.append("⚠️ Semantic retrieval module not available")
            except Exception as retrieval_error:
                thinking_log.append(f"❌ Semantic retrieval failed: {str(retrieval_error)}")

        except Exception as e:
            thinking_log.append(f"❌ Error setting up semantic retrieval: {str(e)}")

        # If no real retrieval available, return empty list for LLM to handle
        thinking_log.append("⚠️ No semantic retrieval available - will rely on LLM knowledge")
        thinking_log.append("🎯 LLM will generate DCF analysis based on:")
        thinking_log.append("   • Provided financial data")
        thinking_log.append("   • Market context information")
        thinking_log.append("   • LLM's training knowledge of SEC filings and company data")

        # Log the thinking process even without retrieved documents
        self._log_thinking_process(ticker, thinking_log, [])

        # Return empty list - let LLM work with provided financial data only
        return []

    def _perform_real_semantic_search(
        self, ticker: str, queries: List[str], thinking_log: List[str]
    ) -> List[Dict[str, Any]]:
        """Perform real semantic search if retriever is available."""
        all_results = []

        for i, query in enumerate(queries, 1):
            thinking_log.append(f"🔍 Executing query {i}: {query}")

            try:
                # This would call the real semantic retriever
                results = self.semantic_retriever.retrieve_relevant_content(
                    query=query,
                    top_k=3,
                    min_similarity=0.75,
                    content_filter={
                        "ticker": ticker,
                        "document_type": ["sec_10k", "sec_10q", "sec_def14a"],
                    },
                )

                thinking_log.append(f"   📄 Found {len(results)} documents with similarity >= 0.75")

                for result in results:
                    thinking_log.append(
                        f"   • {result.source_document} (score: {result.similarity_score:.3f})"
                    )
                    thinking_log.append(f"     Content preview: {result.content[:100]}...")

                    # Convert to our format
                    formatted_result = {
                        "content": result.content,
                        "source": result.source_document,
                        "document_type": result.document_type.value,
                        "similarity_score": result.similarity_score,
                        "metadata": result.metadata,
                        "thinking_process": f"Retrieved via semantic search for query: {query}",
                        "timestamp": datetime.now().isoformat(),
                    }
                    all_results.append(formatted_result)

            except Exception as e:
                thinking_log.append(f"   ❌ Query {i} failed: {str(e)}")

        # Remove duplicates based on source document
        seen_sources = set()
        unique_results = []
        for result in all_results:
            if result["source"] not in seen_sources:
                unique_results.append(result)
                seen_sources.add(result["source"])

        thinking_log.append(
            f"🎯 Final results: {len(unique_results)} unique documents after deduplication"
        )

        return unique_results[:10]  # Limit to top 10 results

    def _log_thinking_process(
        self, ticker: str, thinking_log: List[str], results: List[Dict[str, Any]]
    ):
        """Save detailed thinking process to debug files."""
        if not self.debug_mode:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        build_dir = self._get_current_build_dir()

        # Save thinking process log
        thinking_file = (
            build_dir / "thinking_process" / f"semantic_retrieval_{ticker}_{timestamp}.txt"
        )
        thinking_file.parent.mkdir(parents=True, exist_ok=True)

        with open(thinking_file, "w", encoding="utf-8") as f:
            f.write(f"🧠 Semantic Retrieval Thinking Process for {ticker}\n")
            f.write(f"{'=' * 60}\n\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n\n")

            f.write("📋 Step-by-Step Thinking Process:\n")
            f.write("-" * 40 + "\n")
            for step in thinking_log:
                f.write(f"{step}\n")

            f.write(f"\n\n📄 Retrieved Documents Summary:\n")
            f.write("-" * 40 + "\n")
            for i, result in enumerate(results, 1):
                f.write(f"\nDocument {i}:\n")
                f.write(f"  📁 Source: {result['source']}\n")
                f.write(f"  📊 Score: {result['similarity_score']}\n")
                f.write(f"  📝 Type: {result['document_type']}\n")
                f.write(f"  🧠 Why relevant: {result.get('thinking_process', 'N/A')}\n")
                f.write(f"  📄 Content preview: {result['content'][:200]}...\n")
                f.write("-" * 20 + "\n")

        # Also save detailed results as JSON
        build_dir = self._get_current_build_dir()
        results_file = build_dir / "semantic_results" / f"retrieved_docs_{ticker}_{timestamp}.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)

        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "ticker": ticker,
                    "timestamp": datetime.now().isoformat(),
                    "thinking_steps": thinking_log,
                    "retrieved_documents": results,
                    "summary": {
                        "total_documents": len(results),
                        "avg_similarity": (
                            sum(r["similarity_score"] for r in results) / len(results)
                            if results
                            else 0
                        ),
                        "document_types": list(set(r["document_type"] for r in results)),
                    },
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        logger.info(f"💾 Saved thinking process to: {thinking_file}")
        logger.info(f"💾 Saved detailed results to: {results_file}")

    def _compile_final_report(self, ticker: str, components: Dict[str, Any]) -> str:
        """Compile all components into a final comprehensive report."""
        report_sections = []

        # Header
        report_sections.append(
            f"""# Comprehensive Financial Analysis Report: {ticker}

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Type**: LLM-Powered DCF Valuation with Risk Assessment
**Model**: GPT-OSS:20B via Ollama + FinLang Embeddings

---
"""
        )

        # DCF Valuation Section
        if "dcf_valuation" in components and components["dcf_valuation"]["success"]:
            report_sections.append("## 📊 DCF Valuation Analysis\n")
            # DCF valuation has different structure - uses 'reports' instead of 'response'
            if "reports" in components["dcf_valuation"]:
                # Use English report for the final compilation
                en_report = components["dcf_valuation"]["reports"].get(
                    "en", "No English DCF report available"
                )
                report_sections.append(en_report)
            elif "response" in components["dcf_valuation"]:
                report_sections.append(components["dcf_valuation"]["response"])
            report_sections.append("\n---\n")

        # Risk Analysis Section
        if "risk_analysis" in components and components["risk_analysis"]["success"]:
            report_sections.append("## ⚠️ Risk Analysis\n")
            report_sections.append(components["risk_analysis"]["response"])
            report_sections.append("\n---\n")

        # Investment Recommendation Section
        if (
            "investment_recommendation" in components
            and components["investment_recommendation"]["success"]
        ):
            report_sections.append("## 💡 Investment Recommendation\n")
            report_sections.append(components["investment_recommendation"]["response"])
            report_sections.append("\n---\n")

        # Footer with metadata
        report_sections.append(
            f"""## 🔧 Analysis Metadata

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
"""
        )

        return "\n".join(report_sections)

    def _calculate_total_duration(self, components: Dict[str, Any]) -> float:
        """Calculate total generation duration from all components."""
        total_duration = 0.0
        for component in components.values():
            if isinstance(component, dict) and "duration_seconds" in component:
                total_duration += component["duration_seconds"]
        return total_duration

    def _save_debug_results(self, ticker: str, result: Dict[str, Any]):
        """Save comprehensive debug results."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save full result data
        debug_file = directory_manager.get_logs_path() / f"dcf_generation_{ticker}_{timestamp}.json"
        debug_file.parent.mkdir(parents=True, exist_ok=True)

        with open(debug_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=str)

        # Save final report separately
        if "final_report" in result:
            report_file = self.debug_dir / "responses" / f"final_report_{ticker}_{timestamp}.md"
            report_file.parent.mkdir(parents=True, exist_ok=True)

            with open(report_file, "w", encoding="utf-8") as f:
                f.write(result["final_report"])

        logger.info(f"🔍 Debug results saved: {debug_file}")

    def _save_comprehensive_debug_results(
        self, ticker: str, result: Dict[str, Any], semantic_results: List[Dict[str, Any]]
    ):
        """Save comprehensive debug results with thinking process for build files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create build-specific debug output directory
        build_debug_dir = Path("data/stage_99_build") / f"build_{timestamp}" / "dcf_debug"
        build_debug_dir.mkdir(parents=True, exist_ok=True)

        # 1. Save comprehensive thinking process report
        thinking_report_file = build_debug_dir / f"THINKING_PROCESS_{ticker}.md"
        with open(thinking_report_file, "w", encoding="utf-8") as f:
            f.write(f"# 🧠 DCF Analysis Thinking Process - {ticker}\n\n")
            f.write(f"**Generated**: {datetime.now().isoformat()}\n\n")
            f.write(f"**Build ID**: build_{timestamp}\n\n")

            f.write("## 📋 Analysis Overview\n\n")
            f.write(f"- **Company**: {ticker}\n")
            f.write(f"- **Documents Retrieved**: {len(semantic_results)}\n")
            f.write(f"- **Analysis Components**: {len(result.get('components', {}))}\n\n")

            f.write("## 🔍 Semantic Retrieval Details\n\n")
            f.write("### 📊 Retrieved SEC Documents\n\n")

            for i, doc in enumerate(semantic_results, 1):
                f.write(f"#### Document {i}: {doc.get('source', 'Unknown')}\n\n")
                f.write(f"- **Document Type**: {doc.get('document_type', 'N/A')}\n")
                f.write(f"- **Similarity Score**: {doc.get('similarity_score', 'N/A'):.3f}\n")
                f.write(f"- **Filing Date**: {doc.get('filing_date', 'N/A')}\n")
                f.write(f"- **Section**: {doc.get('file_section', 'N/A')}\n")
                f.write(
                    f"- **Why This Document Matters**: {doc.get('thinking_process', 'N/A')}\n\n"
                )

                f.write("**Content Preview**:\n")
                f.write("```\n")
                content = doc.get("content", "")
                f.write(content[:500] + "..." if len(content) > 500 else content)
                f.write("\n```\n\n")

                f.write("**DCF Impact Analysis**:\n")
                doc_type = doc.get("document_type", "")
                if "business" in doc_type or "10k" in doc_type:
                    f.write(
                        "- 🔢 **Revenue & Cash Flow**: Core financial metrics for DCF base case\n"
                    )
                    f.write("- 📈 **Growth Trends**: Historical patterns for projection modeling\n")
                elif "risk" in doc_type:
                    f.write(
                        "- ⚠️ **Risk Assessment**: Factors affecting discount rate and scenarios\n"
                    )
                    f.write("- 🎯 **Probability Weighting**: Input for risk-adjusted valuations\n")
                elif "mda" in doc_type:
                    f.write(
                        "- 🚀 **Strategic Direction**: Management guidance for future projections\n"
                    )
                    f.write("- 💡 **Investment Priorities**: CapEx and R&D allocation insights\n")
                elif "executive" in doc_type:
                    f.write("- 👔 **Leadership Quality**: Management execution risk assessment\n")
                    f.write(
                        "- 🎖️ **Experience Factor**: Age and tenure impact on innovation score\n"
                    )
                f.write("\n")
                f.write("---\n\n")

            f.write("## 🎯 DCF Components Generated\n\n")
            components = result.get("components", {})
            for comp_name, comp_data in components.items():
                f.write(f"### {comp_name.replace('_', ' ').title()}\n")
                if isinstance(comp_data, dict) and "success" in comp_data:
                    if comp_data["success"]:
                        f.write("✅ **Status**: Successfully generated\n")
                        if "response" in comp_data:
                            response_len = len(comp_data["response"])
                            f.write(f"📝 **Response Length**: {response_len} characters\n")
                        if "duration_seconds" in comp_data:
                            f.write(
                                f"⏱️ **Generation Time**: {comp_data['duration_seconds']:.2f} seconds\n"
                            )
                    else:
                        f.write("❌ **Status**: Generation failed\n")
                        f.write(f"🚨 **Error**: {comp_data.get('error', 'Unknown error')}\n")
                f.write("\n")

            f.write("## 📊 Bilingual Report Status\n\n")
            dcf_component = components.get("dcf_valuation", {})
            if "reports" in dcf_component:
                reports = dcf_component["reports"]
                if "english" in reports:
                    en_success = reports["english"].get("success", False)
                    f.write(
                        f"🇺🇸 **English Report**: {'✅ Generated' if en_success else '❌ Failed'}\n"
                    )
                if "chinese" in reports:
                    zh_success = reports["chinese"].get("success", False)
                    f.write(
                        f"🇨🇳 **Chinese Report**: {'✅ Generated' if zh_success else '❌ Failed'}\n"
                    )
            f.write("\n")

            f.write("## 🔗 Related Files\n\n")
            f.write(f"- **Full Debug Data**: `dcf_generation_{ticker}_{timestamp}.json`\n")
            f.write(f"- **English Report**: `dcf_en_{ticker}_{timestamp}.md`\n")
            f.write(f"- **Chinese Report**: `dcf_zh_{ticker}_{timestamp}.md`\n")
            f.write(f"- **Semantic Search Details**: `retrieved_docs_{ticker}_{timestamp}.json`\n")

        # 2. Save detailed SEC document analysis
        sec_analysis_file = build_debug_dir / f"SEC_DOCUMENTS_ANALYSIS_{ticker}.json"
        with open(sec_analysis_file, "w", encoding="utf-8") as f:
            sec_analysis = {
                "ticker": ticker,
                "analysis_timestamp": datetime.now().isoformat(),
                "total_documents": len(semantic_results),
                "document_types": list(
                    set(doc.get("document_type", "unknown") for doc in semantic_results)
                ),
                "avg_similarity_score": (
                    sum(doc.get("similarity_score", 0) for doc in semantic_results)
                    / len(semantic_results)
                    if semantic_results
                    else 0
                ),
                "documents": [],
            }

            for doc in semantic_results:
                doc_analysis = {
                    "source_file": doc.get("source", "Unknown"),
                    "document_type": doc.get("document_type", "Unknown"),
                    "similarity_score": doc.get("similarity_score", 0),
                    "content_length": len(doc.get("content", "")),
                    "filing_info": {
                        "filing_date": doc.get("filing_date", "N/A"),
                        "section": doc.get("file_section", "N/A"),
                        "cik": doc.get("cik", "N/A"),
                    },
                    "dcf_relevance": doc.get("thinking_process", "N/A"),
                    "content_preview": (
                        doc.get("content", "")[:300] + "..."
                        if len(doc.get("content", "")) > 300
                        else doc.get("content", "")
                    ),
                    "full_content": doc.get("content", ""),
                }
                sec_analysis["documents"].append(doc_analysis)

            json.dump(sec_analysis, f, indent=2, ensure_ascii=False)

        # 3. Create summary build log entry
        build_summary_file = build_debug_dir / f"BUILD_SUMMARY_{ticker}.txt"
        with open(build_summary_file, "w", encoding="utf-8") as f:
            f.write(f"DCF Build Summary - {ticker}\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Build ID: build_{timestamp}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n\n")

            f.write("📄 SEC Documents Retrieved:\n")
            for doc in semantic_results:
                f.write(
                    f"  • {doc.get('source', 'Unknown')} (score: {doc.get('similarity_score', 0):.3f})\n"
                )

            f.write(f"\n🎯 Analysis Components:\n")
            for comp_name, comp_data in components.items():
                status = "✅" if comp_data.get("success", False) else "❌"
                f.write(f"  {status} {comp_name.replace('_', ' ').title()}\n")

            f.write(f"\n📊 Output Files Generated:\n")
            f.write(f"  • Thinking Process: THINKING_PROCESS_{ticker}.md\n")
            f.write(f"  • SEC Analysis: SEC_DOCUMENTS_ANALYSIS_{ticker}.json\n")
            f.write(f"  • Build Summary: BUILD_SUMMARY_{ticker}.txt\n")

        # Also call the original debug save method
        self._save_debug_results(ticker, result)

        logger.info(f"💾 Comprehensive build debug saved to: {build_debug_dir}")
        logger.info(f"📋 Key files:")
        logger.info(f"   - Thinking process: {thinking_report_file}")
        logger.info(f"   - SEC analysis: {sec_analysis_file}")
        logger.info(f"   - Build summary: {build_summary_file}")

    def test_system_integration(self) -> Dict[str, Any]:
        """Test the complete system integration."""
        logger.info("🧪 Testing LLM DCF system integration...")

        test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "overall_status": "unknown",
        }

        # Test 1: Embedding model
        embedding_test = self.embedding_model.test_embedding_quality(
            [
                "Apple Inc. financial performance analysis",
                "Risk factors for technology companies",
                "DCF valuation methodology for growth stocks",
            ]
        )
        test_results["tests"]["embedding_model"] = embedding_test

        # Test 2: Ollama connection
        ollama_test = self.ollama_client.test_connection()
        test_results["tests"]["ollama_connection"] = ollama_test

        # Test 3: End-to-end DCF generation
        try:
            dcf_test = self.generate_comprehensive_dcf_report("AAPL")
            test_results["tests"]["dcf_generation"] = {
                "success": dcf_test["success"],
                "components_generated": len(dcf_test.get("components", {})),
                "errors": dcf_test.get("errors", []),
            }
        except Exception as e:
            test_results["tests"]["dcf_generation"] = {"success": False, "error": str(e)}

        # Determine overall status
        if (
            embedding_test.get("status") == "completed"
            and ollama_test.get("success")
            and test_results["tests"]["dcf_generation"].get("success")
        ):
            test_results["overall_status"] = "success"
        else:
            test_results["overall_status"] = "failure"

        # Save test results
        test_file = directory_manager.get_logs_path() / "system_integration_test.json"
        test_file.parent.mkdir(parents=True, exist_ok=True)

        with open(test_file, "w", encoding="utf-8") as f:
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
        debug_info.append(
            f"- **Ollama Client**: Base URL: {self.ollama_client.base_url}, Model: {self.ollama_client.model_name}"
        )
        debug_info.append(f"- **Debug Mode**: {self.debug_mode}")
        debug_info.append(f"- **Debug Directory**: {self.debug_dir}")

        # Recent log files
        debug_info.append("\n## Recent Activity\n")

        log_dir = directory_manager.get_logs_path()
        if log_dir.exists():
            log_files = sorted(
                log_dir.glob("*.json*"), key=lambda x: x.stat().st_mtime, reverse=True
            )[:5]
            for log_file in log_files:
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                debug_info.append(f"- {log_file.name} (Modified: {mtime.isoformat()})")

        # Recent reports
        debug_info.append("\n## Recent Reports\n")

        response_dir = self.debug_dir / "responses"
        if response_dir.exists():
            report_files = sorted(
                response_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True
            )[:5]
            for report_file in report_files:
                mtime = datetime.fromtimestamp(report_file.stat().st_mtime)
                debug_info.append(f"- {report_file.name} (Generated: {mtime.isoformat()})")

        return "\n".join(debug_info)
