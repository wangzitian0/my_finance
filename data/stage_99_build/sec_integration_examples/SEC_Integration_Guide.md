# SEC Integration Guide for DCF Reports

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
