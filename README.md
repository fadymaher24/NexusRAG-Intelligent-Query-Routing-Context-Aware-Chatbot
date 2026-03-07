# NexusRAG - Intelligent Query Routing Context-Aware Chatbot

A production-ready RAG (Retrieval-Augmented Generation) chatbot system for Fashion Forward Hub, an online clothing store. This system intelligently routes queries, provides context-aware responses, and integrates with vector databases for semantic search.

## 🎯 Features

- **Intelligent Query Routing**: Automatically classifies queries as FAQ or Product-related
- **Context-Aware Responses**: Adjusts LLM parameters based on query nature (creative vs technical)
- **Semantic Search**: Uses Weaviate vector database for efficient product retrieval
- **Adaptive Filtering**: Progressively relaxes filters when results are insufficient
- **Production-Ready Architecture**: Implements design patterns (Strategy, Repository, Factory, Singleton)
- **RESTful API**: Flask-based API with CORS support
- **Web Interface**: Beautiful, responsive chat interface
- **CLI Mode**: Command-line interface for testing
- **Comprehensive Logging**: Structured logging with file and console output

## 🏗️ Architecture

The application follows clean architecture principles with clear separation of concerns:

```
app/
├── __init__.py           # Package initialization
├── config.py             # Configuration management (Singleton pattern)
├── models.py             # Data models and DTOs
├── repositories.py       # Data access layer (Repository pattern)
├── llm_client.py         # LLM interaction abstraction
├── strategies.py         # Query routing logic (Strategy pattern)
├── services.py           # Business logic layer
├── api.py                # Flask API endpoints
└── utils/
    ├── __init__.py
    └── logger.py         # Logging configuration
```

### Design Patterns Used

1. **Strategy Pattern**: Different strategies for handling FAQ and Product queries
2. **Repository Pattern**: Abstraction over data access (FAQ and Product repositories)
3. **Factory Pattern**: Centralized creation of service and repository instances
4. **Singleton Pattern**: Configuration and logger instances
5. **Service Layer**: High-level business logic orchestration

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Weaviate instance running (local or remote)
- LLM API access (Together AI, OpenAI, or compatible)

### Installation

1. Clone the repository:

```bash
cd NexusRAG-Intelligent-Query-Routing-Context-Aware-Chatbot
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Ensure your dataset files are in place:

```
dataset/
├── faq.joblib           # FAQ data
└── clothes_json.joblib  # Product data
```

### Running the Application

#### Web Server Mode (Default)

```bash
python main.py
```

Then open your browser to `http://localhost:5001`

#### CLI Mode

```bash
python main.py --mode cli
```

#### Custom Configuration

```bash
# Run on different port
python main.py --port 8000

# Enable debug mode
python main.py --debug

# Custom host and port
python main.py --host 0.0.0.0 --port 8080
```

## 📡 API Endpoints

### Health Check

```bash
GET /health
```

Response:

```json
{
  "status": "healthy",
  "service": "NexusRAG Chatbot"
}
```

### Query Endpoint (Full Response)

```bash
POST /api/query
Content-Type: application/json

{
  "query": "Do you have blue T-shirts?"
}
```

Response:

```json
{
  "success": true,
  "query_type": "Product",
  "task_nature": "technical",
  "response": "Yes, we have several blue T-shirts available...",
  "products": [...],
  "metadata": {
    "temperature": 0.3,
    "top_p": 0.8,
    "max_tokens": 500
  }
}
```

### Chat Endpoint (Simple)

```bash
POST /api/chat
Content-Type: application/json

{
  "message": "What is your return policy?"
}
```

Response:

```json
{
  "response": "Our return policy allows...",
  "query_type": "FAQ"
}
```

## 🎨 Example Queries

### FAQ Queries

- "What is your return policy?"
- "How long does delivery take?"
- "Do you offer international shipping?"
- "How can I contact customer support?"

### Product Queries (Technical)

- "Show me blue T-shirts under $50"
- "Do you have formal dresses for women?"
- "What sneakers do you have in stock?"

### Product Queries (Creative)

- "Create a look for a beach party"
- "Suggest an outfit for a job interview"
- "Help me dress for a winter wedding"

## 🔧 Configuration

All configuration is managed through environment variables or the `app/config.py` file:

- **Weaviate Settings**: Connection parameters for vector database
- **LLM Settings**: Model selection and API configuration
- **Query Routing**: Temperature and top_p values for different query types
- **Flask Settings**: Host, port, and debug mode
- **Logging**: Log level and file location

## 📊 Project Structure

```
NexusRAG-Intelligent-Query-Routing-Context-Aware-Chatbot/
├── app/                      # Main application package
│   ├── __init__.py
│   ├── api.py               # Flask API
│   ├── config.py            # Configuration
│   ├── llm_client.py        # LLM interface
│   ├── models.py            # Data models
│   ├── repositories.py      # Data access
│   ├── services.py          # Business logic
│   ├── strategies.py        # Query routing
│   └── utils/               # Utilities
│       ├── __init__.py
│       └── logger.py        # Logging
├── dataset/                 # Data files
│   ├── faq.joblib
│   └── clothes_json.joblib
├── logs/                    # Application logs
├── src/                     # Legacy source (for compatibility)
├── main.py                  # Main entry point
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

## 🧪 Development

### Adding New Query Types

1. Create a new strategy class in `app/strategies.py` inheriting from `QueryStrategy`
2. Implement the `handle()` method
3. Update the `QueryRouter` to route to your new strategy
4. Add new query type to `models.py` if needed

### Adding New Data Sources

1. Create a new repository class in `app/repositories.py`
2. Inherit from `BaseRepository`
3. Implement required methods
4. Register in `RepositoryFactory`

### Extending the LLM Client

The `LLMClient` class in `app/llm_client.py` provides abstraction over LLM providers. To add support for a new provider:

1. Update the `generate()` method to support your provider
2. Add provider-specific configuration to `config.py`

## 🐛 Troubleshooting

### Weaviate Connection Issues

- Ensure Weaviate is running on the correct port
- Check `WEAVIATE_PORT` and `WEAVIATE_GRPC_PORT` in your `.env`
- Verify the products collection exists in Weaviate

### LLM API Errors

- Verify your API key is correct
- Check API rate limits
- Ensure the model name is valid for your provider

### Import Errors

- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.8+ required)

## 📝 Logging

Logs are written to both console and file (`logs/app.log`). Log levels:

- DEBUG: Detailed information for debugging
- INFO: General informational messages
- WARNING: Warning messages
- ERROR: Error messages with stack traces
- CRITICAL: Critical errors

Configure log level via `LOG_LEVEL` environment variable.

## 🤝 Contributing

This project was converted from a Coursera assignment to a production-ready application. Contributions are welcome!

## 📄 License

See LICENSE file for details.

## 🙏 Acknowledgments

- Original assignment from DeepLearning.AI RAG course
- Fashion Forward Hub for the use case
- Weaviate for vector database capabilities

## 📧 Support

For issues and questions, please open an issue on the repository.

---

**Built with ❤️ using Python, Flask, Weaviate, and LLMs**
