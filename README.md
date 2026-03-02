# NexusRAG: Intelligent Query Routing & Context-Aware Chatbot

An advanced Retrieval-Augmented Generation (RAG) pipeline designed to intelligently route queries, dynamically adjust generation parameters, and provide highly accurate, context-grounded responses about product data.

This project demonstrates a production-ready approach to LLM application development, moving beyond simple wrapper scripts to a robust architecture capable of handling varied user intents with structured, predictable outputs.

## 🚀 Key Features

- **Intelligent LLM Routing:** Analyzes incoming queries to determine their nature and routes them to specialized processing pipelines for optimal handling.
- **Dynamic Parameter Setting:** Employs an intent classifier to distinguish between creative requests (requiring higher temperature/creativity) and technical inquiries (requiring low temperature/high factual accuracy), adjusting LLM parameters on the fly.
- **Context Augmentation (RAG):** Retrieves relevant product information from a local vector database to ground LLM responses, drastically reducing hallucinations and ensuring domain-specific accuracy.
- **Structured JSON Generation:** Forces the LLM to output valid, parsed JSON responses for product information, making the system easily integratable with downstream APIs or front-end applications.
- **Interactive Chatbot Interface:** A conversational UI that allows users to interact naturally with the underlying RAG system.
- **Comprehensive Testing:** Fully tested components ensuring reliability across the routing, retrieval, and generation stages.

## 🗂️ Project Structure

The repository is organized for maintainability and scalability:

```text
nexus-rag/
├── data/
│   └── sample_products.json     # Mock product data used for vector embeddings
├── src/
│   ├── __init__.py
│   ├── router.py                # Query categorization and LLM routing logic
│   ├── classifier.py            # Creative vs. Technical parameter adjustment
│   ├── retriever.py             # Context augmentation and RAG pipeline
│   ├── generator.py             # Structured JSON response generation
│   └── chatbot.py               # Interactive CLI/Web interface
├── tests/
│   ├── __init__.py
│   ├── test_router.py           # Unit tests for routing logic
│   ├── test_classifier.py       # Unit tests for parameter settings
│   ├── test_retriever.py        # Tests for the retrieval accuracy
│   └── test_generator.py        # Validation tests for JSON output formatting
├── .gitignore
├── requirements.txt             # Project dependencies
└── README.md
```
