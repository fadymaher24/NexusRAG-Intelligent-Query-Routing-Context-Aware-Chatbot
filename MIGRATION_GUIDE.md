# Migration Guide: From Jupyter Notebook to Production-Ready Application

## Overview

Your Coursera assignment has been successfully restructured from a Jupyter notebook into a production-ready application with proper design patterns and architecture.

## What Changed?

### Before (Jupyter Notebook)

- Single notebook file with all code
- Functions scattered throughout cells
- No clear separation of concerns
- Hardcoded configurations
- Manual execution of cells
- Limited to Coursera environment

### After (Production Application)

- Modular, maintainable code structure
- Clear separation of concerns (MVC-like architecture)
- Design patterns: Strategy, Repository, Factory, Singleton
- Configuration management via environment variables
- RESTful API with web interface
- CLI mode for testing
- Comprehensive error handling and logging
- Docker support
- Unit tests

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                      API Layer                          │
│  (Flask endpoints, Web UI, Request handling)            │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  Service Layer                          │
│  (Business logic orchestration, ChatbotService)         │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼────┐  ┌─────▼──────┐  ┌───▼────────┐
│  Strategy  │  │    LLM     │  │ Repository │
│  Pattern   │  │   Client   │  │  Pattern   │
│            │  │            │  │            │
│ - Router   │  │ - Generate │  │ - FAQ      │
│ - FAQ      │  │ - Classify │  │ - Product  │
│ - Product  │  │ - Parse    │  │            │
└────────────┘  └────────────┘  └─────┬──────┘
                                      │
                             ┌────────▼────────┐
                             │  Data Sources   │
                             │  - Weaviate DB  │
                             │  - FAQ Files    │
                             └─────────────────┘
```

## Design Patterns Applied

### 1. **Strategy Pattern** (`app/strategies.py`)

Different strategies for handling different query types:

- `FAQQueryStrategy`: Handles FAQ queries
- `ProductQueryStrategy`: Handles product queries
- `QueryRouter`: Routes queries to appropriate strategy

**Why?** Allows easy addition of new query types without modifying existing code.

### 2. **Repository Pattern** (`app/repositories.py`)

Abstract data access layer:

- `FAQRepository`: Access to FAQ data
- `ProductRepository`: Access to product data via Weaviate
- `RepositoryFactory`: Creates repository instances

**Why?** Decouples business logic from data access, makes testing easier.

### 3. **Factory Pattern**

Centralized object creation:

- `RepositoryFactory`: Creates repositories
- `ServiceFactory`: Creates services
- `LLMClientFactory`: Creates LLM clients

**Why?** Ensures consistent object creation and manages singleton instances.

### 4. **Singleton Pattern**

Single instance management:

- `Config`: Configuration settings
- `Logger`: Logging instance

**Why?** Ensures only one instance exists, prevents resource duplication.

### 5. **Service Layer Pattern** (`app/services.py`)

High-level business logic:

- `ChatbotService`: Orchestrates all operations

**Why?** Provides clean API for application logic, separates concerns.

## File Mapping

### Notebook Functions → New Structure

| Notebook Function                    | New Location                                                                 |
| ------------------------------------ | ---------------------------------------------------------------------------- |
| `check_if_faq_or_product()`          | `app/strategies.py` → `QueryClassifier.classify_query_type()`                |
| `query_on_faq()`                     | `app/strategies.py` → `FAQQueryStrategy.handle()`                            |
| `decide_task_nature()`               | `app/strategies.py` → `QueryClassifier.classify_task_nature()`               |
| `get_params_for_task()`              | `app/config.py` → `Config.get_llm_params()`                                  |
| `generate_metadata_from_query()`     | `app/strategies.py` → `ProductQueryStrategy.extract_metadata()`              |
| `get_relevant_products_from_query()` | `app/repositories.py` → `ProductRepository.search_with_adaptive_filtering()` |
| `query_on_products()`                | `app/strategies.py` → `ProductQueryStrategy.handle()`                        |
| `answer_query()`                     | `app/services.py` → `ChatbotService.process_query()`                         |
| `generate_with_single_input()`       | `app/llm_client.py` → `LLMClient.generate()`                                 |

## How to Use the New Structure

### 1. Quick Start

```bash
# Setup environment
./setup.sh

# Edit configuration
nano .env

# Run the application
python main.py
```

### 2. As a Web Service

```bash
# Start the server
python main.py

# Access web interface
open http://localhost:5001

# Call API
curl -X POST http://localhost:5001/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Do you have blue T-shirts?"}'
```

### 3. As a CLI Tool

```bash
python main.py --mode cli
```

### 4. In Your Code

```python
from app.services import ChatbotService

