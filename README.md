# Engineering Jobs RAG Chat 🚀

A production-grade RAG system that analyzes AI Engineer job requirements to provide career transition insights. Built with LangGraph, ChromaDB, FastAPI, and React.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              Frontend (React + Tailwind)             │
│  Dark-mode chat interface with markdown support     │
└────────────┬────────────────────────────────────────┘
             │ /api/chat
┌────────────▼────────────────────────────────────────┐
│           Backend (FastAPI + LangGraph)             │
│  ┌───────────────────────────────────────────────┐  │
│  │ Retrieve → Analyze → Generate Pipeline        │  │
│  │ ┌─────────┐  ┌────────┐  ┌──────────┐        │  │
│  │ │ChromaDB │→ │ Groq   │→ │Response  │        │  │
│  │ │(Vector) │  │(Llama) │  │+ Sources │        │  │
│  │ └─────────┘  └────────┘  └──────────┘        │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Features

- **RAG Pipeline**: Retrieve relevant jobs → Analyze relevance → Generate insights
- **Vector Search**: ChromaDB with sentence-transformers embeddings
- **LLM Integration**: Groq's Llama 3 for fast, low-latency responses
- **Clean UI**: Dark-mode developer aesthetic with markdown support
- **Source Citations**: Each answer includes the jobs it references
- **M1 Optimized**: Lightweight, efficient for Apple Silicon

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- GROQ_API_KEY from [console.groq.com](https://console.groq.com)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment (M1 optimized)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template and add your Groq API key
cp .env.example .env
# Edit .env and add: GROQ_API_KEY=your_key_here

# Ingest the dataset into ChromaDB
python ingest.py

# Start the API server
python main.py
```

The backend will be available at `http://localhost:8000`
- Health check: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The frontend will be available at `http://localhost:5173`

### 3. Test the System

1. Open `http://localhost:5173` in your browser
2. Ask a question like:
   - "What are the key skills for AI engineers?"
   - "What's the difference between an AI developer and ML engineer?"
   - "How do I transition into AI engineering?"

## Project Structure

```
engineering-jobs-rag-chat/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── rag_graph.py         # LangGraph orchestration
│   ├── ingest.py            # Data ingestion pipeline
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example         # Environment template
│   └── jobs_db/             # ChromaDB storage (after ingest)
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main React component
│   │   ├── main.tsx         # Entry point
│   │   ├── index.css        # Tailwind styles
│   │   └── components/
│   │       ├── ChatMessage.tsx
│   │       └── ChatInput.tsx
│   ├── vite.config.ts       # Vite configuration
│   ├── tailwind.config.js   # Tailwind CSS config
│   ├── package.json         # Node dependencies
│   └── index.html           # HTML entry point
│
└── README.md
```

## Environment Variables

### Backend (.env)
```
GROQ_API_KEY=your_groq_api_key_here
```

Get your free API key from [Groq Console](https://console.groq.com)

## API Endpoints

### `POST /api/chat`
Process a user question and return RAG response.

**Request:**
```json
{
  "question": "What skills do AI engineers need?"
}
```

**Response:**
```json
{
  "answer": "Based on recent job postings, AI engineers typically need...",
  "sources": [
    "AI Developer at Connecteam",
    "Machine Learning Engineer at TechCorp"
  ]
}
```

### `GET /health`
Health check endpoint.

### `GET /docs`
OpenAPI documentation.

## How It Works

1. **User Question** → Sent to `/api/chat` endpoint
2. **Retrieve** → Query ChromaDB for top 5 relevant jobs
3. **Analyze** → Use Groq/Llama to assess if results answer the question
4. **Generate** → Create thoughtful response with insights and citations
5. **Return** → Stream answer + sources to frontend

## Performance Notes

- **M1 Mac**: ~2-3 second response time (Groq API latency)
- **Embeddings**: Local sentence-transformers (~1-2 per query)
- **Vector Search**: ChromaDB cosine similarity in-memory

## Troubleshooting

### "GROQ_API_KEY not set"
- Make sure you created `.env` file in `backend/` directory
- Add your key: `GROQ_API_KEY=gsk_...`
- Restart the backend server

### "Connection refused" on frontend
- Ensure backend is running: `python main.py`
- Check that CORS is enabled (it is by default)
- Verify proxy config in `vite.config.ts`

### "No relevant jobs found"
- Run `python ingest.py` to ensure data is in ChromaDB
- Check that `jobs_db/` directory exists

### ChromaDB initialization error
- Delete `jobs_db/` directory: `rm -rf backend/jobs_db/`
- Re-run ingestion: `python ingest.py`

## Development

### Adding new LLM models
Edit `rag_graph.py` and change the `model` parameter in `client.chat.completions.create()`:
- `llama-3.1-70b-versatile` (default, fast and capable)
- `llama-3.1-8b-instant` (faster, less powerful)
- `gemma-7b-it` (efficient)
- See [Groq Models](https://console.groq.com/docs/models) for full list

### Customizing the prompt
Edit the prompt strings in `analyze_node()` and `generate_node()` in `rag_graph.py`

### Changing embedding model
In `ingest.py`, ChromaDB uses sentence-transformers by default. For custom embeddings, see [ChromaDB documentation](https://docs.trychroma.com/)

## Technologies Used

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18, TypeScript, Tailwind CSS, Vite | Modern UI with fast HMR |
| **Backend** | FastAPI, Pydantic | Type-safe API layer |
| **RAG** | LangGraph, LangChain | Workflow orchestration |
| **Embeddings** | sentence-transformers | Local, fast embeddings |
| **Vector DB** | ChromaDB | Persistent vector search |
| **LLM** | Groq (Llama 3) | Fast inference API |

## License

MIT

## Next Steps

- [ ] Add user feedback collection
- [ ] Implement conversation memory
- [ ] Add job filtering by location/salary
- [ ] Deploy to production (Vercel/Railway)
- [ ] Add authentication
- [ ] Create admin dashboard for dataset management
