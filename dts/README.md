# DTS (Data Transport Service)

Data transport service layer responsible for data import/export to online databases, abstracting infrastructure details from dcf_engine.

## Responsibilities

### Data Abstraction Layer
- **Unified Data Interface**: Provides unified data access API for upper-level business logic
- **Multi-source Adaptation**: Supports multiple storage backends like Neo4j, MySQL, Redis
- **Data Transformation**: Handles data conversion between different storage formats
- **Cache Management**: Provides intelligent caching mechanisms to improve access performance

### Data Services
- **Read Services**: High-performance data querying and retrieval
- **Write Services**: Batch data import and real-time data updates
- **Transaction Management**: Ensures data consistency and integrity
- **Connection Pool Management**: Optimizes database connection usage

## Architecture Design

```
dcf_engine
    ↓ (calls)
dts (data abstraction layer)
    ↓ (adapts)
Data Storage Layer (Neo4j/MySQL/Redis/Configuration Center)
```

## Modules To Be Implemented

### Core Modules
- [ ] `data_adapter.py` - Data adapter base class
- [ ] `neo4j_adapter.py` - Neo4j data adapter
- [ ] `cache_manager.py` - Cache manager
- [ ] `connection_pool.py` - Connection pool management
- [ ] `data_validator.py` - Data validator

### Service Interfaces
- [ ] `reader_service.py` - Data reading service
- [ ] `writer_service.py` - Data writing service
- [ ] `query_builder.py` - Query builder
- [ ] `schema_manager.py` - Schema manager

## Design Principles

1. **Abstraction Isolation**: Upper-level business logic doesn't depend on specific storage implementations
2. **High Performance**: Optimizes performance through caching and connection pooling
3. **Extensibility**: Supports adding new data sources and storage backends
4. **Fault Tolerance**: Handles network exceptions and storage failures
5. **Monitoring Friendly**: Provides detailed performance and error metrics