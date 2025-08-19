# LLM Configuration and Models

This directory contains LLM (Large Language Model) configurations, prompts, and model settings.

## Purpose

LLM-related configurations for:
- Model selection and parameter settings
- Prompt templates and engineering
- API configurations and endpoints
- Model performance tuning

## Directory Structure

```
llm/
├── configs/           # Model configuration files
├── prompts/          # Prompt templates and engineering
├── models/           # Local model configurations
└── benchmarks/       # Performance benchmarking data
```

## Key Components

### Model Configurations
- **Ollama Settings**: Local model configurations
- **API Configurations**: External LLM API settings
- **Model Parameters**: Temperature, max tokens, etc.
- **Performance Profiles**: Speed vs accuracy trade-offs

### Prompt Engineering
- **DCF Analysis Prompts**: Financial analysis templates
- **SEC Document Prompts**: Document processing templates
- **Graph RAG Prompts**: Knowledge retrieval templates
- **Report Generation Prompts**: Output formatting templates

## Supported Models

### Local Models (via Ollama)
- **gpt-oss:20b** - General-purpose analysis
- **deepseek-r1:1.5b** - Fast testing and development
- Custom fine-tuned models for financial analysis

### API Models
- OpenAI GPT series (configurable)
- Anthropic Claude (configurable)
- Other compatible API endpoints

## Usage

LLM configurations are used by:
- `dcf_engine/pure_llm_dcf.py` - Main DCF analysis
- `dcf_engine/ollama_client.py` - Local model interface
- Graph RAG system - Enhanced retrieval and generation
- Automated report generation workflows

## Configuration Management

### Environment-Based
- Development: Fast, local models
- Testing: Balanced speed/accuracy models  
- Production: High-accuracy models

### Performance Tuning
- Token limit optimization
- Temperature and sampling settings
- Batch processing configurations
- Caching and optimization strategies

## Best Practices

1. **Prompt Versioning**: Track prompt changes and performance
2. **Model Benchmarking**: Regular performance evaluation
3. **Cost Management**: Monitor API usage and costs
4. **Quality Control**: Validate LLM outputs for accuracy
5. **Fallback Strategies**: Handle model failures gracefully

## Development

When working with LLM configurations:
- Test changes with representative datasets
- Document prompt modifications and rationale
- Benchmark performance before production deployment
- Consider cost implications of model choices
- Maintain backwards compatibility where possible