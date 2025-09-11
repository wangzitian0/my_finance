# Neo4j Database Testing Infrastructure

> **Issue #266**: Comprehensive Neo4j Testing Infrastructure

This module provides a comprehensive Neo4j testing infrastructure that ensures database connectivity across development, CI, and production environments.

## 🎯 Features

- **🔄 Multi-Environment Support**: Automatic environment detection (dev/CI/prod)
- **🧪 Dedicated Test Table**: Reusable TestNode table for connectivity validation
- **📊 Health Monitoring**: Comprehensive health checks and metrics
- **🚀 CI Integration**: GitHub Actions workflow with Docker Neo4j
- **⚡ Performance Testing**: Baseline performance validation
- **🔒 Production Safety**: Read-only tests for production environments

## 📁 Module Structure

```
common/database/
├── __init__.py                 # Public API exports
├── neo4j_manager.py           # Connection manager with environment detection
├── test_operations.py         # CRUD operations on test table
├── health_checks.py           # Health monitoring and status reporting
├── health_endpoint.py         # HTTP endpoints for health checks
└── README.md                  # This documentation

tests/database/
├── __init__.py
└── test_neo4j_connectivity.py # Comprehensive test suite

common/config/
├── database_base.yml         # Base configuration (all environments)
└── database_overrides.yml    # Environment-specific overrides
```

## 🚀 Quick Start

### Basic Usage

```python
from common.database import Neo4jManager, TestOperations, HealthChecker

# Automatic environment detection
manager = Neo4jManager()
print(f"Environment: {manager.environment}")

# Test connectivity
connectivity = manager.test_connectivity()
print(f"Connected: {connectivity['connected']}")

# Test CRUD operations
test_ops = TestOperations(manager)
results = test_ops.test_crud_operations()
print(f"All CRUD operations passed: {all(results[op] for op in ['create', 'read', 'update', 'delete'])}")

# Health check
health_checker = HealthChecker(manager)
health_status = health_checker.comprehensive_health_check()
print(f"Health status: {health_status.status}")

manager.close()
```

### Environment-Specific Usage

```python
# Explicit environment
dev_manager = Neo4jManager(environment='development')
ci_manager = Neo4jManager(environment='ci')
prod_manager = Neo4jManager(environment='production')

# Configuration access
config = dev_manager.config
print(f"Host: {config['host']}, Port: {config['port']}")
```

### Health Check Server

```python
from common.database.health_endpoint import create_health_server

# Start health check HTTP server
server = create_health_server(environment='production', port=8080)
server.start()

# Available endpoints:
# http://localhost:8080/health/neo4j           - Basic health check
# http://localhost:8080/health/neo4j/metrics   - Prometheus-style metrics  
# http://localhost:8080/health/neo4j/detailed  - Full diagnostics
```

## 🏗️ Environment Configuration

### Development Environment

```yaml
# common/config/database_development.yml
neo4j:
  host: "localhost"
  port: 7687
  database: "neo4j"
  auth:
    user: "neo4j"
    password: "finance123"
  monitoring:
    enable_crud_tests: true  # Full testing enabled
```

### CI Environment

```yaml
# common/config/database_ci.yml  
neo4j:
  host: "localhost"
  port: 7687
  database: "neo4j"
  auth:
    user: "neo4j" 
    password: "ci_test_password"
  test_settings:
    cleanup_on_exit: true    # Clean up test data
    performance_baseline_ms: 200  # More lenient for CI
```

### Production Environment

```yaml
# common/config/database_production.yml
neo4j:
  host: "${NEO4J_HOST:-neo4j-prod.internal}"
  auth:
    user: "${NEO4J_USER:-neo4j}"
    password: "${NEO4J_PASSWORD}"
  monitoring:
    enable_crud_tests: false  # Read-only for safety
```

## 🧪 Testing

### Unit Tests (No Database Required)

```bash
# Run all unit tests
python -m pytest tests/database/ -v

# Run specific test classes
python -m pytest tests/database/test_neo4j_connectivity.py::TestNeo4jConnectivity -v
python -m pytest tests/database/test_neo4j_connectivity.py::TestNeo4jOperations -v
python -m pytest tests/database/test_neo4j_connectivity.py::TestNeo4jHealthCheck -v
```

### Integration Tests (Requires Neo4j)

```bash
# Run integration tests (requires running Neo4j instance)
python -m pytest tests/database/ -m integration -v

# With Docker Neo4j for CI
docker-compose -f infra/docker/neo4j-ci.docker-compose.yml up -d
python -m pytest tests/database/ -m integration -v
docker-compose -f infra/docker/neo4j-ci.docker-compose.yml down
```

### GitHub Actions CI

The module includes dedicated GitHub Actions workflows:

- **`neo4j-testing.yml`**: Comprehensive Neo4j testing with Docker
- **`test-pipeline.yml`**: Integrated unit testing in main pipeline

## 📊 Health Check Endpoints

### Basic Health Check
```bash
curl http://localhost:8080/health/neo4j
```

```json
{
  "status": "healthy",
  "response_time_ms": 45,
  "last_test_timestamp": "2025-01-11T10:30:00Z", 
  "environment": "production",
  "version": "5.15.0",
  "test_operations": {
    "connection": "success"
  }
}
```

### Metrics for Monitoring
```bash
curl http://localhost:8080/health/neo4j/metrics
```

```json
{
  "neo4j_health_status": 1,
  "neo4j_response_time_ms": 45,
  "neo4j_connection_success": 1,
  "neo4j_environment": "production"
}
```

## 🔧 CI/CD Integration

### Docker Setup

The module provides a pre-configured Docker Compose setup for CI:

