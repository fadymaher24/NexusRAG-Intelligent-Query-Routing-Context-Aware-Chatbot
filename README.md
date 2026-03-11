# RAG — Intelligent Query Routing Context-Aware Chatbot

A RAG (Retrieval-Augmented Generation) chatbot for **Fashion Forward Hub**, an online clothing store. The system intelligently routes user queries, performs semantic search over a vector database, and generates context-aware responses using a local LLM via Ollama.

---

## Features

- **Intelligent Query Routing** — Classifies queries as FAQ or Product using the LLM
- **Semantic Search** — Uses Weaviate vector embeddings (`nomic-embed-text`) to find the most relevant FAQs
- **Context-Aware Responses** — Adjusts LLM temperature/top_p based on task nature (creative vs technical)
- **Adaptive Product Filtering** — Progressively relaxes filters when results are insufficient
- **Clean Architecture** — Strategy, Repository, Factory, and Singleton design patterns
- **RESTful API** — Flask with CORS support
- **Request Tracing** — Per-request UUID trace IDs logged with span durations

---

## Architecture

```text
app/
├── api.py            # Flask endpoints + request tracing
├── config.py         # Singleton config (env-based)
├── models.py         # Data models: FAQ, Product, QueryResponse
├── repositories.py   # Weaviate data access (Repository + Factory pattern)
├── llm_client.py     # Ollama-compatible OpenAI API wrapper
├── strategies.py     # Query classifier + FAQ/Product strategies
├── services.py       # ChatbotService orchestrator
└── utils/
    ├── logger.py     # Structured file + console logging
    ├── tracing.py    # Trace context, span tracking (log-based)
    └── spinner.py    # CLI spinner (interactive mode only)
```

### Query Pipeline

```text
POST /api/chat
      │
      ▼
QueryClassifier
  └─ LLM classifies as FAQ or Product
      │
      ▼
QueryRouter
  ├─ FAQQueryStrategy
  │    └─ faq_repo.search(query, limit=5)   ← semantic search (nomic-embed-text)
  │         └─ LLM generates answer from top-5 FAQs
  │
  └─ ProductQueryStrategy
       └─ ProductRepository.search_with_adaptive_filtering()
            └─ LLM generates answer from relevant products
```

---

## Stack

| Component  | Technology                           |
| ---------- | ------------------------------------ |
| LLM        | Ollama (`llama3.2:3b`) — local, free |
| Embeddings | Ollama (`nomic-embed-text`)          |
| Vector DB  | Weaviate 1.28.1 (Docker)             |
| API        | Flask 3.x                            |
| Vectorizer | `text2vec-ollama` (Weaviate module)  |
| Python     | 3.8+                                 |

---

## Data

### Weaviate Collections

**FAQs** (25 items, vectorized with `nomic-embed-text`)

- Properties: `question`, `answer`, `type`
- Categories: returns & exchanges, shipping & delivery, product info, payment, general

**Products** (44,424 items)

- Properties: `productDisplayName`, `price`, `brandName`, `ageGroup`, `gender`, `baseColour`, `season`, `usage`, `productId`, `masterCategory`, `subCategory`, `articleType`

---

