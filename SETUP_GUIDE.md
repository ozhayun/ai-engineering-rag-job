# Setup Guide - Engineering Jobs RAG Chat

Complete step-by-step guide to get the system running on your M1 Mac.

## Prerequisites

### 1. Get Groq API Key (Free)

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Navigate to "Keys" section
4. Create a new API key
5. Copy the key (looks like: `gsk_...`)

**Groq provides free access to:**
- Llama 2 70B
- Mixtral 8x7B
- LLaMA 2 Chat 13B

### 2. Check System Requirements

```bash
# Check Python version (need 3.10+)
python3 --version

# Check Node version (need 18+)
node --version

# Install if needed:
# Python: https://www.python.org/downloads/
# Node: https://nodejs.org/
```

## Installation Steps

### Option A: Automatic Setup (Recommended)

```bash
cd /path/to/engineering-jobs-rag-chat

# Make script executable (if not already)
chmod +x run.sh

# Run the setup script
./run.sh
```

The script will:
- Create Python virtual environment
- Install all dependencies
- Ingest the dataset into ChromaDB
- Start both backend and frontend

Then open **http://localhost:5173** in your browser.

### Option B: Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your Groq API key
cat > .env << EOF
GROQ_API_KEY=your_key_here_gsk_xxxxx
EOF

# Ingest the dataset (this creates jobs_db/ directory)
python ingest.py

# Start the backend server (runs on http://localhost:8000)
python main.py
```

In a new terminal window:

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server (runs on http://localhost:5173)
npm run dev
```

## Verify Installation

### 1. Backend Health Check

```bash
curl http://localhost:8000/health
# Should return: {"status":"ok"}
```

### 2. API Documentation

Visit: http://localhost:8000/docs

You should see the Swagger UI with the `/api/chat` endpoint documented.

### 3. Frontend Access

Open http://localhost:5173 in your browser. You should see:
- Chat interface with welcome message
- Input box at the bottom
- Dark mode theme

## Test the System

1. Open http://localhost:5173
2. Type a question like:
   ```
   What skills do AI engineers need in 2024?
   ```
3. Press Enter or click the Send button
4. Wait for response (should take 2-5 seconds)

### Expected Response Pattern

```
✅ User Question
   └─ [Your question]

📚 AI Response
   └─ [Analysis of AI Engineer roles based on dataset]
   └─ Sources:
      → AI Developer at Connecteam
      → Senior AI Engineer at TechCorp
      → (etc.)
```

## Troubleshooting

### Issue: "GROQ_API_KEY not set"

**Solution:**
```bash
cd backend
cat > .env << EOF
GROQ_API_KEY=gsk_your_actual_key_here
EOF
```

Then restart the backend: `python main.py`

### Issue: "Connection refused" when opening frontend

**Possible causes:**
1. Backend not running
2. Backend running on different port

**Solution:**
```bash
# Make sure backend is running in another terminal
cd backend
source venv/bin/activate
python main.py
```

### Issue: "No module named 'chromadb'"

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Cannot find module 'react'"

**Solution:**
```bash
cd frontend
npm install
```

### Issue: "jobs_db not found" / "Data not ingested"

**Solution:**
```bash
cd backend
source venv/bin/activate
python ingest.py
```

This creates the `jobs_db/` directory with ChromaDB index.

### Issue: Port 8000 or 5173 already in use

**Kill existing processes:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

Or edit port numbers:
- Backend: Change `port=8000` in `backend/main.py` (last line)
- Frontend: Change `port: 5173` in `frontend/vite.config.ts`

## Understanding the Architecture

### Data Flow

```
User Question
    ↓
Frontend (React) → POST /api/chat
    ↓
Backend (FastAPI)
    ↓
LangGraph Pipeline:
    1️⃣  Retrieve Node
       └─ Query ChromaDB for top 5 jobs
    2️⃣  Analyze Node
       └─ Use Groq/Llama to assess relevance
    3️⃣  Generate Node
       └─ Create response with insights
    ↓
Send Response + Sources
    ↓
Frontend Displays Answer + Source List
```

### Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| **Frontend Framework** | React 18 | Modern, component-based UI |
| **Styling** | Tailwind CSS | Utility-first for dark mode |
| **Build Tool** | Vite | Fast development experience |
| **Backend Framework** | FastAPI | Type-safe, automatic docs |
| **Orchestration** | LangGraph | Stateful workflow management |
| **Embeddings** | Sentence-transformers | Local, CPU-efficient (M1) |
| **Vector DB** | ChromaDB | Simple, embedded vector search |
| **LLM** | Groq API | Fast inference (~200ms) |

## Next Steps After Setup

### 1. Customize the Prompt

Edit `backend/rag_graph.py`:

**For analyze_node():**
```python
prompt = f"""Your custom analysis prompt here
Question: {state['question']}
..."""
```

**For generate_node():**
```python
prompt = f"""Your custom generation prompt here
Sources: {jobs_text}
..."""
```

### 2. Add Your Own Dataset

Replace the dataset path in `backend/ingest.py`:
```python
dataset_path = "/path/to/your/dataset.json"
```

Format should be:
```json
[
  {
    "title": "Job Title",
    "description": "Job description...",
    "company": "Company Name",
    "location": "City, Country",
    "salary": "$X - $Y"
  }
]
```

### 3. Try Different LLM Models

Edit `backend/rag_graph.py` and change the model:

```python
response = client.chat.completions.create(
    model="llama2-70b-4096",  # Try different models
    messages=[...],
)
```

Available Groq models:
- `mixtral-8x7b-32768` (balanced, fast)
- `llama2-70b-4096` (most capable)
- `gemma-7b-it` (efficient)

### 4. Deploy to Production

See `README.md` for deployment options.

## Performance Tips

### M1 Mac Optimization

The system is already optimized for M1:
- **Local embeddings** via sentence-transformers (no network call)
- **Lightweight dependencies** using core LLM/vector DB tools
- **ChromaDB** stores vectors locally

### Expected Performance

- **First response:** 3-5 seconds (network + Groq API)
- **Subsequent responses:** 2-3 seconds (ChromaDB index grows, more accurate retrieval)
- **Embedding time:** ~50-100ms (local)
- **Groq API latency:** ~1500-2000ms (network dependent)

### Monitoring

```bash
# Check API response time
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health

# Monitor backend
watch -n 1 'curl http://localhost:8000/health'
```

## Getting Help

- **API Documentation:** http://localhost:8000/docs
- **Project README:** See `README.md`
- **Error messages:** Check browser console (F12) and backend terminal
- **Groq Models:** https://console.groq.com/docs/models
- **LangGraph Docs:** https://langchain-ai.github.io/langgraph/

## Next Session

To restart the system later:

```bash
cd engineering-jobs-rag-chat

# Option 1: Use the run script
./run.sh

# Option 2: Manual (in separate terminals)
# Terminal 1 - Backend:
cd backend
source venv/bin/activate
python main.py

# Terminal 2 - Frontend:
cd frontend
npm run dev
```

Then visit http://localhost:5173