```bash
# Start Neo4j for testing
docker-compose -f infra/docker/neo4j-ci.docker-compose.yml up -d

# Check health
curl http://localhost:7474/db/data/

# Run tests
python -m pytest tests/database/ -v

# Cleanup
docker-compose -f infra/docker/neo4j-ci.docker-compose.yml down
```

### GitHub Actions Integration

```yaml
# Add to your workflow
services:
  neo4j-ci:
    image: neo4j:5.15-community
    env:
      NEO4J_AUTH: neo4j/ci_test_password
      NEO4J_PLUGINS: '["apoc"]'
    ports:
      - 7474:7474
      - 7687:7687
    options: >-
      --health-cmd "cypher-shell -u neo4j -p ci_test_password 'RETURN 1'"
      --health-interval 10s
      --health-timeout 5s
      --health-retries 10

steps:
  - name: Test Neo4j Integration
    run: |
      python -m pytest tests/database/ -m integration -v
```

## 🎛️ Configuration Options

### Connection Settings

| Option | Development | CI | Production |
|--------|-------------|----| -----------|
| **Host** | localhost | localhost | ${NEO4J_HOST} |
| **Port** | 7687 | 7687 | ${NEO4J_PORT} |
| **Timeout** | 30s | 15s | 60s |
| **Pool Size** | 50 | 10 | 100 |
| **Retries** | 3 | 2 | 5 |

### Test Settings

| Option | Development | CI | Production |
|--------|-------------|----| -----------|
| **CRUD Tests** | ✅ Enabled | ✅ Enabled | ❌ Disabled |
| **Cleanup** | ❌ Manual | ✅ Auto | ❌ Manual |
| **Baseline** | 100ms | 200ms | 50ms |

## 🛠️ Advanced Usage

### Custom Test Operations

```python
from common.database import Neo4jManager, TestOperations

manager = Neo4jManager()
test_ops = TestOperations(manager)

# Create custom test node
test_id = test_ops.create_test_node(
    test_id="my_custom_test",
    test_data={"custom_field": "value"}
)

# Read and verify
node_data = test_ops.read_test_node(test_id)
assert node_data["custom_field"] == "value"

# Update
test_ops.update_test_node(test_id, {"updated": True})

# Cleanup
test_ops.delete_test_node(test_id)
```

### Performance Monitoring

```python
from common.database import Neo4jManager, HealthChecker

manager = Neo4jManager()
health_checker = HealthChecker(manager)

# Check performance against baseline
perf_result = health_checker.check_performance_baseline()
print(f"Baseline met: {perf_result['baseline_met']}")
print(f"Response time: {perf_result['response_time_ms']}ms")

# Get monitoring metrics
metrics = health_checker.monitoring_metrics()
for metric, value in metrics.items():
    print(f"{metric}: {value}")
```

### Environment Detection

```python
import os
from common.database import Neo4jManager

# Test different environment detection
environments = []

# Development (default)
manager = Neo4jManager()
environments.append(manager.environment)

# CI environment
os.environ['CI'] = 'true'
manager = Neo4jManager()
environments.append(manager.environment)

# Production environment  
os.environ['PRODUCTION'] = 'true'
manager = Neo4jManager()
environments.append(manager.environment)

print(f"Detected environments: {environments}")
# Output: ['development', 'ci', 'production']
```

## 🚨 Troubleshooting

### Common Issues

**Connection Failed**
```python
# Check configuration
manager = Neo4jManager()
print(f"URI: {manager.get_connection_uri()}")
print(f"Config: {manager.config}")

# Test connectivity
result = manager.test_connectivity()
if not result['connected']:
    print(f"Error: {result['error']}")
```

**Performance Issues**
```python
# Check performance baseline
health_checker = HealthChecker(manager)
perf = health_checker.check_performance_baseline()

if not perf['baseline_met']:
    print(f"Performance issue: {perf['response_time_ms']}ms > {perf['baseline_threshold_ms']}ms")
```

**Test Failures**
```python
# Debug CRUD operations
test_ops = TestOperations(manager)
results = test_ops.test_crud_operations()

for operation, success in results.items():
    if operation.endswith('_ms'):
        continue
    if not success:
        print(f"Failed operation: {operation}")
        
if results['errors']:
    print(f"Errors: {results['errors']}")
```

### Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `CI` | Detect CI environment | `true` |
| `PRODUCTION` | Detect production | `true` |
| `NEO4J_HOST` | Production host | `neo4j-prod.internal` |
| `NEO4J_USER` | Production username | `finance_user` |
| `NEO4J_PASSWORD` | Production password | `secure_password` |
| `NEO4J_DATABASE` | Production database | `finance_prod` |

## 📚 API Reference

### Neo4jManager

- `Neo4jManager(environment=None)`: Initialize with optional environment override
- `connect()`: Establish database connection
- `get_session()`: Get Neo4j session for queries
- `test_connectivity()`: Test connection and return detailed status
- `close()`: Close database connection

### TestOperations

- `setup_test_schema()`: Create test table schema and constraints
- `create_test_node(test_id, test_data)`: Create test node
- `read_test_node(test_id)`: Read test node data
- `update_test_node(test_id, updates)`: Update test node
- `delete_test_node(test_id)`: Delete test node
- `test_crud_operations()`: Run complete CRUD test suite

### HealthChecker

- `check_basic_connectivity()`: Basic connection test
- `check_database_operations()`: CRUD operations test
- `check_performance_baseline()`: Performance validation
- `comprehensive_health_check()`: Complete health assessment
- `health_check_endpoint()`: HTTP endpoint format
- `monitoring_metrics()`: Metrics for monitoring systems

## 🔗 Related Documentation

- [Issue #266](https://github.com/wangzitian0/my_finance/issues/266): Original implementation issue
- [Neo4j Python Driver Documentation](https://neo4j.com/docs/python-manual/current/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)