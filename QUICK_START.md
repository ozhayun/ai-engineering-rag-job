# Quick Start (5 Minutes)

## 1. One Command Setup

```bash
cd /Users/ozhayun/Projects/engineering-jobs-rag-chat
./run.sh
```

This automatically:
- ✅ Creates Python virtual environment
- ✅ Installs all dependencies
- ✅ Ingests the dataset
- ✅ Starts FastAPI backend
- ✅ Starts React frontend
- ✅ Opens http://localhost:5173

**If this works, skip to "Test It"**

---

## 2. If run.sh doesn't work, do this:

### Terminal 1 - Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env with your Groq API key
echo "GROQ_API_KEY=your_key_here" > .env

# First time: ingest the data
python ingest.py

# Start the server
python main.py
```

**You should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2 - Frontend

```bash
cd frontend
npm install
npm run dev
```

**You should see:**
```
VITE v5.0.8  ready in 234 ms

➜  Local:   http://localhost:5173/
```

---

## 3. Test It

### In your browser:

1. Open **http://localhost:5173**
2. You should see the chat interface
3. Type a question:
   ```
   What are the key skills for AI engineers?
   ```
4. Press Enter
5. Wait 2-3 seconds for response

### Expected output:

```
✨ Based on recent AI engineering job postings...
   → Key skills include: Python, Machine Learning...
   → Most roles require: LLMs, RAG systems...

📚 Sources:
   → AI Developer at Connecteam
   → Senior AI Engineer at TechCorp
```

---

## 4. Verify Everything Works

### Check Backend API
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok"}
```

### Check API Docs
Visit http://localhost:8000/docs
- Should see Swagger UI
- Click "Try it out" on `/api/chat`
- Enter: `{"question": "test"}`
- Should see response

### Check Frontend
Visit http://localhost:5173
- Dark interface visible
- Chat window works
- Can type and send

---

## 5. Common Issues

| Problem | Solution |
|---------|----------|
| "GROQ_API_KEY not set" | Edit `backend/.env` and add your key |
| Port 8000 in use | `lsof -ti:8000 \| xargs kill -9` |
| Port 5173 in use | `lsof -ti:5173 \| xargs kill -9` |
| "No such file or directory" | Make sure you're in project root |
| "ModuleNotFoundError" | Run `pip install -r requirements.txt` again |
| "No jobs found" | Run `python ingest.py` in backend directory |

---

## 6. Next Steps

- **See full setup:** Read `SETUP_GUIDE.md`
- **Understand architecture:** Read `ARCHITECTURE.md`
- **View all features:** Read `README.md`

---

## 7. Get Your Groq API Key (Free)

1. Go to https://console.groq.com
2. Sign up (free account)
3. Click "Keys" in sidebar
4. Create new key
5. Copy it (looks like: `gsk_...`)
6. Add to `backend/.env`:
   ```
   GROQ_API_KEY=gsk_xxxxx
   ```

---

## File Structure Quick Reference

```
engineering-jobs-rag-chat/
├── backend/
│   ├── main.py           ← FastAPI server
│   ├── rag_graph.py      ← RAG pipeline logic
│   ├── ingest.py         ← Data ingestion
│   ├── dataset.json      ← Job data
│   ├── requirements.txt   ← Python dependencies
│   └── .env              ← Your API key (create this)
│
└── frontend/
    ├── src/
    │   ├── App.tsx       ← Main React component
    │   ├── main.tsx      ← Entry point
    │   └── components/   ← UI components
    ├── package.json      ← Node dependencies
    └── vite.config.ts    ← Build config
```

---

## Testing Prompts

Try these questions to test the system:

1. **General:** "What skills do AI engineers need?"
2. **Specific:** "What's the difference between an AI developer and ML engineer?"
3. **Career:** "How do I transition into AI engineering?"
4. **Technical:** "What tools and frameworks are mentioned in AI roles?"
5. **Salary:** "What salary ranges are typical for AI engineers?"

Each should return:
- A thoughtful answer
- List of relevant jobs cited
- Insights specific to your dataset

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Send message |
| `Shift + Enter` | New line in input |
| `Ctrl + C` (terminal) | Stop servers |

---

## Performance Expectations

- **First response:** 3-5 seconds (includes Groq API call)
- **Subsequent:** 2-3 seconds (cached embeddings)
- **Should feel:** Responsive, not real-time

---

## Stop the System

Press `Ctrl + C` in the terminal where `run.sh` is running.

Or if you started manually:
- Terminal 1: `Ctrl + C`
- Terminal 2: `Ctrl + C`

---

## Run Again Later

```bash
cd /Users/ozhayun/Projects/engineering-jobs-rag-chat
./run.sh
```

The system will reuse existing:
- Virtual environment
- Node modules
- Ingested data

So it starts faster the next time!

---

Done! You now have a working RAG system. 🎉

For more details, check out the full documentation:
- `SETUP_GUIDE.md` - Complete setup walkthrough
- `README.md` - Full feature list and docs
- `ARCHITECTURE.md` - Technical deep dive
