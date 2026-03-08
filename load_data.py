"""
Load product and FAQ data into Weaviate.
Run this script once to populate the database.
"""

import joblib
import weaviate
import time
import sys
from weaviate.classes.config import Configure, Property, DataType
from pathlib import Path
from tqdm import tqdm

# Add parent directory to path for imports when running as script
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))


def load_products_to_weaviate():
    """Load products from joblib file into Weaviate."""
    
    print("⚙️  Connecting to Weaviate...")
    start_conn = time.time()
    client = weaviate.connect_to_local(
        port=8079,
        grpc_port=50050
    )
    print(f"✅ Connected in {time.time() - start_conn:.2f}s")
    
    try:
        # Check if products collection exists
        try:
            client.collections.delete("products")
            print("Deleted existing 'products' collection")
        except:
            pass
        
        # Create products collection
        print("Creating 'products' collection...")
        products_collection = client.collections.create(
            name="products",
            properties=[
                Property(name="productDisplayName", data_type=DataType.TEXT),
                Property(name="price", data_type=DataType.NUMBER),
                Property(name="brandName", data_type=DataType.TEXT),
                Property(name="ageGroup", data_type=DataType.TEXT),
                Property(name="gender", data_type=DataType.TEXT),
                Property(name="baseColour", data_type=DataType.TEXT),
                Property(name="season", data_type=DataType.TEXT),
                Property(name="usage", data_type=DataType.TEXT),
                Property(name="productId", data_type=DataType.TEXT),
                Property(name="masterCategory", data_type=DataType.TEXT),
                Property(name="subCategory", data_type=DataType.TEXT),
                Property(name="articleType", data_type=DataType.TEXT),
            ],
            vectorizer_config=Configure.Vectorizer.text2vec_ollama(
                api_endpoint="http://host.docker.internal:11434",
                model="nomic-embed-text"
            )
        )
        print("Collection created successfully")
        
        # Load products data
        data_path = Path(__file__).parent / "dataset" / "clothes_json.joblib"
        print(f"📂 Loading products from {data_path.name}...")
        load_start = time.time()
        products_data = joblib.load(data_path)
        load_time = time.time() - load_start
        
        print(f"✅ Loaded {len(products_data):,} products in {load_time:.2f}s")
        
        # Import products with embeddings
        collection = client.collections.get("products")
        
        print("📥 Importing products to Weaviate...")
        batch_size = 100
        import_start = time.time()
        
        for i in tqdm(range(0, len(products_data), batch_size),
                     desc="Importing",
                     unit="batch",
                     bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'):
            batch = products_data[i:i + batch_size]
            
            with collection.batch.dynamic() as batch_import:
                for item in batch:
                    # Extract vector if exists
                    vector = item.pop('vector', None) if isinstance(item, dict) else None
                    
                    # Clean the data
                    properties = {
                        'productDisplayName': str(item.get('productDisplayName', '')),
                        'price': float(item.get('price', 0)),
                        'brandName': str(item.get('brandName', '')),
                        'ageGroup': str(item.get('ageGroup', '')),
                        'gender': str(item.get('gender', '')),
                        'baseColour': str(item.get('baseColour', '')),
                        'season': str(item.get('season', '')),
                        'usage': str(item.get('usage', '')),
                        'productId': str(item.get('productId', '')),
                        'masterCategory': str(item.get('masterCategory', '')),
                        'subCategory': str(item.get('subCategory', '')),
                        'articleType': str(item.get('articleType', '')),
                    }
                    
                    if vector is not None:
                        batch_import.add_object(
                            properties=properties,
                            vector=vector
                        )
                    else:
                        batch_import.add_object(properties=properties)
        
        import_time = time.time() - import_start
        rate = len(products_data) / import_time if import_time > 0 else 0
        print(f"\n✅ Successfully imported {len(products_data):,} products in {import_time:.2f}s ({rate:.0f} items/s)")
        
        # Verify
        result = collection.aggregate.over_all(total_count=True)
        print(f"Total products in Weaviate: {result.total_count}")
        
    finally:
        client.close()
        print("Disconnected from Weaviate")


def load_faqs_to_weaviate():
    """Load FAQs from joblib file into Weaviate."""
    
    print("\n⚙️  Connecting to Weaviate...")
    start_conn = time.time()
    client = weaviate.connect_to_local(
        port=8079,
        grpc_port=50050
    )
    print(f"✅ Connected in {time.time() - start_conn:.2f}s")
    
    try:
        # Check if FAQs collection exists
        try:
            client.collections.delete("faqs")
            print("Deleted existing 'faqs' collection")
        except:
            pass
        
        # Create FAQs collection
        print("Creating 'faqs' collection...")
        faqs_collection = client.collections.create(
            name="faqs",
            properties=[
                Property(name="question", data_type=DataType.TEXT),
                Property(name="answer", data_type=DataType.TEXT),
                Property(name="type", data_type=DataType.TEXT),
            ],
            vectorizer_config=Configure.Vectorizer.text2vec_ollama(
                api_endpoint="http://host.docker.internal:11434",
                model="nomic-embed-text"
            )
        )
        print("Collection created successfully")
        
        # Load FAQs data
        data_path = Path(__file__).parent / "dataset" / "faq.joblib"
        print(f"📂 Loading FAQs from {data_path.name}...")
        load_start = time.time()
        faqs_data = joblib.load(data_path)
        load_time = time.time() - load_start
        
        print(f"✅ Loaded {len(faqs_data)} FAQs in {load_time:.2f}s")
        
        # Import FAQs with embeddings
        collection = client.collections.get("faqs")
        
        print("📥 Importing FAQs to Weaviate...")
        import_start = time.time()
        
        with collection.batch.dynamic() as batch_import:
            for item in tqdm(faqs_data,
                           desc="Importing",
                           unit="item",
                           bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'):
                # Extract vector if exists
                vector = item.pop('vector', None) if isinstance(item, dict) else None
                
                # Clean the data
                properties = {
                    'question': str(item.get('question', '')),
                    'answer': str(item.get('answer', '')),
                    'type': str(item.get('type', '')),
                }
                
                if vector is not None:
                    batch_import.add_object(
                        properties=properties,
                        vector=vector
                    )
                else:
                    batch_import.add_object(properties=properties)
        
        import_time = time.time() - import_start
        print(f"\n✅ Successfully imported {len(faqs_data)} FAQs in {import_time:.2f}s")
        
        # Verify
        result = collection.aggregate.over_all(total_count=True)
        print(f"Total FAQs in Weaviate: {result.total_count}")
        
    finally:
        client.close()
        print("Disconnected from Weaviate")


if __name__ == "__main__":
    print("=" * 70)
    print("🚀 NexusRAG Data Loader")
    print("=" * 70)
    print()
    
    overall_start = time.time()
    
    try:
        load_products_to_weaviate()
        load_faqs_to_weaviate()
        
        total_time = time.time() - overall_start
        
        print()
        print("=" * 70)
        print(f"✅ Data loading completed successfully in {total_time:.2f}s!")
        print("=" * 70)
        print()
        print("ℹ️  Next steps:")
        print("  1. Verify Weaviate is running: docker-compose ps")
        print("  2. Start the Flask app: python main.py")
        print("  3. Test the API: curl -X POST http://localhost:5001/api/query \\")
        print('                        -H "Content-Type: application/json" \\')
        print('                        -d \'{"query": "return policy"}\'')
        print()
        
    except KeyboardInterrupt:
        print()
        print("⚠️  Data loading interrupted by user")
    except Exception as e:
        print()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
