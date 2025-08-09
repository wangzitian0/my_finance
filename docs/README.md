# My Finance Project Architecture Documentation

This directory contains **architecture and design documentation** for the My Finance DCF investment analysis tool.

> **Note**: Implementation-specific documentation has been moved to respective component directories. See the links below for implemented features.

## 📋 Architecture Documentation Index

### System Architecture
- [System Architecture](architecture.md) - Overall architecture and technology stack
- [ETL Structure Design](ETL_STRUCTURE_DESIGN.md) - ETL pipeline architecture and data warehouse design
- [Data Schema Design](data-schema.md) - Neo4j graph database models and relationships
- [Project Roadmap](PROJECT_ROADMAP.md) - Development plan and milestones

### Feature Design
- [DCF Calculation Engine](dcf-engine.md) - Valuation calculation architecture  
- [Graph RAG System](graph-rag.md) - Retrieval-Augmented Generation system design
- [Data Validation Framework](data-validation.md) - Multi-source data consistency architecture

### Development & Operations
- [Development Environment Setup](development-setup.md) - Local development environment configuration
- [API Documentation](api-docs.md) - Interface specifications and usage
- [Deployment Guide](deployment.md) - Production environment deployment architecture
- [Monitoring and Maintenance](monitoring.md) - System monitoring and observability
- [Evaluation Framework](evaluation.md) - Quality assessment and testing architecture

### Process & Workflow
- [Strategy Release Process](STRATEGY_RELEASE_PROCESS.md) - Investment strategy release workflow
- [Git Workflow Optimization](git-workflow-optimization.md) - Development workflow and branch management

## 🔗 Implementation Documentation Links

### Implemented Features (see component directories)
- **Data Collection**: [`spider/README.md`](../spider/README.md) - YFinance and SEC Edgar spiders
- **Data Management**: [`common/README.md`](../common/README.md) - Metadata system and utilities
- **Build System**: [`scripts/README.md`](../scripts/README.md) - Dataset building and management scripts  
- **Data Pipeline**: [`data/README.md`](../data/README.md) - ETL structure and four-tier dataset strategy

### Additional Components
- **ETL Processing**: [`ETL/README.md`](../ETL/README.md) - Data processing and transformation
- **Graph RAG**: [`graph_rag/README.md`](../graph_rag/README.md) - Retrieval-augmented generation implementation
- **Local LLM**: [`local_llm/README.md`](../local_llm/README.md) - Local language model integration

## 📚 Documentation Strategy

This documentation follows a **separation of concerns** approach:

- **`docs/`** - Architecture, design, and high-level system documentation
- **Component READMEs** - Implementation details, usage guides, and feature-specific documentation
- **Main README** - Project overview and quick start guide

---

*Architecture documentation is maintained as the system evolves. Implementation details are maintained with their respective components.*