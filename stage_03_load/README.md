# Stage 3: Load Phase Data Directory

This directory contains the final processed data products after ETL Stage 3 (Load).

## Directory Structure

```
stage_03_load/
├── dcf_results/           # DCF valuation calculations and results
├── graph_nodes/           # Neo4j node and relationship data
├── embeddings/           # Vector embeddings for semantic search
├── graph_embeddings/     # Combined graph + vector data products  
├── vector_index/         # FAISS vector search indexes
└── graph_rag_cache/      # Cached query results and processed data
```

## Data Products

### dcf_results/
- DCF calculation outputs and valuation models
- Financial metrics and ratios  
- Intrinsic value estimates and analysis reports

### graph_nodes/
- Neo4j graph database nodes (stocks, filings, metrics)
- Relationship mappings and graph structure data
- Node metadata and properties

### embeddings/
- Document chunk embeddings using sentence transformers
- Vector representations of SEC filings and financial documents
- Embedding metadata and chunk mappings

### graph_embeddings/
- Combined graph and vector data for Graph RAG
- Hybrid retrieval indexes combining structured and unstructured data
- Cross-modal embeddings and similarity mappings

### vector_index/
- FAISS indexes for fast similarity search
- Vector search configurations and parameters
- Pre-computed similarity matrices

### graph_rag_cache/
- Cached query results and responses  
- Processed Q&A pairs and reasoning chains
- Performance optimization data

## Integration with Graph RAG Architecture

This directory supports the modular Graph RAG system:

- **ETL Module**: Writes processed data to these directories
- **dcf_engine Module**: Reads data for query processing and answer generation
- **Common Schema**: Ensures consistent data formats across directories

## Build Process

Data in this directory is generated through:

1. **Stage 1 Extract**: Raw data collection → `../stage_01_extract/`
2. **Stage 2 Transform**: Data cleaning and enrichment → `../stage_02_transform/`  
3. **Stage 3 Load**: Final processing and indexing → `stage_03_load/` (this directory)

Each build is tracked in `../build/build_<timestamp>/BUILD_MANIFEST.md` with complete lineage information.