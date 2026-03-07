"""
Load product and FAQ data into Weaviate.
Run this script once to populate the database.
"""

import joblib
import weaviate
from weaviate.classes.config import Configure, Property, DataType
from pathlib import Path
from tqdm import tqdm


def load_products_to_weaviate():
    """Load products from joblib file into Weaviate."""
    
    print("Connecting to Weaviate...")
    client = weaviate.connect_to_local(
        port=8079,
        grpc_port=50050
    )
    
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
            vectorizer_config=Configure.Vectorizer.none()
        )
        print("Collection created successfully")
        
        # Load products data
        data_path = Path(__file__).parent / "dataset" / "clothes_json.joblib"
        print(f"Loading products from {data_path}...")
        products_data = joblib.load(data_path)
        
        print(f"Found {len(products_data)} products")
        
        # Import products with embeddings
        collection = client.collections.get("products")
        
        print("Importing products...")
        batch_size = 100
        for i in tqdm(range(0, len(products_data), batch_size)):
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
        
        print(f"✅ Successfully imported {len(products_data)} products!")
        
        # Verify
        result = collection.aggregate.over_all(total_count=True)
        print(f"Total products in Weaviate: {result.total_count}")
        
    finally:
        client.close()
        print("Disconnected from Weaviate")


def load_faqs_to_weaviate():
    """Load FAQs from joblib file into Weaviate."""
    
    print("\nConnecting to Weaviate...")
    client = weaviate.connect_to_local(
        port=8079,
        grpc_port=50050
    )
    
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
            vectorizer_config=Configure.Vectorizer.none()
        )
        print("Collection created successfully")
        
        # Load FAQs data
        data_path = Path(__file__).parent / "dataset" / "faq.joblib"
        print(f"Loading FAQs from {data_path}...")
        faqs_data = joblib.load(data_path)
        
        print(f"Found {len(faqs_data)} FAQs")
        
        # Import FAQs with embeddings
        collection = client.collections.get("faqs")
        
        print("Importing FAQs...")
        with collection.batch.dynamic() as batch_import:
            for item in tqdm(faqs_data):
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
        
        print(f"✅ Successfully imported {len(faqs_data)} FAQs!")
        
        # Verify
        result = collection.aggregate.over_all(total_count=True)
        print(f"Total FAQs in Weaviate: {result.total_count}")
        
    finally:
        client.close()
        print("Disconnected from Weaviate")


if __name__ == "__main__":
    print("=" * 60)
    print("NexusRAG Data Loader")
    print("=" * 60)
    
    try:
        load_products_to_weaviate()
        load_faqs_to_weaviate()
        print("\n✅ Data loading completed successfully!")
        print("\nYou can now start the Flask app with: python main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
