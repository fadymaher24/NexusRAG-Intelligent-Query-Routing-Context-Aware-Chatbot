# Project Structure

```
NexusRAG-Intelligent-Query-Routing-Context-Aware-Chatbot/
│
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   │
│   ├── config.py                # Configuration management (Singleton)
│   │   └── Config class         # Environment-based configuration
│   │
│   ├── models.py                # Data models and DTOs
│   │   ├── QueryType            # Enum for query types
│   │   ├── TaskNature           # Enum for task nature
│   │   ├── Product              # Product data model
│   │   ├── FAQ                  # FAQ data model
│   │   ├── ProductMetadata      # Metadata for filtering
│   │   └── QueryResponse        # Response model
│   │
│   ├── repositories.py          # Data access layer (Repository Pattern)
│   │   ├── BaseRepository       # Abstract base class
│   │   ├── FAQRepository        # FAQ data access
│   │   ├── ProductRepository    # Product/Weaviate access
│   │   └── RepositoryFactory    # Factory for repositories
│   │
│   ├── llm_client.py           # LLM interaction abstraction
│   │   ├── LLMClient           # Main LLM client
│   │   └── LLMClientFactory    # Factory for LLM client
│   │
│   ├── strategies.py           # Query routing (Strategy Pattern)
│   │   ├── QueryClassifier     # Query type & nature classification
│   │   ├── QueryStrategy       # Abstract strategy base
│   │   ├── FAQQueryStrategy    # FAQ handling strategy
│   │   ├── ProductQueryStrategy # Product handling strategy
│   │   └── QueryRouter         # Routes queries to strategies
│   │
│   ├── services.py             # Business logic layer (Service Pattern)
│   │   ├── ChatbotService      # Main service orchestrator
│   │   └── ServiceFactory      # Factory for services
│   │
│   ├── api.py                  # Flask API endpoints
│   │   ├── create_app()        # App factory
│   │   ├── /health             # Health check endpoint
│   │   ├── /api/query          # Full query endpoint
│   │   ├── /api/chat           # Simple chat endpoint
│   │   └── /                   # Web interface
│   │
│   └── utils/                  # Utility modules
│       ├── __init__.py
│       └── logger.py           # Logging configuration (Singleton)
│
├── dataset/                    # Data files
│   ├── faq.joblib             # FAQ data (loaded by FAQRepository)
│   └── clothes_json.joblib     # Product data (loaded to Weaviate)
│
├── logs/                       # Application logs
│   └── app.log                # Main log file
│
├── tests/                      # Unit tests
│   └── test_app.py            # Test suite
│
├── src/                        # Legacy source (for compatibility)
│   ├── utils.py               # Original utility functions
│   ├── flask_app.py           # Original Flask app
│   └── weaviate_server.py     # Original Weaviate setup
│
├── d/                          # Original assignment files
│   ├── C1M5_Assignment.ipynb  # Original Jupyter notebook
│   └── ...                    # Other assignment files
│
├── main.py                     # Main entry point
│   ├── run_cli()              # CLI mode
│   ├── run_server()           # Server mode
│   └── main()                 # Argument parser
│
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
│
├── setup.sh                    # Setup script
├── Dockerfile                  # Docker configuration
├── docker-compose.yml         # Docker Compose configuration
│
├── README_NEW.md              # Comprehensive documentation
├── MIGRATION_GUIDE.md         # Migration guide from notebook
├── QUICK_REFERENCE.md         # Quick reference guide
└── PROJECT_STRUCTURE.md       # This file

```

## Component Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                             │
│                   (Entry Point)                             │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
    ┌────▼─────┐                  ┌─────▼────┐
    │ CLI Mode │                  │ API Mode │
    │          │                  │ (Flask)  │
    └────┬─────┘                  └─────┬────┘
         │                              │
         └──────────┬───────────────────┘
                    │
         ┌──────────▼──────────┐
         │  ChatbotService     │
         │  (Service Layer)    │
         └──────────┬──────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
    ┌────▼─────┐        ┌─────▼────┐
    │  Query   │        │   LLM    │
    │  Router  │        │  Client  │
    └────┬─────┘        └─────┬────┘
         │                    │
    ┌────┴─────┬──────────────┘
    │          │
