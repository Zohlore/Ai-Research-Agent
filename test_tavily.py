# test_tavily.py
import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")
print(f"API Key: {api_key[:10]}...")

client = TavilyClient(api_key=api_key)

try:
    response = client.search("generative AI statistics 2026", max_results=3)
    print(f"✅ Found {len(response['results'])} results")
    for r in response['results'][:2]:
        print(f"Title: {r['title']}")
except Exception as e:
    print(f"❌ Error: {e}")