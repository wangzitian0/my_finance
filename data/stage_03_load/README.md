# Stage 03 Load - Unified Directory Structure

⚠️ **MIGRATION NOTICE**: The old subdirectory-based structure has been migrated to the unified standard.

## New Standard Format

**Standard Path**: `stage_03_load/YYYYMMDD/TICKER/<files>`

```
stage_03_load/20250818/AAPL/
├── AAPL_graph_nodes.json           # Neo4j graph node definitions
├── AAPL_embeddings.npy             # Vector embeddings for text data  
├── AAPL_vector_index.faiss         # FAISS indices for similarity search
├── AAPL_dcf_results.json           # DCF calculation outputs
└── AAPL_graph_rag_cache.json       # Cached query results
```

## Directory Management

**⚠️ CRITICAL**: Always use the unified DirectoryManager for all operations:

```python
from common.directory_manager import DirectoryManager

dm = DirectoryManager()

# Create standard directory structure
path = dm.create_directory_structure("stage_03_load", "AAPL", "20250818")

# Get standardized file paths
embeddings_path = dm.get_standard_path("stage_03_load", "AAPL", "20250818", "AAPL_embeddings.npy")
graph_nodes_path = dm.get_standard_path("stage_03_load", "AAPL", "20250818", "AAPL_graph_nodes.json")

# List all tickers in stage
tickers = dm.list_tickers_in_stage("stage_03_load", "20250818")

# Validate structure compliance
validation = dm.validate_structure("stage_03_load", "20250818")
```

## Migration Status

✅ **Completed**: Legacy structure migrated to unified format
🗑️ **Removed**: Old subdirectories (dcf_results/, embeddings/, etc.)
📁 **Standard**: All data follows `stage_xx_yyyy/YYYYMMDD/TICKER/` format

## Data Products

### Graph Nodes (`TICKER_graph_nodes.json`)
- Neo4j graph database nodes (stocks, filings, metrics)
- Relationship mappings and graph structure data
- Node metadata and properties

### Embeddings (`TICKER_embeddings.npy`)
- Document chunk embeddings using sentence transformers
- Vector representations of SEC filings and financial documents
- 384-dimensional vectors for semantic search

### Vector Index (`TICKER_vector_index.faiss`)
- FAISS indexes for fast similarity search
- Vector search configurations and parameters
- Pre-computed similarity matrices

### DCF Results (`TICKER_dcf_results.json`)
- DCF calculation outputs and valuation models
- Financial metrics and ratios  
- Intrinsic value estimates and analysis reports

### Graph RAG Cache (`TICKER_graph_rag_cache.json`)
- Cached query results and responses  
- Processed Q&A pairs and reasoning chains
- Performance optimization data

## Integration with Graph RAG Architecture

This directory supports the modular Graph RAG system:

- **ETL Module**: Writes processed data using DirectoryManager
- **dcf_engine Module**: Reads data for query processing and answer generation
- **Common Schema**: Ensures consistent data formats across all stages

## Build Process

Data flows through the unified pipeline:

1. **Stage 00**: Raw data collection → `stage_00_original/YYYYMMDD/TICKER/`
2. **Stage 01**: Data extraction → `stage_01_extract/YYYYMMDD/TICKER/`  
3. **Stage 02**: Data transformation → `stage_02_transform/YYYYMMDD/TICKER/`
4. **Stage 03**: Final processing → `stage_03_load/YYYYMMDD/TICKER/` (this directory)
5. **Stage 99**: Build artifacts → `stage_99_build/build_YYYYMMDD_HHMMSS/`

Each build is tracked in `BUILD_MANIFEST.md` with complete lineage information.

## File Naming Standards

**Format**: `{TICKER}_{component}_{metadata}.{ext}`

**Examples**:
- `AAPL_graph_nodes_complete.json`
- `AAPL_embeddings_384d.npy`
- `AAPL_vector_index_faiss.faiss`
- `AAPL_dcf_results_comprehensive.json`

**Never create files that don't follow this naming convention.**