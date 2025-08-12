#!/usr/bin/env python3
"""
Quick test script for LLM DCF Generator
"""

import sys
from dcf_engine.llm_dcf_generator import LLMDCFGenerator

def main():
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    
    print(f"🧪 Testing LLM DCF Generator for {ticker}...")
    
    try:
        # Initialize generator
        generator = LLMDCFGenerator()
        
        # Generate comprehensive DCF report
        result = generator.generate_comprehensive_dcf_report(ticker)
        
        if result['success']:
            print("✅ LLM DCF generation successful!")
            print(f"📄 Components generated: {list(result['components'].keys())}")
            
            # Print some sample output
            if 'dcf_valuation' in result['components']:
                dcf_data = result['components']['dcf_valuation']
                print(f"📊 DCF Response Preview:")
                print(dcf_data.get('response', '')[:500] + '...')
        else:
            print("❌ LLM DCF generation failed!")
            print(f"Errors: {result['errors']}")
            
    except Exception as e:
        print(f"❌ Error testing LLM DCF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
