import os
import sys
import json
import re
from typing import Dict, Any, List, TypedDict, Annotated
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import StructuredTool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from tavily import TavilyClient

from models import ResearchReport
from logger import logger
from cache import cache          # <-- ADD THIS AT THE TOP

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

class ResearchAgent:
    def __init__(self):
        logger.info("Initializing Research Agent...")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not self.openai_api_key or not self.tavily_api_key:
            raise ValueError("Missing API keys in .env or environment variables")

        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, api_key=self.openai_api_key)
        self.tavily = TavilyClient(api_key=self.tavily_api_key)

        self.tools = self._create_tools()
        self.graph = self._build_graph()
        self.app = self.graph.compile()
        logger.info("Research Agent initialized successfully")

    # ... (keep the rest of the methods as they are, but update `research` method to use cache)

    def research(self, topic: str) -> Dict[str, Any]:
        # Check cache first
        cached = cache.get(topic)
        if cached:
            logger.info(f"✅ Returning cached result for: {topic[:50]}...")
            return cached

        logger.info(f"Starting fresh research on topic: '{topic}'")
        initial_state = {
            "messages": [{
                "role": "user",
                "content": f"""Research this topic thoroughly and provide a comprehensive report: {topic}

You MUST use the web_search tool to gather REAL information. Follow these steps:
1. Break the topic into 3-5 specific questions.
2. For EACH question, use web_search to find real facts, statistics, and data.
3. After at least 3 searches, synthesize the information into a report.

Your final report MUST have:
- A descriptive title
- An introduction
- 3-5 key findings with specific numbers/data from your searches
- A conclusion

Start now by doing your first web_search."""
            }]
        }

        try:
            result = self.app.invoke(initial_state)
            output = result['messages'][-1].content
            logger.info("Agent completed research")
        except Exception as e:
            logger.error(f"Graph execution failed: {e}")
            return {"success": False, "error": str(e), "topic": topic}

        # Parse output into report...
        # (existing parsing logic)

        # After you have `report_dict`, cache the result before returning
        # (you'll need to store the final result dict)
        # For simplicity, we'll create the result dict then cache it.
        try:
            json_match = re.search(r'\{.*\}', output, re.DOTALL)
            if json_match:
                report_dict = json.loads(json_match.group())
                report = ResearchReport(**report_dict)
            else:
                sections = self._extract_sections(output, topic)
                report = ResearchReport(
                    title=sections['title'],
                    introduction=sections['introduction'],
                    key_findings=sections['findings'],
                    conclusion=sections['conclusion']
                )
            result_dict = {"success": True, "report": report.dict(), "topic": topic, "raw_output": output}
            # Cache the result
            cache.set(topic, result_dict)
            return result_dict
        except Exception as e:
            logger.error(f"Parsing failed: {e}")
            return {"success": False, "error": f"Parsing error: {e}", "raw_output": output, "topic": topic}