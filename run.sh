#!/bin/bash

# Engineering Jobs RAG Chat - Startup Script
# Runs both backend and frontend in parallel

set -e

echo "🚀 Starting Engineering Jobs RAG Chat..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Backend setup
echo -e "${BLUE}📦 Setting up backend...${NC}"
cd backend

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install deps
if [ ! -f ".env" ]; then
    echo "  ⚠️  .env file not found. Copy from .env.example and add GROQ_API_KEY"
    cp .env.example .env
fi

echo "  Installing Python dependencies..."
pip install -q -r requirements.txt

# Check if data is ingested
if [ ! -d "jobs_db" ]; then
    echo "  Ingesting dataset into ChromaDB..."
    python ingest.py
fi

# Start backend in background
echo -e "${GREEN}✅ Backend ready. Starting FastAPI...${NC}"
python main.py &
BACKEND_PID=$!

# Frontend setup
echo -e "${BLUE}📦 Setting up frontend...${NC}"
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "  Installing Node dependencies..."
    npm install -q
fi

echo -e "${GREEN}✅ Frontend ready. Starting Vite dev server...${NC}"
npm run dev &
FRONTEND_PID=$!

# Show access information
echo ""
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}✨ System is running!${NC}"
echo ""
echo -e "  ${BLUE}Frontend:${NC}  http://localhost:5173"
echo -e "  ${BLUE}Backend:${NC}   http://localhost:8000"
echo -e "  ${BLUE}API Docs:${NC}  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both services"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
