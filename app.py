import streamlit as st
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# ------------------------------------------------------------------
# 1. LOAD API KEYS: st.secrets (cloud) OR .env (local)
# ------------------------------------------------------------------
load_dotenv()  # local development

# Override environment variables with Streamlit secrets (if available)
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
if "TAVILY_API_KEY" in st.secrets:
    os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]

# Now import the agent (which reads from os.environ)
from agent import get_agent

# ------------------------------------------------------------------
# 2. PAGE CONFIG
# ------------------------------------------------------------------
st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .report-title {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 1rem 0;
    }
    .finding-item {
        background-color: #f0f2f6;
        padding: 0.8rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# 3. HEADER
# ------------------------------------------------------------------
st.markdown('<div class="main-header">🧠 AI Research & Reporting Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Autonomous research assistant powered by LangGraph & OpenAI</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
# 4. SIDEBAR – show key status
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Status")
    # Check if keys are loaded
    openai_ok = bool(os.getenv("OPENAI_API_KEY"))
    tavily_ok = bool(os.getenv("TAVILY_API_KEY"))
    if openai_ok and tavily_ok:
        st.success("✅ API Keys Configured")
    else:
        st.warning("⚠️ Please add API keys in Streamlit secrets or .env")

    st.markdown("---")
    st.markdown("### 🚀 Features")
    st.markdown("""
    - ✅ Autonomous web research
    - ✅ Structured JSON output
    - ✅ Professional logging
    - ✅ Real-time feedback
    - ✅ Exportable reports
    """)

# ------------------------------------------------------------------
# 5. MAIN AREA
# ------------------------------------------------------------------
topic = st.text_area(
    "🔍 What would you like to research?",
    placeholder="e.g., The impact of generative AI on software development in 2026",
    height=80
)

col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
with col_btn1:
    research_btn = st.button("🚀 Start Research", type="primary", use_container_width=True)
with col_btn2:
    example_btn = st.button("📋 Load Example", use_container_width=True)
with col_btn3:
    clear_btn = st.button("🗑️ Clear Results", use_container_width=True)

if example_btn:
    topic = "The future of AI-powered customer support in B2B SaaS companies"

if clear_btn:
    st.session_state['results'] = None
    st.rerun()

# Initialize session state
if 'results' not in st.session_state:
    st.session_state['results'] = None

# ------------------------------------------------------------------
# 6. RESEARCH EXECUTION
# ------------------------------------------------------------------
if research_btn and topic:
    if not openai_ok or not tavily_ok:
        st.error("❌ Missing API keys. Please set them in Streamlit secrets or .env.")
    else:
        with st.spinner("🔬 Researching... This may take 10-20 seconds."):
            try:
                agent = get_agent()
                start_time = time.time()
                result = agent.research(topic)
                duration = time.time() - start_time

                st.session_state['results'] = result
                st.session_state['duration'] = duration

            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

# ------------------------------------------------------------------
# 7. DISPLAY RESULTS
# ------------------------------------------------------------------
if st.session_state['results']:
    result = st.session_state['results']
    duration = st.session_state.get('duration', 0)

    st.info(f"⏱️ Research completed in {duration:.2f} seconds")

    if result.get('success'):
        report = result['report']

        st.markdown("---")
        st.markdown(f"## 📄 {report.get('title', 'Research Report')}")

        # Introduction
        st.markdown("### 📖 Introduction")
        st.write(report.get('introduction', ''))

        # Key Findings
        st.markdown("### 🔑 Key Findings")
        findings = report.get('key_findings', [])
        for i, finding in enumerate(findings, 1):
            st.markdown(f"""
            <div class="finding-item">
                <strong>Finding {i}:</strong> {finding}
            </div>
            """, unsafe_allow_html=True)

        # Conclusion
        st.markdown("### 🎯 Conclusion")
        st.write(report.get('conclusion', ''))

        # Sources (if available)
        sources = report.get('sources')
        if sources:
            st.markdown("### 📚 Sources")
            for source in sources:
                st.markdown(f"- {source}")

        # Export options
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
            markdown_report = f"""
# {report.get('title')}

## Introduction
{report.get('introduction')}

## Key Findings
{''.join([f'**Finding {i+1}:** {f}\n\n' for i, f in enumerate(findings)])}

## Conclusion
{report.get('conclusion')}

---
*Generated by AI Research Agent on {report.get('research_timestamp', datetime.now().isoformat())}*
"""
            st.download_button(
                label="📥 Download Markdown",
                data=markdown_report,
                file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )

        # Show raw JSON
        with st.expander("🔍 View Raw JSON"):
            st.json(report)

    else:
        st.error(f"❌ Research failed: {result.get('error', 'Unknown error')}")
        if result.get('raw_output'):
            with st.expander("🔍 View Raw Output"):
                st.text(result['raw_output'])

# ------------------------------------------------------------------
# 8. FOOTER
# ------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8rem;">
    Built with ❤️ using LangGraph, OpenAI, and Streamlit
</div>
""", unsafe_allow_html=True)