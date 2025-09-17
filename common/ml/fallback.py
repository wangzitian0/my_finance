#!/usr/bin/env python3
"""
ML Fallback Implementation
Moved from utils/ml_fallback.py → ml/fallback.py (Issue #284)

Provides fallback implementations for ML functionality when containers are not available.
"""

import hashlib
import logging
from typing import Any, Dict, List, Optional

# Import existing functionality from utils with error handling
try:
    from ..utils.ml_fallback import (
        NUMPY_AVAILABLE,
        FallbackEmbeddings,
        MLService,
        calculate_similarity,
        encode_texts,
        get_ml_service,
    )
except ImportError:
    # Fallback definitions if utils.ml_fallback is not available
    import hashlib
    from typing import Any, Dict, List, Optional

    NUMPY_AVAILABLE = False

    class FallbackEmbeddings:
        def __init__(self, dimension: int = 384):
            self.dimension = dimension

    class MLService:
        def __init__(self):
            pass

    def calculate_similarity(text1: str, text2: str) -> float:
        return 0.5

    def encode_texts(texts: List[str]):
        return []

    def get_ml_service():
        return MLService()


logger = logging.getLogger(__name__)


class FallbackRetrieval:
    """Simple fallback for document retrieval using text similarity"""

    def __init__(self, documents: Optional[List[str]] = None):
        self.documents = documents or []
        self.embeddings_service = get_ml_service()
        logger.warning("Using fallback retrieval - Vector DB not available")

    def add_documents(self, documents: List[str]):
        """Add documents to the retrieval index"""
        self.documents.extend(documents)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Simple retrieval using text similarity"""
        if not self.documents:
            return []

        # Calculate similarity for each document
        similarities = []
        for i, doc in enumerate(self.documents):
            similarity = calculate_similarity(query, doc)
            similarities.append({"doc_id": i, "text": doc, "score": similarity})

        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x["score"], reverse=True)
        return similarities[:top_k]

    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Alias for search method for compatibility"""
        return self.search(query, top_k)


class FallbackLLM:
    """Simple fallback for LLM functionality using template-based responses"""

    def __init__(self, model_name: str = "fallback"):
        self.model_name = model_name
        self.template_responses = {
            "financial_analysis": self._generate_financial_template,
            "dcf_valuation": self._generate_dcf_template,
            "investment_recommendation": self._generate_investment_template,
            "default": self._generate_default_template,
        }
        logger.warning(f"Using fallback LLM: {model_name} - Real LLM not available")

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using template-based fallback"""
        # Detect prompt type based on keywords
        prompt_lower = prompt.lower()

        if any(keyword in prompt_lower for keyword in ["dcf", "valuation", "intrinsic value"]):
            return self.template_responses["dcf_valuation"](prompt, **kwargs)
        elif any(
            keyword in prompt_lower for keyword in ["financial analysis", "earnings", "revenue"]
        ):
            return self.template_responses["financial_analysis"](prompt, **kwargs)
        elif any(keyword in prompt_lower for keyword in ["recommendation", "buy", "sell", "hold"]):
            return self.template_responses["investment_recommendation"](prompt, **kwargs)
        else:
            return self.template_responses["default"](prompt, **kwargs)

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat interface using the last user message"""
        if not messages:
            return "No messages provided."

        last_message = messages[-1].get("content", "")
        return self.generate(last_message, **kwargs)

    def _generate_financial_template(self, prompt: str, **kwargs) -> str:
        """Generate template response for financial analysis"""
        return f"""
FALLBACK FINANCIAL ANALYSIS

Note: This is a simplified template response. Real LLM services are not available.

Based on the provided information, here's a basic analysis:

1. Revenue Trends: Analysis would require current financial data
2. Profitability: Margins and efficiency metrics need evaluation
3. Cash Flow: Operating cash flow stability assessment needed
4. Balance Sheet: Asset quality and debt levels review required

For accurate analysis, please ensure:
- Current financial statements are available
- LLM services are properly configured
- Vector database contains relevant SEC filings

Generated at: {logger.name}
Model: {self.model_name} (Fallback)
"""

    def _generate_dcf_template(self, prompt: str, **kwargs) -> str:
        """Generate template response for DCF valuation"""
        return f"""
FALLBACK DCF VALUATION

Note: This is a simplified template response. Real LLM services are not available.

DCF Valuation Framework:
1. Revenue Projections: 5-year growth estimates needed
2. Operating Margins: Historical trend analysis required
3. Capital Expenditures: Maintenance vs. growth capex
4. Working Capital: Changes in NWC projections
5. Discount Rate: WACC calculation based on current rates
6. Terminal Value: Sustainable growth rate estimation

Key Assumptions (Template):
- Revenue Growth: [Data needed]
- EBITDA Margin: [Data needed]
- Tax Rate: [Data needed]
- WACC: [Data needed]

For accurate DCF analysis, please ensure:
- Historical financial data is processed
- Market data is current
- LLM services are available for detailed analysis

Generated at: {logger.name}
Model: {self.model_name} (Fallback)
"""

    def _generate_investment_template(self, prompt: str, **kwargs) -> str:
        """Generate template response for investment recommendations"""
        return f"""
FALLBACK INVESTMENT RECOMMENDATION

Note: This is a simplified template response. Real LLM services are not available.

Investment Analysis Framework:
1. Valuation: Compare current price to intrinsic value
2. Growth Prospects: Revenue and earnings growth potential
3. Competitive Position: Market share and moat analysis
4. Financial Health: Balance sheet strength and liquidity
5. Management Quality: Capital allocation and execution
6. Risk Factors: Industry, company, and market risks

Recommendation Process:
- Strong Buy: Significant undervaluation + strong fundamentals
- Buy: Moderate undervaluation + good prospects
- Hold: Fair value + stable outlook
- Sell: Overvaluation or deteriorating fundamentals

For detailed recommendations, please ensure:
- Complete financial data analysis
- Current market conditions assessment
- LLM services configured for nuanced analysis

Generated at: {logger.name}
Model: {self.model_name} (Fallback)
"""

    def _generate_default_template(self, prompt: str, **kwargs) -> str:
        """Generate default template response"""
        return f"""
FALLBACK LLM RESPONSE

Note: This is a simplified template response. Real LLM services are not available.

Your query: {prompt[:100]}...

This is a fallback response. For proper analysis, please:
1. Configure LLM services (DeepSeek, OpenAI, etc.)
2. Ensure vector database is available
3. Verify all required data sources are connected

The system will automatically use real LLM services when available.

Generated at: {logger.name}
Model: {self.model_name} (Fallback)
"""


# Re-export all functionality for the new ml module structure
__all__ = [
    "FallbackEmbeddings",
    "FallbackRetrieval",
    "FallbackLLM",
    "NUMPY_AVAILABLE",
    "MLService",
    "get_ml_service",
    "encode_texts",
    "calculate_similarity",
]

# Make sure functions are available even if original import failed
if "MLService" not in globals():

    class MLService:
        def __init__(self):
            pass


if "get_ml_service" not in globals():

    def get_ml_service():
        return MLService()


if "encode_texts" not in globals():

    def encode_texts(texts):
        return []


if "calculate_similarity" not in globals():

    def calculate_similarity(text1, text2):
        return 0.5
