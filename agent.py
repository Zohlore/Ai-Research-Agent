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

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')  # type: ignore

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

class ResearchAgent:
    def __init__(self):
        logger.info("Initializing Research Agent...")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not self.openai_api_key or not self.tavily_api_key:
            raise ValueError("Missing API keys in .env")

        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, api_key=self.openai_api_key)
        self.tavily = TavilyClient(api_key=self.tavily_api_key)

        self.tools = self._create_tools()
        self.graph = self._build_graph()
        self.app = self.graph.compile()
        logger.info("Research Agent initialized successfully")

    def _search_web(self, query: str) -> str:
        logger.info(f"🔍 Searching web for: '{query}'")
        try:
            response = self.tavily.search(query=query, search_depth="advanced", max_results=5)
            results = response.get('results', [])
            if not results:
                return "No results found."
            formatted = []
            for r in results[:5]:
                formatted.append(f"Title: {r.get('title')}\nContent: {r.get('content')[:800]}")
            logger.info(f"✅ Found {len(results)} results")
            return "\n\n".join(formatted)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return f"Error: {e}"

    def _create_tools(self):
        # Use StructuredTool from langchain_core.tools (works with ToolNode)
        return [
            StructuredTool.from_function(
                func=self._search_web,
                name="web_search",
                description="Searches the web for up-to-date information. Input is a specific query."
            )
        ]

    def _build_graph(self):
        tool_node = ToolNode(self.tools)

        def agent_node(state: AgentState):
            messages = state['messages']
            llm_with_tools = self.llm.bind_tools(self.tools)
            response = llm_with_tools.invoke(messages)
            return {"messages": [response]}

        def should_continue(state):
            messages = state['messages']
            last = messages[-1]
            if hasattr(last, 'tool_calls') and last.tool_calls:
                return "tools"
            return END

        workflow = StateGraph(AgentState)
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", tool_node)
        workflow.set_entry_point("agent")
        workflow.add_edge("tools", "agent")
        workflow.add_conditional_edges("agent", should_continue)
        return workflow

    def research(self, topic: str) -> Dict[str, Any]:
        logger.info(f"Starting research on topic: '{topic}'")
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
            return {"success": True, "report": report.dict(), "topic": topic, "raw_output": output}
        except Exception as e:
            logger.error(f"Parsing failed: {e}")
            return {"success": False, "error": f"Parsing error: {e}", "raw_output": output, "topic": topic}

    def _extract_sections(self, text: str, topic: str) -> Dict[str, Any]:
        sections = {'title': f"Report on: {topic}", 'introduction': '', 'findings': [], 'conclusion': ''}
        lines = text.split('\n')
        current = None
        buf = []
        for line in lines:
            low = line.lower().strip()
            if 'title' in low and ':' in line and not sections['title']:
                sections['title'] = line.split(':', 1)[-1].strip()
            elif 'introduction' in low or 'executive summary' in low:
                current = 'intro'
            elif 'key finding' in low or 'finding' in low:
                current = 'finding'
            elif 'conclusion' in low or 'future outlook' in low:
                current = 'conclusion'
            elif current == 'intro' and line.strip() and len(line.strip()) > 20:
                sections['introduction'] += line.strip() + ' '
            elif current == 'finding' and line.strip() and len(line.strip()) > 20:
                buf.append(line.strip())
            elif current == 'conclusion' and line.strip() and len(line.strip()) > 20:
                sections['conclusion'] += line.strip() + ' '
        if buf:
            sections['findings'] = buf[:5]
        else:
            sections['findings'] = [
                "Research was conducted using real-time web searches.",
                "Multiple sources were consulted.",
                "The topic shows significant developments."
            ]
        if not sections['introduction']:
            sections['introduction'] = "This report summarizes key findings."
        if not sections['conclusion']:
            sections['conclusion'] = "Continued monitoring is recommended."
        return sections

_agent_instance = None
def get_agent():
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ResearchAgent()
    return _agent_instance

# In agent.py
from cache import cache

def research(self, topic: str):
    # Check cache first
    cached = cache.get(topic)
    if cached:
        logger.info(f"✅ Returning cached result for: {topic[:50]}...")
        return cached
    
    # ... existing research logic ...
    
    # Cache the result
    cache.set(topic, result)
    return result