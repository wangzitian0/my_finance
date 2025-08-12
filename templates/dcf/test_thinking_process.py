#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script for Enhanced DCF with Thinking Process Output

This script demonstrates the new thinking process and SEC document retrieval
capabilities in the DCF analysis system.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dcf_engine.llm_dcf_generator import LLMDCFGenerator


def test_thinking_process_output():
    """Test the enhanced thinking process output for DCF generation."""
    print("🧠 Testing Enhanced DCF Thinking Process Output")
    print("=" * 55)
    
    # Initialize DCF generator
    try:
        dcf_generator = LLMDCFGenerator()
        dcf_generator.debug_mode = True  # Ensure debug mode is enabled
        print("✅ DCF Generator initialized with debug mode enabled")
    except Exception as e:
        print(f"❌ Failed to initialize DCF Generator: {e}")
        return False
    
    # Test with Apple to demonstrate SEC document retrieval
    test_ticker = "AAPL"
    print(f"\n📊 Generating DCF with thinking process for {test_ticker}")
    print("-" * 50)
    
    # Enhanced financial data with executive info for age factor testing
    financial_data = {
        "company_info": {
            "name": "Apple Inc.",
            "sector": "Technology", 
            "industry": "Consumer Electronics",
            "cik": "0000320193"
        },
        "financials": {
            "revenue": 365_817_000_000,
            "net_income": 94_680_000_000,
            "free_cash_flow": 92_953_000_000,
            "research_development": 21_914_000_000,
            "total_debt": 124_719_000_000,
            "cash": 62_639_000_000
        },
        "historical": {
            "revenue": [274_515_000_000, 294_135_000_000, 365_817_000_000, 383_285_000_000, 394_328_000_000],
            "rd_expenses": [14_236_000_000, 16_217_000_000, 18_752_000_000, 21_914_000_000, 26_251_000_000],
            "free_cash_flow": [69_391_000_000, 77_434_000_000, 92_953_000_000, 99_584_000_000, 111_443_000_000]
        },
        "executive_info": {
            "ceo_name": "Tim Cook",
            "ceo_age": 62,
            "ceo_tenure": 12,
            "succession_planning": "Moderate"
        }
    }
    
    market_context = {
        "sector_growth_rate": 0.08,
        "risk_free_rate": 0.045,
        "market_risk_premium": 0.065,
        "beta": 1.2
    }
    
    # Generate comprehensive report with thinking process
    try:
        print("🔍 Starting DCF analysis with enhanced semantic retrieval...")
        result = dcf_generator.generate_comprehensive_dcf_report(
            ticker=test_ticker,
            financial_data=financial_data,
            market_context=market_context
        )
        
        if result['success']:
            print("✅ DCF analysis completed successfully!")
            
            # Display thinking process summary
            print(f"\n🧠 Thinking Process Summary:")
            print(f"   📄 SEC Documents Analyzed: {result['debug_info']['semantic_results_count']}")
            
            # Show retrieved documents
            semantic_results = result['debug_info']['semantic_results_details']
            print(f"\n📋 Retrieved SEC Documents:")
            for i, doc in enumerate(semantic_results[:3], 1):  # Show first 3 documents
                print(f"   {i}. {doc.get('source', 'Unknown')}")
                print(f"      📊 Score: {doc.get('similarity_score', 0):.3f}")
                print(f"      📝 Type: {doc.get('document_type', 'N/A')}")
                print(f"      🎯 Why Relevant: {doc.get('thinking_process', 'N/A')}")
                print(f"      📄 Content: {doc.get('content', '')[:100]}...")
                print()
            
            # Show generated components
            components = result.get('components', {})
            print(f"🎯 Generated Analysis Components:")
            for comp_name, comp_data in components.items():
                status = "✅" if comp_data.get('success', False) else "❌"
                print(f"   {status} {comp_name.replace('_', ' ').title()}")
            
            # Show bilingual report status
            dcf_component = components.get('dcf_valuation', {})
            if 'reports' in dcf_component:
                reports = dcf_component['reports']
                print(f"\n🌐 Bilingual Reports:")
                if 'english' in reports:
                    en_success = reports['english'].get('success', False)
                    print(f"   🇺🇸 English: {'✅ Generated' if en_success else '❌ Failed'}")
                if 'chinese' in reports:
                    zh_success = reports['chinese'].get('success', False)
                    print(f"   🇨🇳 Chinese: {'✅ Generated' if zh_success else '❌ Failed'}")
            
            # Show file locations
            if 'thinking_process_files' in result['debug_info']:
                files = result['debug_info']['thinking_process_files']
                print(f"\n📁 Detailed Files Generated:")
                print(f"   🧠 Thinking Process: {files.get('semantic_retrieval', 'N/A')}")
                print(f"   📊 Detailed Results: {files.get('detailed_results', 'N/A')}")
            
            return True
            
        else:
            print(f"❌ DCF analysis failed:")
            for error in result.get('errors', []):
                print(f"   • {error}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False


def demonstrate_output_structure():
    """Demonstrate the structure of thinking process outputs."""
    print(f"\n📋 Build Output Structure:")
    print("-" * 30)
    
    build_structure = """
data/stage_99_build/
└── build_YYYYMMDD_HHMMSS/
    └── dcf_debug/
        ├── THINKING_PROCESS_AAPL.md      # 🧠 Step-by-step analysis
        ├── SEC_DOCUMENTS_ANALYSIS_AAPL.json  # 📊 Detailed SEC data  
        └── BUILD_SUMMARY_AAPL.txt        # 📋 Quick summary

data/llm_debug/
├── thinking_process/
│   └── semantic_retrieval_AAPL_timestamp.txt  # 🔍 Search process
├── semantic_results/
│   └── retrieved_docs_AAPL_timestamp.json     # 📄 Full documents
└── responses/
    ├── dcf_en_AAPL_timestamp.md               # 🇺🇸 English report
    └── dcf_zh_AAPL_timestamp.md               # 🇨🇳 Chinese report
"""
    
    print(build_structure)
    
    print("📄 Key Output Files:")
    print("   🧠 THINKING_PROCESS_*.md: Complete step-by-step analysis reasoning")
    print("   📊 SEC_DOCUMENTS_ANALYSIS_*.json: Detailed document metadata and content")
    print("   📋 BUILD_SUMMARY_*.txt: Quick overview of what was generated")
    print("   🔍 semantic_retrieval_*.txt: Search query execution log")
    print("   🌐 Bilingual DCF reports in both English and Chinese")


def main():
    """Main test execution."""
    print("🧠 Enhanced DCF Thinking Process Test Suite")
    print("=" * 50)
    
    success = test_thinking_process_output()
    demonstrate_output_structure()
    
    if success:
        print(f"\n🎉 All tests passed! Enhanced thinking process is working.")
        print(f"\n🔍 What You Can Now See:")
        print(f"   ✅ Exact SEC documents retrieved for each company")
        print(f"   ✅ Why each document was selected (thinking process)")
        print(f"   ✅ Similarity scores and content previews")
        print(f"   ✅ How each document impacts DCF analysis")
        print(f"   ✅ Step-by-step semantic search execution")
        print(f"   ✅ Complete bilingual report generation")
        
        print(f"\n📁 Check These Locations for Output:")
        print(f"   📊 Build debug: data/stage_99_build/build_*/dcf_debug/")
        print(f"   🧠 Thinking logs: data/llm_debug/thinking_process/")
        print(f"   📄 Retrieved docs: data/llm_debug/semantic_results/")
        print(f"   📝 Final reports: data/llm_debug/responses/")
        
    else:
        print(f"\n❌ Tests failed. Check the error messages above.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())