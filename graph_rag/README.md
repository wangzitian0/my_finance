# Graph RAG System for Financial Analysis

## Overview

This system implements a graph database-based Retrieval-Augmented Generation (Graph RAG) system specifically designed for financial analysis and investment decision support for M7 companies.

## Core Features

### 1. Semantic Embedding
- Generate document semantic vectors using Sentence Transformers
- Support chunked processing and embedding of SEC filings and news content
- Implement vector similarity computation and retrieval

### 2. Structured Query Generation
- Natural language question classification and intent recognition
- Automatic extraction of stock symbols and key entities
- Generate corresponding Cypher query statements

### 3. Semantic Retrieval
- Content retrieval based on vector similarity
- Intelligent ranking combining timeliness and relevance
- Support comprehensive retrieval across multiple document types

### 4. Intelligent Answer Generation
- Intent-based context-aware responses
- Support DCF valuation, risk analysis, comparative analysis and other scenarios
- Automatic generation of data source citations

### 5. Multi-step Reasoning
- Automatic decomposition of complex questions
- Multi-step reasoning chain execution
- Comprehensive analysis result synthesis

### 6. Data Ingestion Pipeline
- Automated ingestion of M7 company data
- Structured storage of Yahoo Finance and SEC data
- Batch generation and storage of semantic embeddings

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Question │ -> │  Query Generator │ -> │   Neo4j Graph   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         v                                              v
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Semantic Search │ <- │ Reasoning Engine │ <- │ Structured Data │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       
         v                       v                       
┌─────────────────┐    ┌─────────────────┐              
│ Relevant Content│ -> │ Answer Generator│              
└─────────────────┘    └─────────────────┘              
                                │                       
                                v                       
                       ┌─────────────────┐              
                       │   Final Answer  │              
                       └─────────────────┘              
```

## Supported Query Types

1. **DCF Valuation Queries**: "What is Apple's DCF valuation?"
2. **Financial Comparative Analysis**: "Compare Apple and Microsoft's financial performance"
3. **Risk Analysis**: "What are Tesla's main risk factors?"
4. **News Impact Analysis**: "How do recent news events affect Netflix stock price?"
5. **Industry Analysis**: "How does Meta perform compared to other tech companies?"
6. **Historical Trend Analysis**: "What is Google's revenue growth trend over the past 3 years?"
7. **Complex Reasoning**: "Should I invest in Amazon based on recent financial performance and market conditions?"

## Neo4j Data Model

### Core Node Types
- **Stock**: Basic stock information
- **SECFiling**: SEC documents (10-K, 10-Q, 8-K)
- **NewsEvent**: News events
- **DCFValuation**: DCF valuation data
- **FinancialMetrics**: Financial metrics
- **DocumentChunk**: Document chunks (for semantic retrieval)

### Relationship Types
- **HAS_FILING**: Stock -> SEC filing
- **MENTIONED_IN**: Stock -> News event
- **HAS_VALUATION**: Stock -> DCF valuation
- **HAS_METRIC**: Stock -> Financial metrics
- **IMPACTS**: News event -> DCF valuation
- **USES**: DCF valuation -> Financial metrics

## Usage

### Quick Start

```bash
# 1. Install dependencies
pixi run install-extras

# 2. Run system tests
p3 test f2  # Graph RAG included in standard testing

# 3. Run interactive demo
pixi run demo-graph-rag

# 4. Setup Graph RAG system
pixi run setup-graph-rag
```

### Programmatic Usage

```python
from graph_rag import GraphRAGSystem

# Initialize system
graph_rag = GraphRAGSystem()

# Answer questions
result = graph_rag.answer_question("What is Apple's DCF valuation?")
print(result['answer'])
```

### Data Ingestion

```python
from graph_rag.data_ingestion import GraphRAGDataIngestion
from graph_rag.semantic_embedding import SemanticEmbedding

# Initialize data ingestion pipeline
embedding = SemanticEmbedding()
ingestion = GraphRAGDataIngestion(embedding)

# Ingest M7 data
stats = ingestion.ingest_m7_data()
print(f"Processed {stats['companies_processed']} companies")
```

## Configuration Options

### Semantic Embedding Model
```python
# Default uses all-MiniLM-L6-v2
graph_rag = GraphRAGSystem(
    embedding_model='sentence-transformers/all-MiniLM-L6-v2'
)

# Or use other models
graph_rag = GraphRAGSystem(
    embedding_model='sentence-transformers/all-mpnet-base-v2'
)
```

### Retrieval Parameters
```python
# Adjust retrieval count and similarity threshold
semantic_content = retriever.retrieve_relevant_content(
    question="Your question",
    graph_data=data,
    top_k=10,           # Return top 10 relevant content
    min_similarity=0.3  # Minimum similarity threshold
)
```

## M7 Company Support

The system is specifically optimized for the following "Magnificent 7" companies:

- **Apple (AAPL)**: CIK 0000320193
- **Microsoft (MSFT)**: CIK 0000789019  
- **Amazon (AMZN)**: CIK 0001018724
- **Alphabet (GOOGL)**: CIK 0001652044
- **Meta (META)**: CIK 0001326801
- **Tesla (TSLA)**: CIK 0001318605
- **Netflix (NFLX)**: CIK 0001065280

## Technology Stack

- **Python 3.12+**: Primary development language
- **Neo4j**: Graph database
- **neomodel**: Python ORM for Neo4j
- **Sentence Transformers**: Semantic embeddings
- **PyTorch**: Machine learning framework
- **BeautifulSoup**: HTML/XML parsing
- **pandas/numpy**: Data processing

## Performance Considerations

### Memory Requirements
- **Minimum**: 4GB RAM (basic functionality)
- **Recommended**: 8GB+ RAM (full functionality)
- **Production**: 16GB+ RAM (large-scale data)

### Storage Requirements
- **M7 Data**: ~500MB
- **Vector Index**: ~1GB
- **Neo4j Database**: ~2GB

## Extension Guide

### Adding New Query Types

1. Add new intent in `QueryIntent` enum
2. Add pattern matching in `StructuredQueryGenerator`
3. Implement corresponding answer generation logic in `IntelligentAnswerGenerator`

### Supporting New Data Sources

1. Extend data models in `ETL/models.py`
2. Add new ingestion methods in `data_ingestion.py`
3. Update semantic embedding processing logic

### Custom Embedding Models

```python
from graph_rag.semantic_embedding import SemanticEmbedding

# Use custom model
embedding = SemanticEmbedding('your-custom-model')
graph_rag = GraphRAGSystem(embedding_system=embedding)
```

## Troubleshooting

### Common Issues

1. **NumPy compatibility warnings**: Normal occurrence, doesn't affect functionality
2. **Sentence embedding model download**: Models are automatically downloaded on first run
3. **Neo4j connection**: Ensure Neo4j service is running

### Log Analysis

```bash
# View detailed logs
tail -f graph_rag_test.log

# View data ingestion logs  
tail -f data/log/ingestion.log
```

## Contributing

1. Fork the project repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Create Pull Request

## License

This project is licensed under the MIT License - see [LICENSE](../LICENSE) file for details.

## Contact

For questions or suggestions, please contact via:

- Create [GitHub Issue](https://github.com/wangzitian0/my_finance/issues)
- Refer to project documentation [docs/](../docs/)

---

*Graph RAG system continuously optimized to provide more accurate and insightful investment analysis*