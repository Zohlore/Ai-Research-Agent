# Streamlit UI
import streamlit as st
import json
import time
from datetime import datetime
from agent import get_agent
from logger import logger

# Page configuration
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

# Header
st.markdown('<div class="main-header">🧠 AI Research & Reporting Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Autonomous research assistant powered by LangChain & OpenAI</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Enter your OpenAI API key. It will not be stored."
    )
    
    tavily_key = st.text_input(
        "Tavily API Key",
        type="password",
        help="Enter your Tavily API key for web search."
    )
    
    st.markdown("---")
    st.markdown("### 📊 Status")
    
    # Status indicators
    if api_key and tavily_key:
        st.success("✅ API Keys Configured")
    else:
        st.warning("⚠️ Please enter API keys")
    
    st.markdown("---")
    st.markdown("### 🚀 Features")
    st.markdown("""
    - ✅ Autonomous web research
    - ✅ Structured JSON output
    - ✅ Professional logging
    - ✅ Real-time feedback
    - ✅ Exportable reports
    """)
    
    st.markdown("---")
    st.markdown("### 📝 Tips")
    st.markdown("""
    - Be specific with your topic
    - Include context or subtopics
    - The agent makes multiple searches
    - Reports are always structured
    """)

# Main content area
col1, col2 = st.columns([3, 1])

with col1:
    # Input section
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

# Handle example load
if example_btn:
    topic = "The future of AI-powered customer support in B2B SaaS companies"

# Handle clear
if clear_btn:
    st.session_state['results'] = None
    st.rerun()

# Initialize session state
if 'results' not in st.session_state:
    st.session_state['results'] = None

# Research execution
if research_btn and topic:
    if not api_key or not tavily_key:
        st.error("❌ Please enter both API keys in the sidebar before starting.")
    else:
        with st.spinner("🔬 Researching... This may take 10-20 seconds."):
            try:
                # Update environment variables
                import os
                os.environ['OPENAI_API_KEY'] = api_key
                os.environ['TAVILY_API_KEY'] = tavily_key
                
                # Initialize agent
                agent = get_agent()
                
                # Start timer
                start_time = time.time()
                
                # Perform research
                result = agent.research(topic)
                
                # Calculate duration
                duration = time.time() - start_time
                
                # Store results
                st.session_state['results'] = result
                st.session_state['duration'] = duration
                
                # Log success
                logger.info(f"Research completed in {duration:.2f} seconds for '{topic}'")
                
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                logger.error(f"Application error: {str(e)}", exc_info=True)

# Display results
if st.session_state['results']:
    result = st.session_state['results']
    duration = st.session_state.get('duration', 0)
    
    # Show duration
    st.info(f"⏱️ Research completed in {duration:.2f} seconds")
    
    if result.get('success'):
        report = result['report']
        
        # Display report
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
        
        # Metadata
        st.markdown("---")
        st.markdown("### 📊 Report Metadata")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Topic", result.get('topic', 'N/A'))
        with col_m2:
            st.metric("Timestamp", report.get('research_timestamp', 'N/A')[:10])
        with col_m3:
            st.metric("Findings", len(findings))
        
        # Export options
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
            findings_text = "\n\n".join(
                f"**Finding {i + 1}:** {finding}"
                for i, finding in enumerate(findings)
            )
            markdown_report = f"""# {report.get('title')}

## Introduction
{report.get('introduction')}

## Key Findings
{findings_text}

## Conclusion
{report.get('conclusion')}

---
*Generated by AI Research Agent on {report.get('research_timestamp')}*
"""
            st.download_button(
                label="📥 Download Markdown",
                data=markdown_report,
                file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        # Show raw JSON in expander
        with st.expander("🔍 View Raw JSON"):
            st.json(report)
            
    else:
        # Error display
        st.markdown("""
        <div class="error-box">
            <strong>❌ Research Failed</strong><br>
            {error}
        </div>
        """.format(error=result.get('error', 'Unknown error')), unsafe_allow_html=True)
        
        # Show raw output if available
        if result.get('raw_output'):
            with st.expander("🔍 View Raw Output"):
                st.text(result['raw_output'])

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8rem;">
    Built using LangChain, OpenAI, and Streamlit
</div>
""", unsafe_allow_html=True)