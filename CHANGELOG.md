# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- M7 data collection configuration files
- Complete M7 build guide documentation
- Pylint configuration to handle dependency conflicts
- M7 build process validation and testing

### Fixed  
- Missing M7 configuration files (`job_yfinance_m7.yml`, `sec_edgar_m7.yml`)
- Pylint circular import issue with dill dependency
- File naming convention inconsistencies for M7 builds
- M7 build process reliability and error handling

### Changed
- Improved M7 data collection robustness
- Enhanced build documentation and troubleshooting guides
- Updated development workflow for M7 data management

## [1.0.0] - 2025-08-01

### Added
- Complete Graph RAG system implementation
- Neo4j schema extensions for financial data
- Semantic embedding with sentence transformers
- Natural language to Cypher query conversion
- Intelligent answer generation with context awareness
- Multi-step reasoning processor
- Data ingestion pipeline for M7 companies
- Automated Git workflow optimization
- Branch cleanup automation
- Git hooks for commit message validation
- Development environment setup with Pixi
- Cross-platform dependency management

### Technical Details
- **Graph RAG Components**: Semantic embedding, query generator, retriever, answer generator
- **Neo4j Extensions**: SECFiling, NewsEvent, DCFValuation, FinancialMetrics nodes
- **M7 Support**: Complete data collection for Magnificent 7 companies
- **Testing**: 80% success rate with comprehensive test suite
- **Documentation**: Complete API docs, architecture guides, and workflow optimization

### Infrastructure
- **Environment**: Pixi-based cross-platform setup
- **Services**: Neo4j graph database, Minikube container orchestration  
- **Data Sources**: Yahoo Finance, SEC Edgar integration
- **Storage**: JSON-based data with graph database backend