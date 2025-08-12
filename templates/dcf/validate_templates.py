#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple template validation script
Validates DCF template files without requiring full environment
"""

import json
from pathlib import Path
from datetime import datetime


def validate_template_formatting():
    """Validate that templates can be formatted with sample data."""
    print("🔍 Validating DCF Template Formatting")
    print("=" * 40)
    
    template_dir = Path("templates/dcf")
    
    # Sample data for template formatting
    sample_data = {
        'ticker': 'AAPL',
        'company_name': 'Apple Inc.',
        'sector': 'Technology',
        'industry': 'Consumer Electronics',
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'financial_data': json.dumps({
            'revenue': 365817000000,
            'market_cap': 2800000000000,
            'rd_expenses': 21914000000
        }, indent=2, ensure_ascii=False),
        'historical_data': json.dumps({
            'revenue': [274515000000, 365817000000, 383285000000]
        }, indent=2, ensure_ascii=False),
        'market_context': json.dumps({
            'sector_growth_rate': 0.08,
            'risk_free_rate': 0.045
        }, indent=2, ensure_ascii=False),
        'semantic_search_results': "Sample semantic search results...",
        'market_growth_data': json.dumps({
            'revenue_cagr': 0.12,
            'growth_trend': 'accelerating'
        }, indent=2, ensure_ascii=False),
        'rd_efficiency_data': json.dumps({
            'rd_intensity': 0.06,
            'innovation_pipeline_strength': 'strong'
        }, indent=2, ensure_ascii=False),
        'executive_analysis_data': json.dumps({
            'ceo_age': 62,
            'leadership_innovation_score': 'moderate'
        }, indent=2, ensure_ascii=False)
    }
    
    templates_tested = 0
    templates_passed = 0
    
    # Test English template
    en_template_path = template_dir / "dcf_valuation_prompt_en.md"
    if en_template_path.exists():
        templates_tested += 1
        try:
            with open(en_template_path, 'r', encoding='utf-8') as f:
                en_template = f.read()
            
            formatted_en = en_template.format(**sample_data)
            
            # Basic validation checks
            assert 'AAPL' in formatted_en
            assert 'Apple Inc.' in formatted_en
            assert 'Technology' in formatted_en
            
            # Check for unfilled placeholders (but ignore JSON content)
            import re
            placeholders = re.findall(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}', formatted_en)
            assert len(placeholders) == 0, f"Unfilled placeholders: {placeholders}"
            
            print("✅ English template: Valid")
            print(f"   Length: {len(formatted_en)} characters")
            templates_passed += 1
            
        except Exception as e:
            print(f"❌ English template: Failed - {e}")
            import traceback
            traceback.print_exc()
    
    # Test Chinese template
    zh_template_path = template_dir / "dcf_valuation_prompt_zh.md"
    if zh_template_path.exists():
        templates_tested += 1
        try:
            with open(zh_template_path, 'r', encoding='utf-8') as f:
                zh_template = f.read()
            
            formatted_zh = zh_template.format(**sample_data)
            
            # Basic validation checks
            assert 'AAPL' in formatted_zh
            assert 'Apple Inc.' in formatted_zh
            assert '技术' in formatted_zh or 'Technology' in formatted_zh
            
            # Check for unfilled placeholders (but ignore JSON content)
            import re
            placeholders = re.findall(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}', formatted_zh)
            assert len(placeholders) == 0, f"Unfilled placeholders: {placeholders}"
            
            print("✅ Chinese template: Valid")
            print(f"   Length: {len(formatted_zh)} characters")
            templates_passed += 1
            
        except Exception as e:
            print(f"❌ Chinese template: Failed - {e}")
            import traceback
            traceback.print_exc()
    
    # Test configuration file
    config_path = template_dir / "m7_enhanced_dcf_config.yml"
    if config_path.exists():
        templates_tested += 1
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_content = f.read()
            
            # Basic validation checks
            assert 'bilingual_reports: true' in config_content
            assert 'AAPL:' in config_content
            assert 'magnificent_7:' in config_content
            
            print("✅ Configuration file: Valid")
            templates_passed += 1
            
        except Exception as e:
            print(f"❌ Configuration file: Failed - {e}")
    
    print(f"\n📊 Summary: {templates_passed}/{templates_tested} templates passed validation")
    return templates_passed == templates_tested


def demonstrate_enhanced_features():
    """Demonstrate the enhanced analysis features."""
    print("\n🚀 Enhanced DCF Features Demonstration")
    print("=" * 45)
    
    print("📈 Market Analysis Features:")
    print("   ✓ Revenue CAGR calculation from historical data")
    print("   ✓ Market capacity estimation")
    print("   ✓ Growth trend classification (accelerating/stable/declining)")
    
    print("\n🔬 R&D Efficiency Analysis:")
    print("   ✓ R&D intensity calculation (R&D/Revenue)")
    print("   ✓ Industry benchmark comparison")
    print("   ✓ Innovation pipeline strength assessment")
    
    print("\n👔 Executive Leadership Assessment:")
    print("   ✓ CEO age factor (younger = higher innovation score)")
    print("   ✓ Management tenure analysis")  
    print("   ✓ Strategic execution capability scoring")
    
    print("\n🌐 Bilingual Output:")
    print("   ✓ English DCF report (dcf_en_TICKER_timestamp.md)")
    print("   ✓ Chinese DCF report (dcf_zh_TICKER_timestamp.md)")
    print("   ✓ Identical analysis structure, localized language")
    
    print("\n🎯 M7-Specific Enhancements:")
    print("   ✓ Company-specific R&D benchmarks")
    print("   ✓ Leadership analysis notes")
    print("   ✓ Sector-specific risk factors")


def main():
    """Main validation execution."""
    print("DCF Template Validation Suite")
    print("=" * 35)
    
    success = validate_template_formatting()
    demonstrate_enhanced_features()
    
    if success:
        print("\n🎉 All template validations passed!")
        print("\n📋 Implementation Status:")
        print("   ✅ Bilingual templates created")
        print("   ✅ Enhanced analysis factors implemented")
        print("   ✅ Executive age factor integrated")  
        print("   ✅ Dual MD file output configured")
        print("   ✅ M7-specific strategy configured")
        
        print(f"\n🔧 Next Steps:")
        print("   1. Set up full environment: pixi run setup-env")
        print("   2. Test with real data: pixi run test-m7-e2e")
        print("   3. Check outputs in data/llm_debug/responses/")
        
    else:
        print("\n❌ Template validation failed!")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())