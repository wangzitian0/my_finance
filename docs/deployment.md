# 部署指南

## 部署架构选择

### 1. 开发环境部署
**适用场景**: 本地开发、功能测试
**硬件要求**: 8GB+ RAM, 4核+ CPU
**部署方式**: Docker Compose

### 2. 生产环境部署  
**适用场景**: 正式投资分析使用
**硬件要求**: 16GB+ RAM, 8核+ CPU, SSD存储
**部署方式**: Kubernetes + Ansible

## Docker Compose部署（推荐用于开发）

### 1. 创建docker-compose.yml
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

### 2. 部署命令
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f app

# 停止服务
docker-compose down
```

## Ansible自动化部署

### 1. 生产环境初始化
```bash
# 编辑inventory文件
vim ansible/inventory/production

# 运行初始化playbook
ansible-playbook ansible/init.yml -i ansible/inventory/production --ask-become-pass

# 部署应用
ansible-playbook ansible/setup.yml -i ansible/inventory/production
```

### 2. Ansible配置文件
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
# 应用配置
app_name: my_finance
app_version: latest
app_port: 8000

# Neo4j配置
neo4j_version: 5.15
neo4j_memory_heap: 4g
neo4j_password: "{{ vault_neo4j_password }}"

# 安全配置
firewall_allowed_ports:
  - 22    # SSH
  - 80    # HTTP
  - 443   # HTTPS
  - 8000  # App
```

## Kubernetes部署（企业级）

### 1. Kubernetes配置文件

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

### 2. 部署到Kubernetes
```bash
# 创建命名空间
kubectl apply -f k8s/namespace.yaml

# 创建密钥
kubectl create secret generic finance-secrets \
  --from-literal=claude-api-key=your_claude_key \
  -n finance

# 部署Neo4j
kubectl apply -f k8s/neo4j-pvc.yaml
kubectl apply -f k8s/neo4j-deployment.yaml
kubectl apply -f k8s/neo4j-service.yaml

# 部署应用
kubectl apply -f k8s/app-deployment.yaml
kubectl apply -f k8s/app-service.yaml

# 检查部署状态
kubectl get pods -n finance
kubectl get services -n finance
```

## 环境配置管理

### 1. 环境变量模板
**.env.production**:
```bash
# 数据库配置
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_secure_password

# LLM API配置
CLAUDE_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_api_key

# 数据源API
ALPHA_VANTAGE_KEY=your_alpha_vantage_key
FINNHUB_API_KEY=your_finnhub_key

# 应用配置  
APP_ENV=production
DEBUG=False
LOG_LEVEL=INFO
MAX_WORKERS=4

# 安全配置
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=your_domain.com,api.your_domain.com
```

### 2. 配置验证脚本
```python
import os
import sys

def validate_environment():
    """验证生产环境配置"""
    
    required_vars = [
        'NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD',
        'CLAUDE_API_KEY', 'SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"错误: 缺少必需的环境变量: {', '.join(missing_vars)}")
        sys.exit(1)
    
    # 验证数据库连接
    try:
        from neomodel import config, db
        config.DATABASE_URL = os.getenv('NEO4J_URI')
        db.cypher_query("RETURN 1")
        print("✓ Neo4j连接成功")
    except Exception as e:
        print(f"✗ Neo4j连接失败: {e}")
        sys.exit(1)
    
    print("✓ 环境配置验证通过")

if __name__ == "__main__":
    validate_environment()
```

## 监控和日志

### 1. 日志配置
```yaml  
# docker-compose.override.yml (生产环境)
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

### 2. 健康检查端点
```python
from fastapi import FastAPI, HTTPException
from datetime import datetime
import asyncio

app = FastAPI()

@app.get("/api/v1/health")
async def health_check():
    """系统健康检查"""
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }
    
    # 检查Neo4j连接
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
    
    # 检查磁盘空间
    import shutil
    disk_usage = shutil.disk_usage("/")
    free_space_gb = disk_usage.free / (1024**3)
    
    if free_space_gb < 5:  # 少于5GB
        health_status["status"] = "degraded"
    
    health_status["components"]["disk"] = {
        "free_space_gb": round(free_space_gb, 2)
    }
    
    if health_status["status"] != "healthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status
```

## 数据备份策略

### 1. Neo4j数据备份
```bash
#!/bin/bash
# backup_neo4j.sh

BACKUP_DIR="/backup/neo4j"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="neo4j_backup_${DATE}"

# 创建备份目录
mkdir -p ${BACKUP_DIR}

# 执行备份
docker exec finance-neo4j neo4j-admin database dump \
  --database=neo4j \
  --to-path=/data/dumps/${BACKUP_NAME}.dump

# 复制到备份目录
docker cp finance-neo4j:/data/dumps/${BACKUP_NAME}.dump ${BACKUP_DIR}/

# 压缩备份
gzip ${BACKUP_DIR}/${BACKUP_NAME}.dump

# 删除7天前的备份
find ${BACKUP_DIR} -name "*.gz" -mtime +7 -delete

echo "备份完成: ${BACKUP_DIR}/${BACKUP_NAME}.dump.gz"
```

### 2. 自动化备份计划
```bash
# 添加到crontab
crontab -e

# 每日凌晨2点执行备份
0 2 * * * /path/to/backup_neo4j.sh >> /var/log/neo4j_backup.log 2>&1
```

## 故障排除

### 常见部署问题

1. **Neo4j启动失败**
```bash
# 检查内存配置
docker logs finance-neo4j

# 调整内存限制
# 在docker-compose.yml中修改:
# NEO4J_dbms_memory_heap_max__size=1g
```

2. **应用连接数据库失败**
```bash
# 检查网络连接
docker network ls
docker network inspect finance_finance_network

# 验证数据库可达性
docker exec finance-app ping neo4j
```

3. **端口冲突**
```bash
# 检查端口占用
netstat -tulpn | grep :7474

# 修改端口映射
# 在docker-compose.yml中修改端口
```

---

*部署配置持续优化以确保系统稳定性和可维护性*