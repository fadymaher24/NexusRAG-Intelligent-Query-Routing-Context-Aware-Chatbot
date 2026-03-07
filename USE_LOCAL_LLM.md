# Using Local LLM with Ollama (Free Alternative)

Instead of using Together AI (paid), you can run a local LLM using Ollama.

## Setup Ollama

1. **Install Ollama** (on Fedora):

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

2. **Start Ollama**:

```bash
ollama serve
```

3. **Pull a model** (in another terminal):

```bash
ollama pull llama3.2:3b
```

4. **Update your .env file**:

```env
# Use Ollama instead of Together AI
LLM_MODEL=llama3.2:3b
LLM_API_KEY=
LLM_API_BASE_URL=http://localhost:11434/v1
```

5. **Restart your Flask application**:

```bash
python main.py
```

## Benefits

- ✅ Completely free
- ✅ No API key needed
- ✅ Works offline
- ✅ Private (data stays on your machine)

## Downsides

- ⚠️ Slower than cloud-based APIs
- ⚠️ Requires ~2GB RAM for the 3B model
- ⚠️ Need to keep Ollama running in background
