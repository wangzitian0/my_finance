# API文档

## Graph RAG问答API

### 端点概览
```
POST /api/v1/ask          # 智能问答
GET  /api/v1/valuation    # 获取DCF估值
POST /api/v1/analyze      # 深度分析
GET  /api/v1/health       # 系统健康检查
```

### 1. 智能问答接口

#### POST /api/v1/ask
**描述**: 基于Graph RAG的智能投资问答

**请求格式**:
```json
{
  "question": "根据最近的新闻，苹果公司的DCF估值如何？",
  "ticker": "AAPL",
  "analysis_depth": "detailed",
  "include_reasoning": true
}
```

**响应格式**:
```json
{
  "answer": "基于最新数据分析，苹果公司当前DCF估值为...",
  "confidence_score": 0.85,
  "reasoning_chain": [...],
  "data_sources": [...],
  "valuation_summary": {
    "intrinsic_value": 185.50,
    "current_price": 178.20,
    "upside_potential": 4.1
  }
}
```

### 2. DCF估值接口

#### GET /api/v1/valuation/{ticker}
**描述**: 获取最新DCF估值结果

**路径参数**:
- `ticker`: 股票代码 (如: AAPL, MSFT)

**查询参数**:
- `include_sensitivity`: 是否包含敏感性分析 (default: false)
- `refresh`: 是否强制重新计算 (default: false)

**响应示例**:
```json
{
  "ticker": "AAPL",
  "valuation_date": "2025-07-30T10:30:00Z",
  "intrinsic_value": 185.50,
  "current_price": 178.20,
  "upside_downside_pct": 4.1,
  "bankruptcy_probability": 0.02,
  "model_assumptions": {
    "wacc": 0.089,
    "terminal_growth_rate": 0.025,
    "projection_years": 5
  },
  "sensitivity_analysis": {
    "wacc_sensitivity": [...],
    "growth_sensitivity": [...]
  }
}
```

## 数据收集API

### 3. 手动数据更新

#### POST /api/v1/data/refresh
**描述**: 触发特定股票的数据更新

**请求格式**:
```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL"],
  "data_sources": ["sec", "yfinance", "news"],
  "priority": "high"
}
```

**响应格式**:
```json
{
  "job_id": "refresh_20250730_103045",
  "status": "queued",
  "estimated_completion": "2025-07-30T10:45:00Z",
  "tickers_count": 3
}
```

## 系统监控API

### 4. 健康检查

#### GET /api/v1/health
**描述**: 系统组件健康状态检查

**响应格式**:
```json
{
  "status": "healthy",
  "timestamp": "2025-07-30T10:30:00Z",
  "components": {
    "neo4j": {
      "status": "healthy",
      "response_time_ms": 45,
      "last_check": "2025-07-30T10:29:55Z"
    },
    "llm_service": {
      "status": "healthy", 
      "model": "claude-3-haiku",
      "response_time_ms": 1250
    },
    "data_pipeline": {
      "status": "healthy",
      "last_update": "2025-07-30T09:15:00Z",
      "pending_jobs": 2
    }
  }
}
```

## 错误处理

### 标准错误格式
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid ticker symbol provided",
    "details": {
      "field": "ticker",
      "provided_value": "INVALID", 
      "valid_examples": ["AAPL", "MSFT", "GOOGL"]
    },
    "request_id": "req_20250730_103045_abc123"
  }
}
```

### 常见错误码
- `VALIDATION_ERROR`: 请求参数验证失败
- `TICKER_NOT_FOUND`: 股票代码不存在
- `INSUFFICIENT_DATA`: 数据不足以进行分析
- `RATE_LIMIT_EXCEEDED`: 请求频率超限
- `INTERNAL_ERROR`: 系统内部错误

## 认证和限流

### API Key认证
```bash
curl -H "Authorization: Bearer your_api_key_here" \
     -H "Content-Type: application/json" \
     https://api.myfinance.com/v1/ask
```

### 请求限制
- **免费版**: 100次/小时
- **专业版**: 1000次/小时  
- **企业版**: 无限制

---

*API文档持续更新，以反映最新功能*