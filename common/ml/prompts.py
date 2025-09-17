#!/usr/bin/env python3
"""
Prompt Management and LLM Integration
New prompt management system for Issue #284.

Centralized prompt templates and LLM interaction utilities.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union


class PromptType(Enum):
    """Types of prompts for different use cases."""

    FINANCIAL_ANALYSIS = "financial_analysis"
    DCF_VALUATION = "dcf_valuation"
    SEC_FILING = "sec_filing"
    RISK_ASSESSMENT = "risk_assessment"
    MARKET_SUMMARY = "market_summary"
    INVESTMENT_RECOMMENDATION = "investment_recommendation"


class PromptManager:
    """
    Centralized prompt management for LLM interactions.
    """

    def __init__(self):
        self.prompts = {}
        self._load_default_prompts()

    def _load_default_prompts(self):
        """Load default prompt templates."""
        self.prompts = {
            PromptType.FINANCIAL_ANALYSIS: {
                "system": "You are a financial analyst specializing in equity research and valuation.",
                "template": """
Analyze the financial performance of {company_name} ({ticker}) based on the following data:

{financial_data}

Provide:
1. Financial strength assessment
2. Key performance indicators analysis
3. Competitive position
4. Growth prospects
5. Risk factors
""",
                "variables": ["company_name", "ticker", "financial_data"],
            },
            PromptType.DCF_VALUATION: {
                "system": "You are a valuation expert using discounted cash flow analysis.",
                "template": """
Perform a DCF valuation for {company_name} ({ticker}) with these assumptions:

Free Cash Flow: {fcf}
Growth Rate (Years 1-5): {growth_rate}%
Terminal Growth Rate: {terminal_growth}%
WACC: {wacc}%
Shares Outstanding: {shares_outstanding}

Calculate:
1. Projected free cash flows (5 years)
2. Terminal value
3. Enterprise value
4. Equity value per share
5. Investment thesis
""",
                "variables": [
                    "company_name",
                    "ticker",
                    "fcf",
                    "growth_rate",
                    "terminal_growth",
                    "wacc",
                    "shares_outstanding",
                ],
            },
            PromptType.SEC_FILING: {
                "system": "You are an expert in SEC filing analysis and regulatory compliance.",
                "template": """
Analyze this SEC filing excerpt for {company_name} ({ticker}):

Filing: {filing_type} dated {filing_date}
Content: {content}

Extract and summarize:
1. Material financial information
2. Business developments
3. Risk disclosures
4. Forward-looking statements
5. Regulatory implications
""",
                "variables": ["company_name", "ticker", "filing_type", "filing_date", "content"],
            },
            PromptType.INVESTMENT_RECOMMENDATION: {
                "system": "You are a portfolio manager making investment recommendations.",
                "template": """
Based on comprehensive analysis of {company_name} ({ticker}):

Valuation: {valuation}
Current Price: {current_price}
Target Price: {target_price}
Risk Rating: {risk_rating}

Additional Context:
{analysis_context}

Provide:
1. Investment recommendation (Strong Buy/Buy/Hold/Sell/Strong Sell)
2. Price target justification
3. Key catalysts
4. Risk considerations
5. Position sizing recommendation
""",
                "variables": [
                    "company_name",
                    "ticker",
                    "valuation",
                    "current_price",
                    "target_price",
                    "risk_rating",
                    "analysis_context",
                ],
            },
        }

    def get_prompt(self, prompt_type: PromptType) -> Dict[str, Any]:
        """
        Get prompt template by type.

        Args:
            prompt_type: Type of prompt to retrieve

        Returns:
            Dictionary with prompt template information
        """
        return self.prompts.get(prompt_type, {})

    def render_prompt(self, prompt_type: PromptType, **kwargs) -> Dict[str, str]:
        """
        Render a prompt with provided variables.

        Args:
            prompt_type: Type of prompt to render
            **kwargs: Variables for template substitution

        Returns:
            Dictionary with 'system' and 'user' messages

        Raises:
            KeyError: If prompt type not found
            ValueError: If required variables are missing
        """
        if prompt_type not in self.prompts:
            raise KeyError(f"Prompt type {prompt_type} not found")

        prompt_config = self.prompts[prompt_type]
        required_vars = prompt_config.get("variables", [])

        # Check for missing variables
        missing_vars = set(required_vars) - set(kwargs.keys())
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")

        # Render template
        user_message = prompt_config["template"].format(**kwargs)

        return {"system": prompt_config.get("system", ""), "user": user_message}

    def add_custom_prompt(
        self, prompt_type: Union[str, PromptType], system: str, template: str, variables: List[str]
    ):
        """
        Add a custom prompt template.

        Args:
            prompt_type: Prompt type identifier
            system: System message for the prompt
            template: Template string with {variable} placeholders
            variables: List of required variables
        """
        self.prompts[prompt_type] = {"system": system, "template": template, "variables": variables}

    def list_prompts(self) -> List[str]:
        """List all available prompt types."""
        return [pt.value if isinstance(pt, PromptType) else str(pt) for pt in self.prompts.keys()]


# Global prompt manager instance
prompt_manager = PromptManager()


# Convenience functions
def get_financial_analysis_prompt(**kwargs) -> Dict[str, str]:
    """Get financial analysis prompt."""
    return prompt_manager.render_prompt(PromptType.FINANCIAL_ANALYSIS, **kwargs)


def get_dcf_valuation_prompt(**kwargs) -> Dict[str, str]:
    """Get DCF valuation prompt."""
    return prompt_manager.render_prompt(PromptType.DCF_VALUATION, **kwargs)


def get_sec_filing_prompt(**kwargs) -> Dict[str, str]:
    """Get SEC filing analysis prompt."""
    return prompt_manager.render_prompt(PromptType.SEC_FILING, **kwargs)


def get_investment_recommendation_prompt(**kwargs) -> Dict[str, str]:
    """Get investment recommendation prompt."""
    return prompt_manager.render_prompt(PromptType.INVESTMENT_RECOMMENDATION, **kwargs)
