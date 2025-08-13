# SEC Recall Usage Guide for DCF Reports

This guide demonstrates how to effectively use SEC filing recall in DCF valuation analysis.

## Overview

SEC recall refers to the process of retrieving and citing specific information from SEC filings to support DCF valuation assumptions. This approach provides:

1. **Regulatory Backing**: All assumptions are grounded in official company disclosures
2. **Transparency**: Clear citation trail for all valuation inputs
3. **Accuracy**: Data comes from audited financial statements
4. **Compliance**: Meets investment research standards for source documentation

## Complete Workflow

### Step 1: Query Formulation
Create DCF-specific search queries that target relevant financial information:

```python
dcf_queries = [
    {
        'query': 'AAPL revenue growth outlook guidance',
        'dcf_purpose': 'Revenue Growth Projections',
        'target_sections': ['MD&A', 'Business Outlook']
    },
    {
        'query': 'AAPL free cash flow capital expenditures',
        'dcf_purpose': 'Free Cash Flow Modeling', 
        'target_sections': ['Cash Flow Statement', 'CapEx Discussion']
    }
]
```

### Step 2: Semantic Search Execution
Execute semantic search against SEC filing corpus:

```python
from ETL.semantic_retrieval import SemanticRetriever

retriever = SemanticRetriever(embeddings_path)
results = []

for query_info in dcf_queries:
    search_results = retriever.retrieve_relevant_content(
        query=query_info['query'],
        top_k=5,
        min_similarity=0.75,
        content_filter={'ticker': 'AAPL', 'document_type': ['sec_10k', 'sec_10q']}
    )
    results.extend(search_results)
```

### Step 3: Result Ranking and Filtering
Rank results by DCF relevance:

```python
def calculate_dcf_relevance_score(result, dcf_purpose):
    base_score = result.similarity_score
    
    # Component-specific weights
    weights = {
        'Revenue Growth Projections': 1.2,
        'Free Cash Flow Modeling': 1.3,
        'Risk Assessment': 1.0
    }
    
    # Document type preferences
    doc_weights = {'10-K': 1.1, '10-Q': 1.0, '8-K': 0.9}
    
    return base_score * weights[dcf_purpose] * doc_weights[result.doc_type]
```

### Step 4: Insight Extraction
Extract actionable DCF insights:

```python
def extract_dcf_insights(ranked_results):
    insights = {
        'revenue_projections': [],
        'cash_flow_modeling': [],
        'risk_assessment': []
    }
    
    for result in ranked_results[:10]:  # Top 10 results
        insight = {
            'content': result.content,
            'citation': f"{result.source_document} ({result.filing_date})",
            'dcf_application': generate_dcf_application(result),
            'quantitative_data': extract_numbers(result.content),
            'confidence_score': result.dcf_relevance_score
        }
        
        # Map to appropriate DCF component
        component = map_to_dcf_component(result.dcf_purpose)
        insights[component].append(insight)
    
    return insights
```

### Step 5: Citation Management
Maintain proper citations throughout the analysis:

```python
def create_citation_index(insights):
    citations = {}
    citation_counter = 1
    
    for component, component_insights in insights.items():
        for insight in component_insights:
            source = insight['citation']
            if source not in citations:
                citations[source] = f"[{citation_counter}]"
                citation_counter += 1
    
    return citations
```

### Step 6: DCF Integration
Integrate SEC insights into DCF model:

```python
def integrate_sec_data_into_dcf(insights, citations):
    dcf_assumptions = {}
    
    # Revenue projections
    if insights['revenue_projections']:
        revenue_data = insights['revenue_projections'][0]
        dcf_assumptions['revenue_growth'] = {
            'assumption': '6-8% annual growth',
            'source': revenue_data['citation'],
            'rationale': revenue_data['dcf_application'],
            'citation_ref': citations[revenue_data['citation']]
        }
    
    # Cash flow modeling
    if insights['cash_flow_modeling']:
        cf_data = insights['cash_flow_modeling'][0]
        dcf_assumptions['fcf_margin'] = {
            'assumption': '24-26% of revenue',
            'source': cf_data['citation'],
            'rationale': cf_data['dcf_application'],
            'citation_ref': citations[cf_data['citation']]
        }
    
    return dcf_assumptions
```

