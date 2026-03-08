#!/usr/bin/env python3
"""
Simple working examples for Weaviate collections.
These examples use fetch_objects instead of semantic search.
"""

import weaviate
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from weaviate.classes.query import Filter


def main():
    print("\n" + "🚀 WEAVIATE COLLECTIONS - WORKING EXAMPLES")
    
    # Connect
    print("\n⚙️  Connecting to Weaviate...")
    client = weaviate.connect_to_local(port=8079, grpc_port=50050)
    print("✅ Connected!\n")
    
    try:
        # Example 1: List collections
        print("="*70)
        print("EXAMPLE 1: List All Collections")
        print("="*70)
        collections = client.collections.list_all()
        print(f"\nFound {len(collections)} collection(s):")
        for name in collections:
            collection = client.collections.get(name)
            result = collection.aggregate.over_all(total_count=True)
            print(f"  • {name}: {result.total_count:,} items")
        
        # Example 2: Get FAQs
        print("\n" + "="*70)
        print("EXAMPLE 2: Browse FAQs")
        print("="*70)
        faqs = client.collections.get("faqs")
        results = faqs.query.fetch_objects(limit=5)
        
        print(f"\nShowing 5 FAQs:\n")
        for i, obj in enumerate(results.objects, 1):
            props = obj.properties
            print(f"{i}. Q: {props['question']}")
            print(f"   A: {props['answer']}")
            print(f"   Category: {props['type']}\n")
        
        # Example 3: Filter products by gender
        print("="*70)
        print("EXAMPLE 3: Filter Products by Gender")
        print("="*70)
        products = client.collections.get("products")
        
        print("\n🔍 Finding Women's products...")
        results = products.query.fetch_objects(
            filters=Filter.by_property("gender").equal("Women"),
            limit=5
        )
        
        print(f"Found {len(results.objects)} results:\n")
        for i, obj in enumerate(results.objects, 1):
            props = obj.properties
            print(f"{i}. {props['productDisplayName']}")
            print(f"   ${props['price']} | {props['baseColour']} | {props['articleType']}\n")
        
        # Example 4: Filter by category
        print("="*70)
        print("EXAMPLE 4: Filter by Category")
        print("="*70)
        
        print("\n🔍 Finding Footwear...")
        results = products.query.fetch_objects(
            filters=Filter.by_property("masterCategory").equal("Footwear"),
            limit=5
        )
        
        print(f"Found {len(results.objects)} results:\n")
        for i, obj in enumerate(results.objects, 1):
            props = obj.properties
            print(f"{i}. {props['productDisplayName']}")
            print(f"   ${props['price']} | {props['gender']} | {props['season']}\n")
        
        # Example 5: Multiple filters
        print("="*70)
        print("EXAMPLE 5: Multiple Filters")
        print("="*70)
        
        print("\n🔍 Finding Men's Casual Apparel under $100...")
        results = products.query.fetch_objects(
            filters=(
                Filter.by_property("gender").equal("Men") &
                Filter.by_property("usage").equal("Casual") &
                Filter.by_property("masterCategory").equal("Apparel") &
                Filter.by_property("price").less_than(100)
            ),
            limit=5
        )
        
        print(f"Found {len(results.objects)} results:\n")
        for i, obj in enumerate(results.objects, 1):
            props = obj.properties
            print(f"{i}. {props['productDisplayName']}")
            print(f"   ${props['price']} | {props['articleType']} | {props['baseColour']}\n")
        
        # Example 6: Product statistics
        print("="*70)
        print("EXAMPLE 6: Product Statistics")
        print("="*70)
        
        print("\n📊 Statistics:")
        
        # Total
        result = products.aggregate.over_all(total_count=True)
        print(f"Total Products: {result.total_count:,}")
        
        # By gender
        print("\nBy Gender:")
        for gender in ["Men", "Women", "Boys", "Girls", "Unisex"]:
            results = products.query.fetch_objects(
                filters=Filter.by_property("gender").equal(gender),
                limit=10000
            )
            count = len(results.objects)
            if count > 0:
                print(f"  • {gender}: {count:,} items")
        
        # By category
        print("\nBy Master Category:")
        for category in ["Apparel", "Footwear", "Accessories", "Personal Care", "Free Items"]:
            results = products.query.fetch_objects(
                filters=Filter.by_property("masterCategory").equal(category),
                limit=10000
            )
            count = len(results.objects)
            if count > 0:
                print(f"  • {category}: {count:,} items")
        
        # Example 7: Price range queries
        print("\n" + "="*70)
        print("EXAMPLE 7: Price Range Queries")
        print("="*70)
        
        print("\n🔍 Finding products between $50 and $100...")
        results = products.query.fetch_objects(
            filters=(
                Filter.by_property("price").greater_or_equal(50) &
                Filter.by_property("price").less_or_equal(100)
            ),
            limit=5
        )
        
        print(f"Found {len(results.objects)} results:\n")
        for i, obj in enumerate(results.objects, 1):
            props = obj.properties
            print(f"{i}. {props['productDisplayName']}")
            print(f"   ${props['price']} | {props['gender']} | {props['masterCategory']}\n")
        
        print("="*70)
        print("✅ All examples completed successfully!")
        print("="*70)
        print("\n💡 Tips:")
        print("  • Use inspect_weaviate.py to browse collections")
        print("  • Check WEAVIATE_GUIDE.md for detailed documentation")
        print("  • Semantic search requires vector embeddings (not configured)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()
        print("\n🔌 Disconnected from Weaviate")


if __name__ == "__main__":
    main()
