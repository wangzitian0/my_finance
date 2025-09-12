# SSOT Governance and Development Standards

**Authority**: Delegated from CLAUDE.md to specialized agents
**Maintained By**: infra-ops-agent (infrastructure SSOT), backend-architect-agent (business logic SSOT)
**Compliance Monitoring**: hrbp-agent

## 🔥 SSOT Configuration Governance

**POLICY**: All configurations, file operations, and architectural decisions must adhere to SSOT principles with designated agent oversight.

### Agent Responsibility Assignments

**INFRA-OPS-AGENT - SSOT Infrastructure Authority**:
- **SSOT Configuration Management**: Maintain integrity of `common/config/` centralized configurations
- **SSOT File System Architecture**: Ensure `common.core.directory_manager` compliance across codebase  
- **SSOT Module Validation**: Verify SSOT principles in infrastructure components and shared utilities
- **Configuration Consistency**: Validate configuration files follow centralized management patterns
- **Path Management**: Enforce DirectoryManager usage for all infrastructure operations

**BACKEND-ARCHITECT-AGENT - SSOT Business Logic Authority**:
- **SSOT Business Development**: Ensure business logic follows SSOT principles and proper architectural placement
- **Code Organization Standards**: Enforce proper separation between business logic and infrastructure code
- **DRY Principle Enforcement**: Validate Don't Repeat Yourself principles in business logic development
- **Architectural Consistency**: Ensure business logic is placed in correct modules/submodules following two-tier modularity
- **Logic Placement Validation**: Prevent business logic from being incorrectly placed in infrastructure modules

### Clear Agent Role Separation

**INFRASTRUCTURE DEVELOPMENT** (infra-ops-agent domain):
```yaml
infrastructure_scope:
  - common/ directory architecture and maintenance
  - P3 CLI system development and optimization
  - Environment setup and container management  
  - System monitoring and operational intelligence
  - Configuration management and SSOT infrastructure
  - Build systems and deployment pipelines
  - Storage backend abstraction and data layer management
```

**BUSINESS DEVELOPMENT** (backend-architect-agent domain):
```yaml
business_logic_scope:
  - DCF calculation engines and financial modeling
  - RAG system architecture and semantic search
  - Trading logic and investment analysis algorithms
  - SEC filing processing and data extraction
  - Financial data transformation and analysis
  - Business rule implementation and validation
  - Domain-specific API design and integration
```

**ROLE BOUNDARY ENFORCEMENT**:
- **NO OVERLAP**: Infrastructure agents NEVER implement business logic
- **NO OVERLAP**: Business agents NEVER modify infrastructure systems
- **CLEAR INTERFACES**: Business logic consumes infrastructure services through well-defined APIs
- **PROPER ESCALATION**: Cross-boundary issues route through agent-coordinator for proper delegation

## 🎯 SSOT Development Standards

### SSOT Business Logic Requirements

**MANDATORY SSOT COMPLIANCE FOR ALL BUSINESS DEVELOPMENT**:

```yaml
SSOT_BUSINESS_LOGIC_STANDARDS:
  # Configuration Access (REQUIRED)
  - Use config_manager for ALL business configuration loading
  - NEVER hard-code business parameters or thresholds
  - Load company lists, financial parameters through centralized config system
  
  # Path Operations (REQUIRED)
  - Use directory_manager for ALL file path resolution
  - NEVER construct paths manually in business logic
  - Use DataLayer enums for all data access patterns
  
  # Code Organization (REQUIRED) 
  - Follow two-tier modularity: modules/submodules/<business_logic>
  - Place logic in correct architectural layer (ETL/, dcf_engine/, graph_rag/)
  - Separate concerns between data processing, analysis, and presentation
  
  # DRY Principle Enforcement (REQUIRED)
  - Extract common business logic into reusable modules
  - Avoid code duplication across financial calculations
  - Create shared utilities for repeated business patterns
  - Implement proper inheritance and composition patterns
```

### Python DRY Principle Enforcement

