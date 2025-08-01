#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Graph RAG System Demo

Interactive demonstration of the Graph RAG system for financial analysis.
"""

import logging
import sys
from pathlib import Path
import json
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from graph_rag import GraphRAGSystem

# Setup minimal logging for demo
logging.basicConfig(level=logging.WARNING)

class GraphRAGDemo:
    """
    Interactive demo of the Graph RAG system.
    """
    
    def __init__(self):
        """Initialize the demo."""
        print("🚀 Initializing Graph RAG System...")
        self.graph_rag = GraphRAGSystem()
        
        # Pre-defined demo queries
        self.demo_queries = {
            '1': {
                'query': "What is the DCF valuation for Apple?",
                'description': "Simple DCF valuation query"
            },
            '2': {
                'query': "Compare Apple and Microsoft financial performance",
                'description': "Financial comparison analysis"
            },
            '3': {
                'query': "What are the main risk factors for Tesla?",
                'description': "Risk analysis query"
            },
            '4': {
                'query': "Based on recent financial performance and news, should I invest in Amazon?",
                'description': "Complex multi-step reasoning query"
            },
            '5': {
                'query': "How does Meta perform compared to other technology companies?",
                'description': "Sector analysis query"
            }
        }
        
        print("✅ Graph RAG System ready!")
        
        # Check if embedding model is available
        if not self.graph_rag.semantic_embedding.model:
            print("⚠️  Note: Semantic embedding model not available.")
            print("   Install sentence-transformers for full functionality:")
            print("   pip install sentence-transformers")
    
    def run_interactive_demo(self):
        """Run interactive demonstration."""
        
        print("\n" + "="*60)
        print("🧠 GRAPH RAG FINANCIAL ANALYSIS DEMO")
        print("="*60)
        
        print("\nThis demo showcases the Graph RAG system's ability to:")
        print("• Answer complex financial questions")  
        print("• Perform multi-step reasoning")
        print("• Generate DCF valuations")
        print("• Analyze risks and market conditions")
        
        while True:
            self.show_menu()
            choice = input("\nEnter your choice (1-6, or 'q' to quit): ").strip()
            
            if choice.lower() == 'q':
                print("\n👋 Thank you for trying Graph RAG!")
                break
            elif choice == '6':
                self.custom_query_mode()
            elif choice in self.demo_queries:
                self.run_demo_query(choice)
            else:
                print("❌ Invalid choice. Please try again.")
    
    def show_menu(self):
        """Display the demo menu."""
        
        print("\n" + "-"*60)
        print("DEMO MENU")
        print("-"*60)
        
        for key, query_info in self.demo_queries.items():
            print(f"{key}. {query_info['description']}")
            print(f"   Query: \"{query_info['query']}\"")
        
        print("6. Enter custom query")
        print("q. Quit demo")
    
    def run_demo_query(self, choice: str):
        """Run a pre-defined demo query."""
        
        query_info = self.demo_queries[choice]
        query = query_info['query']
        description = query_info['description']
        
        print(f"\n🔍 Running: {description}")
        print(f"📝 Query: \"{query}\"")
        print("\n⏳ Processing...")
        
        try:
            # Get answer from Graph RAG system
            result = self.graph_rag.answer_question(query)
            
            # Display results
            self.display_result(result, query)
            
        except Exception as e:
            print(f"\n❌ Error processing query: {str(e)}")
            print("This might be due to missing dependencies or data.")
    
    def custom_query_mode(self):
        """Allow user to enter custom queries."""
        
        print("\n" + "="*50)
        print("CUSTOM QUERY MODE")
        print("="*50)
        
        print("Enter your financial analysis question.")
        print("Examples:")
        print("• 'What is Google's current valuation?'")
        print("• 'Compare Netflix and Disney stock performance'")
        print("• 'What are Microsoft's biggest risks?'")
        print("\nType 'back' to return to main menu.")
        
        while True:
            query = input("\n💭 Your question: ").strip()
            
            if query.lower() == 'back':
                break
            elif not query:
                print("Please enter a question.")
                continue
            
            print(f"\n🔍 Analyzing: \"{query}\"")
            print("⏳ Processing...")
            
            try:
                result = self.graph_rag.answer_question(query)
                self.display_result(result, query)
                
                # Ask if user wants to continue
                continue_choice = input("\n❓ Ask another question? (y/n): ").strip().lower()
                if continue_choice != 'y':
                    break
                    
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Please try a different question.")
    
    def display_result(self, result: dict, original_query: str):
        """Display the analysis result in a formatted way."""
        
        print("\n" + "="*60)
        print("📊 ANALYSIS RESULT")
        print("="*60)
        
        # Display the answer
        answer = result.get('answer', 'No answer generated')
        print(f"\n{answer}")
        
        # Display metadata
        print(f"\n📈 ANALYSIS METADATA:")
        print(f"Reasoning Type: {result.get('reasoning_type', 'unknown').title()}")
        print(f"Confidence Score: {result.get('confidence', 0):.1%}")
        
        # Display reasoning steps if available
        if result.get('reasoning_type') == 'multi_step':
            steps = result.get('steps', 0)
            print(f"Reasoning Steps: {steps}")
            
            if 'sub_questions' in result:
                print(f"\nSub-questions analyzed:")
                for i, sub_q in enumerate(result['sub_questions'], 1):
                    print(f"  {i}. {sub_q}")
        
        # Display sources if available
        sources = result.get('sources', [])
        if sources:
            print(f"\nData Sources: {', '.join(sources)}")
        
        # Display additional metadata
        metadata = result.get('metadata', {})
        if metadata:
            print(f"\nTechnical Details:")
            for key, value in metadata.items():
                if key not in ['query_type']:  # Skip redundant info
                    print(f"  {key.replace('_', ' ').title()}: {value}")
    
    def run_system_health_check(self):
        """Run a quick system health check."""
        
        print("\n🔧 SYSTEM HEALTH CHECK")
        print("-" * 30)
        
        # Check components
        checks = {
            'Graph RAG System': self.graph_rag is not None,
            'Semantic Embedding': self.graph_rag.semantic_embedding is not None,
            'Embedding Model': self.graph_rag.semantic_embedding.model is not None,
            'Query Generator': self.graph_rag.query_generator is not None,
            'Answer Generator': self.graph_rag.answer_generator is not None,
            'Reasoning Processor': self.graph_rag.reasoning_processor is not None
        }
        
        all_good = True
        for component, status in checks.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {component}")
            if not status:
                all_good = False
        
        if all_good:
            print("\n🎉 All systems operational!")
        else:
            print("\n⚠️  Some components may have issues.")
            print("This is normal if optional dependencies aren't installed.")
        
        return all_good


def main():
    """Main demo function."""
    
    try:
        # Initialize demo
        demo = GraphRAGDemo()
        
        # Run system health check
        print("\n🔧 Running system check...")
        health_ok = demo.run_system_health_check()
        
        if not health_ok:
            print("\n⚠️  Some components have issues, but demo can still run.")
            proceed = input("Continue with demo? (y/n): ").strip().lower()
            if proceed != 'y':
                print("Demo cancelled.")
                return
        
        # Run interactive demo
        demo.run_interactive_demo()
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        print("Please check your Python environment and dependencies.")


if __name__ == "__main__":
    main()