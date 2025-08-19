# Templates Directory

This directory contains template files used throughout the system for various outputs and configurations.

## Template Categories

### DCF Analysis Templates (`dcf/`)
- **`dcf_valuation_prompt_en.md`** - English DCF valuation analysis template for LLM prompting
- **`m7_enhanced_dcf_config.yml`** - Enhanced configuration for Magnificent 7 DCF analysis

## Template Usage

Templates are used by:
- **DCF Engine** - For generating valuation reports and analysis
- **LLM Integration** - As prompts for financial analysis generation
- **Build System** - For consistent configuration across different scopes (M7, N100, etc.)

## Template Structure

Templates use placeholder syntax for dynamic content:
- `{ticker}` - Company ticker symbol
- `{company_name}` - Full company name
- `{financial_data}` - JSON formatted financial data
- `{semantic_search_results}` - Results from SEC document retrieval

## Adding New Templates

When adding new templates:
1. Use descriptive filenames indicating purpose and language
2. Include proper placeholder documentation
3. Update this README with template descriptions
4. Test templates with actual data before committing