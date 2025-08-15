# Memory Systems Demo API

FastAPI backend providing REST endpoints for Mem0 and Zep memory integrations.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export OPENAI_API_KEY="your-openai-key"
export MEM0_API_KEY="your-mem0-key" 
export ZEP_API_KEY="your-zep-key"
```

3. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Endpoints

### POST /mem0/query
Query using Mem0 memory system
```json
{
  "user_id": "user123",
  "query": "What did we discuss about the project?"
}
```

### POST /zep/query  
Query using Zep memory system
```json
{
  "user_id": "user123", 
  "query": "What did we discuss about the project?"
}
```

### GET /health
Health check endpoint

### GET /
API information and available endpoints

## Response Format
```json
{
  "response": "AI response text",
  "memory_saved": true,
  "context_found": true,
  "retrieved_memory": "Previous memories that were found and used for context"
}
```