## Best Practices

### 1. Query Design
- **Be Specific**: Target exact DCF components (revenue growth, not just revenue)
- **Use Company Context**: Include ticker symbol for precise results
- **Multiple Angles**: Create several queries per DCF component

### 2. Result Selection
- **Prioritize Recent Filings**: 10-K > 10-Q > 8-K for comprehensiveness
- **Check Filing Dates**: Ensure data is current and relevant
- **Verify Content Quality**: Review extracted content for completeness

### 3. Citation Standards
- **Document Source**: Always include filing type and date
- **Section Reference**: Specify the relevant section when possible
- **Maintain Index**: Keep consistent citation numbering

### 4. Assumption Validation
- **Cross-Reference**: Verify assumptions across multiple filings
- **Consistency Check**: Ensure data consistency across time periods
- **Confidence Assessment**: Rate confidence based on data quality

## Example Implementation

### Complete DCF Component Analysis

```python
def create_sec_backed_dcf_component(ticker, component_name, sec_insights):
    """Create a complete DCF component with SEC backing."""
    
    return {
        'component': component_name,
        'ticker': ticker,
        'assumptions': extract_assumptions(sec_insights),
        'supporting_evidence': [
            {
                'insight': insight['content'][:200] + '...',
                'source': insight['citation'],
                'relevance': insight['dcf_application']
            }
            for insight in sec_insights[:3]  # Top 3 insights
        ],
        'confidence_level': assess_confidence(sec_insights),
        'methodology_note': f'Assumptions derived from SEC filing analysis using semantic recall'
    }
```

### Final Report Generation

```python
def generate_sec_enhanced_dcf_report(ticker, dcf_components, citations):
    """Generate complete DCF report with SEC citations."""
    
    report = f"""
# SEC Filing-Enhanced DCF Analysis: {ticker}

## Executive Summary
This DCF valuation incorporates insights from {len(citations)} SEC filings to ensure 
all assumptions are backed by official company disclosures.

## DCF Components

### Revenue Projections
{dcf_components['revenue']['assumptions']}
Source: {dcf_components['revenue']['supporting_evidence'][0]['source']}

### Free Cash Flow Modeling  
{dcf_components['cash_flow']['assumptions']}
Source: {dcf_components['cash_flow']['supporting_evidence'][0]['source']}

## Citations
"""
    
    for i, (source, ref) in enumerate(citations.items(), 1):
        report += f"\n{ref} {source}"
    
    report += "\n\n*All data sourced from official SEC filings*"
    
    return report
```

## Quality Assurance

### 1. Data Validation
- Verify numerical data against original filings
- Check for data consistency across periods
- Validate calculation methodologies

### 2. Citation Accuracy
- Ensure all citations are complete and accurate
- Verify filing dates and document types
- Check section references when available

### 3. Assumption Reasonableness
- Compare assumptions to industry benchmarks
- Validate against historical company performance
- Assess consistency with management guidance

## Troubleshooting

### Common Issues

1. **No Results Found**
   - Broaden search terms
   - Check ticker symbol accuracy
   - Verify SEC data availability

2. **Low Relevance Scores**
   - Refine query specificity
   - Adjust similarity thresholds
   - Review DCF component mapping

3. **Missing Quantitative Data**
   - Target financial statement sections
   - Use multiple queries per component
   - Supplement with MD&A sections

4. **Citation Formatting Issues**
   - Standardize citation format
   - Include all required elements
   - Maintain consistent numbering

---

**Issue #75 Requirement 6**: ✅ Example template showing SEC recall usage completed.
