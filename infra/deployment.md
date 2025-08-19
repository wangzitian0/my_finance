# Deployment Guide

## Deployment Architecture Options

### 1. Development Environment Deployment
**Use Case**: Local development, feature testing
**Hardware Requirements**: 8GB+ RAM, 4+ CPU cores
**Deployment Method**: Docker Compose

### 2. Production Environment Deployment  
**Use Case**: Formal investment analysis usage
**Hardware Requirements**: 16GB+ RAM, 8+ CPU cores, SSD storage
**Deployment Method**: Kubernetes + Ansible

## Docker Compose Deployment (Recommended for Development)

### 1. Create docker-compose.yml
```yaml
version: '3.8'

services:
  neo4j:
    image: neo4j:5.15
    container_name: finance-neo4j
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/finance123
      - NEO4J_PLUGINS=["apoc"]
      - NEO4J_dbms_memory_heap_initial__size=512m
      - NEO4J_dbms_memory_heap_max__size=2g
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    networks:
      - finance_network
  
  app:
    build: .
    container_name: finance-app
    ports:
      - "8000:8000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=finance123
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
    depends_on:
      - neo4j
    volumes:
      - ./data:/app/data
      - ./output:/app/output
    networks:
      - finance_network
  
  ollama:
    image: ollama/ollama:latest
    container_name: finance-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - finance_network

volumes:
  neo4j_data:
  neo4j_logs:
  ollama_data:

networks:
  finance_network:
    driver: bridge
```

### 2. Deployment Commands
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

## Ansible Automated Deployment

### 1. Production Environment Initialization
```bash
# Edit inventory file
vim ansible/inventory/production

# Run initialization playbook
ansible-playbook ansible/init.yml -i ansible/inventory/production --ask-become-pass

# Deploy application
ansible-playbook ansible/setup.yml -i ansible/inventory/production
```

### 2. Ansible Configuration Files
**ansible/inventory/production**:
```ini
[finance_servers]
finance-prod-01 ansible_host=your_server_ip

[finance_servers:vars]
ansible_user=ubuntu
ansible_ssh_private_key_file=~/.ssh/your_key.pem
```

**ansible/group_vars/all.yml**:
```yaml
# Application configuration
app_name: my_finance
app_version: latest
app_port: 8000

# Neo4j configuration
neo4j_version: 5.15
neo4j_memory_heap: 4g
neo4j_password: "{{ vault_neo4j_password }}"

# Security configuration
firewall_allowed_ports:
  - 22    # SSH
  - 80    # HTTP
  - 443   # HTTPS
  - 8000  # App
```

## Kubernetes Deployment (Enterprise Level)

### 1. Kubernetes Configuration Files

**k8s/namespace.yaml**:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: finance
```

**k8s/neo4j-deployment.yaml**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: neo4j
  namespace: finance
spec:
  replicas: 1
  selector:
    matchLabels:
      app: neo4j
  template:
    metadata:
      labels:
        app: neo4j
    spec:
      containers:
      - name: neo4j
        image: neo4j:5.15
        ports:
        - containerPort: 7474
        - containerPort: 7687
        env:
        - name: NEO4J_AUTH
          value: neo4j/finance123
        - name: NEO4J_PLUGINS
          value: '["apoc"]'
        volumeMounts:
        - name: neo4j-data
          mountPath: /data
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
      volumes:
      - name: neo4j-data
        persistentVolumeClaim:
          claimName: neo4j-pvc
```

**k8s/app-deployment.yaml**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: finance-app
  namespace: finance
spec:
  replicas: 3
  selector:
    matchLabels:
      app: finance-app
  template:
    metadata:
      labels:
        app: finance-app
    spec:
      containers:
      - name: app
        image: finance-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: NEO4J_URI
          value: bolt://neo4j-service:7687
        - name: CLAUDE_API_KEY
          valueFrom:
            secretKeyRef:
              name: finance-secrets
              key: claude-api-key
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1"
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
```

### 2. Deploy to Kubernetes
```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets
kubectl create secret generic finance-secrets \
  --from-literal=claude-api-key=your_claude_key \
  -n finance

# Deploy Neo4j
kubectl apply -f k8s/neo4j-pvc.yaml
kubectl apply -f k8s/neo4j-deployment.yaml
kubectl apply -f k8s/neo4j-service.yaml

# Deploy application
kubectl apply -f k8s/app-deployment.yaml
kubectl apply -f k8s/app-service.yaml

