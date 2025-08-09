# Stage 3 Load - Data Products

This directory contains the final processed data products from the ETL pipeline.

## Directory Structure

### Core Data Products

- **`dcf_results/`** - DCF valuation calculations and analysis results
- **`graph_nodes/`** - Neo4j graph database nodes and relationships  
- **`embeddings/`** - Semantic vector embeddings and metadata

### Graph RAG Extensions  

- **`graph_embeddings/`** - Combined graph + embedding data structures
- **`vector_index/`** - FAISS vector indexes for similarity search
- **`graph_rag_cache/`** - Cached query results and responses

## Data Products Usage

### DCF Results
```bash
# DCF analysis outputs
data/stage_03_load/dcf_results/
├── dcf_analysis_{date}.json        # Calculated valuations
├── valuation_summary_{date}.json   # Summary reports  
└── sensitivity_analysis_{date}.json # Risk scenarios
```

### Graph Nodes
```bash
# Neo4j graph data
data/stage_03_load/graph_nodes/
├── stock_nodes.json              # Company stock information
├── sec_filing_nodes.json         # SEC document metadata
├── financial_metrics_nodes.json  # Financial data points
└── relationships.json            # Graph relationships
```

### Embeddings  
```bash
# Semantic embeddings
data/stage_03_load/embeddings/
├── embeddings_metadata.json      # Document chunk metadata
├── embeddings_vectors.npy        # Vector embeddings array
└── vector_index.faiss            # FAISS similarity index
```

### Graph RAG Cache
```bash
# Query result caching
data/stage_03_load/graph_rag_cache/
├── query_cache.json             # Cached Q&A responses
├── retrieval_cache.json         # Cached search results
└── session_history.json         # Query history
```

## Integration Points

### ETL Pipeline (Stage 3)
- **Graph Integration**: `ETL/graph_data_integration.py` → `graph_nodes/`  
- **Semantic Processing**: `ETL/semantic_retrieval.py` → `embeddings/` + `vector_index/`
- **DCF Calculations**: `ETL/` → `dcf_results/`

### DCF Engine  
- **Query Processing**: `dcf_engine/rag_orchestrator.py` reads from all directories
- **Answer Generation**: `dcf_engine/graph_rag_engine.py` uses cached results
- **Response Caching**: Results stored in `graph_rag_cache/`

## Data Lifecycle

1. **ETL Load Stage** creates core data products (`dcf_results/`, `graph_nodes/`, `embeddings/`)
2. **Graph RAG Processing** creates extended products (`graph_embeddings/`, `vector_index/`)  
3. **Query Engine** uses all products and caches results (`graph_rag_cache/`)
4. **Build Process** packages everything for deployment

## Monitoring & Maintenance

- **Data Freshness**: Check file timestamps in each directory
- **Index Health**: Monitor `vector_index/` for corruption or size issues  
- **Cache Management**: Periodically clear `graph_rag_cache/` for storage
- **Build Manifests**: Reference `../build/` for processing history