# Create and setup service
with ChatbotService() as service:
    # Process a query
    response = service.process_query("What is your return policy?")

    if response.success:
        print(response.response)
```

### 5. Using Docker

```bash
# Build and run with docker-compose
docker-compose up

# Access at http://localhost:5001
```

## Configuration

All configuration is managed through environment variables (`.env` file):

```bash
# Weaviate
WEAVIATE_HOST=localhost
WEAVIATE_PORT=8079

# LLM
LLM_MODEL=meta-llama/Llama-3.2-3B-Instruct-Turbo
LLM_API_KEY=your_key_here

# Application
FLASK_PORT=5001
LOG_LEVEL=INFO
```

## Testing

### Run Unit Tests

```bash
python -m pytest tests/
```

### Manual Testing

```python
# Test in Python REPL
from app.services import ChatbotService

service = ChatbotService()
service.setup()

# Test FAQ query
response = service.process_query("What is your return policy?")
print(response.to_dict())

# Test Product query
response = service.process_query("Show me blue T-shirts")
print(response.to_dict())

service.cleanup()
```

## Adding New Features

### Add a New Query Type

1. Create a new strategy class:

```python
# In app/strategies.py
class NewQueryStrategy(QueryStrategy):
    def handle(self, query: str) -> Dict[str, Any]:
        # Your logic here
        return {...}
```

2. Update the router:

```python
# In app/strategies.py
class QueryRouter:
    def route(self, query: str):
        # Add routing logic for new type
        if query_type == QueryType.NEW_TYPE:
            return self.new_strategy.handle(query)
```

### Add a New Data Source

1. Create a new repository:

```python
# In app/repositories.py
class NewDataRepository(BaseRepository):
    def get_all(self):
        # Your logic here
        pass
```

2. Register in factory:

```python
class RepositoryFactory:
    @classmethod
    def get_new_repository(cls):
        # Return instance
        pass
```

## Deployment

### Production Checklist

- [ ] Update `.env` with production configuration
- [ ] Set `FLASK_DEBUG=False`
- [ ] Configure production database credentials
- [ ] Set up proper logging (`LOG_LEVEL=WARNING`)
- [ ] Enable HTTPS (use reverse proxy like nginx)
- [ ] Set up monitoring and alerting
- [ ] Configure auto-restart (systemd, supervisor, or k8s)
- [ ] Set up backup for data files
- [ ] Review and update security settings

### Deployment Options

1. **Traditional Server**

   ```bash
   # Use gunicorn for production
   gunicorn -w 4 -b 0.0.0.0:5001 'app.api:create_app()'
   ```

2. **Docker**

   ```bash
   docker-compose up -d
   ```

3. **Cloud Platforms**
   - AWS: Elastic Beanstalk, ECS, or Lambda
   - GCP: Cloud Run, App Engine
   - Azure: App Service, Container Instances
   - Heroku: Direct deployment

## Benefits of New Structure

1. **Maintainability**: Clear code organization, easy to find and fix bugs
2. **Scalability**: Add features without breaking existing code
3. **Testability**: Isolated components, easy to unit test
4. **Reusability**: Components can be reused in other projects
5. **Professional**: Industry-standard patterns and practices
6. **Production-Ready**: Error handling, logging, configuration management
7. **Flexibility**: Multiple interfaces (API, CLI, programmatic)
8. **Documentation**: Clear README, inline documentation
9. **Deployment**: Docker support, easy deployment options
10. **Team-Friendly**: Clear structure makes collaboration easier

## Migration Notes

### Compatibility

The new structure maintains compatibility with your original notebook's functionality. All original functions have been preserved as methods in appropriate classes.

### Data Files

Your original data files (`faq.joblib`, `clothes_json.joblib`) work without modification.

### LLM Integration

The LLM client abstracts the original `generate_with_single_input()` function. You can easily swap LLM providers by updating the `LLMClient` class.

## Next Steps

1. **Review Configuration**: Update `.env` with your settings
2. **Test Locally**: Run `python main.py --mode cli` to test
3. **Deploy**: Choose deployment option and deploy
4. **Monitor**: Set up logging and monitoring
5. **Iterate**: Add features, improve based on usage

## Support

If you encounter any issues:

1. Check the logs in `logs/app.log`
2. Verify configuration in `.env`
3. Ensure all dependencies are installed
4. Check Weaviate connection

## Conclusion

Your Coursera assignment has been transformed into a professional, production-ready application. The new structure follows industry best practices and is ready for real-world deployment.

Happy coding! 🚀