┌───▼───┐  ┌──▼────┐
│  FAQ  │  │Product│
│Strategy│  │Strategy│
└───┬───┘  └───┬───┘
    │          │
┌───▼───┐  ┌───▼────┐
│  FAQ  │  │Product │
│ Repo  │  │  Repo  │
└───┬───┘  └───┬────┘
    │          │
┌───▼───┐  ┌───▼────┐
│FAQ    │  │Weaviate│
│Files  │  │   DB   │
└───────┘  └────────┘
```

## Layer Responsibilities

### 1. Entry Point Layer (`main.py`)

- **Purpose**: Application bootstrapping
- **Responsibilities**:
  - Parse command-line arguments
  - Configure application
  - Start CLI or server mode
- **Dependencies**: Service layer

### 2. API Layer (`app/api.py`)

- **Purpose**: HTTP interface
- **Responsibilities**:
  - Handle HTTP requests
  - Validate input
  - Format responses
  - Serve web interface
- **Dependencies**: Service layer
- **Accessed by**: External clients

### 3. Service Layer (`app/services.py`)

- **Purpose**: Business logic orchestration
- **Responsibilities**:
  - Coordinate between components
  - Manage application lifecycle
  - Error handling
  - Transaction management
- **Dependencies**: Strategies, LLM, Repositories
- **Accessed by**: API layer, CLI

### 4. Strategy Layer (`app/strategies.py`)

- **Purpose**: Query routing and handling
- **Responsibilities**:
  - Classify queries
  - Route to appropriate handler
  - Execute query-specific logic
- **Dependencies**: LLM client, Repositories
- **Accessed by**: Service layer

### 5. Repository Layer (`app/repositories.py`)

- **Purpose**: Data access abstraction
- **Responsibilities**:
  - Load and query data
  - Abstract data sources
  - Manage connections
- **Dependencies**: Data sources
- **Accessed by**: Strategy layer

### 6. LLM Client Layer (`app/llm_client.py`)

- **Purpose**: LLM interaction
- **Responsibilities**:
  - Generate responses
  - Parse JSON
  - Handle API calls
- **Dependencies**: External LLM API
- **Accessed by**: Strategy layer

### 7. Model Layer (`app/models.py`)

- **Purpose**: Data structures
- **Responsibilities**:
  - Define data models
  - Validate data
  - Convert between formats
- **Dependencies**: None
- **Accessed by**: All layers

### 8. Configuration Layer (`app/config.py`)

- **Purpose**: Centralized configuration
- **Responsibilities**:
  - Load environment variables
  - Provide configuration values
  - Manage defaults
- **Dependencies**: Environment
- **Accessed by**: All layers

### 9. Utility Layer (`app/utils/`)

- **Purpose**: Cross-cutting concerns
- **Responsibilities**:
  - Logging
  - Helper functions
  - Common utilities
- **Dependencies**: None
- **Accessed by**: All layers

## Data Flow

### FAQ Query Flow

```
User Input → API → Service → Router → Classifier → FAQStrategy
                                                        ↓
                                                   FAQ Repo
                                                        ↓
                                                   Load FAQs
                                                        ↓
                                                  LLM Client
                                                        ↓
                                                   Generate
                                                        ↓
User Response ← API ← Service ← Router ← FAQStrategy ←┘
```

### Product Query Flow

```
User Input → API → Service → Router → Classifier → ProductStrategy
                                                         ↓
                                                    Classify Nature
                                                         ↓
                                                    Extract Metadata
                                                         ↓
                                                    Product Repo
                                                         ↓
                                                  Search Weaviate
                                                         ↓
                                                    LLM Client
                                                         ↓
                                                     Generate
                                                         ↓
