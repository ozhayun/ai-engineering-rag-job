"""
RAG orchestration using LangGraph.
Implements retrieve → analyze → generate pipeline.
Focuses on finding common skills across all job descriptions.
"""

from typing import TypedDict, List
from langgraph.graph import StateGraph, END
import chromadb
from groq import Groq
import os
import re

# Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
GENERATION_TEMPERATURE = float(os.getenv("GENERATION_TEMPERATURE", "0.7"))
ROUTER_TEMPERATURE = float(os.getenv("ROUTER_TEMPERATURE", "0"))
MAX_TOKENS_GENERATE = int(os.getenv("MAX_TOKENS_GENERATE", "400"))
MAX_TOKENS_ROUTER = int(os.getenv("MAX_TOKENS_ROUTER", "5"))
MAX_QUESTION_LENGTH = int(os.getenv("MAX_QUESTION_LENGTH", "2000"))


def validate_question(question: str) -> str:
    """Validate and sanitize user question."""
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    sanitized = question.strip()
    if len(sanitized) > MAX_QUESTION_LENGTH:
        raise ValueError(f"Question exceeds maximum length ({MAX_QUESTION_LENGTH} characters)")

    return sanitized


class RAGState(TypedDict):
    """State for the RAG graph."""
    question: str
    all_jobs: str  # All job descriptions combined
    final_answer: str
    intent: str  # "on_topic" | "off_topic" — set by router_node


def retrieve_relevant_jobs(question: str, db_path: str = "./jobs_db", limit: int = 10) -> str:
    """Retrieve the most relevant job descriptions (to fit within token limits)."""
    print(f"📚 Retrieving {limit} most relevant jobs...")

    try:
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_collection(name="engineering_jobs")
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        raise RuntimeError("Unable to access job database. Please ensure data has been ingested with 'python ingest.py'")

    try:
        # Query for relevant jobs
        results = collection.query(
            query_texts=[question],
            n_results=limit,
            include=["documents", "metadatas"]
        )
    except Exception as e:
        print(f"❌ Query error: {str(e)}")
        raise RuntimeError("Error querying job database")

    job_texts = []
    if results and results["documents"]:
        for i, doc in enumerate(results["documents"][0], 1):
            title = results["metadatas"][0][i-1].get("title", f"Job {i}") if results["metadatas"] else f"Job {i}"
            # Limit each job description to avoid token explosion
            truncated_doc = doc[:1500] if len(doc) > 1500 else doc
            job_texts.append(f"## {title}\n\n{truncated_doc}")

    combined = "\n\n---\n\n".join(job_texts)
    print(f"  Loaded {len(job_texts)} relevant job descriptions")
    return combined


def retrieve_node(state: RAGState) -> RAGState:
    """Retrieve most relevant job descriptions based on user's question."""
    try:
        validated_question = validate_question(state['question'])
        print(f"🔍 Processing: {validated_question[:50]}...")

        all_jobs = retrieve_relevant_jobs(validated_question, limit=10)
        state["all_jobs"] = all_jobs
    except ValueError as e:
        print(f"❌ Validation error: {str(e)}")
        state["all_jobs"] = ""
        raise

    return state


def generate_node(state: RAGState) -> RAGState:
    """Generate insights based on the user's specific question."""
    print("✍️  Analyzing jobs based on your question...")

    if not state["all_jobs"]:
        state["final_answer"] = "No job descriptions found in database."
        return state

    try:
        # Validate API key
        if not os.getenv("GROQ_API_KEY"):
            raise RuntimeError("GROQ_API_KEY environment variable not set")

        client = Groq()

        # Strategic Career Analyst system prompt
        system_prompt = """You are a Strategic Career Analyst specializing in AI Engineering roles. You have deep expertise in identifying market trends, skill requirements, and career paths based on real job market data.

Your core responsibility is to synthesize insights from multiple job postings to help professionals understand what the market demands.

KEY RULES:
1. Answer ONLY using information from the provided job postings
2. Never acknowledge lack of data by saying "Information not provided" — instead, synthesize and aggregate what IS present
3. Name specific frameworks and tools mentioned across postings (LangGraph, MCP, RAG, etc.) as market signals
4. Aggregate insights across ALL provided jobs — never describe a single job in isolation
5. Do NOT mention specific company names
6. Use clear markdown formatting: headers for categories, bullet points for items
7. Show only the most common/important patterns
8. Be concise and actionable"""

        user_prompt = f"""Based on these AI Engineering job postings, answer the following question:

{state['question']}

Job Postings Data:
{state['all_jobs']}"""

        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=GENERATION_TEMPERATURE,
            max_tokens=MAX_TOKENS_GENERATE
        )

        state["final_answer"] = response.choices[0].message.content
        print("  Response generated")

    except RuntimeError as e:
        print(f"❌ Configuration error: {str(e)}")
        state["final_answer"] = f"Configuration error: {str(e)}"
    except Exception as e:
        print(f"❌ Groq API Error: {str(e)}")
        state["final_answer"] = "Error generating response. Please try again."

    return state


def router_node(state: RAGState) -> RAGState:
    """Route question to on-topic or off-topic handler."""
    print(f"🧭 Routing question...")

    try:
        # Validate API key
        if not os.getenv("GROQ_API_KEY"):
            raise RuntimeError("GROQ_API_KEY environment variable not set")

        client = Groq()

        router_prompt = f"""Classify this question as ONLY one of two categories:
- "on_topic": AI engineering jobs, ML/AI skills, frameworks (LangGraph, MCP, RAG, etc.), career advice for tech roles, Python/Go/Rust/TypeScript, system design, or anything about finding/evaluating AI engineering positions
- "off_topic": general knowledge questions, personal matters, other career fields, casual conversation

Question: {state['question']}

Respond with ONLY the word "on_topic" or "off_topic". No explanation."""

        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": router_prompt}],
            temperature=ROUTER_TEMPERATURE,
            max_tokens=MAX_TOKENS_ROUTER
        )

        intent = response.choices[0].message.content.strip().lower()
        state["intent"] = "on_topic" if "on_topic" in intent else "off_topic"
        print(f"  Classified as: {state['intent']}")

    except RuntimeError as e:
        print(f"❌ Configuration error: {str(e)}")
        state["intent"] = "off_topic"
    except Exception as e:
        print(f"❌ Router Error: {str(e)}")
        state["intent"] = "off_topic"

    return state


def off_topic_node(state: RAGState) -> RAGState:
    """Handle off-topic questions with a polite refusal."""
    print("💬 Handling off-topic question...")

    state["final_answer"] = "I specialize in AI Engineering roles. I don't have data on that topic, but I can help you find a path to your next AI Engineering job. Interested?"

    return state


def route_by_intent(state: RAGState) -> str:
    """Route to retrieve or off_topic_response based on intent."""
    return "retrieve" if state.get("intent") == "on_topic" else "off_topic_response"


def build_rag_graph():
    """Build the RAG workflow graph."""
    graph = StateGraph(RAGState)

    # Add nodes
    graph.add_node("router", router_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    graph.add_node("off_topic_response", off_topic_node)

    # Define flow
    graph.set_entry_point("router")

    # Conditional edges from router
    graph.add_conditional_edges("router", route_by_intent, {
        "retrieve": "retrieve",
        "off_topic_response": "off_topic_response"
    })

    # On-topic path
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)

    # Off-topic path
    graph.add_edge("off_topic_response", END)

    return graph.compile()


# Export compiled graph
rag_workflow = build_rag_graph()
