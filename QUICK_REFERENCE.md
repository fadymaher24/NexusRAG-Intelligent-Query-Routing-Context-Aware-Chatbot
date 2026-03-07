# Quick Reference Guide

## Installation & Setup

```bash
# Clone repository
cd NexusRAG-Intelligent-Query-Routing-Context-Aware-Chatbot

# Run setup script
./setup.sh

# Or manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Running the Application

### Web Server (Default)

```bash
python main.py
# Access: http://localhost:5001
```

### CLI Mode

```bash
python main.py --mode cli
```

### Custom Configuration

```bash
# Different port
python main.py --port 8000

# Debug mode
python main.py --debug

# Custom host and port
python main.py --host 0.0.0.0 --port 8080
```

### Docker

```bash
# Build and run
docker-compose up

# Run in background
docker-compose up -d

# Stop
docker-compose down
```

## API Usage

### Health Check

```bash
curl http://localhost:5001/health
```

### Query Endpoint (Full Details)

```bash
curl -X POST http://localhost:5001/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Do you have blue T-shirts under $50?"}'
```

### Chat Endpoint (Simple)

```bash
curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is your return policy?"}'
```

### Python Client

```python
import requests

response = requests.post('http://localhost:5001/api/query',
    json={'query': 'Show me casual dresses'})
data = response.json()
print(data['response'])
```

## Configuration

### Environment Variables (.env)

```bash
# Weaviate
WEAVIATE_HOST=localhost
WEAVIATE_PORT=8079
WEAVIATE_GRPC_PORT=50050

# LLM
LLM_MODEL=meta-llama/Llama-3.2-3B-Instruct-Turbo
LLM_API_KEY=your_api_key_here
LLM_API_BASE_URL=https://api.together.xyz

# Flask
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
FLASK_DEBUG=False

# Logging
LOG_LEVEL=INFO
```

## Example Queries

### FAQ Queries

```bash
# Return policy
"What is your return policy?"

# Shipping
"How long does delivery take?"

# Contact
"How can I contact customer support?"

# International
"Do you ship internationally?"
```

### Product Queries - Technical

```bash
# Specific items
"Show me blue T-shirts under $50"

# Categories
"What dresses do you have for women?"

# Color and type
"Do you have red sneakers?"

# Price range
"Show me casual shirts between $20 and $40"
```

### Product Queries - Creative

```bash
# Occasion-based
"Create a look for a beach party"

# Style advice
"Suggest an outfit for a job interview"

# Seasonal
"Help me dress for a winter wedding"

# Activity-based
"What should I wear for a morning jog?"
```

## Common Operations

### Check Logs

```bash
# View latest logs
tail -f logs/app.log

# Search for errors
grep ERROR logs/app.log

# Search for specific query
grep "Processing query" logs/app.log
```

### Test Connection

```python
from app.repositories import RepositoryFactory

# Test FAQ repository
faq_repo = RepositoryFactory.get_faq_repository()
faq_repo.load_data()
faqs = faq_repo.get_all()
print(f"Loaded {len(faqs)} FAQs")

# Test Product repository
product_repo = RepositoryFactory.get_product_repository()
product_repo.connect()
products = product_repo.get_all()
print(f"Loaded {len(products)} products")
```

### Run Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=app

# Verbose output
python -m pytest tests/ -v
```

## Troubleshooting

### Weaviate Connection Issues

```bash
# Check if Weaviate is running
curl http://localhost:8079/v1/.well-known/ready

# Check docker logs
docker-compose logs weaviate

# Restart Weaviate
docker-compose restart weaviate
```

### LLM API Issues

```python
# Test LLM connection
from app.llm_client import LLMClient

client = LLMClient()
response = client.generate("Test prompt", max_tokens=10)
print(response)
```

### Import Errors

```bash
# Ensure in virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Data Files Missing

```bash
# Check for data files
ls -la dataset/

# Should see:
# - faq.joblib
# - clothes_json.joblib
```

## Development

### Add New Endpoint

```python
# In app/api.py
@app.route('/api/new-endpoint', methods=['POST'])
def new_endpoint():
    data = request.get_json()
    # Your logic here
    return jsonify({'result': 'success'}), 200
