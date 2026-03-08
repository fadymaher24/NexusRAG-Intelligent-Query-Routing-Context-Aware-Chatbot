# Weaviate Collections - Quick Reference

## 📚 What Collections Exist?

Your Weaviate database has **2 collections**:

### 1. **Products** Collection

- **44,424 items** - E-commerce product catalog
- **12 properties**: productDisplayName, price, brandName, ageGroup, gender, baseColour, season, usage, productId, masterCategory, subCategory, articleType
- **Categories**:
  - Men: 10,000 items
  - Women: 10,000 items
  - Boys: 830 items
  - Girls: 655 items
  - Unisex: 2,161 items
- **Master Categories**: Apparel (10K), Footwear (9.2K), Accessories (10K), Personal Care (2.4K), Free Items (105)

### 2. **FAQs** Collection

- **25 items** - Frequently Asked Questions
- **3 properties**: question, answer, type
- **Categories**: returns and exchanges, shipping and delivery, product information, general information, payment information

---

## 🔍 How to Explore Collections?

### Option 1: Use the Inspector Tool (Easiest)

```bash
# View all collections with samples
python inspect_weaviate.py

# View specific collection
python inspect_weaviate.py products
python inspect_weaviate.py faqs
```

### Option 2: Run Working Examples

```bash
# Shows 7 different examples with real data
python weaviate_examples_simple.py
```

### Option 3: Read the Guide

```bash
# Comprehensive documentation
cat WEAVIATE_GUIDE.md
```

---

## 💻 Quick Code Examples

### Connect to Weaviate

```python
import weaviate
client = weaviate.connect_to_local(port=8079, grpc_port=50050)
# ... do work ...
client.close()
```

### List All Collections

```python
collections = client.collections.list_all()
# Returns: ['Faqs', 'Products']
```

### Get Collection Count

```python
collection = client.collections.get("products")
result = collection.aggregate.over_all(total_count=True)
print(result.total_count)  # 44,424
```

### Browse FAQs

```python
faqs = client.collections.get("faqs")
results = faqs.query.fetch_objects(limit=10)
for obj in results.objects:
    print(obj.properties)
```

### Filter Products

```python
from weaviate.classes.query import Filter

products = client.collections.get("products")

# Women's products
results = products.query.fetch_objects(
    filters=Filter.by_property("gender").equal("Women"),
    limit=5
)

# Multiple filters
results = products.query.fetch_objects(
    filters=(
        Filter.by_property("gender").equal("Men") &
        Filter.by_property("masterCategory").equal("Apparel") &
        Filter.by_property("price").less_than(100)
    ),
    limit=10
)

# Price range
results = products.query.fetch_objects(
    filters=(
        Filter.by_property("price").greater_or_equal(50) &
        Filter.by_property("price").less_or_equal(100)
    ),
    limit=10
)
```

---

## 🗂️ Collection Schemas

### Products Schema

```
productDisplayName: TEXT    - "Murcia Women Casual Brown Handbag"
price: NUMBER               - 60.0
brandName: TEXT             - ""
ageGroup: TEXT              - ""
gender: TEXT                - "Women"
baseColour: TEXT            - "Brown"
season: TEXT                - "Winter"
usage: TEXT                 - "Casual"
productId: TEXT             - ""
masterCategory: TEXT        - "Accessories"
subCategory: TEXT           - "Bags"
articleType: TEXT           - "Handbags"
```

### FAQs Schema

```
question: TEXT              - "How long does it take to process a return?"
answer: TEXT                - "Return processing typically takes 5-7 business days..."
type: TEXT                  - "returns and exchanges"
```

---

## 🛠️ Available Filter Operations

```python
# Equality
Filter.by_property("gender").equal("Women")

# Comparison
Filter.by_property("price").less_than(100)
Filter.by_property("price").greater_than(50)
Filter.by_property("price").less_or_equal(100)
Filter.by_property("price").greater_or_equal(50)

# Logical operators
filter1 & filter2  # AND
filter1 | filter2  # OR
```

---

## 📊 Sample Queries

### Find Women's Footwear

```python
results = products.query.fetch_objects(
    filters=(
        Filter.by_property("gender").equal("Women") &
        Filter.by_property("masterCategory").equal("Footwear")
    ),
    limit=10
)
```

### Find Blue Casual Apparel

```python
results = products.query.fetch_objects(
    filters=(
        Filter.by_property("baseColour").equal("Blue") &
        Filter.by_property("usage").equal("Casual") &
        Filter.by_property("masterCategory").equal("Apparel")
    ),
    limit=10
)
```

### Find Affordable Items ($10-$30)

```python
results = products.query.fetch_objects(
    filters=(
        Filter.by_property("price").greater_or_equal(10) &
        Filter.by_property("price").less_or_equal(30)
    ),
    limit=10
)
```

---

## 🔧 Maintenance Commands

### Reload Data

```bash
python load_data.py
```

### Check Weaviate Status

```bash
curl http://localhost:8079/v1/meta
```

### Access Web Console

Open: http://localhost:8079

---

## ⚠️ Important Notes

1. **No Semantic Search**: The collections are configured without vector embeddings, so `near_text()` queries won't work. Use `fetch_objects()` with filters instead.

2. **FAQs Have Vectors**: The FAQs collection supports semantic search via the repository:

   ```python
   from app.repositories import FAQRepository
   repo = FAQRepository()
   repo.connect()
   results = repo.search("shipping policy", limit=5)
   ```

3. **Large Result Sets**: Fetch limit is typically 10,000. For larger datasets, use pagination or aggregations.

---

## 📖 More Resources

- **Detailed Guide**: `WEAVIATE_GUIDE.md`
- **Code Examples**: `weaviate_examples_simple.py`
- **Inspector Tool**: `inspect_weaviate.py`
- **Data Loader**: `load_data.py`
- **Repository Code**: `app/repositories.py`

---

## 🚀 Quick Start Commands

```bash
# View everything
python inspect_weaviate.py

# Run examples
python weaviate_examples_simple.py

# Query specific collection
python inspect_weaviate.py products "" 10
python inspect_weaviate.py faqs "" 10

# Reload data
python load_data.py
```
