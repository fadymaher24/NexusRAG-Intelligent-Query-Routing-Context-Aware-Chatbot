"""
Inspect Weaviate collections and their contents.
This script helps you explore what's stored in Weaviate.
"""

import weaviate
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import config


def inspect_weaviate_collections():
    """Connect to Weaviate and inspect all collections."""
    
    print("=" * 70)
    print("🔍 WEAVIATE COLLECTIONS INSPECTOR")
    print("=" * 70)
    
    # Connect to Weaviate
    print(f"\n⚙️  Connecting to Weaviate at {config.WEAVIATE_HOST}:{config.WEAVIATE_PORT}...")
    try:
        client = weaviate.connect_to_local(
            port=config.WEAVIATE_PORT,
            grpc_port=config.WEAVIATE_GRPC_PORT
        )
        print("✅ Connected successfully!\n")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    try:
        # List all collections
        print("📚 AVAILABLE COLLECTIONS:")
        print("-" * 70)
        
        collections = client.collections.list_all()
        
        if not collections:
            print("No collections found in Weaviate.")
            return
        
        for collection_name in collections:
            print(f"\n📦 Collection: {collection_name}")
            print("   " + "─" * 60)
            
            try:
                collection = client.collections.get(collection_name)
                
                # Get collection schema/properties
                config_data = collection.config.get()
                print(f"   Properties:")
                for prop in config_data.properties:
                    print(f"      • {prop.name}: {prop.data_type}")
                
                # Get count
                result = collection.aggregate.over_all(total_count=True)
                count = result.total_count
                print(f"\n   📊 Total items: {count:,}")
                
                # Show sample records
                if count > 0:
                    print(f"\n   🔍 Sample records (first 3):")
                    results = collection.query.fetch_objects(limit=3)
                    
                    for idx, obj in enumerate(results.objects, 1):
                        print(f"\n      Record #{idx}:")
                        for key, value in obj.properties.items():
                            # Truncate long values
                            if isinstance(value, str) and len(value) > 50:
                                value = value[:50] + "..."
                            print(f"         {key}: {value}")
                
            except Exception as e:
                print(f"   ❌ Error inspecting collection: {e}")
        
        print("\n" + "=" * 70)
        print("✅ Inspection complete!")
        print("=" * 70)
        
    finally:
        client.close()
        print("\n🔌 Disconnected from Weaviate")


def query_collection(collection_name: str, query_text: str = None, limit: int = 5):
    """
    Query a specific collection.
    
    Args:
        collection_name: Name of the collection to query
        query_text: Optional search query
        limit: Maximum number of results
    """
    
    print("=" * 70)
    print(f"🔍 QUERYING COLLECTION: {collection_name}")
    print("=" * 70)
    
    # Connect to Weaviate
    print(f"\n⚙️  Connecting to Weaviate...")
    try:
        client = weaviate.connect_to_local(
            port=config.WEAVIATE_PORT,
            grpc_port=config.WEAVIATE_GRPC_PORT
        )
        print("✅ Connected!\n")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    try:
        collection = client.collections.get(collection_name)
        
        if query_text:
            print(f"🔎 Searching for: '{query_text}'")
            # Note: This requires vectors to be present
            results = collection.query.fetch_objects(limit=limit)
        else:
            print(f"📋 Fetching {limit} records:")
            results = collection.query.fetch_objects(limit=limit)
        
        print(f"\n📊 Found {len(results.objects)} results:\n")
        
        for idx, obj in enumerate(results.objects, 1):
            print(f"{'─' * 70}")
            print(f"Record #{idx}:")
            print(f"{'─' * 70}")
            for key, value in obj.properties.items():
                print(f"  {key}: {value}")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()
        print("🔌 Disconnected from Weaviate")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Query specific collection
        collection_name = sys.argv[1]
        query_text = sys.argv[2] if len(sys.argv) > 2 else None
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        query_collection(collection_name, query_text, limit)
    else:
        # Inspect all collections
        inspect_weaviate_collections()
        
        print("\n💡 TIP: To query a specific collection, run:")
        print("   python inspect_weaviate.py <collection_name> [query] [limit]")
        print("\nExamples:")
        print("   python inspect_weaviate.py products")
        print("   python inspect_weaviate.py faqs")
