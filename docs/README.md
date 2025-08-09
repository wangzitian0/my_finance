# Architecture Documentation

This directory contains **pure architecture and design documentation** for the My Finance system. 

> **🎯 Purpose**: High-level system design, architectural decisions, and strategic direction
> 
> **📋 Not Included**: Implementation details, tutorials, or step-by-step guides (see Wiki and Issues)

## 📐 Core Architecture Documents

### 🏛️ System Design
- **[Architecture Overview](ARCHITECTURE_OVERVIEW.md)** - Complete system architecture and vision
- **[Design Decisions](DESIGN_DECISIONS.md)** - ADRs (Architecture Decision Records) with rationale
- **[System Architecture](architecture.md)** - Technical architecture and technology stack
- **[Data Schema Design](data-schema.md)** - Neo4j graph database conceptual models

### 🏗️ Component Architecture
- **[ETL Structure Design](ETL_STRUCTURE_DESIGN.md)** - Data pipeline architecture principles
- **[DCF Calculation Engine](dcf-engine.md)** - Valuation calculation architecture
- **[Graph RAG System](graph-rag.md)** - Retrieval-Augmented Generation system design
- **[Data Validation Framework](data-validation.md)** - Multi-source consistency architecture

### 🚀 Strategic Documentation
- **[Project Roadmap](PROJECT_ROADMAP.md)** - Development phases and strategic milestones
- **[Strategy Release Process](STRATEGY_RELEASE_PROCESS.md)** - Investment strategy deployment workflow

### 🔧 Operations Architecture
- **[Deployment Architecture](deployment.md)** - Production deployment patterns and infrastructure
- **[Monitoring & Observability](monitoring.md)** - System observability and operational excellence
- **[API Design](api-docs.md)** - API architecture and interface specifications
- **[Evaluation Framework](evaluation.md)** - Quality assessment and testing architecture

### 📈 Process Architecture
- **[Git Workflow Optimization](git-workflow-optimization.md)** - Development workflow and branch strategies

## 🔗 Related Documentation

### Implementation Details
- **Component READMEs**: Implementation guides in respective directories
- **GitHub Issues**: Specific tasks and implementation details
- **GitHub Wiki**: Tutorials, setup guides, and best practices

### Navigation
- **[Main README](../README.md)** - Project overview and quick start
- **[Component Documentation](../README.md#documentation)** - Implementation-specific guides

## 📚 Documentation Philosophy

This architecture documentation follows the **C4 Model** principles:

1. **Context** - System landscape and external dependencies
2. **Container** - High-level technology choices and deployment units  
3. **Component** - Major building blocks and their responsibilities
4. **Code** - Detailed implementation (covered in component READMEs)

### Audience
- **Software Architects**: System design and technical strategy
- **Senior Engineers**: Component architecture and integration patterns
- **Engineering Managers**: Technical roadmap and strategic decisions
- **DevOps Engineers**: Deployment and operational architecture

### Maintenance
- **Reviews**: Quarterly architecture review sessions
- **Updates**: Updated when architectural decisions change
- **Versioning**: Major architecture changes increment version numbers

---

*Architecture documentation captures the "why" and "what" of system design. Implementation documentation captures the "how".*