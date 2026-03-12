# Engineering Jobs RAG Chat - Architecture Document

## System Overview

This is a production-grade RAG (Retrieval-Augmented Generation) system designed to analyze AI Engineer job postings and provide career transition insights. The system is built with a clear separation between the data retrieval pipeline and the user-facing interface.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Browser                             │
│              (http://localhost:5173)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                    HTTP POST /api/chat
                    {question: "..."}
                         │
┌────────────────────────▼────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                    │
│  • Type-safe request/response handling                      │
│  • CORS enabled for local development                       │
│  • Exposes REST API with auto-generated docs                │
└────────────────────────┬────────────────────────────────────┘
                         │
                    Invokes
                         │
┌────────────────────────▼────────────────────────────────────┐
│           LangGraph RAG Workflow (Stateful)                 │
│                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   │
│  │   RETRIEVE   │──▶│   ANALYZE    │──▶│  GENERATE    │   │
│  │              │   │              │   │              │   │
│  │ • ChromaDB   │   │ • Groq Llama │   │ • Groq Llama │   │
│  │ • Top 5 jobs │   │ • Relevance  │   │ • Formatted  │   │
│  │ • Cosine sim │   │ • Check if   │   │ • Sources    │   │
│  │   matching   │   │   answerable │   │ • Citations  │   │
│  └──────────────┘   └──────────────┘   └──────────────┘   │
│         │                   │                   │           │
│         └───────────────────┴───────────────────┘           │
│              Shared RAGState Dictionary                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                   Returns
                         │
         ┌───────────────────────────────────┐
         │  {answer: "...", sources: [...]}  │
         └───────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│           React Frontend (Port 5173)                        │
│                                                              │
│  • Markdown rendering with GFM support                      │
│  • Sources section with citations                          │
│  • Dark mode developer aesthetic                           │
│  • Auto-scroll to latest message                           │
│  • Loading states & error handling                         │
└─────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. Frontend (React + TypeScript)

**Directory:** `frontend/src/`

#### App.tsx (Main Component)
- Manages message state (user + assistant messages)
- Handles API communication via `/api/chat`
- Implements auto-scroll behavior
- Shows loading states during API calls

```typescript
interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  sources?: string[];
  isLoading?: boolean;
}
```

#### ChatMessage.tsx (Message Display)
- Renders markdown with syntax highlighting
- Shows sources as citations below assistant responses
- Uses `react-markdown` with GitHub Flavored Markdown support
- Styling: User messages (blue), Assistant messages (dark gray)

#### ChatInput.tsx (Input Handler)
- Textarea with auto-resize functionality
- Enter to send, Shift+Enter for newline
- Disabled during loading state
- Clear on successful submission

#### index.css (Tailwind Styles)
- Dark mode utilities via Tailwind
- Scrollbar customization
- Base typography setup

### 2. Backend (FastAPI + Python)

**Directory:** `backend/`

#### main.py (API Server)
```python
@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse
```

- **Health Check:** `GET /health`
- **Chat Endpoint:** `POST /api/chat`
- **Documentation:** `GET /docs` (Swagger UI)
- **CORS:** Enabled for localhost:5173

#### rag_graph.py (Workflow Orchestration)

**LangGraph State Machine:**

```python
class RAGState(TypedDict):
    question: str
    retrieved_jobs: List[JobResult]
    analysis: str
    final_answer: str
    sources: List[str]
```

**Three-stage Pipeline:**

1. **retrieve_node()**
   - Queries ChromaDB for top 5 similar jobs
   - Input: User question
   - Output: `retrieved_jobs` with relevance scores
   - Uses cosine distance conversion to similarity

2. **analyze_node()**
   - Sends retrieved jobs + question to Groq Llama
   - Determines if data answers the question
   - Output: Brief relevance analysis (2-3 sentences)
   - Temperature: 0.3 (deterministic)

3. **generate_node()**
   - Crafts thoughtful response based on analysis
   - Adds job citations as sources
   - Output: Formatted answer + source list
   - Temperature: 0.7 (creative but coherent)

#### ingest.py (Data Pipeline)

```python
def ingest_jobs(dataset_path: str, db_path: str = "./jobs_db")
```

- Loads JSON dataset (~199 AI engineer jobs)
- Extracts title + description for embedding
- Creates ChromaDB collection with metadata
- Batches inserts (100 at a time)
- Creates persistent `jobs_db/` directory

**Metadata stored:**
```python
{
    "title": "AI Developer",
    "company": "Connecteam",
    "location": "Tel Aviv, Israel",
    "salary": "$120k - $180k",
    "job_index": "0"
}
```

### 3. Vector Database (ChromaDB)

**Location:** `backend/jobs_db/`

**Configuration:**
- Storage: DuckDB + Parquet (persistent)
- Distance metric: Cosine similarity
- Embedding model: sentence-transformers (default in Chroma)
- Collection name: `engineering_jobs`

**Query Process:**
```
User Question (string)
    ↓
embedding (1536-dim vector)
    ↓
ChromaDB cosine search
    ↓
Top 5 results + distances
```

### 4. LLM Integration (Groq API)

**Provider:** Groq (Fast inference)
**Model:** Mixtral 8x7B (default) / Llama 2 70B (optional)
**Latency:** ~200-500ms per request
**Cost:** Free tier available

**Two use cases:**

1. **Analyze Stage**
   - Prompt: "Are these jobs relevant to the question?"
   - Max tokens: 200
   - Temperature: 0.3 (deterministic)

2. **Generate Stage**
   - Prompt: "Create insights about AI engineer roles"
   - Max tokens: 400
   - Temperature: 0.7 (creative)

## Data Flow (Detailed)

### Initial Setup
```
1. Load dataset.json (199 jobs)
   └─ Extract: title, description
   └─ Compute embeddings locally (sentence-transformers)

2. Store in ChromaDB
   └─ Persistent storage: backend/jobs_db/
   └─ Indexed by cosine similarity
```

### Runtime (User Query)
```
1. User types: "What skills do AI engineers need?"
   └─ Frontend: POST to /api/chat with question

2. FastAPI main.py receives request
   └─ Validates input (Pydantic)
   └─ Initializes RAGState
   └─ Invokes rag_workflow.invoke(state)

3. LangGraph executes:

   a) RETRIEVE NODE
      └─ ChromaDB.query(question_text, n_results=5)
      └─ Compute embedding of question
      └─ Find top 5 jobs by cosine similarity
      └─ State.retrieved_jobs = [Job1, Job2, Job3, Job4, Job5]

   b) ANALYZE NODE
      └─ Format jobs text
      └─ Send to Groq: "Are these relevant?"
      └─ Groq analyzes (2-3 sentence response)
      └─ State.analysis = "Yes, these show key skills..."

   c) GENERATE NODE
      └─ Format jobs + analysis
      └─ Send to Groq: "Create career advice based on these"
      └─ Groq generates detailed response
      └─ Extract source citations
      └─ State.final_answer = "Based on your question..."
      └─ State.sources = ["AI Developer at Connecteam", ...]

4. Return ChatResponse
   └─ answer: "Full response text"
   └─ sources: ["Job1", "Job2", ...]

5. Frontend renders
   └─ Display answer in markdown
   └─ Show sources section below
```

## Technology Decisions

### Why LangGraph?
- Stateful workflow management
- Clear node/edge abstraction
- Easy to add/modify steps
- Built-in tracing/debugging
- Type hints for safety

### Why ChromaDB?
- Embedded (no external DB needed)
- Persistent storage
- Simple vector search API
- M1 native support
- No query language to learn

### Why Groq?
- Free API tier
- ~200-500ms latency (good for M1)
- Multiple model options (Llama 3.1, Gemma, etc.)
- Simple API (OpenAI compatible)
- No rate limits on free tier

### Why React + Tailwind?
- Component reusability
- Tailwind's dark mode support
- Fast development with Vite
- TypeScript for safety
- Large ecosystem (react-markdown, etc.)

## Performance Characteristics

### Local Execution
- **Embedding:** 50-100ms (sentence-transformers on M1)
- **ChromaDB search:** 10-20ms (in-memory)
- **Groq API call:** 1500-2500ms (network dependent)
- **Total:** 2-3 seconds per query

### Bottleneck Analysis
1. **Network latency to Groq** (largest)
2. **Groq inference** (second largest)
3. Local embedding + retrieval (negligible)

### Scaling Considerations
- ChromaDB handles ~100k jobs efficiently
- For >1M jobs, consider dedicated vector DB (Pinecone, Weaviate)
- Groq free tier: reasonable throughput for demo/MVP
- Frontend: single-page app handles chat history in memory

## Error Handling

### Frontend
- Network errors caught and displayed to user
- Loading states prevent double-submission
- Graceful fallback messages

### Backend
- Pydantic validation on input
- Try-catch around RAG workflow
- HTTP 500 with error message if workflow fails
- Missing `.env` file handled gracefully

### Data Pipeline
- Check dataset file exists before ingestion
- Batch error handling in ChromaDB adds
- Graceful handling of malformed JSON

## Security Considerations

### API Security
- CORS configured (localhost only in dev)
- No authentication (add JWT for production)
- Input validation via Pydantic
- No sensitive data in responses

### Data Privacy
- Vector DB is local (no cloud storage)
- No user data logged
- API key in `.env` (not in code)
- Dataset is public job postings

### Recommendations for Production
1. Add authentication (API key or OAuth)
2. Rate limiting on `/api/chat`
3. Remove CORS wildcards, restrict to frontend domain
4. Audit logging for all API calls
5. Encrypt ChromaDB if needed (currently plain text)

## Extensibility Points

### Adding New Data Sources
```python
# In ingest.py
def ingest_from_api():
    # Fetch from LinkedIn API, Indeed, etc.
    # Transform to standard format
    # Call collection.add()
```

### Custom Prompts
```python
# In rag_graph.py, edit analyze_node() and generate_node()
prompt = f"""Your custom prompt here
Context: {additional_context}
"""
```

### Different Embedding Models
```python
# ChromaDB supports custom embeddings:
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
collection = client.get_or_create_collection(
    name="...",
    embedding_function=OpenAIEmbeddingFunction()
)
```

### Alternative LLM Providers
```python
# Replace Groq with OpenAI, Anthropic, etc.
# Just change the API call in generate_node()
from anthropic import Anthropic
client = Anthropic()
response = client.messages.create(...)
```

## Testing Strategy

### Unit Tests (Recommended Addition)
```python
# test_rag_graph.py
def test_retrieve_node():
    state = RAGState(question="test", ...)
    result = retrieve_node(state)
    assert len(result["retrieved_jobs"]) <= 5
```

### Integration Tests
```bash
# Test API endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}'
```

### E2E Tests (Recommended Addition)
```python
# Playwright/Cypress test
def test_ask_question():
    navigate("http://localhost:5173")
    type_question("What skills...")
    assert_response_appears()
    assert_sources_shown()
```

## Monitoring & Observability

### Current Logging
- Backend prints workflow progress
- Frontend logs errors to console

### Recommended Additions
```python
# Add structured logging
import logging
logger = logging.getLogger(__name__)

# Add metrics
from prometheus_client import Counter
api_calls = Counter('api_calls_total', 'Total API calls')

# Add tracing
from opentelemetry import trace
```

## Deployment Considerations

### For Production
1. **Backend:** Deploy to Railway, Fly.io, or AWS Lambda
2. **Frontend:** Deploy to Vercel, Netlify
3. **Vector DB:** Consider managed ChromaDB or migrate to Pinecone
4. **LLM:** Keep Groq (free) or switch to self-hosted if needed

### Environment Variables
```bash
GROQ_API_KEY=gsk_...  # Required
DATABASE_URL=...      # If using managed DB
LOG_LEVEL=INFO        # For logging
```

### CI/CD
```yaml
# GitHub Actions example
- name: Run tests
  run: pytest backend/
- name: Build frontend
  run: cd frontend && npm run build
- name: Deploy
  run: # Deploy commands
```

## Summary

This RAG system demonstrates:
- ✅ Clean separation of concerns (frontend/backend)
- ✅ Type safety (TypeScript + Python type hints)
- ✅ Scalable architecture (can add caching, async, etc.)
- ✅ Production-ready patterns (error handling, validation)
- ✅ Developer experience (auto-docs, hot reload)
- ✅ M1 optimization (local embeddings, no heavy deps)

The system is designed to be maintainable, extensible, and ready for both learning and production use.