**ANTI-PATTERNS TO PREVENT**:
```python
# ❌ WRONG: Duplicated DCF calculation logic across files
# In dcf_engine/calculations.py
def calculate_dcf_apple():
    # Apple-specific DCF logic...
    pass

# In dcf_engine/analysis.py  
def analyze_apple_valuation():
    # Duplicate DCF calculation logic...
    pass

# ✅ CORRECT: Single source of truth with reusable components
# In dcf_engine/core/valuation.py
class DCFCalculator:
    def calculate_dcf(self, company_data, assumptions):
        # Reusable DCF logic for all companies
        pass

# In dcf_engine/companies/apple.py
class AppleAnalysis:
    def __init__(self):
        self.calculator = DCFCalculator()
    
    def analyze_valuation(self):
        return self.calculator.calculate_dcf(self.company_data, self.assumptions)
```

### Code Quality Standards

**ARCHITECTURAL PLACEMENT VALIDATION**:
```yaml
CORRECT_LOGIC_PLACEMENT:
  # ETL Layer - Data Processing Logic
  ETL/:
    - SEC filing download and parsing
    - Data extraction and transformation  
    - Data quality validation and cleansing
    - External API integration logic
    
  # DCF Engine Layer - Financial Analysis Logic  
  dcf_engine/:
    - Financial calculation algorithms
    - Valuation models and assumptions
    - Company-specific analysis logic
    - Financial reporting and output generation
    
  # Graph RAG Layer - Knowledge Processing Logic
  graph_rag/:
    - Semantic search and retrieval
    - Knowledge graph construction
    - Document processing and indexing
    - Question answering and response generation
    
  # Common Layer - Shared Infrastructure (infra-ops domain)
  common/:
    - Configuration management utilities
    - Directory and path management
    - Storage backend abstraction
    - Logging and monitoring infrastructure
```

## 🚨 SSOT Compliance Monitoring

### Automated Compliance Validation

**MANDATORY PRE-PR COMPLIANCE CHECKS**:
```bash
# SSOT Configuration Compliance
bash scripts/config/validate_ssot_compliance.sh

# Business Logic Placement Validation  
bash scripts/quality/validate_logic_placement.sh

# DRY Principle Compliance Check
bash scripts/quality/validate_dry_principles.sh

# Infrastructure/Business Separation Check
bash scripts/quality/validate_agent_boundaries.sh
```

### Violation Response Protocol

**SSOT GOVERNANCE VIOLATIONS**:
```yaml
CRITICAL_VIOLATIONS:
  # Immediate PR blocking violations
  - Business logic placed in common/ infrastructure modules
  - Infrastructure modifications by business development agents  
  - Hard-coded configurations in business logic
  - Duplicate business logic across multiple modules
  - Direct path construction bypassing directory_manager in business code
  
ESCALATION_PROCESS:
  level_1: Automated validation failure blocks PR
  level_2: HRBP agent violation tracking and remediation
  level_3: Mandatory agent retraining and architecture review
```

## 🔧 UNIFIED I/O CONSTRAINTS

**CRITICAL**: All file I/O operations must use the SSOT DirectoryManager system exclusively. No exceptions.

**ENFORCEMENT**: All PR creation must pass I/O compliance checks. Any non-SSOT I/O patterns will block PR approval.

**📖 DETAILED RULES**: See `common/README.md` for complete I/O standards, violation levels, migration guide, and compliance validation procedures.

### Quick Reference

**✅ REQUIRED Pattern**
```python
from common.core.directory_manager import directory_manager, DataLayer
data_path = directory_manager.get_layer_path(DataLayer.RAW_DATA, partition="20250901")
```

**❌ PROHIBITED Patterns**
```python
data_path = Path("build_data/stage_00_raw/20250901")  # FORBIDDEN
from common.io_utils import load_json                 # REMOVED
```

### Validation Command
```bash
bash scripts/config/validate_io_compliance.sh  # Run before PR creation
```

---

**GOVERNANCE DELEGATION**: This document is maintained by specialized agents under HRBP oversight. All modifications must follow CLAUDE.md change management protocols.