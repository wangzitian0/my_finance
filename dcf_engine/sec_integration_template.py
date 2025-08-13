#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEC Integration Template for DCF Reports

This template demonstrates how to properly integrate SEC filing data
into DCF valuation reports using the Graph RAG system.

Issue #75 requirement 4: Create SEC integration template for DCF reports
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class SECIntegrationTemplate:
    """
    Template class showing how to integrate SEC filing data into DCF reports.
    
    This class demonstrates:
    1. How to retrieve SEC documents for a ticker
    2. How to extract relevant financial information
    3. How to structure SEC data for DCF analysis
    4. How to create citations and references
    """
    
    def __init__(self):
        """Initialize the SEC integration template."""
        # Set data directory directly
        self.data_dir = Path("data/stage_00_original")
        
        logger.info("📋 SEC Integration Template initialized")
    
    def find_sec_documents(self, ticker: str) -> Dict[str, List[Path]]:
        """
        Find available SEC documents for a ticker.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            Dictionary mapping document types to file paths
        """
        logger.info(f"🔍 Finding SEC documents for {ticker}")
        
        sec_documents = {
            '10k': [],
            '10q': [],
            '8k': [],
            'other': []
        }
        
        # Look in SEC Edgar data directory (stage_01_extract)
        sec_dir = Path("data/stage_01_extract/sec_edgar")
        if not sec_dir.exists():
            logger.warning(f"SEC directory not found: {sec_dir}")
            return sec_documents
        
        # Find ticker directory in most recent partition
        ticker_dirs = []
        for partition_dir in sorted(sec_dir.iterdir(), reverse=True):
            if partition_dir.is_dir() and partition_dir.name.isdigit():
                ticker_dir = partition_dir / ticker.upper()
                if ticker_dir.exists():
                    ticker_dirs.append(ticker_dir)
                    break  # Use most recent partition
        
        if not ticker_dirs:
            logger.warning(f"No SEC data found for ticker {ticker}")
            return sec_documents
        
        # Categorize documents by type
        ticker_dir = ticker_dirs[0]
        for sec_file in ticker_dir.glob("*_sec_edgar_*.txt"):
            filename = sec_file.name.lower()
            
            if '_10k_' in filename:
                sec_documents['10k'].append(sec_file)
            elif '_10q_' in filename:
                sec_documents['10q'].append(sec_file)
            elif '_8k_' in filename:
                sec_documents['8k'].append(sec_file)
            else:
                sec_documents['other'].append(sec_file)
        
        # Log findings
        total_docs = sum(len(docs) for docs in sec_documents.values())
        logger.info(f"📄 Found {total_docs} SEC documents for {ticker}:")
        for doc_type, docs in sec_documents.items():
            if docs:
                logger.info(f"   - {doc_type.upper()}: {len(docs)} documents")
        
        return sec_documents
    
    def extract_sec_snippets(self, ticker: str, max_snippets: int = 5) -> List[Dict[str, Any]]:
        """
        Extract relevant snippets from SEC documents for DCF analysis.
        
        Args:
            ticker: Stock ticker symbol
            max_snippets: Maximum number of snippets to extract
            
        Returns:
            List of SEC document snippets with metadata
        """
        logger.info(f"📝 Extracting SEC snippets for {ticker}")
        
        sec_documents = self.find_sec_documents(ticker)
        snippets = []
        
        # Priority order for DCF analysis
        priority_order = ['10k', '10q', '8k', 'other']
        
        for doc_type in priority_order:
            if len(snippets) >= max_snippets:
                break
                
            for doc_path in sec_documents[doc_type]:
                if len(snippets) >= max_snippets:
                    break
                
                try:
                    # Read document content
                    with open(doc_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Extract relevant sections for DCF
                    dcf_relevant_snippet = self._extract_dcf_relevant_content(
                        content, doc_path, doc_type
                    )
                    
                    if dcf_relevant_snippet:
                        snippets.append(dcf_relevant_snippet)
                        logger.info(f"   ✅ Extracted snippet from {doc_path.name}")
                    
                except Exception as e:
                    logger.error(f"   ❌ Error reading {doc_path}: {e}")
                    continue
        
        logger.info(f"📄 Successfully extracted {len(snippets)} SEC snippets")
        return snippets
    
    def _extract_dcf_relevant_content(
        self, 
        content: str, 
        doc_path: Path, 
        doc_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extract DCF-relevant content from a SEC document.
        
        Args:
            content: Full document content
            doc_path: Path to the document
            doc_type: Type of SEC document (10k, 10q, 8k)
            
        Returns:
            Dictionary with extracted content and metadata
        """
        # Look for sections relevant to DCF analysis
        dcf_keywords = [
            # Revenue and growth indicators
            'revenue', 'net sales', 'total revenue', 'revenue growth',
            'sales growth', 'organic growth', 'recurring revenue',
            
            # Cash flow indicators
            'cash flow', 'free cash flow', 'operating cash flow', 
            'cash from operations', 'capital expenditures', 'capex',
            
            # Profitability indicators
            'operating income', 'operating margin', 'ebitda', 
            'net income', 'profit margin', 'gross margin',
            
            # Future outlook
            'outlook', 'guidance', 'forecast', 'expected', 'projected',
            'future', 'strategy', 'investment', 'expansion',
            
            # Risk factors
            'risk factors', 'risks', 'uncertainty', 'competition',
            'regulatory', 'market conditions'
        ]
        
        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Find paragraphs containing DCF-relevant keywords
        relevant_paragraphs = []
        for paragraph in paragraphs:
            paragraph_lower = paragraph.lower()
            
            # Check if paragraph contains relevant keywords
            keyword_matches = []
            for keyword in dcf_keywords:
                if keyword in paragraph_lower:
                    keyword_matches.append(keyword)
            
            # Include paragraph if it has multiple keywords or is substantial
            if len(keyword_matches) >= 2 or (len(keyword_matches) >= 1 and len(paragraph) > 200):
                relevant_paragraphs.append({
                    'content': paragraph,
                    'keywords': keyword_matches,
                    'relevance_score': len(keyword_matches)
                })
        
        if not relevant_paragraphs:
            return None
        
        # Take the most relevant paragraph
        best_paragraph = max(relevant_paragraphs, key=lambda x: x['relevance_score'])
        
        # Create snippet with metadata
        snippet = {
            'content': best_paragraph['content'][:1500],  # Limit content length
            'source_document': doc_path.name,
            'document_type': f'sec_{doc_type}',
            'keywords_matched': best_paragraph['keywords'],
            'relevance_score': best_paragraph['relevance_score'],
            'filing_date': self._extract_filing_date(doc_path.name),
            'dcf_relevance': self._determine_dcf_relevance(best_paragraph['keywords']),
            'citation': f"Source: {doc_path.name} - SEC {doc_type.upper()} Filing",
            'metadata': {
                'file_path': str(doc_path),
                'extraction_date': datetime.now().isoformat(),
                'content_length': len(best_paragraph['content'])
            }
        }
        
        return snippet
    
    def _extract_filing_date(self, filename: str) -> str:
        """Extract filing date from SEC filename if available."""
        # SEC filenames often contain dates like: AAPL_sec_edgar_10k_20231002.txt
        parts = filename.split('_')
        for part in parts:
            if part.isdigit() and len(part) == 8:  # YYYYMMDD format
                try:
                    date_obj = datetime.strptime(part, '%Y%m%d')
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        return 'Unknown'
    
    def _determine_dcf_relevance(self, keywords: List[str]) -> str:
        """Determine how the content is relevant to DCF analysis."""
        revenue_keywords = {'revenue', 'sales', 'growth'}
        cash_flow_keywords = {'cash flow', 'free cash flow', 'capex', 'capital expenditures'}
        profitability_keywords = {'margin', 'profit', 'income', 'ebitda'}
        outlook_keywords = {'outlook', 'guidance', 'forecast', 'future', 'strategy'}
        risk_keywords = {'risk', 'uncertainty', 'competition', 'regulatory'}
        
        keyword_set = set(keywords)
        
        relevance_areas = []
        
        if keyword_set & revenue_keywords:
            relevance_areas.append("Revenue Growth Analysis")
        if keyword_set & cash_flow_keywords:
            relevance_areas.append("Cash Flow Projections")
        if keyword_set & profitability_keywords:
            relevance_areas.append("Profitability Assessment")
        if keyword_set & outlook_keywords:
            relevance_areas.append("Forward-Looking Guidance")
        if keyword_set & risk_keywords:
            relevance_areas.append("Risk Factor Analysis")
        
        if relevance_areas:
            return f"DCF Input for: {', '.join(relevance_areas)}"
        else:
            return "General Business Context"
    
    def create_sec_enhanced_dcf_context(self, ticker: str) -> Dict[str, Any]:
        """
        Create a complete SEC-enhanced context for DCF analysis.
        
        This is the main method that demonstrates how to integrate SEC data
        into a DCF report template.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Complete context dictionary for DCF analysis
        """
        logger.info(f"🎯 Creating SEC-enhanced DCF context for {ticker}")
        
        # Extract SEC snippets
        sec_snippets = self.extract_sec_snippets(ticker, max_snippets=10)
        
        # Organize snippets by DCF component
        dcf_context = {
            'ticker': ticker.upper(),
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'sec_data_available': len(sec_snippets) > 0,
            'total_sec_documents': len(sec_snippets),
            'dcf_components': {
                'revenue_growth': [],
                'cash_flow_analysis': [],
                'profitability_trends': [],
                'forward_guidance': [],
                'risk_factors': [],
                'general_business': []
            },
            'citations': [],
            'methodology_note': (
                "This DCF analysis incorporates data from SEC filings to provide "
                "regulatory-backed financial insights and forward-looking guidance."
            )
        }
        
        # Categorize snippets by DCF component
        for snippet in sec_snippets:
            dcf_relevance = snippet.get('dcf_relevance', '')
            citation = snippet.get('citation', '')
            
            # Add to citations
            if citation not in dcf_context['citations']:
                dcf_context['citations'].append(citation)
            
            # Categorize by DCF component
            keywords = set(snippet.get('keywords_matched', []))
            
            if any(kw in keywords for kw in ['revenue', 'sales', 'growth']):
                dcf_context['dcf_components']['revenue_growth'].append(snippet)
            elif any(kw in keywords for kw in ['cash flow', 'free cash flow', 'capex']):
                dcf_context['dcf_components']['cash_flow_analysis'].append(snippet)
            elif any(kw in keywords for kw in ['margin', 'profit', 'income', 'ebitda']):
                dcf_context['dcf_components']['profitability_trends'].append(snippet)
            elif any(kw in keywords for kw in ['outlook', 'guidance', 'forecast', 'future']):
                dcf_context['dcf_components']['forward_guidance'].append(snippet)
            elif any(kw in keywords for kw in ['risk', 'uncertainty', 'competition']):
                dcf_context['dcf_components']['risk_factors'].append(snippet)
            else:
                dcf_context['dcf_components']['general_business'].append(snippet)
        
        # Add summary statistics
        dcf_context['summary'] = {
            'revenue_insights': len(dcf_context['dcf_components']['revenue_growth']),
            'cash_flow_insights': len(dcf_context['dcf_components']['cash_flow_analysis']),
            'profitability_insights': len(dcf_context['dcf_components']['profitability_trends']),
            'guidance_insights': len(dcf_context['dcf_components']['forward_guidance']),
            'risk_insights': len(dcf_context['dcf_components']['risk_factors']),
            'total_citations': len(dcf_context['citations'])
        }
        
        logger.info(f"📊 SEC context created with {len(sec_snippets)} insights:")
        for component, data in dcf_context['dcf_components'].items():
            if data:
                logger.info(f"   - {component}: {len(data)} insights")
        
        return dcf_context
    
    def generate_sec_enhanced_dcf_prompt(self, ticker: str) -> str:
        """
        Generate an LLM prompt that incorporates SEC data for DCF analysis.
        
        This demonstrates how to structure SEC data for LLM consumption
        in DCF valuation.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Formatted prompt string for LLM DCF analysis
        """
        logger.info(f"📝 Generating SEC-enhanced DCF prompt for {ticker}")
        
        # Get SEC context
        sec_context = self.create_sec_enhanced_dcf_context(ticker)
        
        # Build prompt sections
        prompt_sections = []
        
        # Header
        prompt_sections.append(f"""DCF Valuation Analysis for {ticker} - SEC Filing Enhanced

**Data Sources**: 
- SEC Filings: {sec_context['total_sec_documents']} documents analyzed
- Filing Citations: {len(sec_context['citations'])} sources
- Analysis Date: {sec_context['analysis_date']}

**SEC Data Integration**: This analysis incorporates actual SEC filing data to provide regulatory-backed insights for DCF valuation.

""")
        
        # Revenue Growth Section
        if sec_context['dcf_components']['revenue_growth']:
            prompt_sections.append("## 📈 Revenue Growth Analysis (SEC Filing Insights)\n")
            for i, insight in enumerate(sec_context['dcf_components']['revenue_growth'][:2], 1):
                prompt_sections.append(f"**SEC Insight {i} - {insight['citation']}**:")
                prompt_sections.append(f"```")
                prompt_sections.append(insight['content'][:500] + "...")
                prompt_sections.append(f"```")
                prompt_sections.append(f"*Filing Date: {insight['filing_date']} | Relevance: {insight['dcf_relevance']}*\n")
        
        # Cash Flow Section
        if sec_context['dcf_components']['cash_flow_analysis']:
            prompt_sections.append("## 💰 Cash Flow Analysis (SEC Filing Insights)\n")
            for i, insight in enumerate(sec_context['dcf_components']['cash_flow_analysis'][:2], 1):
                prompt_sections.append(f"**SEC Insight {i} - {insight['citation']}**:")
                prompt_sections.append(f"```")
                prompt_sections.append(insight['content'][:500] + "...")
                prompt_sections.append(f"```")
                prompt_sections.append(f"*Filing Date: {insight['filing_date']} | Relevance: {insight['dcf_relevance']}*\n")
        
        # Forward Guidance Section
        if sec_context['dcf_components']['forward_guidance']:
            prompt_sections.append("## 🔮 Management Guidance (SEC Filing Insights)\n")
            for i, insight in enumerate(sec_context['dcf_components']['forward_guidance'][:2], 1):
                prompt_sections.append(f"**SEC Insight {i} - {insight['citation']}**:")
                prompt_sections.append(f"```")
                prompt_sections.append(insight['content'][:500] + "...")
                prompt_sections.append(f"```")
                prompt_sections.append(f"*Filing Date: {insight['filing_date']} | Relevance: {insight['dcf_relevance']}*\n")
        
        # Risk Factors Section
        if sec_context['dcf_components']['risk_factors']:
            prompt_sections.append("## ⚠️ Risk Factors (SEC Filing Insights)\n")
            for i, insight in enumerate(sec_context['dcf_components']['risk_factors'][:2], 1):
                prompt_sections.append(f"**SEC Insight {i} - {insight['citation']}**:")
                prompt_sections.append(f"```")
                prompt_sections.append(insight['content'][:300] + "...")
                prompt_sections.append(f"```")
                prompt_sections.append(f"*Filing Date: {insight['filing_date']} | Relevance: {insight['dcf_relevance']}*\n")
        
        # DCF Analysis Request
        prompt_sections.append("""## 🎯 DCF Analysis Request

Based on the SEC filing insights provided above, please conduct a comprehensive DCF valuation analysis for {ticker}:

**Required Analysis Components:**

1. **Revenue Projections** (5-year forecast)
   - Use SEC filing revenue data and management guidance
   - Consider business segment growth rates mentioned in filings
   - Factor in competitive and regulatory insights from risk factors

2. **Free Cash Flow Projections**
   - Base projections on historical cash flow patterns from SEC data
   - Incorporate CapEx guidance from management discussions
   - Consider working capital trends mentioned in filings

3. **Terminal Value Calculation**
   - Use long-term growth assumptions supported by SEC strategic outlook
   - Consider industry maturity factors mentioned in risk sections

4. **Discount Rate (WACC)**
   - Factor in business risks identified in SEC filings
   - Consider regulatory and competitive risks for risk premium adjustment

5. **Valuation Summary**
   - Present intrinsic value per share with SEC data backing
   - Include sensitivity analysis based on SEC-identified risk factors
   - Provide BUY/HOLD/SELL recommendation with SEC filing support

**Citation Requirements**: Please reference specific SEC filing insights in your analysis and explain how each piece of data influences your valuation assumptions.

**Methodology Note**: {methodology_note}
""".format(ticker=ticker, methodology_note=sec_context['methodology_note']))
        
        # Citations section
        if sec_context['citations']:
            prompt_sections.append("## 📚 SEC Filing Sources\n")
            for i, citation in enumerate(sec_context['citations'], 1):
                prompt_sections.append(f"{i}. {citation}")
        
        return "\n".join(prompt_sections)
    
    def save_template_examples(self, ticker: str = "AAPL") -> Dict[str, str]:
        """
        Save template examples to demonstrate SEC integration.
        
        Args:
            ticker: Ticker to use for examples (default: AAPL)
            
        Returns:
            Dictionary of saved file paths
        """
        logger.info(f"💾 Saving SEC integration template examples for {ticker}")
        
        # Create examples directory
        examples_dir = Path("data/stage_99_build") / "sec_integration_examples"
        examples_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = {}
        
        try:
            # 1. Save SEC context example
            sec_context = self.create_sec_enhanced_dcf_context(ticker)
            context_file = examples_dir / f"sec_context_example_{ticker}.json"
            with open(context_file, 'w', encoding='utf-8') as f:
                json.dump(sec_context, f, indent=2, ensure_ascii=False)
            saved_files['sec_context'] = str(context_file)
            
            # 2. Save LLM prompt example
            llm_prompt = self.generate_sec_enhanced_dcf_prompt(ticker)
            prompt_file = examples_dir / f"sec_enhanced_dcf_prompt_{ticker}.md"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(llm_prompt)
            saved_files['llm_prompt'] = str(prompt_file)
            
            # 3. Save integration guide
            guide_content = self._create_integration_guide()
            guide_file = examples_dir / "SEC_Integration_Guide.md"
            with open(guide_file, 'w', encoding='utf-8') as f:
                f.write(guide_content)
            saved_files['integration_guide'] = str(guide_file)
            
            logger.info(f"✅ Template examples saved:")
            for example_type, file_path in saved_files.items():
                logger.info(f"   - {example_type}: {file_path}")
            
        except Exception as e:
            logger.error(f"❌ Error saving template examples: {e}")
        
        return saved_files
    
    def _create_integration_guide(self) -> str:
        """Create a comprehensive integration guide."""
        return """# SEC Integration Guide for DCF Reports

This guide explains how to integrate SEC filing data into DCF valuation reports using the Graph RAG system.

## Overview

The SEC Integration Template provides a standardized way to:
1. Extract relevant SEC filing data for DCF analysis
2. Structure the data for LLM consumption
3. Create properly cited DCF reports with regulatory backing

## Key Components

### 1. Document Discovery
- **Method**: `find_sec_documents(ticker)`
- **Purpose**: Locate all available SEC documents for a ticker
- **Output**: Categorized list of 10-K, 10-Q, 8-K, and other filings

### 2. Content Extraction
- **Method**: `extract_sec_snippets(ticker, max_snippets)`
- **Purpose**: Extract DCF-relevant content from SEC documents
- **Filtering**: Uses keyword matching for revenue, cash flow, profitability, guidance, and risk factors

### 3. DCF Context Creation
- **Method**: `create_sec_enhanced_dcf_context(ticker)`
- **Purpose**: Organize SEC data by DCF analysis components
- **Components**:
  - Revenue Growth Analysis
  - Cash Flow Analysis  
  - Profitability Trends
  - Forward Guidance
  - Risk Factors

### 4. LLM Prompt Generation
- **Method**: `generate_sec_enhanced_dcf_prompt(ticker)`
- **Purpose**: Create structured prompts that incorporate SEC data
- **Features**: Proper citations, relevance scoring, content organization

## Usage Examples

### Basic SEC Data Extraction
```python
from dcf_engine.sec_integration_template import SECIntegrationTemplate

# Initialize template
sec_template = SECIntegrationTemplate()

# Find available documents
sec_docs = sec_template.find_sec_documents("AAPL")
print(f"Found {sum(len(docs) for docs in sec_docs.values())} SEC documents")

# Extract relevant snippets
snippets = sec_template.extract_sec_snippets("AAPL", max_snippets=5)
for snippet in snippets:
    print(f"- {snippet['citation']}: {snippet['dcf_relevance']}")
```

### Complete DCF Context Creation
```python
# Create comprehensive SEC-enhanced context
dcf_context = sec_template.create_sec_enhanced_dcf_context("AAPL")

# Access organized data
revenue_insights = dcf_context['dcf_components']['revenue_growth']
cash_flow_insights = dcf_context['dcf_components']['cash_flow_analysis']
guidance_insights = dcf_context['dcf_components']['forward_guidance']
```

### LLM-Ready Prompt Generation
```python
# Generate structured prompt for LLM
llm_prompt = sec_template.generate_sec_enhanced_dcf_prompt("AAPL")

# The prompt includes:
# - Organized SEC filing excerpts
# - Proper citations and filing dates
# - DCF analysis instructions
# - Specific reference requirements
```

## Integration with Existing DCF Engine

To integrate with the existing LLM DCF Generator:

1. **Import the template**:
```python
from dcf_engine.sec_integration_template import SECIntegrationTemplate
```

2. **Modify `_retrieve_financial_context` method**:
```python
def _retrieve_financial_context(self, ticker: str, financial_data: Dict[str, Any]):
    # Use SEC template for enhanced context
    sec_template = SECIntegrationTemplate()
    sec_context = sec_template.create_sec_enhanced_dcf_context(ticker)
    
    # Convert to expected format
    return self._convert_sec_context_to_results(sec_context)
```

3. **Update prompt generation**:
```python
def generate_comprehensive_dcf_report(self, ticker: str, ...):
    # Get SEC-enhanced prompt
    sec_template = SECIntegrationTemplate()
    enhanced_prompt = sec_template.generate_sec_enhanced_dcf_prompt(ticker)
    
    # Use enhanced prompt for LLM generation
    dcf_result = self.ollama_client.generate_with_sec_context(enhanced_prompt)
```

## Data Quality and Validation

### Content Filtering
- **Keyword Matching**: Uses comprehensive DCF-relevant keyword lists
- **Relevance Scoring**: Prioritizes paragraphs with multiple keyword matches
- **Length Filtering**: Ensures substantial content (>200 characters)

### Citation Standards
- **Source Attribution**: Every snippet includes original document name
- **Filing Dates**: Extracted from filenames when available
- **Document Types**: Properly categorized (10-K, 10-Q, 8-K)

### Error Handling
- **File Access**: Graceful handling of unreadable files
- **Content Extraction**: UTF-8 encoding with error tolerance
- **Missing Data**: Fallback to available information

## Output Examples

### SEC Context Structure
```json
{
  "ticker": "AAPL",
  "analysis_date": "2025-08-13",
  "sec_data_available": true,
  "total_sec_documents": 8,
  "dcf_components": {
    "revenue_growth": [
      {
        "content": "Revenue increased 2.8% year over year...",
        "source_document": "AAPL_sec_edgar_10k_20231002.txt",
        "citation": "Source: AAPL_sec_edgar_10k_20231002.txt - SEC 10K Filing",
        "dcf_relevance": "DCF Input for: Revenue Growth Analysis"
      }
    ]
  },
  "citations": ["Source: AAPL_sec_edgar_10k_20231002.txt - SEC 10K Filing"]
}
```

### LLM Prompt Structure
```markdown
# DCF Valuation Analysis for AAPL - SEC Filing Enhanced

**Data Sources**: 
- SEC Filings: 8 documents analyzed
- Filing Citations: 3 sources

## 📈 Revenue Growth Analysis (SEC Filing Insights)

**SEC Insight 1 - Source: AAPL_sec_edgar_10k_20231002.txt - SEC 10K Filing**:
```
Revenue increased 2.8% year over year to $383.3 billion in fiscal 2023...
```
*Filing Date: 2023-10-02 | Relevance: DCF Input for: Revenue Growth Analysis*

## 🎯 DCF Analysis Request

Based on the SEC filing insights provided above, please conduct a comprehensive DCF valuation analysis...
```

## Best Practices

1. **Always cite sources**: Include document names and filing dates
2. **Limit content length**: Keep snippets under 1500 characters for LLM efficiency
3. **Prioritize relevance**: Use keyword matching and scoring for content selection
4. **Handle missing data**: Gracefully degrade when SEC data is unavailable
5. **Validate extractions**: Review extracted content for DCF relevance

## Files Generated

This template creates the following example files:
- `sec_context_example_AAPL.json`: Complete SEC context data structure
- `sec_enhanced_dcf_prompt_AAPL.md`: LLM-ready prompt with SEC integration
- `SEC_Integration_Guide.md`: This comprehensive guide

## Troubleshooting

### No SEC Documents Found
- Check that `data/stage_00_original/sec_edgar/` contains data
- Verify ticker format (uppercase)
- Ensure SEC data has been collected for the ticker

### Poor Content Extraction
- Review keyword lists in `_extract_dcf_relevant_content`
- Adjust relevance scoring thresholds
- Consider document quality and formatting

### LLM Integration Issues
- Verify prompt structure and length
- Check citation formatting
- Ensure proper JSON serialization for context data

---

**Issue #75 Requirement 4**: ✅ SEC integration template for DCF reports completed.
"""


def main():
    """Demonstrate the SEC integration template."""
    print("🧪 SEC Integration Template Demo")
    print("=" * 50)
    
    # Initialize template
    template = SECIntegrationTemplate()
    
    # Test with AAPL (Magnificent 7 company)
    ticker = "AAPL"
    
    try:
        # 1. Find SEC documents
        print(f"\n📋 Step 1: Finding SEC documents for {ticker}")
        sec_docs = template.find_sec_documents(ticker)
        
        # 2. Extract snippets
        print(f"\n📄 Step 2: Extracting SEC snippets")
        snippets = template.extract_sec_snippets(ticker, max_snippets=3)
        
        # 3. Create DCF context
        print(f"\n🎯 Step 3: Creating DCF context")
        dcf_context = template.create_sec_enhanced_dcf_context(ticker)
        
        # 4. Generate LLM prompt
        print(f"\n📝 Step 4: Generating LLM prompt")
        llm_prompt = template.generate_sec_enhanced_dcf_prompt(ticker)
        
        # 5. Save examples
        print(f"\n💾 Step 5: Saving template examples")
        saved_files = template.save_template_examples(ticker)
        
        print(f"\n✅ SEC integration template demo completed!")
        print(f"📁 Examples saved to: data/stage_99_build/sec_integration_examples/")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error in demo: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    main()