```

### Add New Query Type

```python
# 1. Add to models.py
class QueryType(Enum):
    FAQ = "FAQ"
    PRODUCT = "Product"
    NEW_TYPE = "NewType"  # Add this

# 2. Create strategy in strategies.py
class NewTypeStrategy(QueryStrategy):
    def handle(self, query: str):
        # Implementation
        pass

# 3. Update router
def route(self, query: str):
    if query_type == QueryType.NEW_TYPE:
        return self.new_strategy.handle(query)
```

### Modify LLM Parameters

```python
# Update config.py
self.CREATIVE_TEMPERATURE = 1.2  # Increase creativity
self.TECHNICAL_TEMPERATURE = 0.1  # More focused

# Or use environment variables
export CREATIVE_TEMPERATURE=1.2
```

## Production Deployment

### Using Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 'app.api:create_app()'

# With timeout
gunicorn -w 4 -b 0.0.0.0:5001 --timeout 120 'app.api:create_app()'
```

### Using Systemd

```bash
# Create service file: /etc/systemd/system/nexusrag.service
[Unit]
Description=NexusRAG Chatbot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/NexusRAG
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:5001 'app.api:create_app()'
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable nexusrag
sudo systemctl start nexusrag
sudo systemctl status nexusrag
```

### Using Nginx (Reverse Proxy)

```nginx
# /etc/nginx/sites-available/nexusrag
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/nexusrag /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Monitoring

### Check Service Health

```bash
# Health endpoint
curl http://localhost:5001/health

# Check response time
time curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

### Monitor Logs

```bash
# Follow logs in real-time
tail -f logs/app.log

# Count errors
grep -c ERROR logs/app.log

# Show last 100 lines
tail -n 100 logs/app.log
```

### Resource Usage

```bash
# Using Docker
docker stats

# Using system tools
htop
ps aux | grep python
```

## Backup

### Backup Data

```bash
# Backup dataset
tar -czf backup-dataset-$(date +%Y%m%d).tar.gz dataset/

# Backup logs
tar -czf backup-logs-$(date +%Y%m%d).tar.gz logs/

# Backup configuration
cp .env .env.backup
```

### Restore Data

```bash
# Restore dataset
tar -xzf backup-dataset-YYYYMMDD.tar.gz

# Restore configuration
cp .env.backup .env
```

## Performance Tuning

### Optimize Weaviate Queries

```python
# In repositories.py, adjust limits
self.search_by_text(query, limit=10)  # Instead of 20

# Reduce vectorization
self.search_by_text(query, filters=filters, limit=5)
```

### Cache Responses

```python
# Add to services.py
from functools import lru_cache

@lru_cache(maxsize=128)
def process_query_cached(self, query: str):
    return self.process_query(query)
```

### Connection Pooling

```python
# Update repositories.py
# Reuse Weaviate connections
# Keep repositories in memory
```

## Security

### Secure API Keys

```bash
# Never commit .env file
echo ".env" >> .gitignore

# Use environment variables in production
export LLM_API_KEY="your-secret-key"
```

### Add Authentication

```python
# In app/api.py
from flask import request
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != os.getenv('API_KEY'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/query', methods=['POST'])
@require_api_key
def handle_query():
    # Your code
```

### Rate Limiting

```python
# Install flask-limiter
pip install flask-limiter

# Add to app/api.py
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/query')
@limiter.limit("10 per minute")
def handle_query():
    # Your code
```

## Quick Tips

1. **Always activate virtual environment**: `source venv/bin/activate`
2. **Check logs first**: Most issues are logged in `logs/app.log`
3. **Test locally before deployment**: Use CLI mode for quick testing
4. **Keep dependencies updated**: `pip install -U -r requirements.txt`
5. **Monitor resource usage**: Keep an eye on memory and CPU
6. **Backup regularly**: Data files and configuration
7. **Use environment variables**: Never hardcode secrets
8. **Test after changes**: Run tests after modifying code
9. **Document changes**: Update README for significant changes
10. **Version control**: Commit regularly with meaningful messages

---

**For More Information:**

- Full Documentation: [README_NEW.md](README_NEW.md)
- Migration Guide: [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
- Original Assignment: [d/C1M5_Assignment.ipynb](d/C1M5_Assignment.ipynb)
