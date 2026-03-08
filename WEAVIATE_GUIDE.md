# Weaviate Collections Guide

## Overview

This NexusRAG application uses **Weaviate** as its vector database to store and query two main types of data:

1. **Products** - E-commerce product catalog
2. **FAQs** - Frequently Asked Questions

---

## 📦 Available Collections

### 1. **Products Collection**

**Purpose**: Stores product catalog with 44,424+ clothing items

**Schema Properties**:

- `productDisplayName` (TEXT) - Full product name
- `price` (NUMBER) - Product price
- `brandName` (TEXT) - Brand name
- `ageGroup` (TEXT) - Target age group
- `gender` (TEXT) - Gender category (Men/Women/Unisex)
- `baseColour` (TEXT) - Primary color
- `season` (TEXT) - Season (Winter/Summer/Fall/Spring)
- `usage` (TEXT) - Usage context (Casual/Sports/Formal/etc.)
- `productId` (TEXT) - Unique product identifier
- `masterCategory` (TEXT) - Main category (Apparel/Footwear/Accessories)
- `subCategory` (TEXT) - Sub-category (Topwear/Shoes/Bags/etc.)
- `articleType` (TEXT) - Specific article type (Shirts/Handbags/Sports Shoes/etc.)

**Features**:

- Vector embeddings for semantic search
- Supports filtering by attributes
- Full-text search capabilities

**Example Products**:

```
- Murcia Women Casual Brown Handbag ($60)
- John Players Men Solid Blue Shirt ($113)
- Reebok Men Zigdynamic White Sports Shoes ($115)
```

---

### 2. **FAQs Collection**

**Purpose**: Stores frequently asked questions and answers (25 items)

**Schema Properties**:

- `question` (TEXT) - The FAQ question
- `answer` (TEXT) - The answer text
- `type` (TEXT) - Category type

**FAQ Categories**:

- `returns and exchanges` - Return policies, refund processing
- `shipping and delivery` - Shipping info, delivery times
- `product information` - Product details, inventory updates
- `general information` - Account, ordering, contact info
- `payment information` - Payment methods, security

**Example FAQs**:

```
Q: How long does it take to process a return?
A: Return processing typically takes 5-7 business days from when
   the item is received at our warehouse.
Type: returns and exchanges

Q: Do you ship internationally?
A: Yes, we offer international shipping to select countries.
   Check our 'Shipping Information' page for more details.
Type: shipping and delivery
```

---

## 🔍 How to Inspect Collections

### Using the Inspector Tool

I've created `inspect_weaviate.py` for you to easily explore collections:

#### 1. **View All Collections** (Overview)

```bash
python inspect_weaviate.py
```

Shows all collections with:

- Schema/properties
- Total item count
- Sample records (first 3)

#### 2. **Query Specific Collection**

```bash
python inspect_weaviate.py <collection_name> [query] [limit]
```

**Examples**:

```bash
# View 5 products
python inspect_weaviate.py products

# View 10 FAQs
python inspect_weaviate.py faqs "" 10

# View 20 products
python inspect_weaviate.py products "" 20
```

---

## 💻 Programmatic Access

### Using the Repository Pattern

The application uses repository classes to access collections:

#### **ProductRepository**

```python
from app.repositories import ProductRepository

# Initialize
repo = ProductRepository()
repo.connect()

# Get all products
products = repo.get_all()

# Search by text
results = repo.search_by_text("blue shirt", limit=10)

# Search with filters
from weaviate.classes.query import Filter
results = repo.search_by_text(
    "shoes",
    filters=[Filter.by_property("gender").equal("Men")],
    limit=20
)

# Clean up
repo.disconnect()
```

#### **FAQRepository**

```python
from app.repositories import FAQRepository

# Initialize
repo = FAQRepository()
repo.connect()

# Get all FAQs
faqs = repo.get_all()

# Search FAQs
results = repo.search("return policy", limit=5)

# Get formatted FAQ layout
faq_text = repo.get_faq_layout()

# Clean up
repo.disconnect()
```

---

## 🔄 Loading/Reloading Data

### Initial Data Load

To populate collections with data:

```bash
python load_data.py
```

This script:

1. Connects to Weaviate
2. Deletes existing collections (if any)
3. Creates fresh collections with proper schema
4. Loads data from:
   - `dataset/clothes_json.joblib` → Products
   - `dataset/faq.joblib` → FAQs
