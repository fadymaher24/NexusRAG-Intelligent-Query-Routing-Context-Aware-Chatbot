#!/usr/bin/env python3
"""
Quick examples for working with Weaviate collections.
Run this file to see various usage examples.
"""

import weaviate
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.repositories import ProductRepository, FAQRepository
from weaviate.classes.query import Filter


def example1_list_all_collections():
    """Example 1: List all collections."""
    print("\n" + "="*70)
    print("EXAMPLE 1: List All Collections")
    print("="*70)
    
    client = weaviate.connect_to_local(port=8079, grpc_port=50050)
    collections = client.collections.list_all()
    
    print(f"Found {len(collections)} collection(s):")
    for name in collections:
        collection = client.collections.get(name)
        result = collection.aggregate.over_all(total_count=True)
        print(f"  • {name}: {result.total_count:,} items")
    
    client.close()


def example2_search_products():
    """Example 2: Search for products."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Search Products")
    print("="*70)
    
    repo = ProductRepository()
    repo.connect()
    
    # Search for blue shirts
    print("\n🔍 Searching for 'blue shirt'...")
    results = repo.search_by_text("blue shirt", limit=5)
    
    print(f"Found {len(results)} results:\n")
    for i, product in enumerate(results, 1):
        print(f"{i}. {product.productDisplayName}")
        print(f"   Price: ${product.price} | Gender: {product.gender}")
        print(f"   Category: {product.masterCategory} > {product.articleType}\n")
    
    repo.disconnect()


def example3_filter_products():
    """Example 3: Filter products by attributes."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Filter Products")
    print("="*70)
    
    repo = ProductRepository()
    repo.connect()
    
    # Find women's shoes
    print("\n🔍 Searching for women's shoes...")
    results = repo.search_by_text(
        "shoes",
        filters=[Filter.by_property("gender").equal("Women")],
        limit=5
    )
    
    print(f"Found {len(results)} results:\n")
    for i, product in enumerate(results, 1):
        print(f"{i}. {product.productDisplayName}")
        print(f"   ${product.price} | {product.baseColour} | {product.season}\n")
    
    repo.disconnect()


def example4_search_faqs():
    """Example 4: Search FAQs."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Search FAQs")
    print("="*70)
    
    repo = FAQRepository()
    repo.connect()
    
    # Search for shipping questions
    print("\n🔍 Searching for 'shipping' FAQs...")
    results = repo.search("shipping delivery", limit=3)
    
    print(f"Found {len(results)} results:\n")
    for i, faq in enumerate(results, 1):
        print(f"{i}. Q: {faq.question}")
        print(f"   A: {faq.answer}")
        print(f"   Type: {faq.type}\n")
    
    repo.disconnect()


def example5_get_all_faqs():
    """Example 5: Get all FAQs."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Get All FAQs")
    print("="*70)
    
    repo = FAQRepository()
    repo.connect()
    
    faqs = repo.get_all()
    
    print(f"\nTotal FAQs: {len(faqs)}\n")
    
    # Group by type
    by_type = {}
    for faq in faqs:
        if faq.type not in by_type:
            by_type[faq.type] = []
        by_type[faq.type].append(faq)
    
    print("FAQs by category:")
    for faq_type, items in by_type.items():
        print(f"  • {faq_type}: {len(items)} questions")
    
    repo.disconnect()


def example6_product_statistics():
    """Example 6: Get product statistics."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Product Statistics")
    print("="*70)
    
    client = weaviate.connect_to_local(port=8079, grpc_port=50050)
    
    try:
        products = client.collections.get("products")
        
        # Total count
        result = products.aggregate.over_all(total_count=True)
        print(f"\n📊 Total Products: {result.total_count:,}")
        
        # Sample by gender
        print("\nSamples by Gender:")
        for gender in ["Men", "Women", "Unisex"]:
            results = products.query.fetch_objects(
                filters=Filter.by_property("gender").equal(gender),
                limit=1000
            )
            print(f"  • {gender}: {len(results.objects)} products")
        
        # Sample by category
        print("\nSamples by Master Category:")
        for category in ["Apparel", "Footwear", "Accessories"]:
            results = products.query.fetch_objects(
                filters=Filter.by_property("masterCategory").equal(category),
                limit=1000
            )
            print(f"  • {category}: {len(results.objects)} products")
    
    finally:
        client.close()


def example7_raw_query():
    """Example 7: Raw Weaviate query."""
    print("\n" + "="*70)
    print("EXAMPLE 7: Raw Weaviate Query")
    print("="*70)
    
    client = weaviate.connect_to_local(port=8079, grpc_port=50050)
    
    try:
        # Get products collection
        products = client.collections.get("products")
        
        # Fetch with multiple filters
        print("\n🔍 Filtering: Red colored, Women's Apparel, Price < 100")
        
        results = products.query.fetch_objects(
            filters=(
                Filter.by_property("baseColour").equal("Red") &
                Filter.by_property("gender").equal("Women") &
                Filter.by_property("masterCategory").equal("Apparel") &
                Filter.by_property("price").less_than(100)
            ),
            limit=5
        )
        
        print(f"\nFound {len(results.objects)} results:\n")
        for i, obj in enumerate(results.objects, 1):
            props = obj.properties
            print(f"{i}. {props['productDisplayName']}")
            print(f"   ${props['price']} | {props['baseColour']} | {props['articleType']}\n")
    
    finally:
        client.close()


if __name__ == "__main__":
    print("\n" + "🚀 WEAVIATE COLLECTIONS - USAGE EXAMPLES")
    
    try:
        example1_list_all_collections()
        example2_search_products()
        example3_filter_products()
        example4_search_faqs()
        example5_get_all_faqs()
        example6_product_statistics()
        example7_raw_query()
        
        print("\n" + "="*70)
        print("✅ All examples completed successfully!")
        print("="*70)
        print("\n💡 Check WEAVIATE_GUIDE.md for more detailed documentation")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("  1. Weaviate is running: docker-compose up -d weaviate")
        print("  2. Data is loaded: python load_data.py")
