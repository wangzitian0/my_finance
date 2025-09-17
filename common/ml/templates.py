#!/usr/bin/env python3
"""
ML Templates and Prompt Management
Moved from templates/ → ml/templates.py (Issue #284)

Template and prompt management for ML/AI operations.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional


class TemplateManager:
    """
    Template management system for prompts and ML operations.
    """

    def __init__(self):
        self.templates = {}
        self.prompts = {}

    def register_template(self, name: str, template: str, variables: List[str] = None):
        """
        Register a template with variables.

        Args:
            name: Template name
            template: Template string with {variable} placeholders
            variables: List of required variables
        """
        self.templates[name] = {
            "template": template,
            "variables": variables or [],
        }

    def render_template(self, name: str, **kwargs) -> str:
        """
        Render a template with provided variables.

        Args:
            name: Template name
            **kwargs: Template variables

        Returns:
            Rendered template string

        Raises:
            KeyError: If template not found
            ValueError: If required variables missing
        """
        if name not in self.templates:
            raise KeyError(f"Template '{name}' not found")

        template_info = self.templates[name]
        template = template_info["template"]
        required_vars = template_info["variables"]

        # Check for missing required variables
        missing_vars = set(required_vars) - set(kwargs.keys())
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")

        return template.format(**kwargs)

    def load_templates_from_config(self, config: Dict[str, Any]):
        """
        Load templates from configuration dictionary.

        Args:
            config: Configuration with template definitions
        """
        templates_config = config.get("templates", {})
        for name, template_config in templates_config.items():
            self.register_template(
                name=name,
                template=template_config.get("template", ""),
                variables=template_config.get("variables", []),
            )


# Default financial analysis templates
DEFAULT_TEMPLATES = {
    "dcf_analysis": {
        "template": """
Perform DCF analysis for {company_name} ({ticker}) based on the following financial data:

Revenue: {revenue}
Growth Rate: {growth_rate}
WACC: {wacc}
Terminal Growth Rate: {terminal_growth_rate}

Please provide:
1. Discounted cash flow calculation
2. Enterprise value estimation
3. Equity value per share
4. Investment recommendation (Buy/Hold/Sell)
5. Key risks and assumptions
""",
        "variables": [
            "company_name",
            "ticker",
            "revenue",
            "growth_rate",
            "wacc",
            "terminal_growth_rate",
        ],
    },
    "financial_summary": {
        "template": """
Generate a financial summary for {company_name} ({ticker}):

Key Metrics:
- Market Cap: {market_cap}
- P/E Ratio: {pe_ratio}
- Revenue: {revenue}
- Net Income: {net_income}

Please provide:
1. Financial strength assessment
2. Competitive position analysis
3. Growth prospects
4. Risk factors
""",
        "variables": ["company_name", "ticker", "market_cap", "pe_ratio", "revenue", "net_income"],
    },
    "sec_filing_analysis": {
        "template": """
Analyze the following SEC filing excerpt for {company_name} ({ticker}):

Filing Type: {filing_type}
Filing Date: {filing_date}
Content: {content}

Please extract:
1. Key financial metrics
2. Business developments
3. Risk factors
4. Forward-looking statements
5. Material changes
""",
        "variables": ["company_name", "ticker", "filing_type", "filing_date", "content"],
    },
}


# Global template manager instance
template_manager = TemplateManager()

# Load default templates
for name, config in DEFAULT_TEMPLATES.items():
    template_manager.register_template(name, config["template"], config["variables"])


def get_template(name: str) -> str:
    """Get a template by name."""
    return template_manager.templates[name]["template"]


def render_template(name: str, **kwargs) -> str:
    """Render a template with variables."""
    return template_manager.render_template(name, **kwargs)


def list_templates() -> List[str]:
    """List all available templates."""
    return list(template_manager.templates.keys())
