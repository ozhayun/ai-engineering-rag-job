"""
Data ingestion pipeline for engineering jobs dataset.
Reads JSON, creates embeddings, and stores in ChromaDB.
"""

import json
import os
import sys
from pathlib import Path
import chromadb

def ingest_jobs(dataset_path: str, db_path: str = "./jobs_db"):
    """
    Ingest job data from JSON file into ChromaDB.

    Args:
        dataset_path: Path to the JSON dataset file
        db_path: Path where ChromaDB will be stored
    """

    # Load dataset
    print(f"Loading dataset from {dataset_path}...")
    with open(dataset_path, 'r', encoding='utf-8') as f:
        jobs = json.load(f)

    print(f"Found {len(jobs)} jobs")

    # Initialize ChromaDB with persistent storage (new API)
    print(f"Initializing ChromaDB at {db_path}...")
    client = chromadb.PersistentClient(path=db_path)

    # Create or get collection
    collection = client.get_or_create_collection(
        name="engineering_jobs",
        metadata={"hnsw:space": "cosine"}
    )

    # Add jobs to collection
    print("Adding jobs to ChromaDB...")
    documents = []
    metadatas = []
    ids = []

    for idx, job in enumerate(jobs):
        job_id = f"job_{idx}"

        title = job.get('title', 'Unknown Title')
        description = job.get('description', '')

        # Use title + description for embedding
        text = f"{title} {description}"

        # Extract company from description
        company = "Unknown"
        if description:
            text_lower = description.lower()

            # Pattern 1: "Who X is:" at the start
            if "who " in text_lower and " is:" in text_lower:
                start = text_lower.find("who ") + 4
                end = text_lower.find(" is:", start)
                if end > start:
                    company = description[start:end].strip()

            # Pattern 2: "X is seeking" or "X is looking"
            if company == "Unknown":
                for pattern in [" is seeking", " is looking", " is hiring"]:
                    if pattern in text_lower:
                        start = text_lower.rfind(" ", 0, text_lower.find(pattern)) + 1
                        end = text_lower.find(pattern, start)
                        if start < end:
                            candidate = description[start:end].strip()
                            # Must start with capital letter and not be a section header
                            if (candidate and
                                candidate[0].isupper() and
                                len(candidate) < 100 and
                                not any(x in candidate.lower() for x in ['about', 'description', 'job details', 'requirements', 'responsibilities', 'the job'])):
                                company = candidate
                                break

            # Pattern 3: First capitalized phrase in first 200 chars
            if company == "Unknown":
                first_part = description[:200]
                lines = [l.strip() for l in first_part.split('\n') if l.strip()]
                for line in lines:
                    if (line and
                        line[0].isupper() and
                        not line.endswith(':') and
                        len(line) < 100 and
                        not any(x in line.lower() for x in ['about', 'description', 'job', 'engineer', 'developer', 'we', 'the', 'are looking', 'are seeking'])):
                        company = line
                        break

        documents.append(text)
        metadatas.append({
            "title": title,
            "company": company[:100] if company else 'Unknown',  # Limit length
            "location": job.get('location', 'Not specified'),
            "salary": job.get('salary', 'Not specified'),
            "job_index": str(idx)
        })
        ids.append(job_id)

    # Add to collection in batches
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch_end = min(i + batch_size, len(documents))
        collection.add(
            documents=documents[i:batch_end],
            metadatas=metadatas[i:batch_end],
            ids=ids[i:batch_end]
        )
        print(f"  Added {batch_end}/{len(documents)} jobs")

    print("✅ Data ingestion complete!")
    return collection

if __name__ == "__main__":
    # Dataset path (uses local copy in backend directory)
    dataset_path = "./dataset.json"
    db_path = "./jobs_db"

    # Check if dataset exists
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset not found at {dataset_path}")
        print(f"   Make sure you have dataset.json in the backend directory")
        sys.exit(1)

    # Run ingestion
    ingest_jobs(dataset_path, db_path)