User Response ← API ← Service ← Router ← ProductStrategy ←┘
```

## Design Pattern Mapping

### Singleton Pattern

- **Files**: `app/config.py`, `app/utils/logger.py`
- **Purpose**: Single instance management
- **Classes**: `Config`, `Logger`

### Factory Pattern

- **Files**: `app/repositories.py`, `app/services.py`, `app/llm_client.py`
- **Purpose**: Object creation
- **Classes**: `RepositoryFactory`, `ServiceFactory`, `LLMClientFactory`

### Strategy Pattern

- **Files**: `app/strategies.py`
- **Purpose**: Algorithm selection
- **Classes**: `QueryStrategy`, `FAQQueryStrategy`, `ProductQueryStrategy`

### Repository Pattern

- **Files**: `app/repositories.py`
- **Purpose**: Data access abstraction
- **Classes**: `BaseRepository`, `FAQRepository`, `ProductRepository`

### Service Layer Pattern

- **Files**: `app/services.py`
- **Purpose**: Business logic encapsulation
- **Classes**: `ChatbotService`

## File Size Overview

| File                  | LOC (approx) | Purpose              |
| --------------------- | ------------ | -------------------- |
| `app/config.py`       | ~100         | Configuration        |
| `app/models.py`       | ~200         | Data models          |
| `app/repositories.py` | ~300         | Data access          |
| `app/llm_client.py`   | ~150         | LLM interface        |
| `app/strategies.py`   | ~400         | Query routing        |
| `app/services.py`     | ~150         | Business logic       |
| `app/api.py`          | ~300         | Flask API            |
| `app/utils/logger.py` | ~80          | Logging              |
| `main.py`             | ~150         | Entry point          |
| **Total**             | **~1,830**   | **Core application** |

## Key Files to Understand

1. **Start Here**: `main.py` - Entry point
2. **Core Logic**: `app/services.py` - Main service
3. **Routing**: `app/strategies.py` - Query handling
4. **Data Access**: `app/repositories.py` - Database operations
5. **Configuration**: `app/config.py` - Settings
6. **API**: `app/api.py` - Web interface

## Extension Points

### Add New Query Type

- Modify: `app/models.py` (add enum value)
- Create: New strategy in `app/strategies.py`
- Update: `QueryRouter` in `app/strategies.py`

### Add New Data Source

- Create: New repository in `app/repositories.py`
- Update: `RepositoryFactory` in `app/repositories.py`

### Add New Endpoint

- Modify: `app/api.py` (add new route)

### Change LLM Provider

- Modify: `app/llm_client.py` (update generate method)

### Modify Query Parameters

- Modify: `app/config.py` (update defaults)
- Or: Update `.env` file

## Dependencies Between Files

```
main.py
  └── app/__init__.py
       ├── app/config.py (no dependencies)
       ├── app/models.py (no dependencies)
       ├── app/utils/logger.py
       │    └── app/config.py
       ├── app/repositories.py
       │    ├── app/models.py
       │    ├── app/config.py
       │    └── app/utils/logger.py
       ├── app/llm_client.py
       │    ├── app/config.py
       │    └── app/utils/logger.py
       ├── app/strategies.py
       │    ├── app/models.py
       │    ├── app/repositories.py
       │    ├── app/llm_client.py
       │    ├── app/config.py
       │    └── app/utils/logger.py
       ├── app/services.py
       │    ├── app/models.py
       │    ├── app/repositories.py
       │    ├── app/llm_client.py
       │    ├── app/strategies.py
       │    ├── app/config.py
       │    └── app/utils/logger.py
       └── app/api.py
            ├── app/services.py
            ├── app/config.py
            └── app/utils/logger.py
```

## Testing Structure

```
tests/
├── test_app.py              # Main test file
├── test_models.py           # Model tests (to be added)
├── test_repositories.py     # Repository tests (to be added)
├── test_strategies.py       # Strategy tests (to be added)
└── test_services.py         # Service tests (to be added)
```

---

This structure provides:

- ✅ Clear separation of concerns
- ✅ Easy to test and maintain
- ✅ Scalable architecture
- ✅ Professional code organization
- ✅ Industry-standard patterns
