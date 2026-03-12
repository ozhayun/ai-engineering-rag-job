#!/usr/bin/env python3
"""
Check available models on your Groq account.
"""

import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq()

try:
    # Get available models
    models = client.models.list()

    print("✅ Connected to Groq API successfully!\n")
    print("Available models:\n")

    for model in models.data:
        print(f"  • {model.id}")

    print(f"\nTotal: {len(models.data)} models available")

except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("\nMake sure:")
    print("  1. GROQ_API_KEY is set in backend/.env")
    print("  2. Your API key is valid")
    print("  3. You have an active Groq account")