## Setup

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (for Weaviate)
- [Ollama](https://ollama.com/) installed and running
- Python 3.8+

### 1. Install Ollama and pull models

```bash
ollama serve   # start in a terminal (or as a system service)

# In another terminal:
ollama pull llama3.2:3b         # chat + classification model
ollama pull nomic-embed-text    # embedding model (used by Weaviate vectorizer)
```

### 2. Clone and install dependencies

```bash
git clone https://github.com/fadymaher24/NexusRAG-Intelligent-Query-Routing-Context-Aware-Chatbot
cd NexusRAG-Intelligent-Query-Routing-Context-Aware-Chatbot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` for local Ollama:

```env
LLM_MODEL=llama3.2:3b
LLM_API_KEY=
LLM_API_BASE_URL=http://localhost:11434/v1

WEAVIATE_HOST=localhost
WEAVIATE_PORT=8079
WEAVIATE_GRPC_PORT=50050

FLASK_HOST=0.0.0.0
FLASK_PORT=5001
LOG_LEVEL=INFO
```

### 4. Start Weaviate

```bash
docker-compose up -d
```

Weaviate runs at `http://localhost:8079`.

### 5. Load data into Weaviate

```bash
python load_data.py
```

Loads all FAQs and products into Weaviate and generates vector embeddings via `nomic-embed-text`.

### 6. Run the server

```bash
python main.py
```

Server runs at `http://localhost:5001`.

---

## API

### Health check

```bash
GET /health
```

```json
{ "status": "healthy", "service": "NexusRAG Chatbot" }
```

### Chat (simple)

```bash
POST /api/chat
Content-Type: application/json

{"message": "What is your return policy?"}
```

```json
{
  "response": "Our return policy allows returns within 30 days...",
  "query_type": "FAQ"
}
```

### Query (full details)

```bash
POST /api/query
Content-Type: application/json

{"query": "Show me blue T-shirts under $50"}
```

```json
{
  "success": true,
  "query_type": "Product",
  "task_nature": "technical",
  "response": "Here are some blue T-shirts under $50...",
  "products": [...],
  "metadata": {"temperature": 0.3, "top_p": 0.8, "max_tokens": 500}
}
```

---

## Example Queries

**FAQ queries** (semantic search over 25 FAQs):

- "What is your return policy?"
- "How long does delivery take?"
- "Do you offer international shipping?"
- "How can I contact customer support?"

**Product queries — technical** (filtered Weaviate search):

- "Show me blue T-shirts under $50"
- "What formal dresses do you have for women?"
- "Do you have red sneakers?"

**Product queries — creative** (higher temperature, styled answers):

- "Create a look for a beach party"
- "Suggest an outfit for a job interview"
- "Help me dress for a winter wedding"

---

## Configuration Reference

| Variable             | Default                                  | Description                                     |
| -------------------- | ---------------------------------------- | ----------------------------------------------- |
| `LLM_MODEL`          | `meta-llama/Llama-3.2-3B-Instruct-Turbo` | Model name                                      |
| `LLM_API_BASE_URL`   | _(empty)_                                | API base URL (e.g. `http://localhost:11434/v1`) |
| `LLM_API_KEY`        | _(empty)_                                | API key (leave empty for Ollama)                |
| `WEAVIATE_HOST`      | `localhost`                              | Weaviate host                                   |
| `WEAVIATE_PORT`      | `8079`                                   | Weaviate HTTP port                              |
| `WEAVIATE_GRPC_PORT` | `50050`                                  | Weaviate gRPC port                              |
| `FLASK_PORT`         | `5001`                                   | Flask server port                               |
| `LOG_LEVEL`          | `INFO`                                   | Logging level                                   |

---

## Running Modes

### Web server (default)

```bash
python main.py
# open http://localhost:5001
```

### CLI (interactive)

```bash
python main.py --mode cli
```

### Custom port / debug

```bash
python main.py --port 8000 --debug
```

### Background (nohup)

```bash
nohup python main.py > /tmp/nexusrag.log 2>&1 &
```

---

## Tests

```bash
python -m pytest tests/
```

---

## Docker (full stack)

```bash
docker-compose up -d    # start Weaviate + app
docker-compose down     # stop
```

> Ollama must run on the host (`ollama serve`). The container reaches it via `host.docker.internal`.

---

## Logs

Each request gets a UUID trace ID. All spans are logged with durations:

```text
[trace_id=abc-123] [handle_query_request] Starting
[trace_id=abc-123] Query classified as: FAQ
[trace_id=abc-123] Found 5 FAQs matching query
[trace_id=abc-123] [process_query] Query processed successfully in 3200ms
```

```bash
tail -f logs/app.log
# or if started with nohup:
tail -f /tmp/nexusrag.log
```

---

## License

See [LICENSE](LICENSE).
