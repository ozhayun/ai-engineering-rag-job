"""
FastAPI backend for engineering jobs RAG chat.
Exposes /api/chat endpoint with streaming responses.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
import os
from typing import List
from dotenv import load_dotenv
from rag_graph import rag_workflow, RAGState

# Load environment variables from .env file
load_dotenv()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


# Models
class ChatRequest(BaseModel):
    """Request body for chat endpoint."""
    question: str


class ChatResponse(BaseModel):
    """Response body for chat endpoint."""
    answer: str


# Initialize FastAPI app
app = FastAPI(
    title="Engineering Jobs RAG Chat",
    description="RAG system for analyzing AI Engineer job requirements",
    version="1.0.0"
)

# Add slowapi limiter middleware
app.state.limiter = limiter
from slowapi.middleware import SlowAPIMiddleware

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Max 10 requests per minute."},
    )

app.add_middleware(SlowAPIMiddleware)

# Add security headers middleware (after CORS, before app logic)
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# CORS middleware - restricted to specific methods and headers (must be last added, first applied)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)


# Routes
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
def chat(request: Request, body: ChatRequest):
    """
    Chat endpoint that processes career questions using RAG.

    Args:
        request: HTTP request (required for rate limiting)
        body: ChatRequest with user question

    Returns:
        ChatResponse with answer and sources
    """
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    if len(body.question) > 2000:
        raise HTTPException(status_code=400, detail="Question exceeds maximum length (2000 characters)")

    try:
        # Initialize state
        initial_state: RAGState = {
            "question": body.question,
            "all_jobs": "",
            "final_answer": ""
        }

        # Run the RAG workflow
        final_state = rag_workflow.invoke(initial_state)

        return ChatResponse(
            answer=final_state["final_answer"]
        )

    except HTTPException:
        # Re-raise HTTP exceptions (like rate limit errors)
        raise
    except Exception as e:
        import traceback
        print(f"❌ Error processing request: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        # Return generic error message to client
        raise HTTPException(status_code=500, detail="An error occurred processing your request. Please ensure the backend is running and GROQ_API_KEY is configured.")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Engineering Jobs RAG Chat API",
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat (POST)",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn

    # Check for Groq API key
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️  Warning: GROQ_API_KEY environment variable not set")

    uvicorn.run(app, host="0.0.0.0", port=8000)
