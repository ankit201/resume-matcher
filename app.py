"""
TechCorp AI Resume Matcher - Main Streamlit Application
=========================================================

Enterprise-grade AI-powered resume screening solution.
Demonstrates explainable AI and comprehensive resume matching.

Navigation:
- 🎯 Live Demo: Single resume matching with detailed analysis
-  Batch Processing: Multiple resume screening
"""

import streamlit as st
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="TechCorp AI Resume Matcher",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/resume-matcher',
        'Report a bug': "https://github.com/yourusername/resume-matcher/issues",
        'About': "# TechCorp AI Resume Matcher\n\nEnterprise AI-powered talent screening solution."
    }
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main theme colors - Professional tech company palette */
    :root {
        --primary-color: #0066CC;
        --secondary-color: #00A86B;
        --danger-color: #DC3545;
        --warning-color: #FFC107;
        --info-color: #17A2B8;
        --dark-color: #2C3E50;
        --light-color: #F8F9FA;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #0066CC 0%, #004C99 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid var(--primary-color);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .metric-card h3 {
        color: var(--dark-color);
        font-size: 1.1rem;
        margin: 0 0 0.5rem 0;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-color);
    }
    
    /* Info boxes */
    .info-box {
        background: #E3F2FD;
        border-left: 4px solid #2196F3;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    .success-box {
        background: #E8F5E9;
        border-left: 4px solid #4CAF50;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: #FFF3E0;
        border-left: 4px solid #FF9800;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: var(--light-color);
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        border-top: 1px solid #ddd;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("## 🎯 Navigation")
    st.markdown("---")
    
    # Navigation links
    st.markdown("""
    ### 📄 Pages
    - **🎯 Live Demo** - Test single resume matching
    - ** Batch Processing** - Multiple resume screening
    """)
    


# Main content
st.markdown("""
<div class="main-header">
    <h1>🎯 TechCorp AI Resume Matcher</h1>
    <p>Enterprise-grade AI-powered resume screening with explainability</p>
</div>
""", unsafe_allow_html=True)

# Welcome section
st.markdown("## 👋 Welcome to the AI Resume Matcher Demo")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
        <h3>🎯 Live Demo</h3>
        <p>Test single resume matching with detailed analysis and explanations</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <h3>� Batch Processing</h3>
        <p>Process multiple resumes efficiently with parallel analysis</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <h3>🤖 AI-Powered</h3>
        <p>Google Gemini 2.5 Flash for intelligent resume analysis</p>
    </div>
    """, unsafe_allow_html=True)

# Key features
st.markdown("---")
st.markdown("## ✨ Key Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🧠 Intelligent Matching
    - **5-Dimensional Analysis**: Technical skills, experience, education, cultural fit, growth potential
    - **Google Gemini 2.5 Flash**: Fast, intelligent LLM analysis
    - **Semantic Search**: Efficient pre-filtering with bi-encoder embeddings
    - **Explainable AI**: Clear reasoning for every decision
    - **Parallel Processing**: 3.6x faster with concurrent evaluations
    
    ### 🚀 Skills Matching
    - **LLM-Powered**: Intelligent understanding beyond keyword matching
    - **Semantic Understanding**: Recognizes skill equivalents and categories
    - **Context-Aware**: Understands frameworks, tools, and technologies
    - **Evidence-Based**: Provides explanations for each skill match
    """)

with col2:
    st.markdown("""
    ### 📊 Processing & Reports
    - **Batch Processing**: Screen multiple resumes efficiently
    - **Detailed Reports**: Comprehensive scoring breakdowns
    - **Export Options**: JSON format for integration
    - **Processing Metrics**: Track time and performance
    
    ### 🚀 Technical Excellence
    - **Gemini Native PDF**: Direct PDF parsing without text extraction
    - **Sentence Transformers**: Fast bi-encoder semantic search
    - **Modular Architecture**: Clean, maintainable codebase
    - **Cost Tracking**: Monitor API usage and expenses
    - **Two-Stage Pipeline**: Fast semantic filter + deep LLM analysis
    """)

# Problem statement
st.markdown("---")
st.markdown("## 🎯 Solving TechCorp's Challenges")

st.markdown("""
<div class="info-box">
    <h3>Current Pain Points</h3>
    <ul>
        <li><strong>40% False Rejection Rate</strong> - Qualified candidates rejected due to keyword-based screening</li>
        <li><strong>Slow Manual Review</strong> - Time-consuming manual screening process</li>
        <li><strong>Zero Transparency</strong> - No explanation for rejection decisions</li>
        <li><strong>Inconsistent Evaluation</strong> - Different reviewers apply different standards</li>
        <li><strong>Limited Scale</strong> - Can't efficiently process hundreds of resumes</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="success-box">
    <h3>Our Solution</h3>
    <ul>
        <li><strong>AI-Powered Analysis</strong> - Deep understanding beyond keywords with LLM intelligence</li>
        <li><strong>Fast Processing</strong> - 50 seconds per resume with parallel evaluation</li>
        <li><strong>Full Explainability</strong> - Clear reasoning for every decision and score</li>
        <li><strong>Consistent Standards</strong> - Same criteria applied to every candidate</li>
        <li><strong>Batch Processing</strong> - Efficiently screen large candidate pools</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Getting started
st.markdown("---")
st.markdown("## 🚀 Getting Started")

tab1, tab2, tab3 = st.tabs(["Quick Start", "Setup Guide", "API Configuration"])

with tab1:
    st.markdown("""
    ### 3-Step Quick Start
    
    1. **Upload Data**
       ```bash
       # Place PDFs in data directories
       cp your_resumes.pdf data/resumes/
       cp job_description.txt data/job_descriptions/
       ```
    
    2. **Navigate to Demo**
       - Click **"🎯 Live Demo"** in the sidebar
       - Or use the pages in the top navigation
    
    3. **Run Analysis**
       - Upload resume and job description
       - Click "Match Resume"
       - View detailed results and explanations
    """)

with tab2:
    st.markdown("""
    ### Installation & Setup
    
    ```bash
    # 1. Clone repository
    git clone https://github.com/yourusername/resume-matcher.git
    cd resume-matcher
    
    # 2. Run setup script (installs UV automatically)
    chmod +x setup.sh
    ./setup.sh
    
    # 3. Configure API keys
    cp .env.example .env
    nano .env  # Add your API keys
    
    # 4. Run application
    source .venv/bin/activate
    streamlit run app.py
    
    # Or use UV directly (no activation needed)
    uv run streamlit run app.py
    ```
    
    See [MIGRATION_NOTES.md](MIGRATION_NOTES.md) for detailed instructions.
    """)

with tab3:
    st.markdown("""
    ### API Key Configuration
    
    Edit `.env` file with your credentials:
    
    ```env
    # Required: Google Gemini for LLM analysis
    GOOGLE_API_KEY=AIza...
    GEMINI_MODEL=gemini-2.5-flash
    
    # Optional: Custom settings
    SEMANTIC_THRESHOLD=0.7
    MIN_MATCH_SCORE=60
    ```
    
    **API Key Source:**
    - Google AI Studio: https://makersuite.google.com/app/apikey
    
    **Note:** Gemini 2.5 Flash tier is currently free with rate limits. 
    Perfect for development and moderate production use.
    """)

# Footer
st.markdown("""
<div class="footer">
    <p><strong>TechCorp AI Resume Matcher</strong> v2.0</p>
    <p>Built with Streamlit, Google Gemini 2.5 Flash, Sentence Transformers, and ❤️</p>
    <p>© 2024 TechCorp Global. For demonstration purposes.</p>
</div>
""", unsafe_allow_html=True)