5. Shows import progress and statistics

**Expected Output**:

```
⚙️  Connecting to Weaviate...
✅ Connected in 0.15s
Creating 'products' collection...
Collection created successfully
📂 Loading products from clothes_json.joblib...
✅ Loaded 44,424 products in 0.25s
📥 Importing products to Weaviate...
✅ Successfully imported 44,424 products in 45.23s (982 items/s)
Total products in Weaviate: 44424
```

---

## 🛠️ Manual Weaviate Queries

### Using Weaviate Client Directly

```python
import weaviate

# Connect
client = weaviate.connect_to_local(port=8079, grpc_port=50050)

# Get collection
products = client.collections.get("products")

# Count items
result = products.aggregate.over_all(total_count=True)
print(f"Total: {result.total_count}")

# Fetch objects
results = products.query.fetch_objects(limit=10)
for obj in results.objects:
    print(obj.properties)

# Near text search (semantic)
results = products.query.near_text(
    query="red dress",
    limit=5
).objects

# Filter results
from weaviate.classes.query import Filter
results = products.query.fetch_objects(
    filters=Filter.by_property("gender").equal("Women"),
    limit=10
)

# Close connection
client.close()
```

---

## 🌐 Weaviate Console

Access Weaviate's web interface:

**URL**: http://localhost:8079

From the console you can:

- Browse all collections
- Execute GraphQL queries
- View schema details
- Monitor cluster health
- Perform administrative tasks

---

## 📊 Collection Statistics

Current data (as of inspection):

| Collection | Items  | Properties | Vector Support |
| ---------- | ------ | ---------- | -------------- |
| Products   | 44,424 | 12         | ✅ Yes         |
| FAQs       | 25     | 3          | ✅ Yes         |

---

## 🔧 Configuration

Weaviate settings are configured in `.env`:

```bash
WEAVIATE_HOST=localhost
WEAVIATE_PORT=8079
WEAVIATE_GRPC_PORT=50050
```

These are used by `app/config.py` to connect to Weaviate.

---

## 📝 Common Operations

### Check if Weaviate is Running

```bash
curl http://localhost:8079/v1/meta
```

### Check Collection Exists

```python
client = weaviate.connect_to_local(port=8079, grpc_port=50050)
collections = client.collections.list_all()
print("products" in collections)  # True if exists
client.close()
```

### Delete a Collection

```python
client = weaviate.connect_to_local(port=8079, grpc_port=50050)
client.collections.delete("products")
client.close()
```

### Get Collection Schema

```python
client = weaviate.connect_to_local(port=8079, grpc_port=50050)
collection = client.collections.get("products")
schema = collection.config.get()
for prop in schema.properties:
    print(f"{prop.name}: {prop.data_type}")
client.close()
```

---

## 🚀 Quick Start Examples

### Example 1: Find Women's Blue Clothing

```python
from app.repositories import ProductRepository

repo = ProductRepository()
repo.connect()

results = repo.search_by_text(
    "blue clothing",
    filters=[
        Filter.by_property("gender").equal("Women"),
        Filter.by_property("masterCategory").equal("Apparel")
    ],
    limit=10
)

for product in results:
    print(f"{product.productDisplayName} - ${product.price}")

repo.disconnect()
```

### Example 2: Find Shipping FAQs

```python
from app.repositories import FAQRepository

repo = FAQRepository()
repo.connect()

# Search for shipping related questions
results = repo.search("shipping delivery", limit=5)

for faq in results:
    print(f"Q: {faq.question}")
    print(f"A: {faq.answer}\n")

repo.disconnect()
```

---

## 🐛 Troubleshooting

### Weaviate Connection Refused

```bash
# Ensure Weaviate is running
docker-compose up -d weaviate

# Check if port 8079 is accessible
curl http://localhost:8079/v1/.well-known/ready
```

### Collections Not Found

```bash
# Reload data
python load_data.py
```

### Empty Results

- Verify data was loaded: `python inspect_weaviate.py`
- Check if vectors exist for semantic search
- Try using fetch_objects() instead of near_text()

---

## 📚 Additional Resources

- [Weaviate Documentation](https://weaviate.io/developers/weaviate)
- [Weaviate Python Client](https://weaviate.io/developers/weaviate/client-libraries/python)
- Project files:
  - `load_data.py` - Data loading script
  - `app/repositories.py` - Repository patterns
  - `inspect_weaviate.py` - Inspector tool
