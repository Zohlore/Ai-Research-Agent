# AI Research & Reporting Agent

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.2.x-green.svg)](https://www.langchain.com/langgraph)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-orange.svg)](https://openai.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.58.x-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> An autonomous AI agent that researches any topic and generates professional, data-backed reports using real-time web searches.

##  What This Does

-  **Autonomous Research**: Breaks topics into 3-5 questions and performs real web searches
-  **Structured Output**: Generates validated JSON reports with Pydantic
-  **Professional Logging**: Comprehensive logging with file and console handlers
-  **Web Interface**: Clean Streamlit UI for non-technical users
-  **Export Options**: Download reports as JSON or Markdown

##  Sample Report

**Topic:** *"The impact of generative AI in software development in 2026"*

### Key Findings:

-  The global market for generative AI in software development is projected to grow from **$868.13 million in 2026** to **$13.47 billion by 2035** (CAGR of 35.62%)
-  Developers using AI tools like GitHub Copilot are **53.2% more likely** to pass all unit tests
-  Code generation and auto-completion will hold a **38% market share** by 2026
-  AI is reshaping the entire software development lifecycle, including testing, debugging, and DevOps

  Tech Stack

- **Python** 3.9+ – Core logic
- **LangGraph** – Agent orchestration with StateGraph
- **LangChain** – Tool binding and LLM integration
- **OpenAI GPT-4o-mini** – Language model
- **Tavily** – Web search API
- **Pydantic** – Data validation
- **Streamlit** – Web interface

  Architecture

┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Streamlit │────▶│ Agent │────▶│ Tavily │
│ UI │ │ (LangGraph)│ │ Search │
└─────────────┘ └─────────────┘ └─────────────┘
│
▼
┌─────────────┐
│ OpenAI │
│ GPT-4o │
└─────────────┘
│
▼
┌─────────────┐
│ Pydantic │
│ Validation│
└─────────────┘


##  Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-research-agent.git
cd ai-research-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Configure credentials
cp .env.example .env
# Edit .env with your API keys

Usage
Run the Web Application
streamlit run app.py

Then open http://localhost:8501 in your browser.


Enter API Keys
In the sidebar, enter your:

OpenAI API Key – from platform.openai.com

Tavily API Key – from app.tavily.com


Research a Topic
Enter a topic in the text area

Click "Start Research"

Watch the agent perform web searches

Review the structured report

Export Reports
JSON – For developers and APIs

Markdown – For documentation


Security Features
Environment Variables: No hardcoded credentials

API Key Validation: Checks for valid keys before execution

Error Handling: Graceful failures with user feedback

Logging: Full audit trail for debugging


Future Enhancements
Add chat history and conversation memory

Add email reports

Add PDF export

Add source citations

Add multi-language support

Add multiple agent types (Research, Analysis, Summary)


License
MIT – Feel free to use for your own projects!

Built as part of an AI/ML portfolio project.


---

### Step 5: Update `requirements.txt`

Make sure it has all dependencies:

```txt
langchain-core>=1.4.8
langchain-openai>=1.3.3
langgraph>=1.2.7
tavily-python>=0.7.26
streamlit>=1.58.0
python-dotenv>=1.2.2
pydantic>=2.13.4
requests>=2.34.2