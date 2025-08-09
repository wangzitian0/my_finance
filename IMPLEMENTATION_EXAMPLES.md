# Documentation Architecture Implementation Examples

This document provides examples of how the new three-tier documentation architecture works.

## 🏗️ Three-Tier Architecture

### 1. **docs/** - Pure Architecture & Design
**Purpose**: High-level system design, strategic decisions, architectural patterns  
**Audience**: Architects, senior engineers, technical managers  
**Update Frequency**: When architectural decisions change (quarterly)

**Example Content**:
```
docs/DESIGN_DECISIONS.md:
- ADR-001: Four-tier data strategy decision
- ADR-002: ETL stage-based architecture decision
- Rationale, consequences, alternatives considered
```

### 2. **GitHub Issues** - Implementation Tasks & Details
**Purpose**: Specific, actionable implementation tasks with technical details  
**Audience**: Developers implementing features  
**Update Frequency**: Active development (daily/weekly)

**Example Content**:
```
Issue #123: [FEATURE] Implement SEC 8-K filing parser
- Component: spider
- Priority: P1
- Technical Details: 
  - Add 8K parsing to sec_edgar_spider.py
  - Update data schema for 8K events
  - Add validation rules
- Acceptance Criteria:
  - [ ] 8K filings parsed and stored
  - [ ] Tests pass for sample 8K documents
  - [ ] Metadata correctly generated
```

### 3. **GitHub Wiki** - Tutorials & How-To Guides
**Purpose**: Practical guides, setup instructions, workflows, troubleshooting  
**Audience**: All users, especially new developers  
**Update Frequency**: As needed when processes change

**Example Content**:
```
Wiki Page: "Development Environment Setup"
- Step-by-step installation guide
- Common troubleshooting issues
- Platform-specific instructions
- Screenshots and examples
```

## 📊 Content Distribution Examples

### Example 1: Adding New Data Source

**Architecture Decision** (`docs/DESIGN_DECISIONS.md`):
```markdown
## ADR-008: Support for Alternative Data Sources

**Decision**: Extend spider framework to support pluggable data sources
**Rationale**: Enable integration of news feeds, analyst reports, etc.
**Consequences**: More flexible but more complex spider architecture
```

**Implementation Task** (GitHub Issue):
```markdown
# [FEATURE] Implement Reuters News Spider

**Component**: spider  
**Priority**: P2

**Technical Details**:
- Create `reuters_spider.py` following spider interface
- Add authentication handling for Reuters API
- Implement rate limiting (5 req/sec)
- Add news article parsing and sentiment analysis

**Acceptance Criteria**:
- [ ] Reuters spider collects news articles
- [ ] Sentiment scores calculated and stored
- [ ] Rate limiting prevents API violations
- [ ] Tests cover error scenarios
```

**Tutorial Guide** (GitHub Wiki):
```markdown
# Adding a New Data Source

This guide walks you through adding a new data source to the spider system.

## Step 1: Create Spider Class
```python
class MyDataSpider(BaseSpider):
    def __init__(self, config):
        super().__init__(config)
    # ... implementation details
```

## Step 2: Configuration
Add your data source to `data/config/`:
```yaml
source: my_data_source
# ... configuration example
```
## ... rest of tutorial
```

### Example 2: Performance Optimization

**Architecture Decision** (`docs/ARCHITECTURE_OVERVIEW.md`):
```markdown
## Performance Characteristics

**Target Performance**:
- Data Collection: <5 minutes for M7, <30 minutes for NASDAQ100
- DCF Calculation: <1 second per company
```

**Implementation Task** (GitHub Issue):
```markdown
# [PERFORMANCE] Optimize Neo4j Query Performance

**Component**: graph_rag  
**Priority**: P1

**Technical Details**:
- Add database indexes for frequent queries
- Optimize Cypher queries in semantic_retriever.py
- Implement query result caching
- Add query performance monitoring

**Acceptance Criteria**:
- [ ] Average query time < 100ms
- [ ] Cache hit rate > 80%
- [ ] Performance tests pass
```

**How-To Guide** (GitHub Wiki):
```markdown
# Performance Optimization Guide

## Monitoring Performance
Use these commands to check system performance:
```bash
pixi run performance-test
pixi run monitor-queries
```

## Common Bottlenecks
1. **Neo4j Queries**: Add indexes for frequent lookups
2. **Data Processing**: Use parallel processing for large datasets
3. **File I/O**: Batch operations when possible

## Optimization Checklist
- [ ] Database indexes added
- [ ] Caching implemented
- [ ] Parallel processing used
- [ ] Performance tests added
```

## 🔍 Benefits of This Architecture

### Clear Separation of Concerns
- **Strategic decisions** documented once in architecture docs
- **Implementation tasks** tracked and managed in Issues  
- **Practical knowledge** accessible in Wiki tutorials

### Improved Maintainability
- **Architecture docs** updated only when design changes
- **Issues** closed when tasks complete, reducing clutter
- **Wiki** updated as processes evolve

### Better User Experience
- **Architects** find strategic context in docs/
- **Developers** find specific tasks in Issues
- **New users** find tutorials in Wiki

### Enhanced Collaboration
- **Architecture discussions** happen in Issue comments
- **Implementation progress** tracked in Issue status
- **Knowledge sharing** facilitated through Wiki

---

*This three-tier approach ensures the right information is in the right place for the right audience.*