# Check deployment status
kubectl get pods -n finance
kubectl get services -n finance
```

## Environment Configuration Management

### 1. Environment Variable Template
**.env.production**:
```bash
# Database configuration
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_secure_password

# LLM API configuration
CLAUDE_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_api_key

# Data source API
ALPHA_VANTAGE_KEY=your_alpha_vantage_key
FINNHUB_API_KEY=your_finnhub_key

# Application configuration  
APP_ENV=production
DEBUG=False
LOG_LEVEL=INFO
MAX_WORKERS=4

# Security configuration
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=your_domain.com,api.your_domain.com
```

### 2. Configuration Validation Script
```python
import os
import sys

def validate_environment():
    """Validate production environment configuration"""
    
    required_vars = [
        'NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD',
        'CLAUDE_API_KEY', 'SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    # Validate database connection
    try:
        from neomodel import config, db
        config.DATABASE_URL = os.getenv('NEO4J_URI')
        db.cypher_query("RETURN 1")
        print("✓ Neo4j connection successful")
    except Exception as e:
        print(f"✗ Neo4j connection failed: {e}")
        sys.exit(1)
    
    print("✓ Environment configuration validation passed")

if __name__ == "__main__":
    validate_environment()
```

## Monitoring and Logging

### 1. Logging Configuration
```yaml  
# docker-compose.override.yml (production environment)
version: '3.8'

services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "5"
    volumes:
      - ./logs:/app/logs

  neo4j:
    logging:
      driver: "json-file" 
      options:
        max-size: "100m"
        max-file: "3"
```

### 2. Health Check Endpoint
```python
from fastapi import FastAPI, HTTPException
from datetime import datetime
import asyncio

app = FastAPI()

@app.get("/api/v1/health")
async def health_check():
    """System health check"""
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }
    
    # Check Neo4j connection
    try:
        from neomodel import db
        db.cypher_query("RETURN 1")
        health_status["components"]["neo4j"] = {
            "status": "healthy",
            "response_time_ms": 50
        }
    except Exception as e:
        health_status["components"]["neo4j"] = {
            "status": "unhealthy", 
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check disk space
    import shutil
    disk_usage = shutil.disk_usage("/")
    free_space_gb = disk_usage.free / (1024**3)
    
    if free_space_gb < 5:  # Less than 5GB
        health_status["status"] = "degraded"
    
    health_status["components"]["disk"] = {
        "free_space_gb": round(free_space_gb, 2)
    }
    
    if health_status["status"] != "healthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status
```

## Data Backup Strategy

### 1. Neo4j Data Backup
```bash
#!/bin/bash
# backup_neo4j.sh

BACKUP_DIR="/backup/neo4j"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="neo4j_backup_${DATE}"

# Create backup directory
mkdir -p ${BACKUP_DIR}

# Execute backup
docker exec finance-neo4j neo4j-admin database dump \
  --database=neo4j \
  --to-path=/data/dumps/${BACKUP_NAME}.dump

# Copy to backup directory
docker cp finance-neo4j:/data/dumps/${BACKUP_NAME}.dump ${BACKUP_DIR}/

# Compress backup
gzip ${BACKUP_DIR}/${BACKUP_NAME}.dump

# Delete backups older than 7 days
find ${BACKUP_DIR} -name "*.gz" -mtime +7 -delete

echo "Backup completed: ${BACKUP_DIR}/${BACKUP_NAME}.dump.gz"
```

### 2. Automated Backup Schedule
```bash
# Add to crontab
crontab -e

# Execute backup daily at 2 AM
0 2 * * * /path/to/backup_neo4j.sh >> /var/log/neo4j_backup.log 2>&1
```

## Troubleshooting

### Common Deployment Issues

1. **Neo4j startup failure**
```bash
# Check memory configuration
docker logs finance-neo4j

# Adjust memory limits
# Modify in docker-compose.yml:
# NEO4J_dbms_memory_heap_max__size=1g
```

2. **Application database connection failure**
```bash
# Check network connectivity
docker network ls
docker network inspect finance_finance_network

# Verify database reachability
docker exec finance-app ping neo4j
```

3. **Port conflicts**
```bash
# Check port usage
netstat -tulpn | grep :7474

# Modify port mapping
# Change ports in docker-compose.yml
```

---

*Deployment configuration is continuously optimized to ensure system stability and maintainability*