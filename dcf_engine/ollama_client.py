#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama Client for DCF Analysis

Integrates with local Ollama server running gpt-oss:20b for generating
intelligent DCF reports and financial analysis.
"""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
import yaml

logger = logging.getLogger(__name__)


class OllamaClient:
    """
    Client for interacting with local Ollama server for financial analysis.

    Provides methods for generating DCF reports, risk analysis, and investment
    recommendations using the gpt-oss:20b model.
    """

    def __init__(self, config_path: Optional[str] = None, mock_mode: bool = False):
        """
        Initialize Ollama client.

        Args:
            config_path: Path to configuration file
            mock_mode: Enable mock mode for testing (explicit parameter only)
        """
        self.config = self._load_config(config_path)
        # Only use explicit parameter - no env vars or config-based mock mode
        self.mock_mode = mock_mode

        # Support both old format (ollama section) and new format (llm_service section)
        llm_config = self.config.get("llm_service", self.config.get("ollama", {}))

        if self.mock_mode:
            logger.info("🚀 Running in EXPLICIT mock mode for testing")
            self.base_url = "mock://localhost"
            self.model_name = "mock-model"
            self.timeout = 5
        else:
            self.base_url = llm_config.get("base_url", "http://localhost:11434")
            self.model_name = llm_config.get("model_name", llm_config.get("model", "deepseek-r1:1.5b"))
            self.timeout = llm_config.get("timeout", 45)

        # Generation parameters - support both config formats and mock mode
        generation_config = self.config.get("generation", {})
        self.max_tokens = llm_config.get(
            "max_tokens", generation_config.get("max_tokens", 2048 if self.mock_mode else 4096)
        )
        self.temperature = llm_config.get("temperature", generation_config.get("temperature", 0.3))
        self.top_p = llm_config.get("top_p", generation_config.get("top_p", 0.9))

        # Debug settings
        self.debug_mode = self.config.get("dcf_generation", {}).get("debug_mode", True)
        self.log_requests = self.config.get("logging", {}).get("log_requests", not self.mock_mode)
        self.log_responses = self.config.get("logging", {}).get("log_responses", not self.mock_mode)
        self.debug_dir = Path("data/llm")

        # Template directory
        self.template_dir = self.debug_dir / "templates"
        # Fallback to project templates if data templates don't exist
        self.fallback_template_dir = Path("templates/dcf")

        if not self.mock_mode:
            self._verify_ollama_connection()
            self._ping_pong_test()
        else:
            logger.info("🏃 Skipping Ollama connection verification in mock mode")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if config_path is None:
            # Use DeepSeek fast config as default (no mock mode)
            config_path = "data/llm/configs/deepseek_fast.yml"

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "ollama": {
                "base_url": "http://localhost:11434",
                "model_name": "gpt-oss:20b",
                "timeout": 45,
                "max_tokens": 4096,
                "temperature": 0.3,
                "top_p": 0.9,
            },
            "dcf_generation": {"debug_mode": True},
            "logging": {"log_requests": True, "log_responses": True},
        }

    def _verify_ollama_connection(self):
        """Verify connection to Ollama server."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model.get("name", "") for model in models]

                if self.model_name in model_names:
                    logger.info(f"✅ Connected to Ollama, model {self.model_name} available")
                else:
                    logger.warning(
                        f"⚠️ Model {self.model_name} not found. Available models: {model_names}"
                    )

                if self.debug_mode:
                    self._save_connection_info(models)
            else:
                logger.error(f"❌ Failed to connect to Ollama server: {response.status_code}")

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ollama server not reachable: {e}")
            logger.info("Make sure Ollama is running: ollama serve")

    def _ping_pong_test(self):
        """Perform a quick ping-pong test with the model to verify response time."""
        try:
            start_time = time.time()
            logger.info(f"🏓 Ping-pong test with {self.model_name}...")

            # Simple test prompt
            test_prompt = "Say only: PONG"

            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": test_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0,
                        "num_predict": 10,  # Very short response
                    },
                },
                timeout=30,  # Shorter timeout for ping test
            )

            response_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "").strip()
                logger.info(f"🏓 Ping-pong successful: '{answer}' ({response_time:.1f}s)")

                # Warn if response time is slow
                if response_time > 15:
                    logger.warning(
                        f"⚠️  Model response slow ({response_time:.1f}s) - expect longer DCF generation"
                    )
                elif response_time > 30:
                    logger.error(
                        f"❌ Model response very slow ({response_time:.1f}s) - consider using fast-build"
                    )
            else:
                logger.error(f"❌ Ping-pong failed: HTTP {response.status_code}")

        except Exception as e:
            logger.warning(f"⚠️  Ping-pong test failed: {e}")

    def _save_connection_info(self, models: List[Dict]):
        """Save connection and model info for debugging."""
        connection_info = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "target_model": self.model_name,
            "available_models": models,
            "connection_status": "connected",
        }

        debug_file = Path("data/log") / "ollama_connection.json"
        debug_file.parent.mkdir(parents=True, exist_ok=True)

        with open(debug_file, "w", encoding="utf-8") as f:
            json.dump(connection_info, f, indent=2)

    def generate_completion(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate completion from Ollama model.

        Args:
            prompt: Input prompt for the model
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream the response

        Returns:
            Dictionary containing the response and metadata
        """
        # Return mock response in CI fast testing mode
        if self.mock_mode:
            return self._generate_mock_completion(prompt)

        request_data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature or self.temperature,
                "top_p": self.top_p,
                "num_predict": max_tokens or self.max_tokens,
            },
        }

        request_id = self._generate_request_id()
        start_time = time.time()

        if self.log_requests:
            self._log_request(request_id, request_data)

        try:
            response = requests.post(
                f"{self.base_url}/api/generate", json=request_data, timeout=self.timeout
            )

            response.raise_for_status()
            response_data = response.json()

            end_time = time.time()
            duration = end_time - start_time

            result = {
                "success": True,
                "response": response_data.get("response", ""),
                "model": response_data.get("model", self.model_name),
                "duration_seconds": duration,
                "total_duration": response_data.get("total_duration", 0),
                "load_duration": response_data.get("load_duration", 0),
                "prompt_eval_count": response_data.get("prompt_eval_count", 0),
                "eval_count": response_data.get("eval_count", 0),
                "request_id": request_id,
            }

            if self.log_responses:
                self._log_response(request_id, result)

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "request_id": request_id,
                "duration_seconds": time.time() - start_time,
            }

    def generate_dcf_report(
        self,
        ticker: str,
        financial_data: Dict[str, Any],
        market_context: Dict[str, Any],
        semantic_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Generate comprehensive DCF valuation report.

        Args:
            ticker: Stock ticker symbol
            financial_data: Financial metrics and ratios
            market_context: Market conditions and sector data
            semantic_results: Relevant financial intelligence from embeddings

        Returns:
            Generated DCF report and metadata
        """
        # Load DCF valuation prompt template
        template_path = self.template_dir / "dcf_valuation_prompt.md"

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()
        except FileNotFoundError:
            logger.error(f"DCF template not found: {template_path}")
            return {"success": False, "error": "DCF template not found"}

        # Format the prompt with data
        formatted_prompt = self._format_dcf_prompt(
            prompt_template, ticker, financial_data, market_context, semantic_results
        )

        # Generate the report
        result = self.generate_completion(
            prompt=formatted_prompt,
            temperature=0.3,  # Lower temperature for factual analysis
            max_tokens=3000,
        )

        if result["success"]:
            # Save the generated report
            if self.debug_mode:
                self._save_generated_report("dcf", ticker, result["response"], result)

        return result

    def generate_bilingual_dcf_report(
        self,
        ticker: str,
        financial_data: Dict[str, Any],
        market_context: Dict[str, Any],
        semantic_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Generate bilingual (English and Chinese) DCF valuation reports.

        Args:
            ticker: Stock ticker symbol
            financial_data: Enhanced financial metrics including market size, R&D, executive info
            market_context: Market conditions and sector data
            semantic_results: Relevant financial intelligence from embeddings

        Returns:
            Dictionary containing both English and Chinese reports and metadata
        """
        results = {"success": True, "reports": {}}

        # Enhance financial data with additional analysis factors
        enhanced_data = self._enhance_financial_data(financial_data, ticker)

        # Generate English report
        en_result = self._generate_single_language_report(
            ticker, enhanced_data, market_context, semantic_results, "en"
        )

        # Generate Chinese report
        zh_result = self._generate_single_language_report(
            ticker, enhanced_data, market_context, semantic_results, "zh"
        )

        if en_result["success"]:
            results["reports"]["english"] = en_result
            # Save English report
            if self.debug_mode:
                self._save_generated_report("dcf_en", ticker, en_result["response"], en_result)
        else:
            results["success"] = False
            results["english_error"] = en_result.get("error", "Unknown error")

        if zh_result["success"]:
            results["reports"]["chinese"] = zh_result
            # Save Chinese report
            if self.debug_mode:
                self._save_generated_report("dcf_zh", ticker, zh_result["response"], zh_result)
        else:
            results["success"] = False
            results["chinese_error"] = zh_result.get("error", "Unknown error")

        return results

    def _generate_single_language_report(
        self,
        ticker: str,
        financial_data: Dict,
        market_context: Dict,
        semantic_results: List,
        language: str,
    ) -> Dict[str, Any]:
        """Generate DCF report in specified language."""
        # Load appropriate template
        template_filename = f"dcf_valuation_prompt_{language}.md"
        template_path = self.template_dir / template_filename

        # Try fallback template location if primary doesn't exist
        if not template_path.exists():
            template_path = self.fallback_template_dir / template_filename

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()
        except FileNotFoundError:
            logger.error(f"DCF template not found: {template_path}")
            return {"success": False, "error": f"DCF template not found: {template_filename}"}

        # Format the prompt with enhanced data
        formatted_prompt = self._format_enhanced_dcf_prompt(
            prompt_template, ticker, financial_data, market_context, semantic_results
        )

        # Generate the report
        result = self.generate_completion(
            prompt=formatted_prompt,
            temperature=0.3,  # Lower temperature for factual analysis
            max_tokens=4000,  # Increased for comprehensive analysis
        )

        return result

    def _enhance_financial_data(self, financial_data: Dict, ticker: str) -> Dict:
        """Enhance financial data with additional analysis factors."""
        enhanced = financial_data.copy()

        # Add market analysis factors
        enhanced["market_analysis"] = {
            "market_size_growth": self._calculate_market_growth(financial_data),
            "revenue_growth_breakdown": self._analyze_revenue_growth(financial_data),
            "rd_efficiency": self._calculate_rd_efficiency(financial_data),
            "competitive_positioning": self._assess_competitive_position(financial_data),
        }

        # Add executive analysis factors
        enhanced["executive_analysis"] = {
            "leadership_age_factor": self._analyze_leadership_age(financial_data),
            "management_tenure": self._analyze_management_tenure(financial_data),
            "strategic_execution_score": self._calculate_execution_score(financial_data),
        }

        return enhanced

    def _calculate_market_growth(self, data: Dict) -> Dict:
        """Calculate market size and growth metrics."""
        historical = data.get("historical", {})
        revenue_data = historical.get("revenue", [])

        if len(revenue_data) >= 3:
            # Calculate CAGR over available period
            recent_revenue = revenue_data[-1] if revenue_data else 0
            old_revenue = revenue_data[0] if len(revenue_data) > 0 else recent_revenue
            years = len(revenue_data) - 1

            if years > 0 and old_revenue > 0:
                cagr = ((recent_revenue / old_revenue) ** (1 / years)) - 1
            else:
                cagr = 0
        else:
            cagr = 0

        return {
            "revenue_cagr": cagr,
            "market_capacity_estimate": recent_revenue * 10 if "recent_revenue" in locals() else 0,
            "growth_trend": (
                "accelerating" if cagr > 0.15 else "stable" if cagr > 0.05 else "declining"
            ),
        }

    def _analyze_revenue_growth(self, data: Dict) -> Dict:
        """Analyze revenue growth patterns from available data."""
        historical = data.get("historical", {})
        revenue_data = historical.get("revenue", [])

        # Calculate organic growth estimate from historical data if available
        organic_growth = 0.0
        if len(revenue_data) >= 2:
            recent_growth = (
                (revenue_data[-1] - revenue_data[-2]) / revenue_data[-2]
                if revenue_data[-2] > 0
                else 0
            )
            organic_growth = max(0, recent_growth)  # Use actual data

        return {
            "organic_growth_estimate": organic_growth,
            "revenue_trend": (
                "increasing"
                if len(revenue_data) >= 2 and revenue_data[-1] > revenue_data[-2]
                else "stable"
            ),
            "data_points_available": len(revenue_data),
        }

    def _calculate_rd_efficiency(self, data: Dict) -> Dict:
        """Calculate R&D efficiency metrics from actual data."""
        financials = data.get("financials", {})
        historical = data.get("historical", {})

        rd_expense = financials.get("research_development", 0)
        revenue = financials.get("revenue", 1)  # Avoid division by zero

        rd_intensity = rd_expense / revenue if revenue > 0 else 0

        # Calculate R&D growth trend if historical data available
        rd_historical = historical.get("rd_expenses", [])
        rd_growth_trend = "stable"
        if len(rd_historical) >= 2:
            if rd_historical[-1] > rd_historical[-2]:
                rd_growth_trend = "increasing"
            elif rd_historical[-1] < rd_historical[-2]:
                rd_growth_trend = "decreasing"

        return {
            "rd_intensity": rd_intensity,
            "rd_growth_trend": rd_growth_trend,
            "rd_absolute_amount": rd_expense,
            "historical_rd_points": len(rd_historical),
        }

    def _assess_competitive_position(self, data: Dict) -> Dict:
        """Assess competitive positioning from available financial data."""
        financials = data.get("financials", {})
        historical = data.get("historical", {})

        # Assess based on margin trends if available
        revenue = financials.get("revenue", 0)
        net_income = financials.get("net_income", 0)
        margin = net_income / revenue if revenue > 0 else 0

        return {
            "current_margin": margin,
            "has_historical_data": len(historical.get("revenue", [])) > 1,
            "data_source": "financial_metrics",
        }

    def _analyze_leadership_age(self, data: Dict) -> Dict:
        """Analyze executive leadership age and experience from provided data."""
        executive_info = data.get("executive_info", {})

        ceo_age = executive_info.get("ceo_age", None)
        ceo_tenure = executive_info.get("ceo_tenure", None)

        # Only calculate innovation score if we have real age data
        leadership_score = None
        if ceo_age is not None:
            leadership_score = "high" if ceo_age < 55 else "moderate"

        return {
            "ceo_age": ceo_age,
            "ceo_tenure": ceo_tenure,
            "ceo_name": executive_info.get("ceo_name", None),
            "leadership_innovation_score": leadership_score,
            "data_availability": "provided" if ceo_age is not None else "not_available",
        }

    def _analyze_management_tenure(self, data: Dict) -> Dict:
        """Analyze management team tenure and stability from available data."""
        executive_info = data.get("executive_info", {})

        return {
            "ceo_tenure": executive_info.get("ceo_tenure", None),
            "succession_planning": executive_info.get("succession_planning", None),
            "management_stability": executive_info.get("management_stability", None),
            "data_source": "executive_info" if executive_info else "not_available",
        }

    def _calculate_execution_score(self, data: Dict) -> Dict:
        """Calculate strategic execution capability score from financial performance."""
        historical = data.get("historical", {})

        # Base execution assessment on data availability and trends
        has_good_data = len(historical.get("revenue", [])) >= 3

        return {
            "data_quality": "good" if has_good_data else "limited",
            "historical_periods": len(historical.get("revenue", [])),
            "assessment_basis": "financial_trends" if has_good_data else "limited_data",
        }

    def generate_risk_analysis(
        self, ticker: str, financial_data: Dict[str, Any], semantic_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive risk analysis report.

        Args:
            ticker: Stock ticker symbol
            financial_data: Financial risk indicators
            semantic_results: Relevant risk intelligence

        Returns:
            Generated risk analysis and metadata
        """
        template_path = self.template_dir / "risk_analysis_prompt.md"

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()
        except FileNotFoundError:
            logger.error(f"Risk template not found: {template_path}")
            return {"success": False, "error": "Risk template not found"}

        # Format the prompt
        logger.debug(f"🐛 Risk analysis - financial_data keys: {list(financial_data.keys()) if financial_data else 'None'}")
        formatted_prompt = self._format_risk_prompt(
            prompt_template, ticker, financial_data, semantic_results
        )
        logger.debug(f"🐛 Risk analysis prompt formatted successfully")

        result = self.generate_completion(
            prompt=formatted_prompt,
            temperature=0.4,  # Slightly higher for nuanced risk assessment
            max_tokens=2500,
        )
        logger.debug(f"🐛 Risk analysis completion result: {result.get('success', False)}")

        if result["success"] and self.debug_mode:
            self._save_generated_report("risk", ticker, result["response"], result)

        return result

    def generate_investment_recommendation(
        self,
        ticker: str,
        dcf_results: Dict[str, Any],
        risk_analysis: Dict[str, Any],
        semantic_results: List[Dict[str, Any]],
        financial_data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Generate investment recommendation based on DCF and risk analysis.

        Args:
            ticker: Stock ticker symbol
            dcf_results: DCF valuation results
            risk_analysis: Risk assessment results
            semantic_results: Market intelligence

        Returns:
            Investment recommendation and rationale
        """
        template_path = self.template_dir / "investment_recommendation_prompt.md"

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()
        except FileNotFoundError:
            logger.error(f"Investment template not found: {template_path}")
            return {"success": False, "error": "Investment template not found"}

        # Format the prompt
        formatted_prompt = self._format_investment_prompt(
            prompt_template, ticker, dcf_results, risk_analysis, semantic_results, financial_data
        )

        result = self.generate_completion(
            prompt=formatted_prompt,
            temperature=0.5,  # Higher temperature for investment creativity
            max_tokens=2000,
        )

        if result["success"] and self.debug_mode:
            self._save_generated_report("investment", ticker, result["response"], result)

        return result

    def _format_dcf_prompt(
        self,
        template: str,
        ticker: str,
        financial_data: Dict,
        market_context: Dict,
        semantic_results: List,
    ) -> str:
        """Format DCF prompt template with actual data."""
        # Extract company information
        company_info = financial_data.get("company_info", {})

        # Format semantic search results
        formatted_semantic = self._format_semantic_results(semantic_results)

        return template.format(
            ticker=ticker.upper(),
            company_name=company_info.get("name", ticker),
            sector=company_info.get("sector", "Unknown"),
            industry=company_info.get("industry", "Unknown"),
            analysis_date=datetime.now().strftime("%Y-%m-%d"),
            financial_data=json.dumps(financial_data, indent=2),
            historical_data=json.dumps(financial_data.get("historical", {}), indent=2),
            market_context=json.dumps(market_context, indent=2),
            semantic_search_results=formatted_semantic,
        )

    def _format_enhanced_dcf_prompt(
        self,
        template: str,
        ticker: str,
        financial_data: Dict,
        market_context: Dict,
        semantic_results: List,
    ) -> str:
        """Format enhanced DCF prompt template with comprehensive data."""
        # Extract company information
        company_info = financial_data.get("company_info", {})

        # Format semantic search results
        formatted_semantic = self._format_semantic_results(semantic_results)

        # Extract enhanced analysis data
        market_analysis = financial_data.get("market_analysis", {})
        executive_analysis = financial_data.get("executive_analysis", {})

        return template.format(
            ticker=ticker.upper(),
            company_name=company_info.get("name", ticker),
            sector=company_info.get("sector", "Unknown"),
            industry=company_info.get("industry", "Unknown"),
            analysis_date=datetime.now().strftime("%Y-%m-%d"),
            financial_data=json.dumps(financial_data, indent=2, ensure_ascii=False),
            historical_data=json.dumps(
                financial_data.get("historical", {}), indent=2, ensure_ascii=False
            ),
            market_context=json.dumps(market_context, indent=2, ensure_ascii=False),
            semantic_search_results=formatted_semantic,
            # Enhanced analysis factors
            market_growth_data=json.dumps(
                market_analysis.get("market_size_growth", {}), indent=2, ensure_ascii=False
            ),
            rd_efficiency_data=json.dumps(
                market_analysis.get("rd_efficiency", {}), indent=2, ensure_ascii=False
            ),
            executive_analysis_data=json.dumps(executive_analysis, indent=2, ensure_ascii=False),
        )

    def _format_risk_prompt(
        self, template: str, ticker: str, financial_data: Dict, semantic_results: List
    ) -> str:
        """Format risk analysis prompt template."""
        logger.debug(f"🐛 _format_risk_prompt - financial_data type: {type(financial_data)}")
        company_info = financial_data.get("company_info", {})
        formatted_semantic = self._format_semantic_results(semantic_results)

        # Debug the template.format call
        logger.debug(f"🐛 About to call template.format with financial_data keys: {list(financial_data.keys())}")
        try:
            result = template.format(
                ticker=ticker.upper(),
                company_name=company_info.get("name", ticker),
                market_cap=financial_data.get("market_cap", "Unknown"),
                sector=company_info.get("sector", "Unknown"),
                analysis_date=datetime.now().strftime("%Y-%m-%d"),
                financial_data=json.dumps(financial_data, indent=2),
                semantic_results=formatted_semantic,
            )
            logger.debug(f"🐛 template.format succeeded")
            return result
        except Exception as e:
            logger.error(f"🐛 template.format failed: {e}")
            raise

    def _format_investment_prompt(
        self,
        template: str,
        ticker: str,
        dcf_results: Dict,
        risk_analysis: Dict,
        semantic_results: List,
        financial_data: Dict = None,
    ) -> str:
        """Format investment recommendation prompt template."""
        formatted_semantic = self._format_semantic_results(semantic_results)

        return template.format(
            ticker=ticker.upper(),
            analysis_date=datetime.now().strftime("%Y-%m-%d"),
            dcf_results=json.dumps(dcf_results, indent=2),
            risk_analysis=json.dumps(risk_analysis, indent=2),
            financial_data=json.dumps(financial_data or {}, indent=2),
            semantic_results=formatted_semantic,
        )

    def _format_semantic_results(self, semantic_results: List[Dict]) -> str:
        """Format semantic search results for prompt inclusion."""
        if not semantic_results:
            return "No relevant financial intelligence found."

        formatted_results = []
        for i, result in enumerate(semantic_results[:5], 1):
            content = result.get("content", str(result))[:500]  # Limit content length
            source = result.get("source", "Unknown source")
            similarity = result.get("similarity_score", 0.0)

            formatted_results.append(
                f"""
**Source {i}** (Relevance: {similarity:.2f}):
Source: {source}
Content: {content}
"""
            )

        return "\n".join(formatted_results)

    def _generate_request_id(self) -> str:
        """Generate unique request ID for tracking."""
        return f"req_{int(time.time())}_{hash(datetime.now()) % 10000}"

    def _log_request(self, request_id: str, request_data: Dict):
        """Log request for debugging."""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "model": request_data["model"],
            "prompt_length": len(request_data["prompt"]),
            "prompt_preview": (
                request_data["prompt"][:200] + "..."
                if len(request_data["prompt"]) > 200
                else request_data["prompt"]
            ),
            "options": request_data["options"],
        }

        log_file = Path("data/log") / "ollama_requests.jsonl"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_data) + "\n")

    def _log_response(self, request_id: str, response_data: Dict):
        """Log response for debugging."""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "success": response_data["success"],
            "duration_seconds": response_data["duration_seconds"],
            "response_length": len(response_data.get("response", "")),
            "response_preview": (
                response_data.get("response", "")[:200] + "..."
                if len(response_data.get("response", "")) > 200
                else response_data.get("response", "")
            ),
            "eval_count": response_data.get("eval_count", 0),
            "prompt_eval_count": response_data.get("prompt_eval_count", 0),
        }

        log_file = Path("data/log") / "ollama_responses.jsonl"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_data) + "\n")

    def _save_generated_report(self, report_type: str, ticker: str, content: str, metadata: Dict):
        """Save generated report for debugging and review."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_type}_{ticker}_{timestamp}.md"

        report_file = self.debug_dir / "responses" / filename
        report_file.parent.mkdir(parents=True, exist_ok=True)

        # Create full report with metadata
        full_report = f"""# {report_type.title()} Report for {ticker}

Generated: {datetime.now().isoformat()}
Model: {metadata.get('model', self.model_name)}
Duration: {metadata.get('duration_seconds', 0):.2f} seconds
Request ID: {metadata.get('request_id', 'unknown')}

---

{content}

---

## Generation Metadata
```json
{json.dumps(metadata, indent=2)}
```
"""

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(full_report)

        logger.info(f"Saved {report_type} report: {report_file}")

    def test_connection(self) -> Dict[str, Any]:
        """Test connection to Ollama server with a simple prompt."""
        test_prompt = "Hello! Please confirm you are working correctly by responding with 'Ollama connection successful'."

        result = self.generate_completion(prompt=test_prompt, max_tokens=50, temperature=0.1)

        if self.debug_mode and result["success"]:
            test_file = Path("data/log") / "connection_test.json"
            test_file.parent.mkdir(parents=True, exist_ok=True)

            with open(test_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)

        return result

    def _generate_mock_completion(self, prompt: str) -> Dict[str, Any]:
        """Generate mock completion for CI fast testing."""
        # Simulate a fast response time
        time.sleep(0.1)

        # Generate different mock responses based on prompt content
        if "DCF" in prompt or "valuation" in prompt:
            mock_response = """
# DCF Analysis Report (Mock Mode)

## Executive Summary
This is a mock DCF analysis generated for CI testing using DeepSeek 1.5b fast mode.

**Target Price**: $150.00 (Mock)
**Current Price**: $100.00 (Mock)  
**Upside**: 50.0%

## Financial Projections
- Revenue Growth: 15% CAGR (Mock)
- EBITDA Margin: 25% (Mock)
- WACC: 8.5% (Mock)

## Investment Recommendation
**BUY** - Mock recommendation for CI testing
            """
        elif "risk" in prompt.lower():
            mock_response = """
# Risk Analysis (Mock Mode)

## Risk Metrics
- Beta: 1.2 (Mock)
- VaR (95%): -15.2% (Mock)
- Sharpe Ratio: 1.8 (Mock)

## Risk Assessment
Medium risk profile with acceptable volatility for CI testing.
            """
        else:
            mock_response = f"""
# Mock LLM Response

This is a mock response generated by DeepSeek 1.5b in CI fast testing mode.

**Model**: deepseek-r1:1.5b
**Mode**: Fast CI Testing
**Timestamp**: {datetime.now().isoformat()}

The original prompt was processed successfully.
            """

        return {
            "success": True,
            "response": mock_response.strip(),
            "model": "deepseek-r1:1.5b",
            "mode": "mock_ci_fast",
            "tokens_used": len(mock_response.split()),
            "generation_time": 0.1,
            "timestamp": datetime.now().isoformat(),
        }
