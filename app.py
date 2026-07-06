import streamlit as st
import os
import json
import time
from datetime import datetime

# ------------------------------------------------------------------
# 1. FORCE SECRETS INTO ENVIRONMENT (CRITICAL)
# ------------------------------------------------------------------
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
else:
    st.error("🚨 OPENAI_API_KEY not found in secrets!")

if "TAVILY_API_KEY" in st.secrets:
    os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]
else:
    st.error("🚨 TAVILY_API_KEY not found in secrets!")

from agent import get_agent

# ------------------------------------------------------------------
# 2. PAGE CONFIG
# ------------------------------------------------------------------
st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🧠",
    layout="wide"
)

# ------------------------------------------------------------------
# 3. SIDEBAR
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Status")

    openai_key = st.secrets.get("OPENAI_API_KEY", "")
    tavily_key = st.secrets.get("TAVILY_API_KEY", "")

    if openai_key and tavily_key:
        st.success("✅ API Keys Configured")
        st.caption(f"OpenAI: {openai_key[:8]}...{openai_key[-4:]}")
        st.caption(f"Tavily: {tavily_key[:8]}...{tavily_key[-4:]}")
    else:
        st.error("❌ API Keys Missing")
        st.code("""
        OPENAI_API_KEY = "sk-proj-..."
        TAVILY_API_KEY = "tvly-..."
        """, language="toml")

    st.markdown("---")
    st.markdown("### 🚀 Features")
    st.markdown("""
    - ✅ Autonomous web research
    - ✅ Structured JSON output
    - ✅ Professional logging
    - ✅ Real-time feedback
    """)

# ------------------------------------------------------------------
# 4. MAIN HEADER
# ------------------------------------------------------------------
st.title("🧠 AI Research & Reporting Agent")
st.markdown("Autonomous research assistant powered by LangGraph & OpenAI")

# ------------------------------------------------------------------
# 5. INPUT & BUTTONS
# ------------------------------------------------------------------
topic = st.text_area(
    "🔍 What would you like to research?",
    placeholder="e.g., The impact of generative AI on software development in 2026",
    height=80
)

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    research_btn = st.button("🚀 Start Research", type="primary", use_container_width=True)
with col2:
    example_btn = st.button("📋 Load Example", use_container_width=True)
with col3:
    clear_btn = st.button("🗑️ Clear Results", use_container_width=True)

if example_btn:
    topic = "The future of AI-powered customer support in B2B SaaS companies"

if clear_btn:
    st.session_state["results"] = None
    st.rerun()

if "results" not in st.session_state:
    st.session_state["results"] = None

# ------------------------------------------------------------------
# 6. RESEARCH EXECUTION
# ------------------------------------------------------------------
if research_btn and topic:
    if not openai_key or not tavily_key:
        st.error("❌ Missing API keys. Please set them in Streamlit secrets.")
    else:
        with st.spinner("🔬 Researching... This may take 10-20 seconds."):
            try:
                agent = get_agent()
                start_time = time.time()
                result = agent.research(topic)
                duration = time.time() - start_time
                st.session_state["results"] = result
                st.session_state["duration"] = duration
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.code(traceback.format_exc())

# ------------------------------------------------------------------
# 7. DISPLAY RESULTS
# ------------------------------------------------------------------
if st.session_state["results"]:
    result = st.session_state["results"]
    duration = st.session_state.get("duration", 0)

    st.info(f"⏱️ Research completed in {duration:.2f} seconds")

    if result.get("success"):
        report = result["report"]

        st.markdown("---")
        st.markdown(f"## 📄 {report.get('title', 'Research Report')}")

        st.markdown("### 📖 Introduction")
        st.write(report.get("introduction", ""))

        st.markdown("### 🔑 Key Findings")
        for i, finding in enumerate(report.get("key_findings", []), 1):
            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 0.8rem; border-radius: 0.5rem; margin: 0.5rem 0; border-left: 4px solid #1f77b4;">
                <strong>Finding {i}:</strong> {finding}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### 🎯 Conclusion")
        st.write(report.get("conclusion", ""))

        sources = report.get("sources")
        if sources:
            st.markdown("### 📚 Sources")
            for source in sources:
                st.markdown(f"- {source}")

        st.markdown("---")
        st.markdown("### 💾 Export Report")
        col_e1, col_e2 = st.columns(2)

        with col_e1:
            json_str = json.dumps(report, indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

        with col_e2:
            # Build markdown report without any backslashes inside f‑string expressions
            findings_text = ""
            for i, f in enumerate(report.get("key_findings", []), 1):
                findings_text += f"**Finding {i}:** {f}\n\n"

            markdown_report = f"""
# {report.get("title", "Research Report")}

## Introduction
{report.get("introduction", "")}

## Key Findings
{findings_text}

## Conclusion
{report.get("conclusion", "")}

---
*Generated by AI Research Agent on {report.get("research_timestamp", datetime.now().isoformat())}*
"""
            st.download_button(
                label="📥 Download Markdown",
                data=markdown_report,
                file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )

        with st.expander("🔍 View Raw JSON"):
            st.json(report)
    else:
        st.error(f"❌ Research failed: {result.get('error', 'Unknown error')}")
        if result.get("raw_output"):
            with st.expander("🔍 View Raw Output"):
                st.text(result["raw_output"])

# ------------------------------------------------------------------
# 8. FOOTER
# ------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8rem;">
    Built with ❤️ using LangGraph, OpenAI, and Streamlit
</div>
""", unsafe_allow_html=True)