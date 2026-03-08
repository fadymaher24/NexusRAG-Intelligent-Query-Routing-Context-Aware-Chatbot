#!/usr/bin/env python3
"""
Test semantic search on FAQs collection.
"""

import weaviate
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from app.repositories import FAQRepository


def test_semantic_search():
    print("\n" + "="*70)
    print("🧪 TESTING SEMANTIC SEARCH ON FAQs")
    print("="*70)
    
    repo = FAQRepository()
    repo.connect()
    
    # Test queries
    queries = [
        "What is your return policy?",
        "What is your turn policy?",  # Typo test
        "How do I send items back?",
        "refund timeframe",
        "How long for returns?",
        "shipping internationally",
        "payment methods accepted",
    ]
    
    for query in queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 70)
        
        try:
            results = repo.search(query, limit=3)
            
            if results:
                for i, faq in enumerate(results, 1):
                    print(f"\n{i}. Q: {faq.question}")
                    print(f"   A: {faq.answer[:100]}...")
                    print(f"   Type: {faq.faq_type}")
            else:
                print("   No results found")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    repo.disconnect()
    print("\n" + "="*70)
    print("✅ Testing complete!")
    print("="*70)


if __name__ == "__main__":
    test_semantic_search()
