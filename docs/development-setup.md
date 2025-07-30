# 开发环境设置

## 基础环境要求

### 系统要求
- **操作系统**: macOS 12+ / Ubuntu 20.04+ / Windows 10+
- **Python**: 3.12+
- **内存**: 8GB+ (推荐16GB+)
- **硬盘**: 20GB+ 可用空间

### 核心依赖
- **Neo4j**: 5.0+ (图数据库)
- **Docker**: 20.10+ (容器化部署)
- **Git**: 2.30+ (版本控制)

## 开发环境配置

### 1. 克隆项目
```bash
git clone git@github.com:wangzitian0/my_finance.git
cd my_finance
```

### 2. Python环境设置
```bash
# 安装pipenv（如果尚未安装）
pip install pipenv

# 创建虚拟环境并安装依赖
pipenv install

# 激活虚拟环境
pipenv shell

# 验证Python版本
python --version  # 应该是3.12+
```

### 3. Neo4j数据库设置

#### 选项A：Docker方式（推荐）
```bash
# 运行Neo4j容器
docker run -d \
  --name neo4j-finance \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/finance123 \
  -e NEO4J_PLUGINS='["apoc"]' \
  -v neo4j_data:/data \
  -v neo4j_logs:/logs \
  neo4j:5.15

# 验证连接
curl http://localhost:7474
```

#### 选项B：Ansible自动化部署
```bash
# 需要sudo权限进行系统设置
ansible-playbook ansible/init.yml --ask-become-pass

# 部署Neo4j和相关配置
ansible-playbook ansible/setup.yml
```

### 4. 环境变量配置
```bash
# 创建.env文件
cp .env.template .env

# 编辑配置文件
vim .env
```

**.env配置示例**：
```bash
# Neo4j连接配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=finance123

# LLM配置
OPENAI_API_KEY=your_openai_key_here
CLAUDE_API_KEY=your_claude_key_here

# 数据源API配置
ALPHA_VANTAGE_KEY=your_alpha_vantage_key
FINNHUB_API_KEY=your_finnhub_key

# 开发模式设置
DEBUG=True
LOG_LEVEL=INFO
```

## IDE配置

### GoLand/PyCharm配置

#### 1. Python解释器设置
```bash
# 找到pipenv的Python路径
pipenv --py
# 输出类似：/Users/username/.local/share/virtualenvs/my_finance-xyz/bin/python

# 在IDE中设置此路径作为项目解释器
```

#### 2. 代码风格配置
- **格式化工具**: Black
- **导入排序**: isort  
- **代码检查**: pylint, mypy
- **文档风格**: Google docstring format

#### 3. 运行配置
创建运行配置用于常用任务：
```yaml
# 数据收集任务
Name: Run Data Collection
Script: run_job.py
Parameters: yfinance_nasdaq100.yml
Working directory: $ProjectFileDir$

# 测试运行
Name: Run Tests
Script: pytest
Parameters: tests/ -v
Working directory: $ProjectFileDir$
```

### VS Code配置

#### 1. 推荐扩展
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.pylint", 
    "ms-python.black-formatter",
    "ms-python.isort",
    "neo4j.cypher",
    "github.copilot"
  ]
}
```

#### 2. 工作区设置(.vscode/settings.json)
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "editor.formatOnSave": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/.mypy_cache": true
  }
}
```

## 本地LLM设置

### 1. Ollama安装和配置
```bash
# 安装Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 下载推荐模型
ollama pull mistral:7b
ollama pull qwen2.5-coder:7b

# 验证安装
ollama list
```

### 2. Open WebUI设置（可选）
```bash
# 安装开发依赖
pipenv install --dev

# 启动Web界面
open-webui serve

# 访问 http://localhost:8080
```

## 数据目录结构

### 创建必要目录
```bash
# 数据存储目录
mkdir -p data/{original,processed,cache}
mkdir -p data/original/{yfinance,sec_edgar,news,analyst_reports}
mkdir -p data/config
mkdir -p data/log

# 文档和输出目录  
mkdir -p docs/assets
mkdir -p output/{reports,visualizations}

# 测试数据目录
mkdir -p tests/fixtures
```

### 权限设置
```bash
# 确保数据目录可写
chmod -R 755 data/
chmod -R 755 output/

# 日志目录权限
chmod -R 644 data/log/
```

## 开发工作流

### 1. 分支管理
```bash
# 创建功能分支
git checkout -b feature/your-feature-name

# 日常提交
git add .
git commit -m "Brief description

Fixes #issue-number

PR: https://github.com/wangzitian0/my_finance/pull/TBD"

# 推送和创建PR
git push -u origin feature/your-feature-name
gh pr create --title "Feature: Description - Fixes #issue" --body "Summary..."
```

### 2. 代码质量检查
```bash
# 运行代码格式化
black .
isort .

# 运行代码检查
pylint src/
mypy src/

# 运行测试
pytest tests/ -v --cov=src/
```

### 3. 数据收集测试
```bash
# 测试Yahoo Finance连接
python run_job.py test_config.yml

# 验证Neo4j连接
python -c "from ETL.models import Stock; print('Neo4j connected!')"

# 检查数据目录
ls -la data/original/yfinance/
```

## 故障排除

### 常见问题

#### 1. Neo4j连接失败
```bash
# 检查Neo4j状态
docker ps | grep neo4j

# 查看日志
docker logs neo4j-finance

# 重启容器
docker restart neo4j-finance
```

#### 2. Python依赖问题
```bash
# 清理并重建环境
pipenv --rm
pipenv install

# 手动安装问题包
pipenv install package_name --verbose
```

#### 3. 权限问题
```bash
# 检查文件权限
ls -la data/

# 修复权限
sudo chown -R $USER:$USER data/
chmod -R 755 data/
```

#### 4. 内存不足
```bash
# 监控内存使用
htop

# 调整Neo4j内存限制
# 编辑docker run命令添加：
# -e NEO4J_dbms_memory_heap_initial__size=512m
# -e NEO4J_dbms_memory_heap_max__size=2g
```

## 性能优化建议

### 1. 开发机器配置
- **SSD硬盘**: 提高数据库I/O性能
- **16GB+内存**: 支持大规模数据处理
- **多核CPU**: 并行数据处理

### 2. Neo4j优化
```bash
# 调整堆内存大小
NEO4J_dbms_memory_heap_max__size=4g

# 启用并行GC
NEO4J_dbms_jvm_additional=-XX:+UseG1GC
```

### 3. Python优化
```bash
# 使用UV作为包管理器（更快）
pip install uv
uv pip install -r requirements.txt

# 启用字节码缓存
export PYTHONOPTIMIZE=1
```

---

*开发环境配置会随着项目需求变化持续更新*