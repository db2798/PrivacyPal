"""This script authenticates with the Google Gemini API using your environment key 
and prints a list of all available models that support text generation, helping you 
identify valid model names for your project."""

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ No API Key found.")
else:
    genai.configure(api_key=api_key)
    print("🔍 querying Google for available models...")
    try:
        found = False
        for m in genai.list_models():
            # We only care about models that can generate text
            if 'generateContent' in m.supported_generation_methods:
                print(f"AVAILABLE: {m.name}")
                found = True
        
        if not found:
            print("❌ No text generation models found. Check your API Key permissions.")
    except Exception as e:
        print(f"❌ Error: {e}")