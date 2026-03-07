# Setup Instructions

## ✅ Fixed Installation Issues

The project has been updated to work with Python 3.14 and modern package versions.

## Quick Setup

### 1. Install Dependencies

```bash
cd /mnt/fady/git-fedora/NexusRAG-Intelligent-Query-Routing-Context-Aware-Chatbot
pip install -r requirements.txt --user
```

### 2. Configure Environment

```bash
cp .env.example .env
nano .env  # Edit with your API keys
```

### 3. Configure Your LLM Provider

The application now uses a standard OpenAI-compatible API interface. Edit your `.env` file:

#### For Together AI (Recommended):

```bash
LLM_API_BASE_URL=https://api.together.xyz/v1
LLM_API_KEY=your_together_api_key
LLM_MODEL=meta-llama/Llama-3.2-3B-Instruct-Turbo
```

#### For OpenAI:

```bash
LLM_API_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your_openai_api_key
LLM_MODEL=gpt-3.5-turbo
```

#### For Local LLM (Ollama/LM Studio):

```bash
LLM_API_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=  # Leave empty for local
LLM_MODEL=llama2
```

### 4. Setup Weaviate

#### Option A: Using Docker (Recommended)

```bash
docker-compose up -d
```

#### Option B: Local Weaviate

Make sure Weaviate is running on port 8079:

```bash
WEAVIATE_HOST=localhost
WEAVIATE_PORT=8079
WEAVIATE_GRPC_PORT=50050
```

### 5. Run the Application

#### Web Server Mode:

```bash
python main.py
# Access: http://localhost:5001
```

#### CLI Mode:

```bash
python main.py --mode cli
```

## What Was Fixed

### 1. **Removed Incompatible Dependencies**

- ❌ pandas 2.0.3 (not compatible with Python 3.14)
- ❌ numpy 1.24.3 (not needed)
- ❌ sentence-transformers (not used in current code)
- ❌ together (replaced with direct API calls)
- ❌ openai (replaced with generic requests)
- ❌ httpx, opentelemetry (not needed)
- ❌ jupyter, ipywidgets (not needed for production)

### 2. **Updated to Compatible Versions**

- ✅ Flask 3.1.3 (Python 3.14 compatible)
- ✅ weaviate-client 4.20.3 (latest version)
- ✅ joblib 1.5.3 (latest version)
- ✅ flask-cors 6.0.2 (latest version)

### 3. **Fixed LLM Client**

- Removed dependency on deleted `src/utils.py`
- Implemented direct HTTP client using `requests`
- Uses standard OpenAI-compatible API format
- Works with multiple LLM providers (Together AI, OpenAI, local models)

### 4. **Cleaned Up Project**

- Removed old `src/` directory
- Removed unused CSV files from dataset
- Removed duplicate documentation
- Removed artifact files

## Testing the Installation

```bash
# Test Python imports
python -c "from app.config import config; print('✓ Config loaded')"
python -c "from app.services import ChatbotService; print('✓ Services loaded')"
python -c "import flask; import weaviate; import joblib; print('✓ All deps OK')"

# Check structure
tree -L 2 -I '.git|.venv|__pycache__'
```

## Troubleshooting

### Issue: Cannot import from app

**Solution**: Make sure you're in the project root directory

### Issue: Weaviate connection failed

**Solution**:

1. Check if Weaviate is running: `curl http://localhost:8079/v1/.well-known/ready`
2. Start with Docker: `docker-compose up -d`

### Issue: LLM API errors

**Solution**:

1. Verify your API key in `.env`
2. Check the API base URL is correct
3. Test without API (will return mock responses)

## Next Steps

1. ✅ Dependencies installed
2. ✅ Configure `.env` with your API keys
3. ✅ Start Weaviate database
4. ✅ Run the application
5. ✅ Test with sample queries

## Directory Structure

```
NexusRAG-Intelligent-Query-Routing-Context-Aware-Chatbot/
├── app/                    # Production application
├── dataset/                # Data files (joblib only)
├── tests/                  # Unit tests
├── main.py                 # Entry point
├── requirements.txt        # Updated dependencies
├── .env                    # Your configuration (create from .env.example)
└── docker-compose.yml      # Docker setup
```

## Support

- Check logs: `tail -f logs/app.log`
- Run tests: `python -m pytest tests/`
- Documentation: See `README.md`, `QUICK_REFERENCE.md`

---

**Status**: ✅ Ready for use with Python 3.14
